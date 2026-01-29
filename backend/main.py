from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import sys
import asyncio
from pathlib import Path
import logging

BACKEND_DIR = Path(__file__).parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from inference.triposr_runner import TripoSRPipeline
from blender.blender_preprocess import BlenderProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Roblox UGC Pipeline API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("temp", exist_ok=True)

app.mount("/files/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/files/uploads", StaticFiles(directory="uploads"), name="uploads")

triposr = TripoSRPipeline(lazy_load=True)
blender_processor = BlenderProcessor()


# pydantic models for request/response
class GenerationRequest(BaseModel):
    prompt: str
    style: str = "cartoon"
    negative_prompt: Optional[str] = None
    num_images: int = 4


class GenerationResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    current_step: str
    result_url: Optional[str] = None
    mesh_url: Optional[str] = None
    error: Optional[str] = None


# in-memory task store
tasks = {}
task_counter = 0


@app.get("/")
async def root():
    return {"message": "Roblox UGC Pipeline API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "triposr_initialized": triposr._initialized,
        "blender_available": blender_processor.blender_executable is not None
    }


@app.post("/generate/image-to-ugc", response_model=GenerationResponse)
async def generate_ugc_from_image(file: UploadFile = File(...)):
    """Generate UGC asset from uploaded image"""
    global task_counter
    
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    task_counter += 1
    task_id = f"task_{task_counter}"

    # save uploaded image
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._-")
    file_path = upload_dir / f"{task_id}_{safe_filename}"

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    tasks[task_id] = TaskStatus(
        task_id=task_id,
        status="queued",
        progress=0,
        current_step="Processing uploaded image",
    )

    asyncio.create_task(process_image_to_ugc(task_id, str(file_path)))

    return GenerationResponse(
        task_id=task_id, status="queued", message="UGC generation from image started"
    )


@app.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get status of a generation task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.get("/download/{task_id}")
async def download_result(task_id: str, format: str = "fbx"):
    """Download the generated UGC file"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    if task.status != "completed" or not task.result_url:
        raise HTTPException(
            status_code=400, detail="Task not completed or no result available"
        )

    return FileResponse(task.result_url, filename=f"ugc_{task_id}.rbxm")


async def process_text_to_ugc(task_id: str, request: GenerationRequest):
    """Background task to process text-to-UGC generation"""
    try:
        # generate images from text
        tasks[task_id].status = "processing"
        tasks[task_id].progress = 10
        tasks[task_id].current_step = "Generating images from text"

        images = await text2image.generate_images(
            prompt=request.prompt,
            style=request.style,
            negative_prompt=request.negative_prompt,
            num_images=request.num_images,
        )

        # generate 3d model
        tasks[task_id].progress = 40
        tasks[task_id].current_step = "Creating 3D model from images"

        mesh_data = await triposr.generate_3d_from_images(images)

        # process in blender
        tasks[task_id].progress = 70
        tasks[task_id].current_step = "Optimizing for Roblox"

        result_path = await blender_processor.process_for_roblox(mesh_data, task_id)

        # confirm completion
        tasks[task_id].progress = 100
        tasks[task_id].current_step = "Complete"
        tasks[task_id].status = "completed"
        tasks[task_id].result_url = result_path

    except Exception as e:
        tasks[task_id].status = "failed"
        tasks[task_id].error = str(e)
        tasks[task_id].current_step = "Failed"


async def process_image_to_ugc(task_id: str, image_path: str):
    """Background task to process image-to-UGC generation"""
    try:
        # step 1: processing image
        tasks[task_id].status = "processing"
        tasks[task_id].progress = 20
        tasks[task_id].current_step = "Processing uploaded image"
        logger.info(f"[{task_id}] Starting image processing: {image_path}")
        
        await asyncio.sleep(0.5)

        # step 2: generate 3d model
        tasks[task_id].progress = 50
        tasks[task_id].current_step = "Creating 3D model from image"
        logger.info(f"[{task_id}] Creating 3D model from image")

        try:
            mesh_path = await triposr.generate_3d_from_single_image(image_path)
            tasks[task_id].mesh_url = mesh_path
            logger.info(f"[{task_id}] 3D mesh generated: {mesh_path}")
        except Exception as e:
            logger.error(f"[{task_id}] TripoSR error: {e}")
            raise Exception(f"3D generation failed: {str(e)}")

        # step 3: process in Blender (if Blender is available)
        tasks[task_id].progress = 80
        tasks[task_id].current_step = "Optimizing for Roblox"
        
        result_path = mesh_path  # Default to the OBJ file
        
        if blender_processor.blender_executable:
            try:
                logger.info(f"[{task_id}] Running Blender processing")
                result_path = await blender_processor.roblox_preprocessing(mesh_path, task_id)
                logger.info(f"[{task_id}] Blender processing complete: {result_path}")
            except Exception as e:
                logger.warning(f"[{task_id}] Blender processing failed: {e}")
                logger.info(f"[{task_id}] Falling back to raw OBJ file")
                # continue with OBJ file if Blender fails
        else:
            logger.info(f"[{task_id}] Blender not available, using raw OBJ")
            tasks[task_id].current_step = "Blender not found - using OBJ format"

        # step 4: complete
        tasks[task_id].progress = 100
        tasks[task_id].current_step = "Complete"
        tasks[task_id].status = "completed"
        tasks[task_id].result_url = result_path
        logger.info(f"[{task_id}] Task completed")

    except Exception as e:
        logger.error(f"[{task_id}] Task failed: {e}")
        tasks[task_id].status = "failed"
        tasks[task_id].error = str(e)
        tasks[task_id].current_step = "Failed"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

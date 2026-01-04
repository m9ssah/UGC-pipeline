from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import asyncio
from pathlib import Path

# from inference.text2image_runner import Text2ImagePipeline  # TODO: implement later
from inference.triposr_runner import TripoSRPipeline
# from blender.blender_preprocess import BlenderProcessor  # TODO: implement later

app = FastAPI(title="Roblox UGC Pipeline API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # react dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# init ML pipelines
# text2image = Text2ImagePipeline()  # TODO: implement later
triposr = TripoSRPipeline()
# blender_processor = BlenderProcessor()  # TODO: implement later


# dantic models for request/response
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
    error: Optional[str] = None


# in-memory task store (prolly moving to redis later)
tasks = {}


@app.get("/")
async def root():
    return {"message": "Roblox UGC Pipeline API", "status": "running"}


@app.post("/generate/text-to-ugc", response_model=GenerationResponse)
async def generate_ugc_from_text(request: GenerationRequest):
    """Generate UGC asset from text prompt"""
    task_id = f"task_{len(tasks) + 1}"

    tasks[task_id] = TaskStatus(
        task_id=task_id, status="queued", progress=0, current_step="Initializing"
    )

    asyncio.create_task(process_text_to_ugc(task_id, request))

    return GenerationResponse(
        task_id=task_id, status="queued", message="UGC generation started"
    )


@app.post("/generate/image-to-ugc")
async def generate_ugc_from_image(file: UploadFile = File(...)):
    """Generate UGC asset from uploaded image"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    task_id = f"task_{len(tasks) + 1}"

    # save uploaded image
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{task_id}_{file.filename}"

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
async def download_result(task_id: str):
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
        # load + preprocess image
        tasks[task_id].status = "processing"
        tasks[task_id].progress = 20
        tasks[task_id].current_step = "Processing uploaded image"

        # gen 3d model
        tasks[task_id].progress = 50
        tasks[task_id].current_step = "Creating 3D model from image"

        mesh_data = await triposr.generate_3d_from_single_image(image_path)

        # process in blender
        tasks[task_id].progress = 80
        tasks[task_id].current_step = "Optimizing for Roblox"

        result_path = await blender_processor.process_for_roblox(mesh_data, task_id)

        # confirm completeion
        tasks[task_id].progress = 100
        tasks[task_id].current_step = "Complete"
        tasks[task_id].status = "completed"
        tasks[task_id].result_url = result_path

    except Exception as e:
        tasks[task_id].status = "failed"
        tasks[task_id].error = str(e)
        tasks[task_id].current_step = "Failed"


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    uvicorn.run(app, host="0.0.0.0", port=8000)

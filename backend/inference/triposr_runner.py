import numpy as np
from PIL import Image
import os
import sys
import logging
from pathlib import Path

TRIPOSR_PATH = Path(__file__).parent.parent.parent / "models" / "TripoSR"
if TRIPOSR_PATH.exists():
    sys.path.insert(0, str(TRIPOSR_PATH))
    logger_setup = logging.getLogger(__name__)
    logger_setup.info(f"Added TripoSR to path: {TRIPOSR_PATH}")
else:
    logger_setup = logging.getLogger(__name__)
    logger_setup.warning(f"TripoSR not found at: {TRIPOSR_PATH}")

# logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import torch
    TORCH_AVAILABLE = True
    
    if torch.cuda.is_available():
        GPU_AVAILABLE = True
        GPU_NAME = torch.cuda.get_device_name(0)
        logger.info(f"using: {GPU_NAME}")
    else:
        GPU_AVAILABLE = False
        logger.warning("using cpu")
        
except ImportError:
    TORCH_AVAILABLE = False
    GPU_AVAILABLE = False
    logger.error("pytorch not available")


class TripoSRPipeline:
    """
    TripoSR image-to-3D pipeline using PyTorch with ROCm.
    
    TripoSR: https://github.com/VAST-AI-Research/TripoSR
    """
    
    def __init__(self, lazy_load: bool = True):
        self.model = None
        self.device = None
        self._initialized = False
        
        if not TORCH_AVAILABLE:
            logger.error("cannot initialize pipeline: pytorch not available")
            return
            
        self.device = torch.device("cuda" if GPU_AVAILABLE else "cpu")
        logger.info(f"Pipeline will use device: {self.device}")
        
        if not lazy_load:
            self._load_model()
    
    def _load_model(self):
        if self._initialized:
            return
            
        try:
            from models.TripoSR.tsr.system import TSR
            
            logger.info("Loading TripoSR model from HuggingFace...")
            self.model = TSR.from_pretrained(
                "stabilityai/TripoSR",
                config_name="config.yaml",
                weight_name="model.ckpt"
            )
            self.model.to(self.device)
            self.model.eval()
            self._initialized = True
            logger.info("TripoSR model loaded successfully")
            
        except ImportError as e:
            logger.error(
                f"TripoSR import failed: {e}\n"
                f"Make sure TripoSR is cloned to: {TRIPOSR_PATH}\n"
                "And dependencies are installed"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load TripoSR model: {e}")
            raise

    def preprocess_image(self, image_path: str) -> Image.Image:
        try:
            image = Image.open(image_path).convert("RGB")
            logger.info(f"Loaded image: {image_path} ({image.size})")
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            raise

    def generate_3d(self, image_path: str, output_dir: str = "outputs") -> str:
        self._load_model()
        
        if not self.model:
            raise RuntimeError("TripoSR model not loaded")
        
        try:
            logger.info(f"Generating 3D model from: {image_path}")
            
            image = self.preprocess_image(image_path)
            
            with torch.no_grad():
                scene_codes = self.model([image], device=self.device)
                meshes = self.model.extract_mesh(scene_codes)
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            mesh_filename = f"mesh_{os.urandom(4).hex()}.obj"
            mesh_path = output_dir / mesh_filename
            
            # triposr returns trimesh objects
            meshes[0].export(str(mesh_path))
            
            logger.info(f"3D mesh saved to: {mesh_path}")
            return str(mesh_path)
            
        except Exception as e:
            logger.error(f"Error generating 3D model: {e}")
            raise

    def preprocess_multi_images(self, image_paths: list[str]) -> list[Image.Image]:
        """Preprocess multiple images for multi-view 3D reconstruction"""
        processed_images = []

        for image_path in image_paths[:4]:  # limited to 4 views
            processed_img = self.preprocess_image(image_path)
            processed_images.append(processed_img)

        # stack images along batch dimension
        if len(processed_images) == 1:
            return processed_images[0]
        else:
            return processed_images

    async def generate_3d_from_images(self, image_paths: list[str]) -> str:
        self._load_model()
        
        if not self.model:
            raise RuntimeError("TripoSR model not loaded")

        try:
            logger.info(f"Generating 3D model from {len(image_paths)} images")

            images = self.preprocess_multi_images(image_paths)

            with torch.no_grad():
                scene_codes = self.model(images, device=self.device)
                meshes = self.model.extract_mesh(scene_codes)

            # save mesh to temporary file
            output_dir = Path("temp/meshes")
            output_dir.mkdir(parents=True, exist_ok=True)

            mesh_file = output_dir / f"mesh_{os.urandom(4).hex()}.obj"
            meshes[0].export(str(mesh_file))

            logger.info(f"3D mesh saved to {mesh_file}")
            return str(mesh_file)

        except Exception as e:
            logger.error(f"Error generating 3D model: {e}")
            raise

    async def generate_3d_from_single_image(self, image_path: str) -> str:
        """Generate 3D mesh from a single image"""
        return await self.generate_3d_from_images([image_path])

    def save_mesh_as_obj(self, mesh_data: np.ndarray, output_path: str):
        """
        Save mesh data as OBJ file
        TODO: adapt based on actual model output format
        """
        try:
            with open(output_path, "w") as f:
                f.write("# Generated by TripoSR\n")
                self.write_placeholder_cube(f)

            logger.info(f"Mesh saved as OBJ: {output_path}")

        except Exception as e:
            logger.error(f"Error saving mesh: {e}")
            raise

    def write_placeholder_cube(self, file_handle):
        """
        Write a placeholder cube mesh (for testing purposes)
        """
        # simple cube vertices
        vertices = [
            [-1, -1, -1],
            [1, -1, -1],
            [1, 1, -1],
            [-1, 1, -1],  # Bottom face
            [-1, -1, 1],
            [1, -1, 1],
            [1, 1, 1],
            [-1, 1, 1],  # Top face
        ]

        # cube faces (triangulated)
        faces = [
            [1, 2, 3],
            [1, 3, 4],  # Bottom
            [5, 6, 7],
            [5, 7, 8],  # Top
            [1, 2, 6],
            [1, 6, 5],  # Front
            [3, 4, 8],
            [3, 8, 7],  # Back
            [2, 3, 7],
            [2, 7, 6],  # Right
            [1, 4, 8],
            [1, 8, 5],  # Left
        ]

        # write vertices
        for vertex in vertices:
            file_handle.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")

        # write faces
        for face in faces:
            file_handle.write(f"f {face[0]} {face[1]} {face[2]}\n")

    def cleanup_temp_meshes(self):
        """Clean up temporary mesh files"""
        temp_dir = Path("temp/meshes")
        if temp_dir.exists():
            for file in temp_dir.glob("*.obj"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete {file}: {e}")


# init global instance
triposr_pipeline = TripoSRPipeline()

import onnx
import onnxruntime as ort
import numpy as np
from PIL import Image
import os
import logging
from pathlib import Path
import tempfile

# logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TripoSRPipeline:
    def __init__(self):
        """Initialize TripoSR pipeline with ONNX Runtime and DirectML for AMD GPUs"""
        self.model_path = "models/triposr.onnx"
        self.session = None

        if not os.path.exists(self.model_path):
            logger.warning(f"TripoSR model not found at {self.model_path}")
            logger.info("You need to download the TripoSR ONNX model")
            return

        try:
            # trying to use DirectML if available, otherwise fallback to cpu
            providers = []

            available_providers = ort.get_available_providers()
            if "DmlExecutionProvider" in available_providers:
                providers.append("DmlExecutionProvider")
                logger.info("Using DirectML")

            providers.append("CPUExecutionProvider")

            # create inference session
            self.session = ort.InferenceSession(self.model_path, providers=providers)

            logger.info(
                f"TripoSR pipeline initialized with providers: {self.session.get_providers()}"
            )

            # get model input/output info
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            self.input_shape = self.session.get_inputs()[0].shape

            logger.info(f"Model input shape: {self.input_shape}")

        except Exception as e:
            logger.error(f"Failed to initialize TripoSR: {e}")
            self.session = None

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for TripoSR input"""
        try:
            # load and resize image
            image = Image.open(image_path).convert("RGB")

            # resize to model input size
            target_size = (256, 256)
            image = image.resize(target_size, Image.Resampling.LANCZOS)

            # convert to numpy array + normalize
            image_array = np.array(image).astype(np.float32)
            image_array = image_array / 255.0

            # add batch dimension and reorder to NCHW format
            image_array = np.transpose(image_array, (2, 0, 1))
            image_array = np.expand_dims(image_array, axis=0)

            return image_array

        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            raise

    def preprocess_multi_images(self, image_paths: list[str]) -> np.ndarray:
        """Preprocess multiple images for multi-view 3D reconstruction"""
        processed_images = []

        for image_path in image_paths[:4]:  # limited to 4 views
            processed_img = self.preprocess_image(image_path)
            processed_images.append(processed_img)

        # stack images along batch dimension
        if len(processed_images) == 1:
            return processed_images[0]
        else:
            return np.concatenate(processed_images, axis=0)

    async def generate_3d_from_images(self, image_paths: list[str]) -> str:
        """Generate 3D mesh from multiple images"""
        if not self.session:
            raise Exception("TripoSR pipeline not initialized")

        try:
            logger.info(f"Generating 3D model from {len(image_paths)} images")

            input_data = self.preprocess_multi_images(image_paths)

            outputs = self.session.run(
                [self.output_name], {self.input_name: input_data}
            )

            # process output (mesh vertices, faces, etc.)
            mesh_data = outputs[0]

            # save mesh to temporary file
            output_dir = Path("temp/meshes")
            output_dir.mkdir(parents=True, exist_ok=True)

            mesh_file = output_dir / f"mesh_{len(os.listdir(output_dir))}.obj"
            self.save_mesh_as_obj(mesh_data, str(mesh_file))

            logger.info(f"3D mesh saved to {mesh_file}")
            return str(mesh_file)

        except Exception as e:
            logger.error(f"Error generating 3D model: {e}")
            raise Exception(f"Failed to generate 3D model: {str(e)}")

    async def generate_3d_from_single_image(self, image_path: str) -> str:
        """Generate 3D mesh from a single image"""
        return await self.generate_3d_from_images([image_path])

    def save_mesh_as_obj(self, mesh_data: np.ndarray, output_path: str):
        """
        Save mesh data as OBJ file
        TODO: adapt based on actual model output format
        """
        try:
            # TripoSR typically outputs vertices and faces

            # Assuming mesh_data contains vertices and faces
            # You may need to adjust this based on the actual model output format

            with open(output_path, "w") as f:
                f.write("# Generated by TripoSR\n")

                # Write vertices (placeholder - adapt to your model output)
                # vertices = mesh_data[0]  # Adjust indexing based on model
                # for vertex in vertices:
                #     f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")

                # Write faces (placeholder - adapt to your model output)
                # faces = mesh_data[1]  # Adjust indexing based on model
                # for face in faces:
                #     f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

                # For now, create a simple placeholder cube
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


def print_model_download_instructions():
    """Print instructions for downloading the TripoSR model"""
    print("\n" + "=" * 60)
    print("TripoSR Model Download Instructions")
    print("=" * 60)
    print("The TripoSR ONNX model is required for 3D generation.")
    print("Please download it from one of these sources:")
    print("")
    print("1. Official TripoSR repository:")
    print("   https://github.com/VAST-AI-Research/TripoSR")
    print("")
    print("2. Hugging Face:")
    print("   https://huggingface.co/stabilityai/TripoSR")
    print("")
    print("3. Convert PyTorch model to ONNX:")
    print("   Follow the conversion guide in the repository")
    print("")
    print(f"Place the model file at: {os.path.abspath('models/triposr.onnx')}")
    print("=" * 60)


if not os.path.exists("models/triposr.onnx"):
    print_model_download_instructions()

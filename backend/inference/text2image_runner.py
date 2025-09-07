import torch
import os
import logging
from pathlib import Path
from PIL import Image

# logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    from diffusers import StableDiffusionXLPipeline
    from diffusers.schedulers import DPMSolverMultistepScheduler

    DIFFUSERS_AVAILABLE = True
    logger.info("Diffusers imported successfully")
except Exception as e:
    logger.warning(f"Failed to import diffusers: {e}")
    logger.info("Text-to-image functionality will be limited")
    DIFFUSERS_AVAILABLE = False
    StableDiffusionXLPipeline = None
    DPMSolverMultistepScheduler = None


# logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Text2ImagePipeline:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing Text2Image pipeline on {self.device}")

        if not DIFFUSERS_AVAILABLE:
            logger.warning(
                "Diffusers not available - text-to-image will use placeholder"
            )
            self.pipe = None
            return

        # loading Stable Diffusion XL model
        try:
            self.pipe = StableDiffusionXLPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True,
                variant="fp16" if self.device == "cuda" else None,
            )

            # optimize for AMD GPUs and CPU users
            if self.device == "cpu":
                # use DML for AMD GPUs if available
                try:
                    import torch_directml

                    self.device = torch_directml.device()
                    logger.info("Using DirectML for AMD GPU acceleration")
                except ImportError:
                    logger.info("DirectML not available, using CPU")

            self.pipe = self.pipe.to(self.device)

            # use faster scheduler
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config,
                use_karras_sigmas=True,
                algorithm_type="dpmsolver++",
            )

            self.pipe.enable_attention_slicing()

            logger.info("Text2Image pipeline initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            self.pipe = None

            logger.info("Text2Image pipeline initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            # fallback  to a lighter model or CPU-only mode
            self.pipe = None

    def enhance_prompt_for_roblox(self, prompt: str, style: str = "cartoon") -> str:
        """Enhance the user prompt for better Roblox-style results"""

        style_modifiers = {
            "cartoon": "cartoon style, clean, simple, colorful, roblox style, plastic materials",
            "realistic": "realistic, detailed textures, high quality, roblox compatible",
            "medieval": "medieval fantasy, armor, weapons, castle theme, roblox style",
            "sci-fi": "futuristic, cyberpunk, neon, technology, space theme, roblox style",
            "cute": "kawaii, adorable, pastel colors, soft, friendly, roblox style",
            "dark": "gothic, dark colors, mysterious, shadow, roblox style",
            "y2k": "early 2000s, retro, gyaru, bright colors, roblox style",
            "streetwear": "urban fashion, trendy, casual, vibrant colors, roblox style",
        }

        base_enhancement = "high quality, 8k, detailed, centered object, white background, clear lighting"
        style_modifier = style_modifiers.get(style, style_modifiers["cartoon"])

        enhanced_prompt = f"{prompt}, {style_modifier}, {base_enhancement}"

        return enhanced_prompt

    def get_negative_prompt(self, custom_negative: str = None) -> str:
        """Generate negative prompt for better quality"""
        base_negative = (
            "blurry, low quality, distorted, deformed, duplicate, "
            "extra limbs, mutation, bad anatomy, wrong anatomy, "
            "signature, complex background, "
            "cluttered, messy, dark, shadow, low resolution"
        )

        if custom_negative:
            return f"{base_negative}, {custom_negative}"
        return base_negative

    async def generate_images(
        self,
        prompt: str,
        style: str = "cartoon",
        negative_prompt: str = None,
        num_images: int = 4,
        num_inference_steps: int = 25,
        guidance_scale: float = 7.5,
    ) -> list[str]:
        """Generate images from text prompt"""

        if not self.pipe:
            logger.warning("No pipeline available, creating placeholder images")
            return await self.create_placeholder_images(prompt, num_images)

        try:
            # enhance prompts
            enhanced_prompt = self.enhance_prompt_for_roblox(prompt, style)
            full_negative_prompt = self.get_negative_prompt(negative_prompt)

            logger.info(
                f"Generating {num_images} images with prompt: {enhanced_prompt}"
            )

            # generate images
            with torch.no_grad():
                results = self.pipe(
                    prompt=enhanced_prompt,
                    negative_prompt=full_negative_prompt,
                    num_images_per_prompt=num_images,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    width=1024,
                    height=1024,
                )

            output_dir = Path("temp/generated_images")
            output_dir.mkdir(parents=True, exist_ok=True)

            image_paths = []
            for i, image in enumerate(results.images):
                image_path = (
                    output_dir / f"generated_{len(os.listdir(output_dir))}_{i}.png"
                )
                image.save(image_path)
                image_paths.append(str(image_path))
                logger.info(f"Saved image: {image_path}")

            return image_paths

        except Exception as e:
            logger.error(f"Error generating images: {e}")
            logger.info("Falling back to placeholder images")
            return await self.create_placeholder_images(prompt, num_images)

    async def create_placeholder_images(
        self, prompt: str, num_images: int
    ) -> list[str]:
        """Create placeholder images when real generation is not available"""
        logger.info(f"Creating {num_images} placeholder images for prompt: {prompt}")

        # create simple colored placeholder images
        output_dir = Path("temp/generated_images")
        output_dir.mkdir(parents=True, exist_ok=True)

        image_paths = []
        colors = [(255, 192, 203), (173, 216, 230), (144, 238, 144), (255, 218, 185)]

        for i in range(num_images):
            # create a simple colored rectangle
            color = colors[i % len(colors)]
            img = Image.new("RGB", (512, 512), color)

            image_path = output_dir / f"placeholder_{i}.png"
            img.save(image_path)
            image_paths.append(str(image_path))

        return image_paths

    async def generate_reference_views(
        self, prompt: str, style: str = "cartoon"
    ) -> list[str]:
        """Generate multiple reference views for better 3D reconstruction"""

        view_prompts = [
            f"{prompt}, front view",
            f"{prompt}, side view",
            f"{prompt}, back view",
            f"{prompt}, three quarter view",
        ]

        all_images = []
        for view_prompt in view_prompts:
            images = await self.generate_images(
                prompt=view_prompt,
                style=style,
                num_images=1,
                num_inference_steps=20,  # faster for reference views
            )
            all_images.extend(images)

        return all_images

    def cleanup_temp_images(self):
        """Clean up temporary generated images"""
        temp_dir = Path("temp/generated_images")
        if temp_dir.exists():
            for file in temp_dir.glob("*.png"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete {file}: {e}")


text2image_pipeline = Text2ImagePipeline()

#!/usr/bin/env python3
"""
Script to download and setup required models for the UGC pipeline
"""

import os
import requests
import subprocess
from pathlib import Path
import logging

# logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_file(url: str, destination: str):
    """Download a file from URL to destination with progress"""
    logger.info(f"Downloading {url}...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0
    
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded_size += len(chunk)
                
                if total_size > 0:
                    progress = (downloaded_size / total_size) * 100
                    print(f"\rProgress: {progress:.1f}%", end='', flush=True)
    
    print()
    logger.info(f"Downloaded {destination}")

def install_git_lfs():
    """Install Git LFS if not available"""
    try:
        subprocess.run(['git', 'lfs', 'version'], check=True, capture_output=True)
        logger.info("Git LFS is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Git LFS not found. Please install Git LFS:")
        logger.error("https://git-lfs.github.io/")
        return False

def download_triposr_model():
    """Download TripoSR model using Git LFS"""
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    triposr_path = model_dir / "triposr.onnx"
    
    if triposr_path.exists():
        logger.info("TripoSR model already exists")
        return True
    
    if not install_git_lfs():
        logger.error("Cannot download TripoSR without Git LFS")
        return False
    
    try:
        # clone TripoSR repository
        logger.info("Cloning TripoSR repository...")
        subprocess.run([
            'git', 'clone', 
            'https://huggingface.co/stabilityai/TripoSR',
            'temp_triposr'
        ], check=True)
        
        # search for ONNX model files
        temp_dir = Path("temp_triposr")
        onnx_files = list(temp_dir.glob("*.onnx"))
        
        if onnx_files:
            # copy the first onnx file found
            import shutil
            shutil.copy2(onnx_files[0], triposr_path)
            logger.info(f"Copied {onnx_files[0]} to {triposr_path}")
        else:
            logger.warning("No ONNX model found in TripoSR repository")
            # create placeholder file with instructions
            with open(triposr_path, 'w') as f:
                f.write("# Download from: https://huggingface.co/stabilityai/TripoSR\n")
        
        # cleanup
        shutil.rmtree("temp_triposr")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone TripoSR repository: {e}")
        return False
    except Exception as e:
        logger.error(f"Error downloading TripoSR: {e}")
        return False

def setup_stable_diffusion():
    """Setup Stable Diffusion XL (this will be downloaded automatically by diffusers)"""
    logger.info("Stable Diffusion XL will be downloaded automatically when first used")
    
    cache_dir = Path.home() / ".cache" / "huggingface" / "diffusers"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    return True

def main():
    """Main setup function"""
    logger.info("Setting up models for UGC Pipeline")
    
    os.makedirs("models", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    if not download_triposr_model():
        logger.warning("TripoSR model setup failed")
    
    setup_stable_diffusion()
    
    logger.info("Model setup completed!")
    logger.info("\nNext steps:")
    logger.info("1. Make sure Blender is installed")
    logger.info("2. Run 'npm start' to start the development server")
    logger.info("3. The first time you use text-to-image, SDXL will be downloaded")

if __name__ == "__main__":
    main()

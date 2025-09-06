"""
Simple test script to verify all imports work
"""

import sys
import os

# add parent directory to path
print(sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    print("Testing imports...")

    print("1. Testing FastAPI...")
    from fastapi import FastAPI

    print("✓ FastAPI imported successfully")

    print("2. Testing text2image module...")
    from backend.inference.text2image_runner import Text2ImagePipeline

    print("✓ Text2ImagePipeline imported successfully")

    print("3. Testing TripoSR module...")
    from backend.inference.triposr_runner import TripoSRPipeline

    print("✓ TripoSRPipeline imported successfully")

    print("4. Testing Blender module...")
    from backend.blender.blender_preprocess import BlenderProcessor

    print("✓ BlenderProcessor imported successfully")

    print("\nAll imports successful")

except Exception as e:
    print(f"import error: {e}")
    import traceback

    traceback.print_exc()

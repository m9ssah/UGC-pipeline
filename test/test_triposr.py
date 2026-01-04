import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

print("=" * 60)
print("Testing TripoSR Pipeline Setup")
print("=" * 60)

# Test 1: Check PyTorch and GPU
print("\n[1/5] Checking PyTorch installation...")
try:
    import torch
    print(f"✓ PyTorch version: {torch.__version__}")
    print(f"✓ CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠ No GPU detected - will use CPU (slower)")
except ImportError as e:
    print(f"✗ PyTorch not installed: {e}")
    sys.exit(1)

# Test 2: Check TripoSR path
print("\n[2/5] Checking TripoSR repository...")
triposr_path = Path(__file__).parent / "models" / "TripoSR"
if triposr_path.exists():
    print(f"✓ TripoSR found at: {triposr_path}")
    tsr_system = triposr_path / "tsr" / "system.py"
    if tsr_system.exists():
        print(f"✓ TSR system module exists")
    else:
        print(f"✗ TSR system module not found at {tsr_system}")
        sys.exit(1)
else:
    print(f"✗ TripoSR not found at: {triposr_path}")
    print("  Clone it with: git clone https://github.com/VAST-AI-Research/TripoSR.git models/TripoSR")
    sys.exit(1)

# Test 3: Check dependencies
print("\n[3/5] Checking dependencies...")
required_modules = {
    "PIL": "Pillow",
    "omegaconf": "omegaconf",
    "einops": "einops",
    "transformers": "transformers",
    "trimesh": "trimesh",
    "huggingface_hub": "huggingface-hub"
}

missing = []
for module, package in required_modules.items():
    try:
        __import__(module)
        print(f"✓ {package}")
    except ImportError:
        print(f"✗ {package} (missing)")
        missing.append(package)

if missing:
    print(f"\n⚠ Missing packages: {', '.join(missing)}")
    print(f"   Install with: pip install -r backend/triposr_requirements.txt")
    sys.exit(1)

# Test 4: Import TripoSR runner
print("\n[4/5] Testing TripoSR runner import...")
try:
    from inference.triposr_runner import TripoSRPipeline
    print("✓ TripoSR runner imported successfully")
except ImportError as e:
    print(f"✗ Failed to import TripoSR runner: {e}")
    sys.exit(1)

# Test 5: Initialize pipeline
print("\n[5/5] Initializing TripoSR pipeline...")
try:
    pipeline = TripoSRPipeline(lazy_load=True)
    print("✓ Pipeline initialized (lazy load mode)")
    print(f"✓ Device: {pipeline.device}")
except Exception as e:
    print(f"✗ Failed to initialize pipeline: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All checks passed!")
print("=" * 60)
print("\nNext steps:")
print("1. Place a test image in the project directory")
print("2. Run: python -c \"from backend.inference.triposr_runner import triposr_pipeline; print(triposr_pipeline.generate_3d('your_image.png'))\"")
print("3. Or create a web server with FastAPI (see next steps)")

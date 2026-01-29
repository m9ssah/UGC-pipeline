# Roblox UGC Pipeline

**Transform any image into a 3D Roblox asset**

This project provides an accessible way for non-technical users to generate Roblox 3D assets from images. Simply upload an image, and the pipeline will convert it into a 3D model ready for import into Roblox Studio.


## Features

- **Image-to-3D Generation**: Upload any image and get a 3D model using TripoSR AI
- **Roblox Optimization**: Automatic mesh processing for Roblox UGC requirements (decimation, triangulation, UV unwrapping)
- **User-Friendly Interface**: Simple web UI - no coding required!
- **FBX Export**: Ready-to-import files for Roblox Studio
- **Real-time Progress**: Track your generation status live

## Prerequisites

Before using this pipeline, you need:

1. **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download Node.js](https://nodejs.org/)
3. **Blender 3.5+** (optional but recommended) - [Download Blender](https://www.blender.org/download/)
4. **Roblox Studio** - For importing the final assets
5. **CUDA-compatible GPU** recommended for better performance 

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/UGC-pipeline.git
cd UGC-pipeline

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install PyTorch with CUDA (for GPU support)
# Visit https://pytorch.org/get-started/locally/ for your specific setup
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install frontend dependencies
cd app
npm install
cd ..
```

### 2. Run the Application

```bash
# Start both backend and frontend
npm start

# Or run separately:
# Terminal 1 - Backend (from project root):
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend (from project root):
cd app
npm start
```

### 3. Open the App

Navigate to **http://localhost:3000** in your browser.

## How to Use

### Generating a 3D Model

1. **Upload an Image**: Drag & drop or click to select an image of the object you want to convert
2. **Click Generate**: The AI will process your image and create a 3D model
3. **Download**: Once complete, download the FBX or OBJ file

### Importing to Roblox Studio

1. Open Roblox Studio and create/open your game
2. Go to **File → Import 3D** or use the **Avatar Importer** for accessories
3. Select the downloaded FBX/OBJ file
4. Adjust scale, position, and materials as needed
5. For UGC accessories, use the **Accessory Fitting Tool (AFT)**
6. Publish through the **Creator Hub**!

## 🏗️ Pipeline Architecture

```
Image Input
    ↓
┌─────────────────────────────────┐
│   TripoSR (Image-to-3D AI)      │
│   - Background removal          │
│   - 3D reconstruction           │
│   - Mesh extraction             │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│   Blender Processing            │
│   - Mesh decimation (<10K tri)  │
│   - Triangulation               │
│   - UV unwrapping               │
│   - FBX export                  │
└─────────────────────────────────┘
    ↓
FBX File (Roblox-Ready)
```

## Configuration

### Backend Settings

Edit `backend/main.py` to configure:
- CORS origins for different frontend URLs
- Output directories
- Mesh processing parameters

### Blender Settings

Edit `backend/blender/blender_preprocess.py` to adjust:
- Mesh decimation ratio (default: 0.3)
- UV unwrapping method
- Export scale

## 📁 Project Structure

```
UGC-pipeline/
├── app/                    # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── services/      # API service
│   │   └── App.tsx        # Main application
├── backend/               # FastAPI backend
│   ├── main.py           # API endpoints
│   ├── inference/        # ML pipelines
│   │   └── triposr_runner.py
│   └── blender/          # Blender processing
│       └── blender_preprocess.py
├── models/               # AI models
│   └── TripoSR/         # TripoSR model code
├── outputs/             # Generated models
├── uploads/             # Uploaded images
└── requirements.txt     # Python dependencies
```

## License

This project uses:
- [TripoSR](https://github.com/VAST-AI-Research/TripoSR) - MIT License
- [Stable Diffusion](https://github.com/CompVis/stable-diffusion) - CreativeML Open RAIL-M

## Acknowledgments

- [VAST-AI-Research](https://github.com/VAST-AI-Research) for TripoSR
- [Stability AI](https://stability.ai/) for the base models
- Roblox for the UGC ecosystem
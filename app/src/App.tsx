import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { ImageUpload } from './components/imageUpload';
import { ProgressTracker } from './components/progressTracker';
import { ExportButton } from './components/exportButton';
import api, { TaskStatus, HealthStatus } from './services/api';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [currentTask, setCurrentTask] = useState<TaskStatus | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // api health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthData = await api.healthCheck();
        setHealth(healthData);
      } catch (err) {
        setError('Backend Connection error. Server should be running on port 8000.');
      }
    };
    checkHealth();
  }, []);

  // poll task status when processing
  useEffect(() => {
    if (!currentTask || currentTask.status === 'completed' || currentTask.status === 'failed') {
      return;
    }

    const pollInterval = setInterval(async () => {
      try {
        const status = await api.getTaskStatus(currentTask.task_id);
        setCurrentTask(status);
        
        if (status.status === 'completed' || status.status === 'failed') {
          setIsProcessing(false);
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error('Failed to poll status:', err);
      }
    }, 1000);

    return () => clearInterval(pollInterval);
  }, [currentTask]);

  const handleImageSelected = useCallback((file: File) => {
    setSelectedFile(file);
    setCurrentTask(null);
    setError(null);
  }, []);

  const handleGenerate = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setError(null);

    try {
      const response = await api.uploadImage(selectedFile);
      setCurrentTask({
        task_id: response.task_id,
        status: 'queued',
        progress: 0,
        current_step: 'Starting...'
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start generation');
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setCurrentTask(null);
    setError(null);
    setIsProcessing(false);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Roblox UGC Generator</h1>
        <p className="subtitle">Transform any image into a 3D Roblox asset</p>
      </header>

      <main className="app-main">
        {/* Health Status */}
        {health && (
          <div className="health-status">
            <span className={`status-dot ${health.status === 'healthy' ? 'healthy' : 'unhealthy'}`} />
            <span>API: {health.status}</span>
            <span className="separator">|</span>
            <span>TripoSR: {health.triposr_initialized ? 'Ready' : 'Loading...'}</span>
            <span className="separator">|</span>
            <span>Blender: {health.blender_available ? 'Available' : 'Not found'}</span>
          </div>
        )}

        {error && (
          <div className="error-banner">
           {error}
          </div>
        )}

        {/* Step 1: Upload Image */}
        <section className="step-section">
          <h2>
            <span className="step-number">1</span>
            Upload an Image
          </h2>
          <p className="step-description">
            Upload an image of the object you want to convert into a 3D model.
            Works best with clear, single-object images on a simple background.
          </p>
          <ImageUpload 
            onImageSelected={handleImageSelected} 
            disabled={isProcessing}
          />
        </section>

        {/* Step 2: Generate */}
        {selectedFile && !currentTask && (
          <section className="step-section">
            <h2>
              <span className="step-number">2</span>
              Generate 3D Model
            </h2>
            <p className="step-description">
              Click the button below to start generating your 3D model using AI.
              This process typically takes 30-60 seconds.
            </p>
            <button 
              className="generate-btn"
              onClick={handleGenerate}
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing...' : 'Generate 3D Model'}
            </button>
          </section>
        )}

        {/* Progress Tracking */}
        {currentTask && (
          <section className="step-section">
            <h2>
              <span className="step-number">2</span>
              Generation Progress
            </h2>
            <ProgressTracker task={currentTask} />
          </section>
        )}

        {/* Step 3: Download */}
        {currentTask?.status === 'completed' && (
          <section className="step-section">
            <h2>
              <span className="step-number">3</span>
              Download & Import to Roblox
            </h2>
            <ExportButton task={currentTask} />
            
            <button className="reset-btn" onClick={handleReset}>
              🔄 Generate Another Model
            </button>
          </section>
        )}

        {/* Failed State */}
        {currentTask?.status === 'failed' && (
          <section className="step-section">
            <button className="retry-btn" onClick={handleReset}>
              🔄 Try Again
            </button>
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Powered by <a href="https://github.com/VAST-AI-Research/TripoSR" target="_blank" rel="noopener noreferrer">TripoSR</a>
          {' '}• Made for Roblox Creators
        </p>
      </footer>
    </div>
  );
}

export default App;


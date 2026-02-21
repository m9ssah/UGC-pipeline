import React, { useState } from 'react';
import api, { TaskStatus } from '../services/api';

interface ExportButtonProps {
  task: TaskStatus | null;
}

export const ExportButton: React.FC<ExportButtonProps> = ({ task }) => {
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async (format: string) => {
    if (!task || task.status !== 'completed') return;

    setDownloading(true);
    try {
      const blob = await api.downloadResult(task.task_id, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ugc_${task.task_id}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download file. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  if (!task || task.status !== 'completed') {
    return null;
  }

  return (
    <div className="export-buttons">
      <h3>Download Your 3D Model</h3>
      <p className="export-hint">
        Download the generated model and import it into Roblox Studio
      </p>
      
      <div className="button-group">
        {task.result_url?.endsWith('.fbx') ? (
          <button 
            className="download-btn primary"
            onClick={() => handleDownload('fbx')}
            disabled={downloading}
          >
            {downloading ? '⏳ Downloading...' : '📥 Download FBX (Roblox Ready)'}
          </button>
        ) : (
          <button 
            className="download-btn primary"
            onClick={() => handleDownload('obj')}
            disabled={downloading}
          >
            {downloading ? '⏳ Downloading...' : '📥 Download OBJ'}
          </button>
        )}
        
        {task.mesh_url && (
          <button 
            className="download-btn secondary"
            onClick={() => handleDownload('obj')}
            disabled={downloading}
          >
            📦 Download OBJ (Raw Mesh)
          </button>
        )}
      </div>

      <div className="roblox-instructions">
        <h4>📋 Next Steps for Roblox Studio:</h4>
        <ol>
          <li>Open Roblox Studio and create/open your game</li>
          <li>Go to <strong>File → Import 3D</strong> (or use Avatar Importer)</li>
          <li>Select the downloaded FBX/OBJ file</li>
          <li>Adjust scale and materials as needed</li>
          <li>Use <strong>Accessory Fitting Tool (AFT)</strong> if creating UGC accessories</li>
          <li>Publish your accessory through the Creator Hub!</li>
        </ol>
      </div>

      <style>{`
        .export-buttons {
          background: linear-gradient(135deg, rgba(72, 187, 120, 0.1), rgba(56, 161, 105, 0.1));
          border: 1px solid rgba(72, 187, 120, 0.3);
          border-radius: 12px;
          padding: 24px;
          margin: 20px 0;
          text-align: center;
        }

        .export-buttons h3 {
          color: #48bb78;
          margin: 0 0 8px 0;
        }

        .export-hint {
          color: #a0aec0;
          font-size: 14px;
          margin-bottom: 20px;
        }

        .button-group {
          display: flex;
          gap: 12px;
          justify-content: center;
          flex-wrap: wrap;
          margin-bottom: 24px;
        }

        .download-btn {
          padding: 14px 28px;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          border: none;
        }

        .download-btn.primary {
          background: linear-gradient(135deg, #48bb78, #38a169);
          color: white;
        }

        .download-btn.primary:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(72, 187, 120, 0.4);
        }

        .download-btn.secondary {
          background: rgba(255, 255, 255, 0.1);
          color: #e2e8f0;
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .download-btn.secondary:hover:not(:disabled) {
          background: rgba(255, 255, 255, 0.2);
        }

        .download-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .roblox-instructions {
          text-align: left;
          background: rgba(0, 0, 0, 0.2);
          border-radius: 8px;
          padding: 16px 20px;
        }

        .roblox-instructions h4 {
          color: #e2e8f0;
          margin: 0 0 12px 0;
        }

        .roblox-instructions ol {
          color: #a0aec0;
          margin: 0;
          padding-left: 20px;
          line-height: 1.8;
        }

        .roblox-instructions strong {
          color: #e2e8f0;
        }
      `}</style>
    </div>
  );
};

export default ExportButton;

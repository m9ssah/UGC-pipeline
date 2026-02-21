// 3D viewer component future implementation
import React from 'react';

interface Viewer3DProps {
  modelUrl?: string;
}

export const Viewer3D: React.FC<Viewer3DProps> = ({ modelUrl }) => {
  if (!modelUrl) {
    return (
      <div className="viewer-placeholder">
        <div className="placeholder-content">
          <span className="placeholder-icon">🎮</span>
          <p>3D Preview</p>
          <span className="placeholder-hint">Model will appear here after generation</span>
        </div>

        <style>{`
          .viewer-placeholder {
            width: 100%;
            height: 300px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px dashed #4a5568;
          }
          
          .placeholder-content {
            text-align: center;
            color: #718096;
          }
          
          .placeholder-icon {
            font-size: 48px;
            display: block;
            margin-bottom: 12px;
          }
          
          .placeholder-hint {
            font-size: 14px;
            display: block;
            margin-top: 8px;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="viewer-container">
      <div className="viewer-info">
        <span className="viewer-icon"></span>
        <p>Model Generated!</p>
        <span className="model-url">Ready for download</span>
      </div>

      <style>{`
        .viewer-container {
          width: 100%;
          height: 300px;
          background: linear-gradient(135deg, rgba(72, 187, 120, 0.1), rgba(56, 161, 105, 0.1));
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 2px solid rgba(72, 187, 120, 0.3);
        }
        
        .viewer-info {
          text-align: center;
          color: #48bb78;
        }
        
        .viewer-icon {
          font-size: 48px;
          display: block;
          margin-bottom: 12px;
        }
        
        .model-url {
          font-size: 14px;
          color: #a0aec0;
          display: block;
          margin-top: 8px;
        }
      `}</style>
    </div>
  );
};

export default Viewer3D;

import React, { useCallback, useState } from 'react';

interface ImageUploadProps {
  onImageSelected: (file: File) => void;
  disabled?: boolean;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({ onImageSelected, disabled }) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = useCallback((file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
      onImageSelected(file);
    }
  }, [onImageSelected]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (disabled) return;
    
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile, disabled]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  }, [disabled]);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  return (
    <div className="image-upload-container">
      <div 
        className={`upload-dropzone ${isDragging ? 'dragging' : ''} ${disabled ? 'disabled' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        {preview ? (
          <div className="preview-container">
            <img src={preview} alt="Preview" className="preview-image" />
            {!disabled && (
              <button 
                className="change-image-btn"
                onClick={() => {
                  setPreview(null);
                }}
              >
                Change Image
              </button>
            )}
          </div>
        ) : (
          <div className="upload-placeholder">
            <div className="upload-icon">📁</div>
            <p>Drag & drop an image here</p>
            <p className="upload-hint">or click to browse</p>
            <input
              type="file"
              accept="image/*"
              onChange={handleInputChange}
              disabled={disabled}
              className="file-input"
            />
          </div>
        )}
      </div>
      
      <style>{`
        .image-upload-container {
          width: 100%;
        }
        
        .upload-dropzone {
          border: 2px dashed #4a5568;
          border-radius: 12px;
          padding: 40px;
          text-align: center;
          transition: all 0.3s ease;
          background: rgba(255, 255, 255, 0.02);
          cursor: pointer;
          position: relative;
        }
        
        .upload-dropzone:hover:not(.disabled) {
          border-color: #667eea;
          background: rgba(102, 126, 234, 0.05);
        }
        
        .upload-dropzone.dragging {
          border-color: #667eea;
          background: rgba(102, 126, 234, 0.1);
          transform: scale(1.01);
        }
        
        .upload-dropzone.disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        
        .upload-placeholder {
          color: #a0aec0;
        }
        
        .upload-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }
        
        .upload-hint {
          font-size: 14px;
          color: #718096;
        }
        
        .file-input {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          opacity: 0;
          cursor: pointer;
        }
        
        .file-input:disabled {
          cursor: not-allowed;
        }
        
        .preview-container {
          position: relative;
        }
        
        .preview-image {
          max-width: 100%;
          max-height: 300px;
          border-radius: 8px;
          object-fit: contain;
        }
        
        .change-image-btn {
          position: absolute;
          bottom: 10px;
          right: 10px;
          padding: 8px 16px;
          background: rgba(0, 0, 0, 0.7);
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 12px;
          transition: background 0.2s;
        }
        
        .change-image-btn:hover {
          background: rgba(0, 0, 0, 0.9);
        }
      `}</style>
    </div>
  );
};

export default ImageUpload;

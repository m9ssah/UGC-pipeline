import React from 'react';
import { TaskStatus } from '../services/api';

interface ProgressTrackerProps {
  task: TaskStatus | null;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({ task }) => {
  if (!task) return null;

  const getStatusColor = () => {
    switch (task.status) {
      case 'completed': return '#48bb78';
      case 'failed': return '#f56565';
      case 'processing': return '#667eea';
      default: return '#a0aec0';
    }
  };

  const getStatusIcon = () => {
    switch (task.status) {
      case 'completed': return '✅';
      case 'failed': return '❌';
      case 'processing': return '⚙️';
      default: return '⏳';
    }
  };

  return (
    <div className="progress-tracker">
      <div className="progress-header">
        <span className="status-icon">{getStatusIcon()}</span>
        <span className="task-id">Task: {task.task_id}</span>
        <span className="status-badge" style={{ backgroundColor: getStatusColor() }}>
          {task.status.toUpperCase()}
        </span>
      </div>

      <div className="progress-bar-container">
        <div 
          className="progress-bar" 
          style={{ 
            width: `${task.progress}%`,
            backgroundColor: getStatusColor()
          }}
        />
        <span className="progress-text">{task.progress}%</span>
      </div>

      <div className="current-step">
        {task.current_step}
      </div>

      {task.error && (
        <div className="error-message">
          <strong>Error:</strong> {task.error}
        </div>
      )}

      <style>{`
        .progress-tracker {
          background: rgba(0, 0, 0, 0.3);
          border-radius: 12px;
          padding: 20px;
          margin: 20px 0;
        }

        .progress-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
        }

        .status-icon {
          font-size: 24px;
        }

        .task-id {
          color: #a0aec0;
          font-family: monospace;
        }

        .status-badge {
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: bold;
          color: white;
          margin-left: auto;
        }

        .progress-bar-container {
          height: 24px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          overflow: hidden;
          position: relative;
          margin-bottom: 12px;
        }

        .progress-bar {
          height: 100%;
          border-radius: 12px;
          transition: width 0.5s ease;
        }

        .progress-text {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          color: white;
          font-weight: bold;
          font-size: 12px;
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }

        .current-step {
          color: #e2e8f0;
          font-size: 14px;
          text-align: center;
        }

        .error-message {
          margin-top: 12px;
          padding: 12px;
          background: rgba(245, 101, 101, 0.2);
          border: 1px solid #f56565;
          border-radius: 8px;
          color: #feb2b2;
          font-size: 14px;
        }
      `}</style>
    </div>
  );
};

export default ProgressTracker;

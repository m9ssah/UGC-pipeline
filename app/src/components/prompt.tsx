// Prompt component - for future text-to-3D functionality
import React from 'react';

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({ onSubmit, disabled }) => {
  const [prompt, setPrompt] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      onSubmit(prompt);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="prompt-form">
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe what you want to create..."
        disabled={disabled}
        className="prompt-input"
      />
      <button type="submit" disabled={disabled || !prompt.trim()} className="prompt-submit">
        Generate
      </button>

      <style>{`
        .prompt-form {
          display: flex;
          gap: 12px;
        }
        
        .prompt-input {
          flex: 1;
          padding: 14px 20px;
          font-size: 16px;
          border: 2px solid #4a5568;
          border-radius: 8px;
          background: rgba(0, 0, 0, 0.3);
          color: #e2e8f0;
          transition: border-color 0.2s;
        }
        
        .prompt-input:focus {
          outline: none;
          border-color: #667eea;
        }
        
        .prompt-input::placeholder {
          color: #718096;
        }
        
        .prompt-submit {
          padding: 14px 28px;
          font-size: 16px;
          font-weight: 600;
          color: white;
          background: linear-gradient(135deg, #667eea, #764ba2);
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .prompt-submit:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .prompt-submit:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </form>
  );
};

export default PromptInput;


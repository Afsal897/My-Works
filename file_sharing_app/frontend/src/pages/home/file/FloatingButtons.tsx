import React from "react";
import { Link } from "react-router-dom";

interface FileData {
  file_id: number;
  filename: string;
  // add other file properties as needed
}

interface FloatingButtonsProps {
  uploadLink: string;
  uploadIcon: string; // path or import for upload icon image
  shareIcon: string;  // path or import for share icon image
  onFileDrop: (fileData: FileData) => void;
}

const FloatingButtons: React.FC<FloatingButtonsProps> = ({
  uploadLink,
  uploadIcon,
  shareIcon,
  onFileDrop,
}) => {
  return (
  <div className="position-fixed bottom-0 end-0 m-4 d-flex flex-column align-items-center gap-3" style={{ zIndex: 1000 }}>
    {/* Upload Button */}
    <Link to={uploadLink} className="text-decoration-none">
      <button
        className="btn btn-primary rounded-circle p-3 shadow-lg position-relative overflow-hidden"
        title="Upload files"
        aria-label="Upload files"
        style={{
          width: '56px',
          height: '56px',
          transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)'
        }}
      >
        <img 
          src={uploadIcon} 
          alt="" 
          className="position-absolute top-50 start-50 translate-middle"
          style={{ width: '24px', height: '24px' }}
          draggable={false}
        />
        <span className="position-absolute top-0 start-0 w-100 h-100 bg-white opacity-0 hover-opacity-10 transition-opacity"></span>
      </button>
    </Link>

    {/* Share Button */}
    <button
      className="btn btn-success rounded-circle p-3 shadow-lg position-relative overflow-hidden"
      title="Share files"
      aria-label="Share files"
      style={{
        width: '56px',
        height: '56px',
        transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)'
      }}
      onDragOver={(e) => {
        e.preventDefault();
        e.currentTarget.classList.add('bg-opacity-75');
      }}
      onDragLeave={(e) => {
        e.preventDefault();
        e.currentTarget.classList.remove('bg-opacity-75');
      }}
      onDrop={(e) => {
        e.preventDefault();
        e.currentTarget.classList.remove('bg-opacity-75');
        try {
          const data = e.dataTransfer.getData("text/plain");
          if (!data) return;
          const fileData: FileData = JSON.parse(data);
          onFileDrop(fileData);
        } catch {
          console.warn("Invalid data dropped");
        }
      }}
    >
      <img 
        src={shareIcon} 
        alt="" 
        className="position-absolute top-50 start-50 translate-middle"
        style={{ width: '24px', height: '24px' }}
        draggable={false}
      />
      <span className="position-absolute top-0 start-0 w-100 h-100 bg-white opacity-0 hover-opacity-10 transition-opacity"></span>
    </button>
  </div>
);
};

export default FloatingButtons;

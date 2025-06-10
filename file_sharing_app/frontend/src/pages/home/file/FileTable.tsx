import React from "react";

export interface FileItem {
  file_id: number;
  filename: string;
  date: string; // ISO string or timestamp
  size: string; // e.g., "10 KB"
}

interface FileTableProps {
  files: FileItem[];
  dropHighlight: boolean;
  handleDragOver: (e: React.DragEvent<HTMLDivElement>) => void;
  handleDrop: (e: React.DragEvent<HTMLDivElement>) => void;
  handleDragLeave: () => void;
  handleDelete: (filename: string, file_id: number) => void;
  handleDownload: (filename: string, file_id: number) => void; // New prop for download
  fileIcon: string; // URL or import of the file icon image
}

const FileTable: React.FC<FileTableProps> = ({
  files,
  dropHighlight,
  handleDragOver,
  handleDrop,
  handleDragLeave,
  handleDelete,
  handleDownload,
  fileIcon,
}) => {
  const EmptyDropArea = () => (
    <div className="text-center py-5 text-muted">
      <i className="bi bi-folder-x fs-1 text-secondary"></i>
      <p className="mt-2 mb-0">No files uploaded</p>
      <small className="text-muted">Drag and drop files here</small>
    </div>
  );

  const DesktopRow = ({ file }: { file: FileItem }) => (
    <tr key={file.file_id} className="align-middle">
      <td
        draggable
        onDragStart={(e) => {
          e.dataTransfer.setData("text/plain", JSON.stringify(file));
          const ghost = document.createElement("div");
          ghost.style.position = "absolute";
          ghost.style.top = "-9999px";
          ghost.style.left = "-9999px";
          ghost.style.pointerEvents = "none";
          ghost.style.display = "flex";
          ghost.style.padding = "4px 8px";
          ghost.style.backgroundColor = "white";
          ghost.style.borderRadius = "4px";
          ghost.style.boxShadow = "0 2px 4px rgba(0, 0, 0, 0.1)";
          ghost.innerHTML = `<img src="${fileIcon}" width="16" height="16" style="margin-right: 6px;" /><span>${file.filename}</span>`;
          document.body.appendChild(ghost);
          e.dataTransfer.setDragImage(ghost, 10, 10);
          setTimeout(() => document.body.removeChild(ghost), 0);
        }}
        className="ps-4"
        style={{ cursor: "grab", minWidth: "200px" }}
      >
        <div className="d-flex align-items-center">
          <img
            src={fileIcon}
            alt=""
            className="me-2"
            style={{ width: 20, height: 20 }}
            draggable={false}
          />
          <span className="text-truncate" style={{ maxWidth: "200px" }}>
            {file.filename}
          </span>
        </div>
      </td>
      <td className="text-muted small">
        {new Date(file.date).toLocaleDateString(undefined, {
          year: "numeric",
          month: "short",
          day: "numeric",
        })}
      </td>
      <td className="text-end pe-4 fw-semibold small">{file.size}</td>
      <td className="text-center">
        <div className="d-flex justify-content-center gap-2">
          <button
            className="btn btn-sm btn-outline-primary rounded-circle"
            style={{ width: "32px", height: "32px" }}
            onClick={() => handleDownload(file.filename, file.file_id)}
          >
            <i className="bi bi-file-arrow-down fs-6"></i>
          </button>
          <button
            className="btn btn-sm btn-outline-danger rounded-circle"
            style={{ width: "32px", height: "32px" }}
            onClick={() => handleDelete(file.filename, file.file_id)}
          >
            <i className="bi bi-trash3 fs-6"></i>
          </button>
        </div>
      </td>
    </tr>
  );

  return (
    <div
      className={`rounded-3 p-3 p-md-4 ${
        dropHighlight
          ? "border-primary border-3 shadow-sm bg-light"
          : "border border-light"
      }`}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onDragLeave={handleDragLeave}
      style={{
        backgroundColor: dropHighlight ? "#f0f8ff" : "white",
        transition: "all 0.2s ease",
      }}
    >
      {/* Desktop Table */}
      <div className="table-responsive rounded-3 border d-none d-md-block">
        <table className="table table-hover align-middle mb-0">
          <thead className="table-light">
            <tr>
              <th className="ps-4">Filename</th>
              <th>Date</th>
              <th className="text-end pe-4">Size</th>
              <th className="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            {files.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center py-5 text-muted">
                  <EmptyDropArea />
                </td>
              </tr>
            ) : (
              files.map((file) => <DesktopRow key={file.file_id} file={file} />)
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile View (Cards / Flex Rows) */}
      <div className="d-block d-md-none">
        {files.length === 0 ? (
          <EmptyDropArea />
        ) : (
          files.map((file) => (
            <div
              key={file.file_id}
              draggable
              onDragStart={(e) => {
                e.dataTransfer.setData("text/plain", JSON.stringify(file));
                const ghost = document.createElement("div");
                ghost.style.position = "absolute";
                ghost.style.top = "-9999px";
                ghost.style.left = "-9999px";
                ghost.style.pointerEvents = "none";
                ghost.style.padding = "4px 8px";
                ghost.style.backgroundColor = "white";
                ghost.style.borderRadius = "4px";
                ghost.style.boxShadow = "0 2px 4px rgba(0, 0, 0, 0.1)";
                ghost.style.fontSize = "14px";
                ghost.style.zIndex = "9999";
                ghost.innerHTML = `<img src="${fileIcon}" width="16" height="16" style="margin-right: 6px;" /><span>${file.filename}</span>`;
                document.body.appendChild(ghost);
                e.dataTransfer.setDragImage(ghost, 10, 10);
                setTimeout(() => document.body.removeChild(ghost), 0);
              }}
              className="border rounded-3 p-3 mb-3 shadow-sm"
              style={{ cursor: "grab" }}
            >
              <div className="d-flex justify-content-between align-items-center mb-2">
                <div className="d-flex align-items-center gap-2">
                  <img
                    src={fileIcon}
                    alt=""
                    style={{ width: 20, height: 20 }}
                    draggable={false}
                  />
                  <span
                    className="fw-semibold text-truncate"
                    style={{
                      maxWidth: "160px",
                      display: "inline-block",
                      overflow: "hidden",
                    }}
                    title={file.filename}
                  >
                    {file.filename}
                  </span>
                </div>
                <div className="d-flex gap-2">
                  <button
                    className="btn btn-sm btn-outline-primary rounded-circle"
                    title="Download"
                    onClick={() => handleDownload(file.filename, file.file_id)}
                  >
                    <i className="bi bi-file-arrow-down"></i>
                  </button>
                  <button
                    className="btn btn-sm btn-outline-danger rounded-circle"
                    onClick={() => handleDelete(file.filename, file.file_id)}
                    title="Delete"
                  >
                    <i className="bi bi-trash3"></i>
                  </button>
                </div>
              </div>
              <div className="text-muted small d-flex justify-content-between">
                <span>{new Date(file.date).toLocaleDateString()}</span>
                <span>{file.size}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FileTable;

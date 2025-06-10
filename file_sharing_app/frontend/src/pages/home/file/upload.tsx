import React, { useState, useEffect } from "react";
import Navbar from "../navbar";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import {
  handleFiles as validateAndHandleFiles,
  startUpload,
  removeFile,
} from "../../../components/upload";
import type { UploadItem } from "../../../components/upload";

const UploadPage: React.FC = () => {
  const [uploadItems, setUploadItems] = useState<UploadItem[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setUploadItems((items) =>
        items.filter((item) =>
          item.status === "success" && item.uploadedAt
            ? Date.now() - item.uploadedAt < 60 * 1000
            : true
        )
      );
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleFilesWrapper = (files: FileList | null) => {
    const newItems = validateAndHandleFiles(files);
    setUploadItems((prev) => [...prev, ...newItems]);
  };

  return (
    <>
      <Navbar />
      <ToastContainer position="top-right" autoClose={3000} />
      <div className="container py-5" style={{ maxWidth: "700px" }}>
        <h1 className="mb-4 text-center">Upload Files</h1>

        <div
          className="border border-secondary rounded p-5 text-center bg-light"
          style={{ cursor: "pointer" }}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            handleFilesWrapper(e.dataTransfer.files);
          }}
          onClick={() => document.getElementById("fileInput")?.click()}
        >
          <i
            className="bi bi-cloud-upload"
            style={{ fontSize: "3rem", color: "#6c757d" }}
          ></i>
          <p className="mt-3 mb-0 fw-semibold text-muted">
            Drag & drop files here or click to browse
          </p>
          <input
            type="file"
            multiple
            id="fileInput"
            style={{ display: "none" }}
            onChange={(e) => handleFilesWrapper(e.target.files)}
          />
        </div>

        {uploadItems.length > 0 && (
          <>
            <button
              onClick={() => startUpload(uploadItems, setUploadItems)}
              className="btn btn-primary mt-4 w-100"
              disabled={uploadItems.every((item) => item.status !== "pending")}
            >
              Start Upload
            </button>

            <div className="mt-4">
              {uploadItems.map((item, idx) => (
                <div
                  key={idx}
                  className={`mb-3 p-3 rounded shadow-sm border ${
                    item.status === "success"
                      ? "border-success"
                      : item.status === "error"
                      ? "border-danger"
                      : "border-secondary"
                  } d-flex flex-column flex-md-row justify-content-between align-items-center`}
                >
                  <div className="me-md-3" style={{ flex: 1 }}>
                    <div className="d-flex justify-content-between align-items-center">
                      <strong>{item.file.name}</strong>
                      <small>{(item.file.size / (1024 * 1024)).toFixed(2)} MB</small>
                    </div>

                    <div className="progress my-2" style={{ height: "10px" }}>
                      <div
                        className={`progress-bar ${
                          item.status === "error" ? "bg-danger" : "bg-primary"
                        }`}
                        role="progressbar"
                        style={{ width: `${item.progress}%` }}
                        aria-valuenow={item.progress}
                        aria-valuemin={0}
                        aria-valuemax={100}
                      />
                    </div>

                    <div className="text-muted" style={{ minHeight: "20px" }}>
                      {item.status === "uploading" && <span>Uploading...</span>}
                      {item.status === "success" && (
                        <span className="text-success">Uploaded ✔</span>
                      )}
                      {item.status === "error" && (
                        <span className="text-danger">Failed ❌: {item.error}</span>
                      )}
                      {item.status === "pending" && <span>Ready to upload</span>}
                    </div>
                  </div>

                  <button
                    className="btn btn-outline-danger btn-sm mt-3 mt-md-0"
                    onClick={() => removeFile(idx, setUploadItems)}
                    disabled={item.status === "uploading"}
                  >
                    ❌
                  </button>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default UploadPage;

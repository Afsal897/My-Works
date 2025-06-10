import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../../api";
import { FaDownload, FaEye, FaCheckCircle, FaTimesCircle } from "react-icons/fa";

interface SharedFile {
  file_id: number;
  filename: string;
  shared_by: number;
  recipient_email: string;
  shared_at: string;
  expires_at: string;
  message: string;
  downloaded: boolean;
}

const SharedFilePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [fileData, setFileData] = useState<SharedFile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const token = searchParams.get("token");

  const fetchSharedFile = async () => {
    if (!token) {
      setError("No token provided in URL.");
      return;
    }

    try {
      const response = await api.get(`/sharepage/${token}`);
      if (response.status === 200) {
        setFileData(response.data);
        console.log("Shared file data:", response.data);
      } else {
        setError("Failed to fetch shared file. Please check the token.");
      }
    } catch (err: any) {
      setError(err.response?.data?.error || "Failed to fetch shared file.");
    }
  };

  useEffect(() => {
    fetchSharedFile();
  }, [token]);

  const handleDownload = async () => {
    if (!token) return;

    try {
      const response = await api.get(`/shared/${token}`, {
        responseType: "blob",
      });

      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileData?.filename || "downloaded_file";
      a.click();
      window.URL.revokeObjectURL(url);

      await fetchSharedFile();
    } catch (error) {
      alert("Download failed.");
    }
  };

  const handleView = () => {
    if (!token) return;
    window.open(`http://localhost:5000/shared/preview/${token}`, "_blank");
  };

  if (error) {
    return <div className="alert alert-danger mt-5 text-center w-75 mx-auto">{error}</div>;
  }

  if (!fileData) {
    return <div className="mt-5 text-center text-muted">Loading file information...</div>;
  }

  return (
    <div className="container mt-5 d-flex justify-content-center">
      <div className="card shadow-lg border-0" style={{ maxWidth: "600px", width: "100%" }}>
        <div className="card-header bg-primary text-white text-center py-3">
          <h4 className="mb-0">📄 Shared File</h4>
        </div>
        <div className="card-body">
          <ul className="list-group list-group-flush mb-4">
            <li className="list-group-item"><strong>📁 Filename:</strong> {fileData.filename}</li>
            <li className="list-group-item"><strong>👤 Shared By :</strong> {fileData.shared_by}</li>
            <li className="list-group-item"><strong>📩 Recipient Email:</strong> {fileData.recipient_email}</li>
            <li className="list-group-item"><strong>⏰ Shared At:</strong> {new Date(fileData.shared_at).toLocaleString()}</li>
            <li className="list-group-item"><strong>🕓 Expires At:</strong> {new Date(fileData.expires_at).toLocaleString()}</li>
            <li className="list-group-item"><strong>📝 Message:</strong> {fileData.message || "None"}</li>
            <li className="list-group-item">
              <strong>✅ Downloaded:</strong>{" "}
              {fileData.downloaded ? (
                <span className="text-success"><FaCheckCircle className="me-1" /> Yes</span>
              ) : (
                <span className="text-danger"><FaTimesCircle className="me-1" /> No</span>
              )}
            </li>
          </ul>

          <div className="d-grid gap-3">
            <button className="btn btn-success" onClick={handleDownload}>
              <FaDownload className="me-2" />
              Download File
            </button>
            <button className="btn btn-outline-primary" onClick={handleView}>
              <FaEye className="me-2" />
              Preview File
            </button>
          </div>
        </div>
        <div className="card-footer text-center text-muted small">
          Link expires on {new Date(fileData.expires_at).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default SharedFilePage;

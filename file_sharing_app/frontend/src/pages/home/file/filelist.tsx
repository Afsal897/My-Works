import React, { useCallback, useEffect, useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { useDataContext } from "../datacontext";
import {
  calculateStorage,
  getPageNumbers,
  handleFileUploadDrop,
  handleFileDelete,
  loadAllData,
} from "../../../components/file";

import uploadIcon from "../../../assets/upload.png";
import shareIcon from "../../../assets/share.png";
import fileIcon from "../../../assets/folder.png";
import api from "../../../api";

import ShareModal from "./ShareModal";
import DeleteModal from "./DeleteModal";
import FloatingButtons from "./FloatingButtons";
import PaginationControls from "./PaginationControls";
import FileTable from "./FileTable";
import HeadAndError from "./headanderror";
// import { Search } from "react-bootstrap-icons";

type FileData = {
  file_id: number;
  filename: string;
};

const FileList: React.FC = () => {
  const {
    files,
    spaceLeft,
    // error,
    paginationInfo,
    setFilePage,
    filePage,
    userPage,
    searchQuery,
    setSearchQuery,
    setFiles,
    setContacts,
    setPaginationInfo,
    setContactPageInfo,
    setSpaceLeft,
    setError,
  } = useDataContext();

  const [dropHighlight, setDropHighlight] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [modalFileName, setModalFileName] = useState("");
  const [modalFileId, setModalFileId] = useState<number | null>(null);
  const [showShareModal, setShowShareModal] = useState(false);
  const [modalFileToShare, setModalFileToShare] = useState<FileData | null>(
    null
  );
  const [recipientEmail, setRecipientEmail] = useState("");
  const [expirationHours, setExpirationHours] = useState("");
  const [shareMessage, setShareMessage] = useState("");
  // const [SearchQuery, setSearchQuery] = useState("");

  const totalStorageMB = 1024;

  const { usedStorageMB, storagePercent, progressColor } = calculateStorage(
    spaceLeft,
    totalStorageMB
  );

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= paginationInfo.total_pages) {
      setFilePage(page);
    }
  };

  const pageNumbers = getPageNumbers(paginationInfo.total_pages, filePage);

  const loadData = useCallback(() => {
    return loadAllData(
      filePage,
      userPage,
      setFiles,
      setContacts,
      setPaginationInfo,
      setContactPageInfo,
      setSpaceLeft,
      setError
    );
  }, [filePage, userPage]);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) =>
      handleFileUploadDrop(e, setDropHighlight, setErrorMessage, loadData),
    [loadData]
  );

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDropHighlight(true);
  };

  const handleDragLeave = () => {
    setDropHighlight(false);
  };

  const handleDelete = (filename: string, file_id: number) => {
    setModalFileName(filename);
    setModalFileId(file_id);
    setShowModal(true);
  };

  const confirmDelete = async () => {
    if (modalFileId !== null) {
      await handleFileDelete(modalFileId, loadData, setErrorMessage);
    }
    setShowModal(false);
  };

  const handleFileDrop = (fileData: FileData) => {
    setModalFileToShare(fileData);
    setShowShareModal(true);
  };

  const handleDownload = async (filename: string, file_id: number) => {
    try {
      const response = await api.get(`/download/${file_id}`, {
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename); // Set filename for download
      document.body.appendChild(link);
      link.click();

      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download failed", error);
      toast.error("Failed to download file.");
    }
  };

  const handleShareSubmit = async (file_id: number) => {
    try {
      const response = await api.post(
        "/share",
        {
          file_id: file_id,
          recipient_email: recipientEmail,
          expiration_hours: parseInt(expirationHours),
          message: shareMessage,
        },
        { validateStatus: () => true }
      );

      if (response.status === 200) {
        toast.success("Share link sent successfully!");
        setShowShareModal(false);
        setRecipientEmail("");
        setExpirationHours("");
        setShareMessage("");
      } else {
        toast.error(response.data.error || "Failed to send share link.");
      }
    } catch (error) {
      console.error("Share error:", error);
      toast.error("An error occurred while sharing.");
    }
  };

  useEffect(() => {
  if (errorMessage) {
    toast.error(errorMessage);
  }
}, [errorMessage]);


  return (
    <>
      <ToastContainer position="top-right" autoClose={3000} />
      <div className="container py-4">
        <HeadAndError
          usedStorageMB={usedStorageMB}
          totalStorageMB={totalStorageMB}
          storagePercent={storagePercent}
          progressColor={progressColor}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
        />

        <FileTable
          files={files}
          dropHighlight={dropHighlight}
          handleDragOver={handleDragOver}
          handleDrop={handleDrop}
          handleDragLeave={handleDragLeave}
          handleDelete={handleDelete}
          handleDownload={handleDownload}
          fileIcon={fileIcon}
        />
        {/* Pagination */}
        <PaginationControls
          paginationInfo={paginationInfo}
          currentPage={filePage}
          onPageChange={handlePageChange}
          getPageNumbers={() => pageNumbers}
        />
        {/* Floating Buttons */}
        <FloatingButtons
          uploadLink="/home/upload"
          uploadIcon={uploadIcon}
          shareIcon={shareIcon}
          onFileDrop={handleFileDrop}
        />
      </div>
      <DeleteModal
        show={showModal}
        fileName={modalFileName}
        onCancel={() => setShowModal(false)}
        onConfirmDelete={confirmDelete}
      />
      <ShareModal
        show={showShareModal}
        fileToShare={modalFileToShare}
        recipientEmail={recipientEmail}
        expirationHours={expirationHours}
        shareMessage={shareMessage}
        onClose={() => setShowShareModal(false)}
        onRecipientEmailChange={setRecipientEmail}
        onExpirationHoursChange={setExpirationHours}
        onShareMessageChange={setShareMessage}
        onShareSubmit={(fileId) => {
          handleShareSubmit(fileId);
          setShowShareModal(false);
        }}
      />
    </>
  );
};

export default FileList;

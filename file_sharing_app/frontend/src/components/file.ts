// fileHandlers.ts
import type { DragEvent } from "react";
import { uploadFileToServer, deleteFile, fetchData } from "./home";

export const calculateStorage = (spaceLeft: number, totalStorageMB: number) => {
  const usedStorageMB = (totalStorageMB * 1024 * 1024 - spaceLeft) / (1024 * 1024);
  const storagePercent = (usedStorageMB / totalStorageMB) * 100;

  const progressColor =
    storagePercent >= 75
      ? "bg-danger"
      : storagePercent >= 50
      ? "bg-warning"
      : storagePercent >= 25
      ? "bg-info"
      : "bg-success";

  return { usedStorageMB, storagePercent, progressColor };
};

export const getPageNumbers = (totalPages: number, currentPage: number) => {
  const maxVisible = 5;
  const half = Math.floor(maxVisible / 2);

  let start = Math.max(1, currentPage - half);
  let end = Math.min(totalPages, start + maxVisible - 1);
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1);
  }

  return Array.from({ length: end - start + 1 }, (_, i) => start + i);
};

export const handleFileUploadDrop = async (
  e: DragEvent<HTMLDivElement>,
  setDropHighlight: (b: boolean) => void,
  setErrorMessage: (msg: string | null) => void,
  loadData: () => Promise<void>
) => {
  e.preventDefault();
  setDropHighlight(false);

  const file = e.dataTransfer.files[0];
  if (!file) return;

  const result = await uploadFileToServer(file);

  if (result.success) {
    await loadData(); // refresh list
  } else {
    setErrorMessage(result.error || "Upload failed");
  }
};

export const handleFileDelete = async (
  file_id: number,
  loadData: () => Promise<void>,
  setErrorMessage: (msg: string | null) => void
) => {
  const result = await deleteFile(file_id);
  if (result.success) {
    await loadData();
  } else {
    setErrorMessage(result.error || "Failed to delete");
  }
};

export const loadAllData = async (
  filePage: number,
  userPage: number,
  setFiles: any,
  setContacts: any,
  setPaginationInfo: any,
  setContactPageInfo: any,
  setSpaceLeft: any,
  setError: any
) => {
  try {
    const result = await fetchData(filePage, userPage);
    setFiles(result.files);
    setContacts(
      result.contacts.map((c: any) => ({
        username: c.username || "Unknown",
        email: c.email,
        avatarUrl: c.avatarUrl || "",
      }))
    );
    setPaginationInfo(result.file_page);
    setContactPageInfo(result.user_page);
    setSpaceLeft(result.space_left);
    setError("");
  } catch (err) {
    console.error("Failed to load data:", err);
    setError("Failed to load data.");
  }
};

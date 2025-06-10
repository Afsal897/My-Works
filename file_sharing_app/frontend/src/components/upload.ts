import { toast } from "react-toastify";
import { uploadFileWithProgress } from "./home";

export interface UploadItem {
  file: File;
  progress: number;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
  uploadedAt?: number;
}

export const handleFiles = (files: FileList | null): UploadItem[] => {
  if (!files) return [];

  const validItems: UploadItem[] = [];
  const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "application/pdf", "text/plain"];
  const maxSize = 100 * 1024 * 1024;

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    if (!allowedTypes.includes(file.type)) {
      toast.error(`${file.name}: File type not allowed.`);
      continue;
    }
    if (file.size > maxSize) {
      toast.error(`${file.name}: File size exceeds 100MB.`);
      continue;
    }
    validItems.push({ file, progress: 0, status: "pending" });
  }

  return validItems;
};

export const startUpload = async (
  uploadItems: UploadItem[],
  setUploadItems: React.Dispatch<React.SetStateAction<UploadItem[]>>
) => {
  const updatedItems = [...uploadItems];
  for (let i = 0; i < updatedItems.length; i++) {
    if (updatedItems[i].status !== "pending") continue;
    updatedItems[i].status = "uploading";
    setUploadItems([...updatedItems]);

    const res = await uploadFileWithProgress(updatedItems[i].file, (percent) => {
      updatedItems[i].progress = percent;
      setUploadItems([...updatedItems]);
    });

    updatedItems[i].status = res.success ? "success" : "error";
    if (res.success) {
      updatedItems[i].uploadedAt = Date.now();
      toast.success(`${updatedItems[i].file.name} uploaded successfully`);
    } else {
      updatedItems[i].error = res.error;
      toast.error(`${updatedItems[i].file.name} failed: ${res.error}`);
    }
    setUploadItems([...updatedItems]);
  }
};

export const removeFile = (
  index: number,
  setUploadItems: React.Dispatch<React.SetStateAction<UploadItem[]>>
) => {
  setUploadItems((items) => items.filter((_, i) => i !== index));
};

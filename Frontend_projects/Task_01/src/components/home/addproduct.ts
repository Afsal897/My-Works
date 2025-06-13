import type { ChangeEvent, FormEvent } from "react";
import api from "../../api"; // Adjust path as needed

export const handleUploadSubmit = async (
  e: FormEvent,
  file: File | null,
  description: string,
  setFile: (file: File | null) => void,
  setDescription: (desc: string) => void,
  setError: React.Dispatch<React.SetStateAction<string>>,
  setSuccess: React.Dispatch<React.SetStateAction<string>>
) => {
  e.preventDefault();

  if (!file && description.trim() === "") {
    setSuccess("");
    setError("Both file and description are required.");
    return;
  }
  if (!file) {
    setSuccess("");
    setError("File part is required.");
    return;
  }
  if (description.trim() === "") {
    setSuccess("");
    setError("Description cannot be empty.");
    return;
  }
  const validTypes = ["image/png", "image/jpeg", "image/jpg"];
  if (!validTypes.includes(file.type)) {
    setSuccess("");
    setError("Invalid file type. Only PNG, JPG, and JPEG files are allowed.");
    setFile(null);
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("description", description);

  try {
    const response = await api.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data", // important for FormData
      },
      validateStatus: () => true,
    });
    if (response.status === 201) {
      setError("");
      setSuccess("Upload successful!");
      setFile(null);
      setDescription("");
      //window.location.href='/home/add_product'
    } else if (response.status === 400) {
      setSuccess("");
      setError(response.data.error);
    } else if (response.status === 413) {
      setSuccess("");
      setError(response.data.error);
    }
  } catch (error: any) {
    console.error("Upload error:", error);
    setSuccess("");
    setError("Something went wrong. Please try again.");
  }
  setTimeout(()=>{
    setError('')
    setSuccess('')
  },2000)
};

export const handleFileChange = (
  e: ChangeEvent<HTMLInputElement>,
  setFile: (file: File | null) => void
) => {
  const selectedFile = e.target.files?.[0] || null;
  setFile(selectedFile);
};

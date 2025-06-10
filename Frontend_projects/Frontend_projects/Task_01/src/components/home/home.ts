import React, { useEffect, useState } from "react";
import api from "../../api";
import toast, { Toaster } from 'react-hot-toast';

interface ContentItem {
  id: number;
  filename: string;
  description: string;
}

const useHomePageLogic = () => {
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState(search);
  const [contents, setContents] = useState<ContentItem[]>([]);
  const [username, setUsername] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState<ContentItem | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isEditingDescription, setIsEditingDescription] = React.useState(false);
  const [newDescription, setNewDescription] = React.useState("");
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [error, setError] = useState("");

  // Debounce input
  useEffect(() => {
    const timeout = setTimeout(() => {
      setDebouncedSearch(search);
      setCurrentPage(1);
    }, 800);
    return () => clearTimeout(timeout);
  }, [search]);

  // Fetch contents
  const fetchHomeData = async () => {
    setLoading(true);
    try {
      const res = await api.get("/home", {
        params: { searchquery: debouncedSearch, page: currentPage },
      });
      setUsername(res.data.username);
      setContents(res.data.contents);
      setTotalPages(res.data.total_pages);
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHomeData();
  }, [debouncedSearch, currentPage]);

  // Modal logic
  const handleCardClick = (item: ContentItem) => {
    setSelectedItem(item);
    setShowModal(true);
    document.body.classList.add("modal-open");
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedItem(null);
    setSelectedFile(null);
    document.body.classList.remove("modal-open");
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFile(e.target.files?.[0] || null);
  };

  const handleReplaceImage = async () => {
    if (!selectedFile || !selectedItem) {
      setError("Please select an image to replace.");
      return;
    }
    const validTypes = ["image/png", "image/jpeg", "image/jpg"];
    if (!validTypes.includes(selectedFile.type)) {
      setError("Invalid file type. Only PNG, JPG, and JPEG files are allowed.");
      setSelectedFile(null);
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await api.put(`/replace/${selectedItem.id}`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.status === 200) {
        fetchHomeData();
        handleCloseModal();
        // Refresh data (optional)
        // You could re-fetch the list or update `contents` directly
      } else {
        console.error("Failed to replace image:", response.data);
        setError("Failed to replace image");
      }
    } catch (error) {
      console.error("Error replacing image:", error);
      setError("An error occurred while replacing the image.");
    }
  };

  const handleDelete = async () => {
    if (!selectedItem) return;
    try {
      const response = await api.delete(`/delete/${selectedItem.id}`);
      if (response.status === 200) {
        console.log(`Deleted content with ID ${selectedItem.id}`);
        toast.success('successfully deleted')
        fetchHomeData();
      } else {
        console.error("Delete failed:", response.status);
        setError("Delete failed");
      }
    } catch (error) {
      console.error(error);
      setError("Something went wrong. Please try again.");
    }
    handleCloseModal(); // Close modal after deletion
  };

  const handleEdit = async () => {
    if (!selectedItem) return;

    try {
      if (newDescription.trim() === "") {
        setError("description cannot be empty");
        return;
      }
      // Example API call (adjust URL and body as needed)
      const response = await api.put(`/edit/${selectedItem.id}`, {
        new_description: newDescription,
      });
      if (response.status === 200) {
        // Refresh or update the contents and selectedItem description accordingly
        setSelectedItem((prev) =>
          prev ? { ...prev, description: newDescription } : prev
        );
        // Optionally, refresh contents list here
      } else {
        setError("Failed to update description");
      }
    } catch (error) {
      console.error("Error updating description:", error);
      setError("Something went wrong. Please try again.");
    } finally {
      setIsEditingDescription(false);
    }
  };

  const handleDownload = async () => {
    if (!selectedItem) return;
    try {
      const response = await api.get(`/download/${selectedItem.id}`, {
        responseType: "blob",
      });
      console.log(response.data);
      if (response.status === 200) {
        const url = window.URL.createObjectURL(response.data);

        const a = document.createElement("a");
        a.href = url;
        a.download = selectedItem.filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        setError("failed to download");
      }
    } catch (error: any) {
      setError("Something went wrong. Please try again.");
    }
  };

  const handleDisplay = (filename: string): string => {
    return `${import.meta.env.VITE_API_URL}/static/uploads/${filename}`;
  };

  const openDeleteModal = (item: any) => {
    setSelectedItem(item);
    setShowDeleteModal(true);
  };

  const handleCloseDeleteModal = () => {
    setShowDeleteModal(false);
  };

  const handleConfirmedDelete = async () => {
    await handleDelete();
    setShowDeleteModal(false);
    handleCloseModal();
  };
  setTimeout(()=>{
    setError('')
  },2000)

  return {
    search,
    setSearch,
    contents,
    username,
    currentPage,
    setCurrentPage,
    totalPages,
    loading,
    selectedItem,
    showModal,
    selectedFile,
    handleCardClick,
    handleCloseModal,
    handleFileSelect,
    handleReplaceImage,
    handleEdit,
    setNewDescription,
    isEditingDescription,
    newDescription,
    setIsEditingDescription,
    handleDownload,
    handleDisplay,
    error,
    handleConfirmedDelete,
    handleCloseDeleteModal,
    openDeleteModal,
    showDeleteModal,
  };
};

export default useHomePageLogic;

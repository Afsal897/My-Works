import api from "../api";

export const fetchData = async (filePage = 1, userPage = 1, search = "") => {
  const res = await api.get(
    `/home?file_page=${filePage}&user_page=${userPage}&search=${encodeURIComponent(search)}`,);
  const data = res.data;
  return {
    space_left: data.space_left || 0,
    files: data.files || [],
    contacts: data.contacts || [],
    file_page: data.file_page || {
      page: 1,
      per_page: 10,
      total_pages: 1,
      total_files: 0,
    },
    user_page: data.user_page || {
      page: 1,
      per_page: 10,
      total_pages: 1,
      total_users: 0,
    },
  };
};

export async function deleteFile(file_id: number): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await api.delete(`/delete/${encodeURIComponent(file_id)}`);

    if (response.status !== 200) {
      const errorData = await response.data;
      return { success: false, error: errorData.message || "Deletion failed" };
    }

    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}



export const uploadFileToServer = async (
  file: File
): Promise<{ success: boolean; error?: string }> => {
  if (!file) return { success: false, error: "No file provided" };

  const allowedTypes = [
    "image/jpeg",
    "image/png",
    "application/pdf",
    "text/plain",
  ];
  if (!allowedTypes.includes(file.type)) {
    return { success: false, error: "File type not allowed" };
  }

  const maxSizeBytes = 100 * 1024 * 1024; // 100 MB
  if (file.size > maxSizeBytes) {
    return { success: false, error: "File size exceeds 100 MB limit" };
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await api.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      validateStatus: () => true,
    });

    if (response.status === 201) {
      return { success: true };
    } else {
      return { success: false, error: response.data?.error || "Upload failed" };
    }
  } catch (error: any) {
    console.error("Error uploading file:", error);
    return { success: false, error: "Network error" };
  }
};


export const uploadFileWithProgress = async (
  file: File,
  onProgress: (percent: number) => void
): Promise<{ success: boolean; error?: string }> => {
  const allowedTypes = [
    "image/jpeg",
    "image/png",
    "application/pdf",
    "text/plain",
  ];
  const maxSizeBytes = 100 * 1024 * 1024;

  if (!file) return { success: false, error: "No file provided" };
  if (!allowedTypes.includes(file.type))
    return { success: false, error: "File type not allowed" };
  if (file.size > maxSizeBytes)
    return { success: false, error: "File size exceeds 100 MB limit" };

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await api.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percent = Math.round(
            (progressEvent.loaded / progressEvent.total) * 100
          );
          onProgress(percent);
        }
      },
      validateStatus: () => true, // handle status manually
    });

    if (response.status === 201) {
      return { success: true };
    } else {
      return { success: false, error: response.data?.error || "Upload failed" };
    }
  } catch (error: any) {
    console.error("Error uploading file:", error);
    return { success: false, error: "Network error" };
  }
};


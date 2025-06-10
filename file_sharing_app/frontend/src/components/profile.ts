import api from "../api";


export const fetchProfileData = async () => {
  const res = await api.get("/profile/profiledata");
  const data = res.data;

  return {
    first_name:data.first_name||"",
    last_name:data.last_name||"",
    username:data.username||"",
    email:data.email||"",
    dob:data.dob||null,
    url:data.profile_picture||"",
    balance_space:data.balance_space||0,
  };
};

export const MAX_SPACE = 1073741824;


export const formatStorage = (bytes: number) =>
  (bytes / (1024 * 1024 * 1024)).toFixed(2) + " GB";

export const getStorageUsedPercent = (remaining: number) =>
  Math.round(((MAX_SPACE - remaining) / MAX_SPACE) * 100);


export const updateProfile = async (data: any) => {
  return await api.put("/profile/savechanges", data, {
    validateStatus: () => true,
  });
};

export const changePassword = async (
  oldPassword: string,
  newPassword: string,
  confirmPassword: string
) => {
  return await api.put("/profile/change_password", {
    password: oldPassword,
    new_password: newPassword,
    confirm_new_password: confirmPassword,
  });
};

export const uploadProfilePicture = async (file: File) => {
  const formData = new FormData();
  formData.append("profile_picture", file);

  return await api.post("/profile/add_profile_picture", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    validateStatus: () => true,
  });
};
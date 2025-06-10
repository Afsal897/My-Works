import api from "../api";
import type { toast } from "react-toastify";


interface RegisterProps {
  e: React.FormEvent<HTMLFormElement>;
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirmpassword: string;
  dob: string;
  profileImage: File | null;
  toast: typeof toast;
  navigate: (path: string) => void;
}

export const handleRegister = async ({
  e,
  first_name,
  last_name,
  email,
  password,
  confirmpassword,
  dob,
  profileImage,
toast,
  navigate,
}: RegisterProps) => {
  e.preventDefault();
  if (!first_name) {
    toast.error("Please enter first name");
    return;
  }
  if (!last_name) {
    toast.error("Please enter last name");
    return;
  }
  if (!email) {
    toast.error("Please enter email");
    return;
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    toast.error("Please enter a valid email address");
    return;
  }
  if (password.trim()==="") {
    toast.error("Please enter password");
    return;
  }
  if (confirmpassword.trim()==="") {
    toast.error("Please confirm your password");
    return;
  }
  if (password !== confirmpassword) {
    toast.error("Passwords do not match");
    return;
  }
  if (!dob) {
    toast.error("Please enter date of birth");
    return;
  }
  try {
    const formData = new FormData();
    formData.append("first_name", first_name);
    formData.append("last_name", last_name);
    formData.append("email", email);
    formData.append("password", password);
    formData.append("confirmpassword", confirmpassword);
    formData.append("dob", dob);

    const MAX_FILE_SIZE_MB = 2;    // Maximum file size in MB
    const ALLOWED_TYPES = ["image/jpeg","image/jpg", "image/png", "image/webp"];

    if (profileImage) {
      const isValidType = ALLOWED_TYPES.includes(profileImage.type);
      const isValidSize = profileImage.size <= MAX_FILE_SIZE_MB * 1024 * 1024;

      if (!isValidType) {
        toast.error("Only JPG, PNG, or WEBP images are allowed.");
      } else if (!isValidSize) {
        toast.error("File size must be under 2MB.");
      } else {
        formData.append("profile_image", profileImage);
      }
    }
    const response = await api.post("/register", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      validateStatus: () => true,
    });

    if (response.status === 201) {
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);
      console.log("Registration successful");
      navigate("/home");
      return;
    } else {
      toast.error(response.data.error || "Registration failed");
    }
  } catch (error: any) {
    toast.error("Oops! Something went wrong. Please try again later.");
  }
};

import type { toast } from "react-toastify";
import api from "../api";

interface LoginProps {
  e: React.FormEvent<HTMLFormElement>;
  email: string;
  password: string;
  toast: typeof toast;
  navigate: (path: string) => void;
}

export const handleLogin = async ({
  e,
  email,
  password,
  toast,
  navigate,
}: LoginProps) => {
  e.preventDefault();

  if (!email && password.trim()==="") {
    toast.error("Please enter email and password");
    return;
  }
  if (!email) {
    toast.error("Please enter email");
    return;
  }
  if (password.trim()==="") {
    toast.error("Please enter password");
    return;
  }
  try {
    const response = await api.post(
      "/login",
      { email, password },
      { validateStatus: () => true }
    );
    if (response.status === 200) {
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);
      console.log("Login successful");
      navigate("/home");
    } else if (response.status === 401) {
      toast.error(response.data.error || "Login failed");
      return;
    } else {
      toast.error(response.data.error || "Login failed");
    }
  } catch (error: any) {
    toast.error("Oops! Something went wrong. Please try again later.");
  }
};

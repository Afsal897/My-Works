import api from "../../api";

export const handleLoginSubmit = async (
  event: React.FormEvent<HTMLFormElement>,
  username: string,
  password: string,
  setError: React.Dispatch<React.SetStateAction<string>>,
  navigate: (path: string) => void
) => {
  event.preventDefault();

  try {
    if (username.trim() === "" && password.trim() === "") {
      setError("username or password empty");
      return;
    }
    if (username.trim() === "") {
      setError("username empty");
      return;
    }
    if (password.trim() === "") {
      setError("password empty");
      return;
    }
    const response = await api.post(
      "/",
      {
        username: username,
        password: password,
      },
      {
        validateStatus: () => true,
      }
    );
    if (response.status === 200) {
      console.log("Login Successful");
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);
      navigate("/home");
    } else if (response.status === 401 || response.status === 400) {
      setError(response.data.message);
    }
  } catch (error: any) {
    setError("Something went wrong. Please try again.");
  }
};

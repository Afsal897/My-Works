import api from "../../api";

export const handleRegisterSubmit = async (
  event: React.FormEvent<HTMLFormElement>,
  username: string,
  password: string,
  confirmpassword: string,
  setError: React.Dispatch<React.SetStateAction<string>>,
  navigate: (path: string) => void
) => {
  event.preventDefault();

  try {
    if (username.trim() === "") {
      setError("Username cannot be empty");
      navigate("/register");
      return;
    }
    if (password.trim() === "") {
      setError("Password cannot be empty");
      navigate("/register");
      return;
    }
    if (confirmpassword.trim() === "") {
      setError("ConfirmPassword cannot be empty");
      navigate("/register");
      return;
    } else if (password.length < 8) {
      setError("password length should be more than 7");
      navigate("/register");
    } else if (password !== confirmpassword) {
      setError("password mismatch");
      navigate("/register");
      return;
    } else {
      const response = await api.post(
        "/signup",
        {
          username: username,
          password1: password,
          password2: confirmpassword,
        },
        {
          validateStatus: () => true,
        }
      );
      if (response.status === 200 || response.status === 201) {
        console.log("registration Successful");
        localStorage.setItem("access_token", response.data.access_token);
        localStorage.setItem("refresh_token", response.data.refresh_token);
        navigate("/home");
      } else if (response.status === 400 || response.status === 409) {
        setError(response.data.message);
      }
    }
  } catch (error: any) {
    setError("Something went wrong. Please try again.");
  }
  setTimeout(() => {
    setError("");
  }, 2000);
};

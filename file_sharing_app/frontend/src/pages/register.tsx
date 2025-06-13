import { useEffect, useState } from "react";
import { handleRegister } from "../components/register";
import { useNavigate } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function Register() {
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [confirmpassword, setConfirmpassword] = useState("");
  const [dob, setDob] = useState("");
  const [isHovered, setIsHovered] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [profileImage, setProfileImage] = useState<File | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      navigate("/home");
    }
  }, [navigate]);

  return (
    <div
      className="d-flex align-items-center justify-content-center py-5 bg-light"
      style={{ minHeight: "100vh" }}
    >
      <div className="card shadow-sm p-4 w-100" style={{ maxWidth: "500px" }}>
        <h3 className="text-center mb-4">Create Account</h3>

        <div className="d-flex flex-column align-items-center mb-4 position-relative">
          <label htmlFor="profileUpload" style={{ cursor: "pointer" }}>
            <img
              src={previewUrl || "/src/assets/add-photo.png"}
              alt="Profile"
              className="rounded-circle border"
              style={{
                width: "100px",
                height: "100px",
                objectFit: previewUrl ? "cover" : "contain",
                border: "2px solid #ccc",
                padding: previewUrl ? "0" : "25px",
                backgroundColor: "#f8f9fa",
              }}
            />
            <input
              type="file"
              id="profileUpload"
              accept="image/*"
              style={{ display: "none" }}
              onChange={(e) => {
                const file = e.target.files?.[0] || null;
                setProfileImage(file);
                if (file) {
                  const reader = new FileReader();
                  reader.onloadend = () => {
                    setPreviewUrl(reader.result as string);
                  };
                  reader.readAsDataURL(file);
                } else {
                  setPreviewUrl("");
                }
              }}
            />
          </label>

          {previewUrl && (
            <button
              type="button"
              onClick={() => {
                setPreviewUrl("");
                setProfileImage(null);
              }}
              aria-label="Remove image"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              style={{
                position: "absolute",
                top: "17%",
                right: "35%",
                transform: "translate(-50%, -50%)",
                backgroundColor: isHovered ? "#ff4d4d" : "white",
                borderRadius: "50%",
                border: "1px solid #ccc",
                width: "22px",
                height: "22px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                fontWeight: "bold",
                lineHeight: "1",
                padding: 0,
                color: isHovered ? "white" : "black",
                boxShadow: "0 0 3px rgba(0,0,0,0.2)",
              }}
            >
              &times;
            </button>
          )}

          <small className="text-muted mt-2">Profile Picture</small>
        </div>

        <form
          onSubmit={(e) =>
            handleRegister({
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
            })
          }
        >
          <div className="row mb-3">
            <div className="col">
              <label htmlFor="first_name" className="form-label">
                First Name <span className="text-danger">*</span>
              </label>
              <input
                type="text"
                className="form-control"
                id="first_name"
                placeholder="First Name"
                value={first_name}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
            <div className="col">
              <label htmlFor="last_name" className="form-label">
                Last Name <span className="text-danger">*</span>
              </label>
              <input
                type="text"
                className="form-control"
                id="last_name"
                placeholder="Last Name"
                value={last_name}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
          </div>

          <div className="mb-3">
            <label htmlFor="email" className="form-label">
              Email Address <span className="text-danger">*</span>
            </label>
            <input
              type="email"
              className="form-control"
              id="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="mb-3">
            <label htmlFor="password" className="form-label">
              Password <span className="text-danger">*</span>
            </label>
            <input
              type={showPassword ? "text" : "password"}
              className="form-control"
              id="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="mb-3">
            <label htmlFor="confirmpassword" className="form-label">
              Confirm Password <span className="text-danger">*</span>
            </label>
            <input
              type={showPassword ? "text" : "password"}
              className="form-control"
              id="confirmpassword"
              placeholder="Confirm Password"
              value={confirmpassword}
              onChange={(e) => setConfirmpassword(e.target.value)}
            />
            <div className="form-check mt-2">
              <input
                className="form-check-input"
                type="checkbox"
                id="showPassword"
                checked={showPassword}
                onChange={() => setShowPassword(!showPassword)}
              />
              <label className="form-check-label" htmlFor="showPassword">
                Show Password
              </label>
            </div>
          </div>

          <div className="mb-3">
            <label htmlFor="dob" className="form-label">
              Date of Birth <span className="text-danger">*</span>
            </label>
            <input
              type="date"
              className="form-control"
              id="dob"
              value={dob}
              onChange={(e) => setDob(e.target.value)}
            />
          </div>

          <div className="d-grid mb-3">
            <button type="submit" className="btn btn-success">
              Register
            </button>
          </div>

          <p className="text-center text-muted">
            Already have an account?{" "}
            <a href="/login" className="text-decoration-none">
              Login here
            </a>
          </p>
        </form>
      </div>
      <ToastContainer
        position="top-right"
        autoClose={4000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        pauseOnHover
        draggable
        theme="colored"
      />
    </div>
  );
}

export default Register;

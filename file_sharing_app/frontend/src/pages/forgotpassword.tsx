import { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function ForgotPassword() {
  const [email, setEmail] = useState<string>("");
  const [countdown, setCountdown] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  useEffect(() => {
    if (countdown === null) return;
    if (countdown === 0) {
      navigate("/login");
      return;
    }

    const timer = setTimeout(() => {
      setCountdown(countdown - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [countdown, navigate]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validateEmail(email)) {
      toast.error("Please enter a valid email address.");
      return;
    }

    try {
      const response = await api.post("/forgot-password", {
        email: email,
      });

      if (response.status === 200) {
        toast.success(response.data.message);
        setSubmitted(true);
        setCountdown(300);
      }
    } catch (error: any) {
      toast.error("Something went wrong. Please try again.");
    }
  };

  return (
    <div className="container mt-5">
      <h2>Forgot Password</h2>
      <form onSubmit={handleSubmit} className="mt-4">
        {!submitted && (
          <div className="mb-3">
            <label htmlFor="email" className="form-label">
              Enter your registered email
            </label>
            <input
              type="email"
              className="form-control"
              id="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={submitted}>
          Send Reset Link
        </button>
      </form>

      {/* Show timer only after successful submit */}
      {submitted && countdown !== null && (
        <div className="mt-3 text-info">
          Link expires in: <strong>{countdown}</strong> seconds
        </div>
      )}
      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
}

export default ForgotPassword;

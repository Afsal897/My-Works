
// Logout.tsx
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    localStorage.clear();
    // Clear auth context/store if needed
    navigate("/"); // Redirect to home or login page
  }, [navigate]);

  return <p>Logging you out...</p>;
};

export default Logout;

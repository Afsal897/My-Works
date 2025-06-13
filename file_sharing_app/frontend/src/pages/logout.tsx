import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Logout() {
  const navigate = useNavigate();
  useEffect(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    
    localStorage.setItem("logout", Date.now().toString());

    navigate("/login");
  }, [navigate]);
  return <p>loging out....</p>;
}

export default Logout;

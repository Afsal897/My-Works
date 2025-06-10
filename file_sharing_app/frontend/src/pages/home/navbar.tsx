import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import "../../App.css";
import { useNavbarContext } from "./navbarContext";
// import api from "../../api";
import { fetchUserData } from "../../components/navbar";

// interface User {
//   first_name: string;
//   last_name: string;
//   username: string;
//   email: string;
//   dob: string;
//   profile_picture: string;
//   balance_space: number;
// }

function Navbar() {
  const {
    username,
    email,
    dob,
    url,
    showText,
    setShowText,
    setUsername,
    setEmail,
    setDOB,
    setUrl,
  } = useNavbarContext();
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  // const [user, setUser] = useState<User | null>(null);

  const handleLogout = () => navigate("/logout");
  const handleEdit = () => navigate("/profile");
  const handleHistory = () => navigate("/history");
  const handleOpen = () => setShowModal(true);
  const handleClose = () => setShowModal(false);
  const handleNotification = () => navigate("/notification");

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  };

  useEffect(() => {
    const navdata = async () => {
      try {
        const res = await fetchUserData();
        const username = res.username;
        const email = res.email;
        const dob = res.dob;
        const url = res.url;

        setUsername(username);
        setEmail(email);
        setDOB(dob);
        setUrl(url);
      } catch (err) {
        console.error("Error loading user data", err);
      }
    };
    navdata();
  }, [url, username, email, dob]);

return (
  <>
    <nav className="navbar bg-light shadow-sm px-3 px-md-4 d-flex justify-content-between align-items-center">
      {/* Brand */}
      <NavLink to="/home/file" className="navbar-brand d-flex align-items-center">
        <img
          src="/src/assets/folder1.png"
          alt="Logo"
          width="30"
          height="30"
          className="me-2"
          draggable={false}
        />
        <strong>File Transfer</strong>
      </NavLink>

      {/* Hamburger icon only visible on mobile */}
      <div className="d-lg-none">
        <button
          className="btn border-0"
          onClick={() => setShowDropdown((prev) => !prev)}
        >
          <img
            src="/src/assets/menu.png"
            alt="Menu"
            width="24"
            height="24"
          />
        </button>
      </div>

      {/* Dropdown menu on mobile */}
      {showDropdown && (
        <div className="position-absolute top-100 start-0 w-100 bg-white border shadow-sm z-3 d-lg-none text-center">
          <NavLink to="/home/file" className="dropdown-item py-2" onClick={() => setShowDropdown(false)}>
            Files
          </NavLink>
          <NavLink to="/home/users" className="dropdown-item py-2" onClick={() => setShowDropdown(false)}>
            Users
          </NavLink>
          <NavLink to="/home/chat" className="dropdown-item py-2" onClick={() => setShowDropdown(false)}>
            Chat
          </NavLink>
        </div>
      )}

      {/* Nav options for desktop */}
      <div className="d-none d-lg-flex gap-4">
        <NavLink
          to="/home/file"
          className={({ isActive }) =>
            `nav-icon d-flex flex-column align-items-center text-decoration-none ${
              isActive ? "text-primary fw-bold" : "text-secondary"
            }`
          }
        >
          <img src="/src/assets/files.png" alt="Files" width="24" draggable={false} />
          <small className="mt-1">Files</small>
        </NavLink>
        <NavLink
          to="/home/users"
          className={({ isActive }) =>
            `nav-icon d-flex flex-column align-items-center text-decoration-none ${
              isActive ? "text-primary fw-bold" : "text-secondary"
            }`
          }
        >
          <img src="/src/assets/group.png" alt="Users" width="24" draggable={false} />
          <small className="mt-1">Users</small>
        </NavLink>
        <NavLink
          to="/home/chat"
          className={({ isActive }) =>
            `nav-icon d-flex flex-column align-items-center text-decoration-none ${
              isActive ? "text-primary fw-bold" : "text-secondary"
            }`
          }
        >
          <img src="/src/assets/chat.png" alt="Chat" width="24" draggable={false} />
          <small className="mt-1">Chat</small>
        </NavLink>
      </div>

      {/* Notification and profile */}
      <div className="d-flex align-items-center gap-3">
        <img
          src="/src/assets/bell.png"
          alt="Notifications"
          width="24"
          height="24"
          style={{ cursor: "pointer" }}
          onClick={handleNotification}
          draggable={false}
        />
        <img
          src={
            url
              ? `http://localhost:5000/static/profile/${url}`
              : "/src/assets/user_profile.png"
          }
          alt="User Profile"
          draggable={false}
          onClick={handleOpen}
          className="rounded-circle border border-secondary"
          width="40"
          height="40"
          style={{ objectFit: "cover", cursor: "pointer" }}
        />
      </div>
    </nav>

    {/* Modal remains unchanged */}
    <Modal show={showModal} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Profile Details</Modal.Title>
      </Modal.Header>
      <Modal.Body className="text-center">
        <img
          src={
            url
              ? `http://localhost:5000/static/profile/${url}`
              : "/src/assets/user_profile.png"
          }
          alt="User Profile"
          draggable={false}
          className="rounded mb-3"
          style={{
            width: "100px",
            height: "100px",
            objectFit: "cover",
            border: "2px solid #ccc",
          }}
        />
        <p className="mb-1"><strong>Username:</strong> {username}</p>
        <p className="mb-1"><strong>Email:</strong> {email}</p>
        <p className="mb-0"><strong>DOB:</strong> {formatDate(dob)}</p>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="outline-warning" onClick={handleHistory}>History</Button>
        <Button variant="outline-warning" onClick={handleEdit}>Profile</Button>
        <Button
          variant="outline-danger"
          onClick={handleLogout}
          onMouseEnter={() => setShowText(true)}
          onMouseLeave={() => setShowText(false)}
          className="d-flex align-items-center gap-2"
        >
          <img src="/src/assets/logout.png" alt="Logout" width="20" height="20" />
          {showText && <span>Logout</span>}
        </Button>
      </Modal.Footer>
    </Modal>
  </>
);


}

export default Navbar;

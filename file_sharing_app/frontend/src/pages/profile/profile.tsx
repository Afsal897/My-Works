import React, { useState, useEffect } from "react";
import { Container, Card, Button } from "react-bootstrap";
import Navbar from "../home/navbar";

import { useNavbarContext } from "../home/navbarContext";
import { fetchProfileData } from "../../components/profile";
import ProfilePicture from "./profilepicture";
import ProfileForm from "./profileform";
import StorageProgress from "./storageprogress";
import PasswordModal from "./passwordmodal";
import { formatDateForInput } from "./profilehelpers";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const UserPage: React.FC = () => {
  const [editMode, setEditMode] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const {
    setFirstName,
    setLastName,
    setUsername,
    setEmail,
    setDOB,
    setUrl,
    setBalanceSpace,
  } = useNavbarContext();

  const loadUserProfile = async () => {
    try {
      const res = await fetchProfileData();
      // alert('hai')
      const {
        first_name,
        last_name,
        username,
        email,
        dob,
        url,
        balance_space,
      } = res;
      setFirstName(first_name);
      setLastName(last_name);
      setUsername(username);
      setEmail(email);
      setDOB(formatDateForInput(dob));
      setUrl(url);
      setBalanceSpace(balance_space);
    } catch (err) {
      toast.error("Error loading user data");
      setTimeout(() => {
        toast.error(null);
      }, 1000);
    }
  };
  const handleError = (msg: string | null) => {
    if (msg) {
      toast.error(msg);
    }
  };

  const handleSuccess = (msg: string | null) => {
    if (msg) {
      toast.success(msg);
    }
  };

  useEffect(() => {
    loadUserProfile();
  }, []);

  return (
    <>
      <Navbar />
      <Container className="mt-5">
        <Card className="shadow-sm border-0">
          <Card.Header className="d-flex justify-content-between align-items-center bg-white">
            <h4 className="mb-0 fw-bold">User Profile</h4>
            <div className="d-flex gap-2">
              <Button
                variant="outline-primary"
                size="sm"
                onClick={() => setIsModalOpen(true)}
              >
                Change Password
              </Button>
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={() => setEditMode(!editMode)}
              >
                Edit
              </Button>
            </div>
          </Card.Header>
          <Card.Body>
            <ProfilePicture
              onUploadError={handleError}
              onUploadSuccess={setUrl}
            />
            <ProfileForm
              editMode={editMode}
              setError={handleError}
              setSuccess={handleSuccess}
              setEditMode={setEditMode}
            />
            <StorageProgress />
          </Card.Body>
        </Card>
      </Container>
      <PasswordModal
        show={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        setError={handleError}
        setSuccess={handleSuccess}
      />
      <ToastContainer position="top-right" autoClose={3000} />
    </>
  );
};

export default UserPage;

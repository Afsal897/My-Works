import React, { useState } from "react";
import { useDataContext } from "../datacontext";
import { Container } from "react-bootstrap";
import RenderPagination from "./renderpagination";
import RenderUserGrid from "./renderusergrid";
import api from "../../../api";
import { toast, ToastContainer } from "react-toastify";

const Users: React.FC = () => {
  const { contacts, userPage, setUserPage, contactPageInfo } = useDataContext();
  const avatarBaseUrl = "http://localhost:5000";

  const [selectedUser, setSelectedUser] = useState<null | (typeof contacts)[0]>(
    null
  );
  const [showModal, setShowModal] = useState(false);

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= contactPageInfo.total_pages && page !== userPage) {
      setUserPage(page);
    }
  };

  const openModal = (user: (typeof contacts)[0]) => {
    setSelectedUser(user);
    setShowModal(true);
  };

  const closeModal = () => {
    setSelectedUser(null);
    setShowModal(false);
  };

  const handleConnect = async () => {
    if (!selectedUser) return;

    try {
      const response = await api.get(`/friend/connect/${selectedUser.email}`, {
        validateStatus: (status) => status >= 200 && status < 500, // treat 4xx as valid
      });

      if (response.status === 200) {
        toast.success(response.data.message || "Connection request sent!");
      } else {
        toast.error(response.data.message || "Failed to connect");
      }
    } catch (error: any) {
      toast.error("Something went wrong. Please try again.");
    }
  };

  return (
    <>
      <ToastContainer position="top-right" autoClose={3000} />
      <Container className="py-4">
        <h2 className="text-center mb-4">
          <strong>User List</strong>
        </h2>
        {contacts.length === 0 ? (
          <p className="text-center">No users found.</p>
        ) : (
          <RenderUserGrid
            contacts={contacts}
            avatarBaseUrl={avatarBaseUrl}
            openModal={openModal}
            showModal={showModal}
            closeModal={closeModal}
            selectedUser={selectedUser}
            handleConnect={handleConnect}
          />
        )}
        {contactPageInfo.total_pages > 1 && (
          <RenderPagination
            totalPages={contactPageInfo.total_pages}
            currentPage={userPage}
            onPageChange={handlePageChange}
          />
        )}
      </Container>
    </>
  );
};

export default Users;

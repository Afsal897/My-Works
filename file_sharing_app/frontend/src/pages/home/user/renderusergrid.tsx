import React from "react";
import { Row, Modal, Button } from "react-bootstrap";
import RenderUserCard from "./renderusercard";

interface Contact {
  username: string;
  email: string;
  avatarUrl?: string;
}

interface RenderUserGridProps {
  contacts: Contact[];
  avatarBaseUrl: string;
  openModal: (contact: Contact) => void;
  showModal: boolean;
  closeModal: () => void;
  selectedUser?: Contact | null;
  handleConnect: () => void;
}

const RenderUserGrid: React.FC<RenderUserGridProps> = ({
  contacts,
  avatarBaseUrl,
  openModal,
  showModal,
  closeModal,
  selectedUser,
  handleConnect,
}) => (
  <>
    <Row className="mt-4">
      {contacts.map((contact, index) => (
        <RenderUserCard
          key={index}
          contact={contact}
          index={index}
          avatarBaseUrl={avatarBaseUrl}
          openModal={openModal}
        />
      ))}
    </Row>

    <Modal show={showModal} onHide={closeModal} centered>
      <Modal.Header closeButton>
        <Modal.Title>User Details</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {selectedUser ? (
          <div className="text-center">
            <img
              src={
                selectedUser.avatarUrl
                  ? avatarBaseUrl + selectedUser.avatarUrl
                  : "/src/assets/user.png"
              }
              alt="User"
              draggable={false}
              className="rounded-circle mb-3"
              style={{
                width: "100px",
                height: "100px",
                objectFit: "cover",
              }}
            />
            <p>
              <strong>Username:</strong> {selectedUser.username || "Unknown"}
            </p>
            <p>
              <strong>Email:</strong> {selectedUser.email}
            </p>
          </div>
        ) : (
          <p>No user selected.</p>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="warning" onClick={handleConnect}>
          Connect
        </Button>
      </Modal.Footer>
    </Modal>
  </>
);

export default RenderUserGrid;

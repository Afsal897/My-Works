import React from "react";
import { Card, Col } from "react-bootstrap";

export interface Contact {
  username: string;
  email: string;
  avatarUrl?: string;
}

interface RenderUserCardProps {
  contact: Contact;
  index: number;
  avatarBaseUrl: string;
  openModal: (contact: Contact) => void;
}

const RenderUserCard: React.FC<RenderUserCardProps> = ({
  contact,
  index,
  avatarBaseUrl,
  openModal,
}) => {
  const { username = "Unknown", email, avatarUrl = "" } = contact;
  const imageUrl = avatarUrl?.trim()
    ? `${avatarBaseUrl}${avatarUrl}`
    : "/src/assets/user.png";

  return (
    <Col key={index} xs={12} sm={6} md={4} lg={3} className="mb-4">
      <Card
        className="h-100 text-center shadow-sm"
        onClick={() => openModal(contact)}
        style={{ cursor: "pointer" }}
      >
        <Card.Img
          variant="top"
          src={imageUrl}
          draggable={false}
          alt={`Avatar of ${username}`}
          className="rounded-circle mx-auto mt-3"
          style={{ width: "70px", height: "70px", objectFit: "cover" }}
        />
        <Card.Body>
          <Card.Title className="mb-1">{username}</Card.Title>
          <Card.Text
            className="text-muted text-truncate mb-0"
            title={email}
            style={{ fontSize: "0.9rem" }}
          >
            {email}
          </Card.Text>
        </Card.Body>
      </Card>
    </Col>
  );
};

export default RenderUserCard;

import React, { useEffect, useState } from "react";
import { Card, Button, Container, Row, Col, Alert, Spinner } from "react-bootstrap";
import api from "../../api";
import { toast } from "react-toastify";
import Navbar from "./navbar";

interface FromUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

interface FriendRequest {
  id: number;
  from_user_id: number;
  created_at: string;
  from_user: FromUser;
}

const Notification: React.FC = () => {
  const [requests, setRequests] = useState<FriendRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRequests = async () => {
    try {
      const response = await api.get("/friend/requests", {
        validateStatus: () => true,
      });
      if (response.status === 200) {
        setRequests(response.data);
      } else {
        toast.error("Failed to load requests");
      }
    } catch (err) {
      toast.error("Error fetching requests");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleAction = async (id: number, action: "accept" | "reject") => {
    try {
      const response = await api.post(`/friend/requests/${id}/${action}`, null, {
        validateStatus: () => true,
      });

      if (response.status === 200) {
        toast.success(response.data.message);
        setRequests((prev) => prev.filter((req) => req.id !== id));
      } else {
        toast.error(response.data.message || "Action failed");
      }
    } catch (err) {
      toast.error("Server error");
    }
  };

  if (loading) return <Spinner animation="border" className="mt-5" />;

  return (
    <>
    <Navbar />
    <Container className="py-4">
      <h3 className="mb-4">🔔 Friend Requests</h3>
      {requests.length === 0 ? (
        <Alert variant="info">No pending requests.</Alert>
      ) : (
        <Row>
          {requests.map((req) => (
            <Col key={req.id} md={6} lg={4} className="mb-4">
              <Card>
                <Card.Body>
                  <Card.Title>{req.from_user.first_name} {req.from_user.last_name}</Card.Title>
                  <Card.Subtitle className="mb-2 text-muted">{req.from_user.email}</Card.Subtitle>
                  <Card.Text>
                    Sent on: {new Date(req.created_at).toLocaleString()}
                  </Card.Text>
                  <div className="d-flex gap-2">
                    <Button
                      variant="success"
                      onClick={() => handleAction(req.id, "accept")}
                    >
                      Accept
                    </Button>
                    <Button
                      variant="danger"
                      onClick={() => handleAction(req.id, "reject")}
                    >
                      Reject
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </Container>
    </>
  );
};

export default Notification;

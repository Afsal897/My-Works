import React, { useState } from "react";
import { Modal, Form, Button } from "react-bootstrap";
import { changePassword } from "../../components/profile";

interface Props {
  show: boolean;
  onClose: () => void;
  setError: (msg: string | null) => void;
  setSuccess: (msg: string | null) => void;
}

const PasswordModal: React.FC<Props> = ({
  show,
  onClose,
  setError,
  setSuccess,
}) => {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSubmitPasswordChange = async () => {
    if (newPassword.trim() === "") {
      setError("Password cannot be empty(space not allowed)");
      return;
    }
    if (confirmPassword.trim() === "") {
      setError("confirm password cannot be empty");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const res = await changePassword(
        oldPassword,
        newPassword,
        confirmPassword
      );
      if (res.status === 200) {
        setSuccess("Password updated.");
        onClose();
      } else {
        setError(res.data.error);
      }
    } catch {
      setError("Password update failed.");
    }
  };

  return (
    <Modal show={show} onHide={onClose} centered backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>Change Password</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Old Password</Form.Label>
            <Form.Control
              type={showPassword ? "text" : "password"}
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>New Password</Form.Label>
            <Form.Control
              type={showPassword ? "text" : "password"}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Confirm Password</Form.Label>
            <Form.Control
              type={showPassword ? "text" : "password"}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </Form.Group>
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
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSubmitPasswordChange}>
          Submit
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default PasswordModal;

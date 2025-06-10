import React, { useMemo } from "react";

interface ShareModalProps {
  show: boolean;
  fileToShare: {
    file_id: number;
    filename: string;
  } | null;
  recipientEmail: string;
  expirationHours: string;
  shareMessage: string;
  onClose: () => void;
  onRecipientEmailChange: (email: string) => void;
  onExpirationHoursChange: (hours: string) => void;
  onShareMessageChange: (msg: string) => void;
  onShareSubmit: (fileId: number) => void;
}

const ShareModal: React.FC<ShareModalProps> = ({
  show,
  fileToShare,
  recipientEmail,
  expirationHours,
  shareMessage,
  onClose,
  onRecipientEmailChange,
  onExpirationHoursChange,
  onShareMessageChange,
  onShareSubmit,
}) => {
  // Simple email validation regex
  const isValidEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  // Validate recipient email and expirationHours
  const isFormValid = useMemo(() => {
    return (
      recipientEmail.trim() !== "" &&
      isValidEmail(recipientEmail) &&
      Number(expirationHours) >= 1
    );
  }, [recipientEmail, expirationHours]);

  if (!show || !fileToShare) return null;

  return (
    <div className="modal show d-block" tabIndex={-1} role="dialog">
      <div className="modal-dialog modal-dialog-centered" role="document">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Share File</h5>
            <button
              type="button"
              className="btn-close"
              aria-label="Close"
              onClick={onClose}
            />
          </div>
          <div className="modal-body">
            <p>
              Sharing file: <strong>{fileToShare.filename}</strong>
            </p>

            {/* Recipient Email */}
            <div className="mb-3">
              <label className="form-label">Recipient's Email Address</label>
              <input
                type="email"
                className={`form-control ${
                  recipientEmail && !isValidEmail(recipientEmail) ? "is-invalid" : ""
                }`}
                value={recipientEmail}
                onChange={(e) => onRecipientEmailChange(e.target.value)}
                placeholder="e.g. user@example.com"
              />
              {recipientEmail && !isValidEmail(recipientEmail) && (
                <div className="invalid-feedback">Please enter a valid email address.</div>
              )}
            </div>

            {/* Expiration Time */}
            <div className="mb-3">
              <label className="form-label">Expiration Time (hours)</label>
              <input
                type="number"
                className={`form-control ${
                  expirationHours && Number(expirationHours) < 1 ? "is-invalid" : ""
                }`}
                value={expirationHours}
                onChange={(e) => {
                  onExpirationHoursChange(e.target.value);
                }}
                placeholder="e.g. 24"
                min={1}
              />
              {expirationHours && Number(expirationHours) < 1 && (
                <div className="invalid-feedback">Expiration time must be at least 1 hour.</div>
              )}
            </div>

            {/* Custom Message */}
            <div className="mb-3">
              <label className="form-label">Message</label>
              <textarea
                className="form-control"
                rows={3}
                value={shareMessage}
                onChange={(e) => onShareMessageChange(e.target.value)}
                placeholder="This message will be included in the email."
              />
            </div>
          </div>
          <div className="modal-footer">
            <button
              className="btn btn-success"
              onClick={() => onShareSubmit(fileToShare.file_id)}
              title="Send"
              disabled={!isFormValid}
            >
              📤
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShareModal;

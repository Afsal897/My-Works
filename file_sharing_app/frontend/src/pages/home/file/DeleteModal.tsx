import React from "react";

interface DeleteModalProps {
  show: boolean;
  fileName: string;
  onCancel: () => void;
  onConfirmDelete: () => void;
}

const DeleteModal: React.FC<DeleteModalProps> = ({
  show,
  fileName,
  onCancel,
  onConfirmDelete,
}) => {
  if (!show) return null;

  return (
    <div className="modal show d-block" tabIndex={-1} role="dialog">
      <div className="modal-dialog modal-dialog-centered" role="document">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Confirm Delete</h5>
            <button
              type="button"
              className="btn-close"
              aria-label="Close"
              onClick={onCancel}
            />
          </div>
          <div className="modal-body">
            <p>
              Are you sure you want to delete <strong>{fileName}</strong>?
            </p>
          </div>
          <div className="modal-footer">
            <button className="btn btn-secondary" onClick={onCancel}>
              Cancel
            </button>
            <button className="btn btn-danger" onClick={onConfirmDelete}>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeleteModal;

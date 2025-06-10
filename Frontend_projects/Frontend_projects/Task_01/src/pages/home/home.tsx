import MyNavbar from "./navbar";
import "bootstrap/dist/css/bootstrap.min.css";
import "../../App.css";
import useHomePageLogic from "../../components/home/home";

const HomePage: React.FC = () => {
  const {
    search,
    setSearch,
    contents,
    username,
    currentPage,
    setCurrentPage,
    totalPages,
    loading,
    selectedItem,
    showModal,
    selectedFile,
    handleCardClick,
    handleCloseModal,
    handleFileSelect,
    handleReplaceImage,
    handleEdit,
    isEditingDescription,
    setNewDescription,
    newDescription,
    setIsEditingDescription,
    handleDownload,
    handleDisplay,
    error,
    handleConfirmedDelete,
    handleCloseDeleteModal,
    openDeleteModal,
    showDeleteModal
  } = useHomePageLogic();



  return (
    <div className="home-container">
      <MyNavbar search={search} setSearch={setSearch} />

      <div className="container py-4">
        <h2 className="mb-4">Welcome, {username}!</h2>

        {loading && <div className="mt-3">Loading...</div>}

        <div className="row">
          {contents.map((item) => (
            <div className="col-md-4 mb-4" key={item.id}>
              <div
                className="card h-100"
                onClick={() => handleCardClick(item)}
                style={{ cursor: "pointer" }}
              >
                <img
                  src={handleDisplay(item.filename)}
                  className="card-img-top"
                  alt="..."
                  style={{ maxHeight: "200px", objectFit: "cover" }}
                />
                <div className="card-body">
                  <h5 className="card-title">{item.description}</h5>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="pagination-fixed-bottom">
          <nav>
            <ul className="pagination justify-content-center mb-0">
              {currentPage > 1 && (
                <li className="page-item" onClick={() => setCurrentPage(1)}>
                  <button className="page-link">&laquo;</button>
                </li>
              )}
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(
                  (num) => num >= currentPage - 2 && num <= currentPage + 2
                )
                .map((num) => (
                  <li
                    className={`page-item ${
                      num === currentPage ? "active" : ""
                    }`}
                    key={num}
                    onClick={() => setCurrentPage(num)}
                  >
                    <button className="page-link">{num}</button>
                  </li>
                ))}
              {currentPage < totalPages && (
                <li
                  className="page-item"
                  onClick={() => setCurrentPage(totalPages)}
                >
                  <button className="page-link">&raquo;</button>
                </li>
              )}
            </ul>
          </nav>
        </div>
      </div>

      {showModal && selectedItem && (
        <div
          className="modal d-block"
          tabIndex={-1}
          role="dialog"
          aria-modal="true"
          aria-labelledby="manageImageTitle"
          onClick={handleCloseModal}
          style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
        >
          <div
            className="modal-dialog modal-dialog-centered"
            role="document"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-content p-3">
              <div className="modal-header">
                <h5 className="modal-title" id="manageImageTitle">
                  Manage Image
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  aria-label="Close"
                  onClick={handleCloseModal}
                ></button>
              </div>
              {error && (
          <div className="alert alert-danger mt-3" role="alert">
            {error}
          </div>
        )}
              <div className="modal-body text-center">
                <img
                  src={handleDisplay(selectedItem.filename)}
                  alt="Preview"
                  className="img-fluid mb-3"
                  style={{ maxHeight: "300px", objectFit: "cover" }}
                />
                {!isEditingDescription ? (
                  <>
                    <p>Description: {selectedItem.description}</p>
                    <div className="d-flex justify-content-end mb-3">
                      <button
                        className="btn btn-outline-warning btn-sm"
                        onClick={() => {
                          setIsEditingDescription(true);
                          setNewDescription(selectedItem.description);
                        }}
                        type="button"
                      >
                        Edit Description
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <input
                      type="text"
                      className="form-control mb-2"
                      value={newDescription}
                      onChange={(e) => setNewDescription(e.target.value)}
                    />
                    <div className="d-flex justify-content-end gap-2 mb-3">
                      <button
                        className="btn btn-success btn-sm"
                        onClick={handleEdit}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => setIsEditingDescription(false)}
                      >
                        Cancel
                      </button>
                    </div>
                  </>
                )}
                <input
                  type="file"
                  className="form-control"
                  onChange={handleFileSelect}
                />
              </div>
              <div className="modal-footer">
                <a onClick={handleDownload} className="btn btn-secondary">
                  Download
                </a>
                <button
                  className="btn btn-danger"
                  onClick={() => openDeleteModal(selectedItem)}
                >
                  Delete
                </button>
                <button
                  className="btn btn-warning"
                  onClick={handleReplaceImage}
                  disabled={!selectedFile}
                >
                  Replace
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={handleCloseModal}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showDeleteModal && (
        <>
          <div
            className="modal d-block"
            tabIndex={-1}
            role="dialog"
            style={{
              backgroundColor: "rgba(0,0,0,0.5)",
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              zIndex: 1100,
            }}
          >
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Confirm Deletion</h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={handleCloseDeleteModal}
                  ></button>
                </div>
                <div className="modal-body">
                  <p>Are you sure you want to delete this content?</p>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleCloseDeleteModal}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="btn btn-danger"
                    onClick={handleConfirmedDelete}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="modal-backdrop fade show"></div>
        </>
      )}
    </div>
  );
};

export default HomePage;

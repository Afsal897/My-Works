import React from "react";

interface PaginationInfo {
  total_pages: number;
  // You can add other pagination info like total_files, per_page if needed
}

interface PaginationControlsProps {
  paginationInfo: PaginationInfo;
  currentPage: number;
  onPageChange: (page: number) => void;
  getPageNumbers: () => number[]; // function that returns array of page numbers to show
}

const PaginationControls: React.FC<PaginationControlsProps> = ({
  paginationInfo,
  currentPage,
  onPageChange,
  getPageNumbers,
}) => {
  if (paginationInfo.total_pages <= 1) return null;

  return (
    <nav className="mt-4 d-flex justify-content-center" aria-label="Page navigation">
      <ul className="pagination">
        <li className={`page-item ${currentPage === 1 ? "disabled" : ""}`}>
          <button
            className="page-link"
            onClick={() => onPageChange(1)}
            aria-label="First page"
            disabled={currentPage === 1}
          >
            &laquo;
          </button>
        </li>

        {getPageNumbers().map((page) => (
          <li
            key={page}
            className={`page-item ${page === currentPage ? "active" : ""}`}
          >
            <button
              className="page-link"
              onClick={() => onPageChange(page)}
              aria-current={page === currentPage ? "page" : undefined}
            >
              {page}
            </button>
          </li>
        ))}

        <li className={`page-item ${currentPage === paginationInfo.total_pages ? "disabled" : ""}`}>
          <button
            className="page-link"
            onClick={() => onPageChange(paginationInfo.total_pages)}
            aria-label="Last page"
            disabled={currentPage === paginationInfo.total_pages}
          >
            &raquo;
          </button>
        </li>
      </ul>
    </nav>
  );
};

export default PaginationControls;

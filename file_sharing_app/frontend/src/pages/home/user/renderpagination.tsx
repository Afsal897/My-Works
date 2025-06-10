import React from "react";
import { Button } from "react-bootstrap";

interface RenderPaginationProps {
  totalPages: number;
  currentPage: number;
  onPageChange: (page: number) => void;
}

const RenderPagination: React.FC<RenderPaginationProps> = ({
  totalPages,
  currentPage,
  onPageChange,
}) => {
  if (totalPages <= 1) return null;

  let start = currentPage - 2;
  let end = currentPage + 2;

  if (start < 1) {
    end += 1 - start;
    start = 1;
  }
  if (end > totalPages) {
    start -= end - totalPages;
    end = totalPages;
  }
  if (start < 1) start = 1;

  const pages = [];
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  return (
    <div className="d-flex justify-content-center mt-4 gap-2 flex-wrap">
      <Button
        variant="outline-primary"
        size="sm"
        disabled={currentPage === 1}
        onClick={() => onPageChange(1)}
      >
        &laquo;
      </Button>

      {pages.map((page) => (
        <Button
          key={page}
          variant={page === currentPage ? "primary" : "outline-primary"}
          size="sm"
          onClick={() => onPageChange(page)}
        >
          {page}
        </Button>
      ))}

      <Button
        variant="outline-primary"
        size="sm"
        disabled={currentPage === totalPages}
        onClick={() => onPageChange(totalPages)}
      >
        &raquo;
      </Button>
    </div>
  );
};

export default RenderPagination;

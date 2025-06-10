import React, { useEffect, useState } from "react";

interface HeadAndErrorProps {
  usedStorageMB: number;
  totalStorageMB: number;
  storagePercent: number;
  progressColor: string;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

const HeadAndError: React.FC<HeadAndErrorProps> = ({
  usedStorageMB,
  totalStorageMB,
  storagePercent,
  progressColor,
  searchQuery,
  setSearchQuery,
}) => {
  const [localSearch, setLocalSearch] = useState(searchQuery);

  useEffect(() => {
    const handler = setTimeout(() => {
      setSearchQuery(localSearch);
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [localSearch, setSearchQuery]);

  useEffect(() => {
    setLocalSearch(searchQuery);
  }, [searchQuery]);

  return (
    <div className="mb-4">
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3">
        {/* Left Side - Title + Search */}
        <div>
          <h2 className="mb-2">My Files</h2>
          <input
            type="text"
            className="form-control"
            placeholder="Search files..."
            value={localSearch}
            onChange={(e) => setLocalSearch(e.target.value)}
            style={{ maxWidth: "300px", width: "180%" }}
          />
        </div>

        {/* Right Side - Storage Usage */}
        <div className="w-100 w-md-auto text-start text-md-end">
          <p className="mb-1 fw-bold">
            Used {usedStorageMB.toFixed(2)} MB OF {totalStorageMB} MB
          </p>
          <div className="d-flex justify-content-end">
            <div
              className="progress"
              style={{ height: "20px", maxWidth: "350px", width: "100%" }}
            >
              <div
                className={`progress-bar ${progressColor}`}
                style={{ width: `${storagePercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeadAndError;

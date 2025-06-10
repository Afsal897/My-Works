import React from "react";
import { ProgressBar } from "react-bootstrap";
import { useNavbarContext } from "../home/navbarContext";
import { getStorageUsedPercent, formatStorage, MAX_SPACE } from "../../components/profile";

const StorageProgress: React.FC = () => {
  const { balanceSpace } = useNavbarContext();

  return (
    <>
      <h6 className="mt-3">Storage Used</h6>
      <ProgressBar
        now={getStorageUsedPercent(balanceSpace)}
        label={`${formatStorage(MAX_SPACE - balanceSpace)} used`}
        striped
        animated
        variant="info"
      />
      <div className="text-end text-muted small mt-1">
        {formatStorage(balanceSpace)} free of {formatStorage(MAX_SPACE)}
      </div>
    </>
  );
};

export default StorageProgress;

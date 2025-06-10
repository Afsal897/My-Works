import React from "react";
import { Camera } from "react-bootstrap-icons";
import { useNavbarContext } from "../home/navbarContext";
import { uploadProfilePicture } from "../../components/profile";

interface Props {
  onUploadError: (msg: string) => void;
  onUploadSuccess: (url: string) => void;
}

const ProfilePicture: React.FC<Props> = ({ onUploadError, onUploadSuccess }) => {
  const { url } = useNavbarContext();

  const handleProfilePictureChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const res = await uploadProfilePicture(file);
      if (res.status === 201) {
        onUploadSuccess(res.data.avatarUrl);
      } else {
        onUploadError(res.data.error || "Upload failed");
      }
    } catch {
      onUploadError("Upload error.");
    }
  };

  return (
    <div className="text-center mb-4 position-relative">
      <img
        src={url ? `http://localhost:5000/static/profile/${url}` : "/src/assets/user.png"}
        className="rounded-circle border border-3 border-primary shadow-sm"
        style={{ width: 150, height: 150, objectFit: "cover" }}
        alt="Profile"
      />
      <label htmlFor="upload-photo" className="position-absolute bottom-0 end-50 translate-middle bg-white rounded-circle p-2 shadow-sm" style={{ cursor: "pointer" }}>
        <Camera size={24} className="text-primary" />
        <input type="file" accept="image/*" id="upload-photo" style={{ display: "none" }} onChange={handleProfilePictureChange} />
      </label>
    </div>
  );
};

export default ProfilePicture;

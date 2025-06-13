import React, { useState } from "react";
import api from "../../../api";
import type { Message } from "./chat";

interface FileItem {
  file_id: number;
  filename: string;
}

interface MessageInputProps {
  newMessage: string;
  setNewMessage: React.Dispatch<React.SetStateAction<string>>;
  handleSendMessage: (customMessage?: Partial<Message>) => void;
  selectedFriend: any;
}

const MessageInput: React.FC<MessageInputProps> = ({
  newMessage,
  setNewMessage,
  handleSendMessage,
  selectedFriend,
}) => {
  const [showModal, setShowModal] = useState(false);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [attachedFile, setAttachedFile] = useState<FileItem | null>(null);

  const openAttachModal = async () => {
    try {
      const response = await api.get("/chat/filenames");
      setFiles(response.data.files || []);
      console.log(response.data);
      setShowModal(true);
    } catch (err) {
      console.error("Failed to fetch filenames", err);
    }
  };

  const handleAttachFile = (file: FileItem) => {
    setAttachedFile(file);

    setShowModal(false);
  };

  const onSendClick = () => {
    if (!selectedFriend) return;

    if (attachedFile) {
      // Send message with attached file info

      handleSendMessage({
        content: newMessage,
        is_file: true,
        file_id: attachedFile.file_id,
        filename: attachedFile.filename,
      });
      setAttachedFile(null);
      setNewMessage(""); // Clear input after sending file
    } else if (newMessage.trim() !== "") {
      // Send normal text message
      handleSendMessage();
      setNewMessage("");
    }
  };

  if (!selectedFriend) return null;

  return (
    <>
      {attachedFile && (
        <div
          style={{
            padding: "8px 14px",
            backgroundColor: "#f0f4ff",
            border: "1px solid #c4d1ff",
            borderRadius: 20,
            margin: "10px 0 0",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            maxWidth: "80%",
            minHeight: 40,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              overflow: "hidden",
              whiteSpace: "nowrap",
              textOverflow: "ellipsis",
              flex: 1,
            }}
          >
            📎{" "}
            <span
              style={{
                marginLeft: 6,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
              title={attachedFile.filename}
            >
              {attachedFile.filename}
            </span>
          </div>
          <button
            onClick={() => setAttachedFile(null)}
            style={{
              background: "transparent",
              border: "none",
              fontSize: 16,
              color: "#333",
              cursor: "pointer",
              marginLeft: 10,
              padding: "2px 6px",
              lineHeight: 1,
            }}
            title="Remove attached file"
          >
            ❌
          </button>
        </div>
      )}

      <div
        style={{
          position: "sticky",
          bottom: 0,
          padding: 10,
          display: "flex",
          alignItems: "center",
          borderTop: "1px solid #ddd",
          backgroundColor: "#fff",
          zIndex: 10,
        }}
      >
        <div style={{ position: "relative", flexGrow: 1 }}>
          <input
            type="text"
            placeholder="Type a message"
            value={newMessage}
            onKeyDown={(e) => e.key === "Enter" && onSendClick()}
            onChange={(e) => setNewMessage(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 40px 10px 14px",
              border: "1px solid #ccc",
              borderRadius: 20,
              outline: "none",
              fontSize: 14,
            }}
          />
          {/* Attach Icon */}
          <button
            onClick={openAttachModal}
            style={{
              position: "absolute",
              right: 10,
              top: "50%",
              transform: "translateY(-50%)",
              background: "none",
              border: "none",
              cursor: "pointer",
              padding: 0,
            }}
            title="Attach File"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              height="30"
              width="30"
              fill="#555"
              viewBox="0 0 24 24"
            >
              <path d="M16.5,6.5L10,13c-0.9,0.9-2.4,0.9-3.3,0S5.8,10.6,6.7,9.7l6.5-6.5c1.6-1.6,4.1-1.6,5.7,0s1.6,4.1,0,5.7l-8.2,8.2 c-2.1,2.1-5.6,2.1-7.8,0s-2.1-5.6,0-7.8L10,3" />
            </svg>
          </button>
        </div>

        <button
          onClick={() => onSendClick()}
          style={{
            marginLeft: 8,
            backgroundColor: "#63b3ed",
            border: "none",
            borderRadius: "50%",
            width: 40,
            height: 40,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
          }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            height="20"
            width="20"
            fill="#fff"
            viewBox="0 0 24 24"
          >
            <path d="M2 21l21-9L2 3v7l15 2-15 2z" />
          </svg>
        </button>
      </div>

      {/* Attach File Modal */}
      {showModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 999,
          }}
          onClick={() => setShowModal(false)}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              padding: 20,
              borderRadius: 12,
              width: "400px",
              maxHeight: "70vh",
              boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
              overflowY: "auto",
              fontFamily: "'Segoe UI', sans-serif",
            }}
          >
            <h3 style={{ marginBottom: 10 }}>📁 Select a File to Attach</h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              {files.length > 0 ? (
                files.map((file) => (
                  <li
                    key={file.file_id}
                    onClick={() => handleAttachFile(file)}
                    style={{
                      padding: "10px 12px",
                      marginBottom: 6,
                      backgroundColor: "#f9f9f9",
                      border: "1px solid #ddd",
                      borderRadius: 8,
                      cursor: "pointer",
                      transition: "background-color 0.2s",
                    }}
                    onMouseEnter={(e) =>
                      (e.currentTarget.style.backgroundColor = "#e9f3ff")
                    }
                    onMouseLeave={(e) =>
                      (e.currentTarget.style.backgroundColor = "#f9f9f9")
                    }
                  >
                    📎 {file.filename}
                  </li>
                ))
              ) : (
                <li style={{ padding: "8px 0" }}>No files available.</li>
              )}
            </ul>
            <button
              onClick={() => setShowModal(false)}
              style={{
                marginTop: 16,
                padding: "8px 16px",
                backgroundColor: "#ccc",
                border: "none",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default MessageInput;

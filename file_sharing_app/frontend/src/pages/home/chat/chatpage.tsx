import React, { useRef, useEffect } from "react";
import downloadIcon from "../../../assets/download.png";
import api from "../../../api";

interface Message {
  id: number;
  sender: string;
  receiver: string;
  content: string;
  timestamp: string;
  is_file?: boolean;
  file_id?: number;
  filename?: string;
}

interface Friend {
  email: string;
  first_name: string;
  last_name: string;
}

interface ChatWindowProps {
  selectedFriend: Friend | null;
  messages: Message[];
  loadingMessages: boolean;
  onMessagesScroll: (e: React.UIEvent<HTMLDivElement>) => void;
  messagesContainerRef: React.RefObject<HTMLDivElement | null>;
}

const chatBubbleStyle = (isMe: boolean): React.CSSProperties => ({
  alignSelf: isMe ? "flex-end" : "flex-start",
  backgroundColor: isMe ? "#63b3ed" : "#e5e5ea",
  color: isMe ? "white" : "black",
  padding: "8px 12px",
  borderRadius: 18,
  maxWidth: "60%",
  marginBottom: 8,
  wordBreak: "break-word",
});

const handleDownload = async (fileId?: number, filename?: string) => {
  if (!fileId) {
    return;
  }
  try {
    const response = await api.get(
      `${import.meta.env.VITE_API_URL}/chat/download/${fileId}`,
      { responseType: "blob" }
    );

    if (response.status !== 200) throw new Error("Download failed");

    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename ? filename : "newname");
    document.body.appendChild(link);
    link.click();

    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Download error:", error);
    // show error toast here if you want
  }
};

const ChatWindow: React.FC<ChatWindowProps> = ({
  selectedFriend,
  messages,
  loadingMessages,
  onMessagesScroll,
  messagesContainerRef,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView();
  }, [messages]);

  return (
    <>
      <div
        style={{
          position: "sticky",
          top: 0,
          padding: 10,
          borderBottom: "1px solid #ddd",
          fontWeight: "bold",
          fontSize: 18,
          backgroundColor: "#fff",
        }}
      >
        {selectedFriend
          ? `${selectedFriend.first_name} ${selectedFriend.last_name}`
          : "Select a friend to chat"}
      </div>

      <div
        ref={messagesContainerRef}
        onScroll={onMessagesScroll}
        style={{
          flexGrow: 1,
          overflowY: "auto",
          height: "90%",
          padding: 10,
          display: "flex",
          flexDirection: "column",
        }}
      >
        {selectedFriend && messages.length === 0 && !loadingMessages && (
          <div
            style={{
              textAlign: "center",
              marginTop: 20,
              color: "#87cefa",
              fontSize: 16,
            }}
          >
            Start a chat
          </div>
        )}

        {[...messages]
          .sort(
            (a, b) =>
              new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
          )
          .map((msg) => {
            const isMe = msg.sender !== selectedFriend?.email;
            return (
              <div key={msg.id} style={chatBubbleStyle(isMe)}>
                {/* File message bubble */}
                {msg.is_file && (
                  <div
                    style={{
                      backgroundColor: isMe ? "#dcf8c6" : "#fff",
                      padding: "10px 14px",
                      borderRadius: 12,
                      display: "flex",
                      alignItems: "center",
                      boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                      maxWidth: 300,
                      marginTop: 4,
                    }}
                  >
                    <span style={{ fontSize: 18, marginRight: 8 }}>📎</span>
                    <strong
                      title={msg.filename}
                      style={{
                        flex: 1,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        color: "#333",
                      }}
                    >
                      {msg.filename?.trim() || "Unnamed File"}
                    </strong>
                    {msg.file_id !== undefined && (
                      <button
                        onClick={() =>
                          handleDownload(msg.file_id, msg.filename)
                        }
                        title="Download File"
                        style={{
                          marginLeft: 10,
                          backgroundColor: "#25d366",
                          borderRadius: 20,
                          padding: 6,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          border: "none",
                          cursor: "pointer",
                        }}
                      >
                        <img
                          src={downloadIcon}
                          alt="Download"
                          style={{ height: 16, width: 16 }}
                        />
                      </button>
                    )}
                  </div>
                )}
                {msg.content?.trim() && (
                  <div
                    style={{
                      marginTop: 4,
                      maxWidth: 300,
                      color: "black",
                      fontSize: 14,
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                    }}
                  >
                    {msg.content}
                  </div>
                )}
                {/* Timestamp */}
                <div
                  style={{
                    fontSize: 10,
                    color: isMe ? "rgba(255,255,255,0.7)" : "rgba(0,0,0,0.45)",
                    marginTop: 6,
                    textAlign: "right",
                  }}
                >
                  {new Date(msg.timestamp).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </div>
            );
          })}

        <div ref={messagesEndRef} />
        {loadingMessages && (
          <div style={{ textAlign: "center", padding: 10 }}>
            Loading messages...
          </div>
        )}
      </div>
    </>
  );
};

export default ChatWindow;

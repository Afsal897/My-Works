import React, { useEffect, useState, useRef, useCallback } from "react";
import api from "../../../api";
import socket from "../../../components/socket";
import { useNavbarContext } from "../navbarContext";
import MessageInput from "./messageinput";
import Sidebar from "./sidebar";
import ChatWindow from "./chatpage";

interface Friend {
  id: string | number;
  email: string;
  first_name: string;
  last_name: string;
  avatar?: string | null;
}

export interface Message {
  id: number;
  sender: string;
  receiver: string;
  content: string;
  timestamp: string;
  is_file?: boolean;
  file_id?: number;
  filename?: string;
}

const FRIENDS_PAGE_SIZE = 20;
const MESSAGES_PAGE_SIZE = 30;

const Chat: React.FC = () => {
  // Navbar context
  const { email } = useNavbarContext();
  const currentUser = { email };

  // State
  const [friends, setFriends] = useState<Friend[]>([]);
  const [friendPage, setFriendPage] = useState(1);
  const [friendTotalPages, setFriendTotalPages] = useState(1);
  const [friendSearch, setFriendSearch] = useState("");
  const [loadingFriends, setLoadingFriends] = useState(false);
  const [selectedFriend, setSelectedFriend] = useState<Friend | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageOffset, setMessageOffset] = useState(0);
  const [hasMoreMessages, setHasMoreMessages] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [newMessage, setNewMessage] = useState("");
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Debounce Hook
  const useDebounce = (callback: (value: string) => void, delay: number) =>
    useCallback(
      (value: string) => {
        if (debounceTimer.current) clearTimeout(debounceTimer.current);
        debounceTimer.current = setTimeout(() => callback(value), delay);
      },
      [callback, delay]
    );

  // Load Friends
  const loadFriends = async (page: number, search: string) => {
    setLoadingFriends(true);
    try {
      const res = await api.get("/chat/friends", {
        params: { page, per_page: FRIENDS_PAGE_SIZE, search },
      });
      setFriendTotalPages(res.data.total_pages);
      setFriends((prev) =>
        page === 1 ? res.data.friends : [...prev, ...res.data.friends]
      );
    } catch (err) {
      console.error("Failed to load friends", err);
    } finally {
      setLoadingFriends(false);
    }
  };

  const debouncedSearch = useDebounce((val: string) => {
    setFriendPage(1);
    loadFriends(1, val);
  }, 500);

  const onFriendSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setFriendSearch(val);
    debouncedSearch(val);
  };

  const onFriendsScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    if (
      scrollHeight - scrollTop - clientHeight < 100 &&
      !loadingFriends &&
      friendPage < friendTotalPages
    ) {
      setFriendPage((prev) => prev + 1);
    }
  };

  const loadMessages = async (friendEmail: string, offset: number) => {
    setLoadingMessages(true);
    try {
      const res = await api.get(`/chat/chat/${friendEmail}`, {
        params: { limit: MESSAGES_PAGE_SIZE, offset },
      });
      setMessages((prev) => (offset === 0 ? res.data : [...res.data, ...prev]));
      setHasMoreMessages(res.data.length === MESSAGES_PAGE_SIZE);
      console.log(messages);
    } catch (err) {
      console.error("Failed to load messages", err);
    } finally {
      setLoadingMessages(false);
    }
  };

  const onMessagesScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const threshold = 30;

    // Only load more when scrolled near the top
    const isNearTop = e.currentTarget.scrollTop <= threshold;

    if (isNearTop && !loadingMessages && hasMoreMessages && selectedFriend) {
      const newOffset = messageOffset + MESSAGES_PAGE_SIZE;

      setLoadingMessages(true); // prevent duplicate loads
      setMessageOffset(newOffset);
      loadMessages(selectedFriend.email, newOffset).finally(() =>
        setLoadingMessages(false)
      );
    }
  };

  const handleSendMessage = async (customMessage?: Partial<Message>) => {
    const content = newMessage.trim();
    if (!selectedFriend) return;

    const tempId = Date.now();

    const baseMsg: Message = {
      id: tempId,
      sender: currentUser.email,
      receiver: selectedFriend.email,
      content: customMessage?.content ?? content,
      timestamp: new Date().toISOString(),
      is_file: customMessage?.is_file ?? false,
      file_id: customMessage?.file_id,
      filename: customMessage?.filename,
    };

    // Don't send empty non-file messages
    if (!baseMsg.content && !baseMsg.is_file) return;

    try {
      socket.emit("send_message", baseMsg);
      setNewMessage("");
    } catch (err) {
      console.error("Failed to send message", err);
    }
  };

  // Effects
  useEffect(() => {
    loadFriends(friendPage, friendSearch);
  }, [friendPage, friendSearch]);

  useEffect(() => {
    if (selectedFriend) {
      setMessages([]);
      setMessageOffset(0);
      setHasMoreMessages(true);
      loadMessages(selectedFriend.email, 0).then(() => {
        setTimeout(() => {
          if (messagesContainerRef.current) {
            const container = messagesContainerRef.current;
            container.scrollTop = container.scrollHeight;
          }
        }, 0); // Wait for DOM to render
      });
    }
  }, [selectedFriend]);

  useEffect(() => {
    if (messageOffset === 0 && messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop =
        messagesContainerRef.current.scrollHeight;
    }
  }, [messages, selectedFriend]);

  useEffect(() => {
    if (!currentUser.email) return;

    const joinRoom = () => {
      socket.emit("join", { email: currentUser.email });
      console.log("Joining socket room for:", currentUser.email);
    };

    if (socket.connected) joinRoom();
    else socket.once("connect", joinRoom);

    socket.on("receive_message", (message: Message) => {
      setMessages((prev) => {
        const exists = prev.some((msg) => msg.id === message.id);
        if (exists) return prev;
        return [...prev, message];
      });
    });

    return () => {
      socket.off("receive_message");
    };
  }, [currentUser.email]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleBack = () => {
    setSelectedFriend(null);
  };

  return (
    <div className="d-flex vh-100 overflow-hidden font-monospace bg-light">
      {/* Sidebar (friends list) */}
      {(!isMobile || !selectedFriend) && (
        <div
          className="border-end bg-white p-2"
          style={{ width: isMobile ? "100%" : "300px", overflowY: "auto" }}
        >
          <Sidebar
            friends={friends}
            selectedFriend={selectedFriend}
            setSelectedFriend={setSelectedFriend}
            friendSearch={friendSearch}
            onFriendSearchChange={onFriendSearchChange}
            onFriendsScroll={onFriendsScroll}
            loadingFriends={loadingFriends}
          />
        </div>
      )}

      {/* Chat panel */}
      {(!isMobile || selectedFriend) && (
        <div className="d-flex flex-column flex-grow-1 bg-light">
          {/* Mobile back button */}
          {isMobile && selectedFriend && (
            <div className="d-flex align-items-center p-2 bg-white border-bottom">
              <button
                onClick={handleBack}
                className="btn btn-outline-secondary btn-sm me-2"
              >
                ←
              </button>
              <div>
                <strong>{selectedFriend.first_name}</strong>
                <div className="text-muted small">{selectedFriend.email}</div>
              </div>
            </div>
          )}

          <div className="flex-grow-1 overflow-auto">
            <ChatWindow
              selectedFriend={selectedFriend}
              messages={messages}
              loadingMessages={loadingMessages}
              onMessagesScroll={onMessagesScroll}
            />
          </div>

          <div className="border-top bg-white">
            <MessageInput
              newMessage={newMessage}
              setNewMessage={setNewMessage}
              handleSendMessage={handleSendMessage}
              selectedFriend={selectedFriend}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;

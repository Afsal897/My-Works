import React from "react";

interface Friend {
  id: number | string;
  avatar?: string | null;
  first_name: string;
  last_name: string;
  email: string;
}

interface SidebarProps {
  friends: Friend[];
  selectedFriend: Friend | null;
  setSelectedFriend: (friend: Friend) => void;
  friendSearch: string;
  onFriendSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onFriendsScroll: (e: React.UIEvent<HTMLDivElement>) => void;
  loadingFriends: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({
  friends,
  selectedFriend,
  setSelectedFriend,
  friendSearch,
  onFriendSearchChange,
  onFriendsScroll,
  loadingFriends,
}) => {
  return (
    <div
      style={{
        width: 300,
        borderRight: "1px solid #ddd",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <input
        type="text"
        placeholder="Search friends..."
        value={friendSearch}
        onChange={onFriendSearchChange}
        style={{
          padding: 10,
          border: "none",
          borderBottom: "1px solid #ddd",
          fontSize: 16,
        }}
      />
      <div style={{ overflowY: "auto", flexGrow: 1 }} onScroll={onFriendsScroll}>
        {friends.map((friend) => (
          <div
            key={friend.id}
            onClick={() => setSelectedFriend(friend)}
            style={{
              padding: 10,
              cursor: "pointer",
              backgroundColor:
                selectedFriend?.id === friend.id ? "#e6f7ff" : "transparent",
              borderBottom: "1px solid #eee",
              display: "flex",
              alignItems: "center",
            }}
          >
            <img
              src={
                friend.avatar
                  ? `http://localhost:5000/static/profile/${friend.avatar}`
                  : "/src/assets/user.png"
              }
              alt="avatar"
              style={{
                width: 40,
                height: 40,
                borderRadius: "50%",
                marginRight: 10,
                objectFit: "cover",
              }}
            />
            <div>
              <div style={{ fontWeight: "bold" }}>
                {friend.first_name} {friend.last_name}
              </div>
              <div style={{ fontSize: 12, color: "#555" }}>{friend.email}</div>
            </div>
          </div>
        ))}
        {loadingFriends && <div style={{ padding: 10 }}>Loading...</div>}
      </div>
    </div>
  );
};

export default Sidebar;

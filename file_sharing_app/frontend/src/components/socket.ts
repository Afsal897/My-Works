// socket.ts
import { io, Socket } from "socket.io-client";
// const token = localStorage.getItem("access_token");

const socket: Socket = io(`${import.meta.env.VITE_API_URL}`, {
  transports: ["websocket"],
});
// socket.ts or somewhere global where socket is created
socket.on("connect", () => {
  console.log("Socket connected:", socket.id);//getting id in front end
});

socket.on("connect_error", (err) => {
  console.error("Socket connection error:", err);
});


export default socket;

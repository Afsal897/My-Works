import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/login";
import Register from "./pages/register";
import PageNotFound from "./pages/404page";
import ProtectedRoute from "./components/protectedRoute";
import Home from "./pages/home/home";
import Logout from "./pages/logout";
import ForgotPassword from "./pages/forgotpassword";
import ResetPassword from "./pages/resetpassword";
import FileList from "./pages/home/file/filelist";
import Chat from "./pages/home/chat/chat"; 
import Users from "./pages/home/user/users";
import { DataProvider } from "./pages/home/datacontext";
import UserPage from "./pages/profile/profile";
import UploadPage from "./pages/home/file/upload";
import { NavbarProvider } from "./pages/home/navbarContext";
import History from "./pages/home/history";
import Notification from "./pages/home/notifications";
import SharedFilePage from "./pages/home/shared";
import { useEffect } from "react";

function App() {

  useEffect(() => {
  const handleStorageChange = (event: StorageEvent) => {
    if (event.key === "logout") {
      localStorage.removeItem("logout")
      // Token was cleared in another tab
      window.location.href = "/login";
    }
  };

  window.addEventListener("storage", handleStorageChange);
  return () => window.removeEventListener("storage", handleStorageChange);
}, []);

  return (
    <NavbarProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/shared" element={< SharedFilePage/>} />

          <Route element={<ProtectedRoute />}>
            <Route
              path="/home"
              element={
                <DataProvider>
                  <Home />
                </DataProvider>
              }
            >
              <Route index element={<Navigate to="file" replace />} />
              <Route path="file" element={<FileList />} />
              <Route path="users" element={<Users />} />
              <Route path="chat" element={<Chat />} />
            </Route>
            <Route path="/home/upload" element={<UploadPage />} />
            <Route path="/notification" element={<Notification />} />
            <Route path="/profile" element={<UserPage />} />
            <Route path="/history" element={<History />} />
            <Route path="/logout" element={<Logout />} />
          </Route>

          <Route path="*" element={<PageNotFound />} />
        </Routes>
      </Router>
      </NavbarProvider>
  );
}

export default App;
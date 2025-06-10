import React, { useEffect } from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./navbar";
import { useDataContext } from "./datacontext";
import { fetchData } from "../../components/home";

const Home: React.FC = () => {
  const {
    filePage,
    userPage,
    searchQuery,
    setFiles,
    setContacts,
    setPaginationInfo,
    setContactPageInfo,
    setSpaceLeft,
    setError,
  } = useDataContext();

  const loadData = async () => {
    try {
      const result = await fetchData(filePage, userPage, searchQuery);
      setFiles(result.files);
      setContacts(
        result.contacts.map((c: any) => ({
          username: c.username || "Unknown",
          email: c.email,
          avatarUrl: c.avatarUrl || "",
        }))
      );
      setPaginationInfo(result.file_page);
      setContactPageInfo(result.user_page);
      setSpaceLeft(result.space_left);
      setError("");
    } catch (err) {
      console.error("Failed to load data:", err);
      setError("Failed to load data.");
    }
  };

  useEffect(() => {
    loadData();
  }, [filePage, userPage, searchQuery]);

  return (
    <>
      <Navbar />
      <div className="container mt-4">
        <Outlet />
      </div>
    </>
  );
};

export default Home;

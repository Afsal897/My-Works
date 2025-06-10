import React, { createContext, useContext, useState } from "react";

interface MyFile {
  file_id: number;
  filename: string;
  size: string;
  date: string;
}

export interface Contact {
  username: string;
  email: string;
  avatarUrl?: string;
}

export interface PaginationInfo {
  page: number;
  per_page: number;
  total_pages: number;
  total_files: number;
}

export interface ContactPageInfo {
  page: number;
  per_page: number;
  total_pages: number;
  total_users: number;
}

interface DataContextType {
  files: MyFile[];
  setFiles: React.Dispatch<React.SetStateAction<MyFile[]>>;
  contacts: Contact[];
  setContacts: React.Dispatch<React.SetStateAction<Contact[]>>;
  spaceLeft: number;
  setSpaceLeft: React.Dispatch<React.SetStateAction<number>>;
  paginationInfo: PaginationInfo;
  setPaginationInfo: React.Dispatch<React.SetStateAction<PaginationInfo>>;
  contactPageInfo: ContactPageInfo;
  setContactPageInfo: React.Dispatch<React.SetStateAction<ContactPageInfo>>;
  error: string;
  setError: React.Dispatch<React.SetStateAction<string>>;
  filePage: number;
  setFilePage: React.Dispatch<React.SetStateAction<number>>;
  userPage: number;
  setUserPage: React.Dispatch<React.SetStateAction<number>>;
  searchQuery: string;
  setSearchQuery: React.Dispatch<React.SetStateAction<string>>;
  // loadData: () => Promise<void>;
}

export const DataContext = createContext<DataContextType | undefined>(undefined);

export const useDataContext = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error("useDataContext must be used within a DataProvider");
  }
  return context;
};

export const DataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [files, setFiles] = useState<MyFile[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [spaceLeft, setSpaceLeft] = useState(1024 * 1024 * 1024); // 1 GB
  const [paginationInfo, setPaginationInfo] = useState<PaginationInfo>({
    page: 1,
    per_page: 10,
    total_pages: 1,
    total_files: 0,
  });
  const [contactPageInfo, setContactPageInfo] = useState<ContactPageInfo>({
    page: 1,
    per_page: 8,
    total_pages: 1,
    total_users: 0,
  });
  const [error, setError] = useState("");
  const [filePage, setFilePage] = useState(1);
  const [userPage, setUserPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <DataContext.Provider
      value={{
        files,
        setFiles,
        contacts,
        setContacts,
        spaceLeft,
        setSpaceLeft,
        paginationInfo,
        setPaginationInfo,
        contactPageInfo,
        setContactPageInfo,
        error,
        setError,
        filePage,
        setFilePage,
        userPage,
        setUserPage,
        searchQuery,
        setSearchQuery,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};

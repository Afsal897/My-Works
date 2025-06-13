import React, { createContext, useContext, useState } from "react";

interface NavbarContextType {
  firstName: string;
  setFirstName: React.Dispatch<React.SetStateAction<string>>;
  lastName: string;
  setLastName: React.Dispatch<React.SetStateAction<string>>;
  username: string;
  setUsername: React.Dispatch<React.SetStateAction<string>>;
  email: string;
  setEmail: React.Dispatch<React.SetStateAction<string>>;
  dob: string | null;
  setDOB: React.Dispatch<React.SetStateAction<string | null>>;
  url: string;
  setUrl: React.Dispatch<React.SetStateAction<string>>;
  balanceSpace: number;
  setBalanceSpace: React.Dispatch<React.SetStateAction<number>>;
  showText: boolean;
  setShowText: React.Dispatch<React.SetStateAction<boolean>>;
}

const NavbarContext = createContext<NavbarContextType | undefined>(undefined);

export const NavbarProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [balanceSpace, setBalanceSpace] = useState(0);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [dob, setDOB] = useState<string | null>(null);
  const [url, setUrl] = useState("");
  const [showText, setShowText] = useState(false);
  

  return (
    <NavbarContext.Provider
      value={{
        firstName,
        setFirstName,
        lastName,
        setLastName,
        username,
        setUsername,
        email,
        setEmail,
        dob,
        setDOB,
        url,
        setUrl,
        balanceSpace,
        setBalanceSpace,
        showText,
        setShowText,
      }}
    >
      {children}
    </NavbarContext.Provider>
  );
};

export const useNavbarContext = (): NavbarContextType => {
  const context = useContext(NavbarContext);
  if (!context) {
    throw new Error("useNavbarContext must be used within a NavbarProvider");
  }
  return context;
};

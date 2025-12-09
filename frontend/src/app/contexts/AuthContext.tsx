// AuthContext.tsx
import axios from "axios";
import { createContext, useState, useEffect } from "react";
interface AuthContextType {
    isLoggedIn: boolean;
    username: string | null;
    setIsLoggedIn: (value: boolean) => void;
    setUsername: (value: string | null) => void;
  }
export const AuthContext = createContext<AuthContextType>({
    isLoggedIn: false,
    username: null,
  setIsLoggedIn: () => {},
  setUsername: () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode}) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    const checkAuthStatus = async () => {
      if (typeof window === "undefined") return;

      const accessToken = localStorage.getItem("accessToken");
      if (!accessToken) {
        setIsLoggedIn(false);
        setUsername(null);
        return;
      }

      try {
        const response = await axios.get(`http://localhost:8000/auth-status/`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          withCredentials: true
        });
        console.log(response)
        if (response.status==200) {
          setIsLoggedIn(true);
          setUsername(response.data.username);
        } else {
          setIsLoggedIn(false);
          setUsername(null);
        }
      } catch (error) {
        console.error("Error checking auth status:", error);
        setIsLoggedIn(false);
        setUsername(null);
      }
    };

    checkAuthStatus();
  }, []);

  return (
    <AuthContext.Provider value={{ isLoggedIn, setIsLoggedIn, username, setUsername }}>
      {children}
    </AuthContext.Provider>
  );
};
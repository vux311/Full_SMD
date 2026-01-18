"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";

interface AuthContextType {
  userId: string | null;
  role: string | null;
  isLoading: boolean;
  setRole: (role: string) => void;
  setUserId: (id: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  userId: null,
  role: null,
  isLoading: true,
  setRole: () => {},
  setUserId: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [role, setRoleState] = useState<string | null>(null);
  const [userId, setUserIdState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Load from localStorage on mount
    const storedRole = localStorage.getItem("role");
    const storedUserId = localStorage.getItem("user_id");
    setRoleState(storedRole);
    setUserIdState(storedUserId);
    setIsLoading(false);
  }, []);

  const setRole = (newRole: string) => {
    localStorage.setItem("role", newRole);
    setRoleState(newRole);
  };

  const setUserId = (id: string) => {
    localStorage.setItem("user_id", id);
    setUserIdState(id);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("role");
    localStorage.removeItem("user_id");
    localStorage.removeItem("full_name");
    localStorage.removeItem("username");
    setRoleState(null);
    setUserIdState(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ userId, role, isLoading, setRole, setUserId, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);

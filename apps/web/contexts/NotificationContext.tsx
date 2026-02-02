"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { io, Socket } from "socket.io-client";
import { useAuth } from "./AuthContext";
import axios from "@/lib/axios";

interface Notification {
  id: string | number;
  title: string;
  message: string;
  type?: "info" | "success" | "warning" | "error";
  isRead: boolean;
  createdAt: string;
  link?: string;
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  markAsRead: (id: string | number) => Promise<void>;
  clearAll: () => void;
  refresh: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const { userId, role } = useAuth();
  const [socket, setSocket] = useState<Socket | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const fetchNotifications = useCallback(async () => {
    if (!userId) return;
    try {
      const res = await axios.get("/notifications");
      setNotifications(Array.isArray(res.data) ? res.data : []);
    } catch (e) {
      console.error("Failed to fetch notifications:", e);
    }
  }, [userId]);

  const refresh = useCallback(async () => {
    await fetchNotifications();
  }, [fetchNotifications]);

  useEffect(() => {
    if (!userId) return;

    fetchNotifications();

    const newSocket = io(process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000", {
        transports: ["websocket"],
        query: { userId: userId }
    });

    newSocket.on("connect", () => {
      console.log("[Socket] Connected to server");
      newSocket.emit("join", { room: `user_${userId}` });
    });

    // Listen for syllabus evaluation (for Lecturers)
    newSocket.on("syllabus_evaluated", (data: any) => {
      refresh(); // Reload from DB to get the official record
      
      // Also show a browser notification
      if ("Notification" in window && window.Notification.permission === "granted") {
        new window.Notification(
            data.action === "APPROVE" ? "Đề cương được duyệt" : "Yêu cầu chỉnh sửa",
            { body: `Môn ${data.subject_code} đã được ${data.action === "APPROVE" ? "duyệt" : "trả lại"}.` }
        );
      }
    });

    // Listen for new submissions (for HoDs, AA, etc.)
    newSocket.on("syllabus_submitted", (data: any) => {
      const relevantRoles = ["Head of Dept", "HoD", "Academic Affairs", "AA", "Admin"];
      if (relevantRoles.includes(role || "")) {
        refresh();
      }
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [userId, role, fetchNotifications, refresh]);

  const markAsRead = async (id: string | number) => {
    try {
      await axios.put(`/notifications/${id}/read`);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, isRead: true } : n));
    } catch (e) {
      console.error("Failed to mark notification as read:", e);
    }
  };

  const clearAll = () => {
    setNotifications([]);
  };

  const unreadCount = notifications.filter(n => !n.isRead).length;

  return (
    <NotificationContext.Provider value={{ 
        notifications, 
        unreadCount, 
        markAsRead, 
        clearAll,
        refresh
    }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error("useNotifications must be used within a NotificationProvider");
  }
  return context;
}

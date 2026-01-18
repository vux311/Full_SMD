"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useNotifications } from "@/contexts/NotificationContext";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { LogOut, Bell } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import axios, { API_BASE } from "@/lib/axios";

export default function Header() {
  const router = useRouter();
  const { setRole: setAuthRole, setUserId, logout } = useAuth();
  const { notifications, unreadCount, markAsRead } = useNotifications();
  const [user, setUser] = useState<{ fullName: string; roles?: { id: number; name: string }[]; avatarFileId?: number } | null>(null);
  const [academicYear, setAcademicYear] = useState("Loading...");
  
  // Hàm fetch user & info
  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) { router.push("/login"); return; }

      try {
        // Lấy User Info
        const userRes = await axios.get("/users/me");
        const userData = userRes.data;
        setUser(userData);

        if (userData?.id) {
          setUserId(userData.id.toString());
        }

        // Store role in context
        if (userData?.role) {
          setAuthRole(userData.role);
        } else if (userData?.roles && userData.roles.length > 0) {
          // Fallback if role string is missing but roles array exists
          const roleName = userData.roles[0].role?.name || userData.roles[0].name;
          if (roleName) setAuthRole(roleName);
        }

        // Lấy Năm học
        try {
          const yearRes = await axios.get("/academic-years/");
          const years = Array.isArray(yearRes.data) ? yearRes.data : [];
          const activeYear = years.find((y: any) => y.is_active || y.isActive);
          setAcademicYear(activeYear?.code || "Chưa cấu hình");
        } catch (e) { /* ignore */ }
      } catch (err: any) {
        console.error("Header fetchData error:", err);
      }
    };
    fetchData();
  }, [router]);

  const handleRead = async (notif: any) => {
      if(!notif.is_read) {
          await markAsRead(notif.id);
      }
      if(notif.link) router.push(notif.link);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="flex items-center justify-between gap-4 py-4 px-6 border-b border-border bg-background sticky top-0 z-10 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="text-sm font-medium text-teal-800 bg-teal-50 px-3 py-1 rounded-full border border-teal-100">
            📅 {academicYear}
        </div>
      </div>

      <div className="flex items-center gap-4">
        {user ? (
            <>
                {/* --- CHUÔNG THÔNG BÁO --- */}
                <Popover>
                    <PopoverTrigger asChild>
                        <Button variant="ghost" size="icon" className="relative">
                            <Bell className="w-5 h-5 text-gray-600" />
                            {unreadCount > 0 && (
                                <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white animate-pulse"></span>
                            )}
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-80 p-0" align="end">
                        <div className="p-3 border-b font-semibold text-sm bg-slate-50 rounded-t-md flex justify-between">
                            <span>Thông báo</span>
                            <span className="text-xs text-gray-500 font-normal">{unreadCount} chưa đọc</span>
                        </div>
                        <div className="max-h-[300px] overflow-y-auto">
                            {notifications.length === 0 ? (
                                <div className="p-8 text-center text-xs text-gray-400">Không có thông báo mới</div>
                            ) : (
                                notifications.map((n: any) => (
                                    <div 
                                        key={n.id} 
                                        onClick={() => handleRead(n)}
                                        className={`p-3 border-b cursor-pointer hover:bg-slate-50 transition-colors ${!n.is_read ? 'bg-blue-50/60' : ''}`}
                                    >
                                        <div className="text-sm font-semibold text-slate-800 mb-0.5">{n.title}</div>
                                        <div className="text-xs text-slate-600 line-clamp-2">{n.message}</div>
                                        <div className="text-[10px] text-slate-400 mt-2 text-right">
                                            {new Date(n.created_at).toLocaleString('vi-VN')}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </PopoverContent>
                </Popover>

                {/* --- USER INFO --- */}
                <div className="text-right hidden md:block">
                    <div className="text-sm font-bold">{user.fullName}</div>
                    <div className="text-xs text-muted-foreground">
                      {user.roles && user.roles.length > 0 
                        ? user.roles.map(r => r.name).join(", ") 
                        : "Chưa có vai trò"}
                    </div>
                </div>
                <Avatar>
                    {user.avatarFileId ? (
                        <AvatarImage src={`${API_BASE}/files/${user.avatarFileId}`} />
                    ) : null}
                    <AvatarFallback className={user.roles?.[0]?.name === "Lecturer" ? "bg-teal-100 text-teal-600" : "bg-purple-100 text-purple-600"}>
                        {user.fullName?.substring(0, 2).toUpperCase() || (user.roles?.[0]?.name === "Lecturer" ? "GV" : "NV")}
                    </AvatarFallback>
                </Avatar>
                <Button variant="ghost" size="icon" onClick={handleLogout} title="Logout">
                    <LogOut className="w-5 h-5 text-gray-500" />
                </Button>
            </>
        ) : (
            <div className="text-sm text-muted-foreground">Loading...</div>
        )}
      </div>
    </header>
  );
}
"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
    LayoutDashboard, 
    FilePlus2, 
    FileCheck, 
    UserCircle, 
    BookOpen,
    Menu,
    UserCog,
    FileClock,
    Settings
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet";

export default function Sidebar() {
  const pathname = usePathname();
  const [role, setRole] = useState("");

  useEffect(() => {
    const userRole = localStorage.getItem("role") || "";
    console.log("Sidebar - User role from localStorage:", userRole);
    setRole(userRole);
  }, []);

  const menuItems = [
    { 
        name: "Dashboard", 
        href: "/", 
        icon: LayoutDashboard,
        roles: ["ALL"] 
    },
    { 
        name: "Biên soạn đề cương", 
        href: "/syllabus/create", 
        icon: FilePlus2,
        roles: ["Lecturer", "Head of Dept", "Admin"] 
    },
    { 
        name: "Yêu cầu phê duyệt", 
        href: "/reviews", 
        icon: FileCheck,
        roles: ["Head of Dept", "Academic Affairs", "Admin"] 
    },
    { 
        name: "Quản trị User", 
        href: "/admin/users", 
        icon: UserCog,
        roles: ["Admin"] 
    },
    { 
        name: "Cấu hình hệ thống",
        href: "/admin/settings", 
        icon: Settings,
        roles: ["Admin"] 
    },
    { 
        name: "Nhật ký hệ thống", 
        href: "/admin/logs", 
        icon: FileClock,
        roles: ["Admin"] 
    },
    { 
        name: "Cổng sinh viên", 
        href: "/portal", 
        icon: BookOpen,
        roles: ["ALL"] 
    },
    { 
        name: "Hồ sơ cá nhân", 
        href: "/profile", 
        icon: UserCircle,
        roles: ["ALL"] 
    },
  ];

  const filteredMenu = menuItems.filter(item => 
    item.roles.includes("ALL") || item.roles.includes(role)
  );
  
  console.log("Sidebar - Filtering menu items. Role:", role, "Filtered count:", filteredMenu.length);

  const NavContent = () => (
    <div className="flex flex-col h-full">
        <div className="mb-8 px-2">
          {/* ĐỔI MÀU LOGO */}
          <h1 className="text-xl font-extrabold text-teal-700 tracking-tight flex items-center gap-2">
            <BookOpen className="w-6 h-6"/> SMD System
          </h1>
          <p className="text-xs text-slate-500 mt-1 ml-8">Syllabus Management</p>
        </div>
        
        <nav className="flex-1 space-y-1">
          {filteredMenu.map((m) => {
            const isActive = pathname === m.href;
            return (
                <Link
                  key={m.href}
                  href={m.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200
                    ${isActive 
                        /* ĐỔI MÀU ACTIVE: Blue -> Teal */
                        ? "bg-teal-50 text-teal-800 shadow-sm border border-teal-100 font-bold" 
                        : "text-slate-600 hover:bg-teal-50 hover:text-teal-700"
                    }`}
                >
                  <m.icon className={`w-5 h-5 ${isActive ? "text-teal-700" : "text-slate-400"}`} />
                  <span>{m.name}</span>
                </Link>
            );
          })}
        </nav>

        <div className="mt-auto border-t pt-4">
             <div className="text-xs text-center text-slate-400">
                v1.2.0-config
             </div>
        </div>
    </div>
  );

  return (
    <>
      <aside className="hidden md:flex md:flex-col md:w-64 md:h-screen md:fixed md:inset-y-0 md:overflow-y-auto md:bg-white md:border-r md:border-slate-200 md:p-4 z-50">
        <NavContent />
      </aside>

      <div className="md:hidden">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="fixed top-3 left-4 z-50 bg-white shadow-sm border">
              <Menu className="w-5 h-5 text-slate-700" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-72 p-4">
            <SheetTitle className="sr-only">Menu</SheetTitle>
            <NavContent />
          </SheetContent>
        </Sheet>
      </div>
    </>
  );
}
"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { BookOpen, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";

function PublicLayoutContent({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { logout, role } = useAuth();

  const handleLogout = () => {
      logout();
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-teal-600 p-2 rounded-lg">
                <BookOpen className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-xl text-teal-900">SMD Portal</span>
          </div>
          <div className="flex gap-4 items-center">
             {role ? (
               <Button variant="ghost" onClick={handleLogout} className="text-red-600 hover:text-red-700 hover:bg-red-50 text-sm">
                  <LogOut className="w-4 h-4 mr-2" /> Đăng xuất
               </Button>
             ) : (
               <Button onClick={() => router.push("/login")} className="bg-teal-600 hover:bg-teal-700 text-white text-sm">
                  Đăng nhập
               </Button>
             )}
          </div>
        </div>
      </header>

      <main className="flex-1 w-full max-w-6xl mx-auto p-4 md:py-8">
        {children}
      </main>

      <footer className="bg-white border-t py-6 text-center text-sm text-gray-500">
        © 2025 University Syllabus Management System. All rights reserved.
      </footer>
    </div>
  );
}

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <PublicLayoutContent>{children}</PublicLayoutContent>
    </AuthProvider>
  );
}
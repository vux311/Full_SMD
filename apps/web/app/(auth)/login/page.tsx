"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { AlertCircle } from "lucide-react";
import axios from "@/lib/axios";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // Use API client and backend contract: POST /auth/login with JSON
      const res = await axios.post("/auth/login", { username, password }, { skipSnake: true } as any);
      const data = res.data;

      // Save tokens as specified by contract
      if (data.access_token) localStorage.setItem("access_token", data.access_token);
      if (data.refresh_token) localStorage.setItem("refresh_token", data.refresh_token);
      
      // Save role from login response first (immediate)
      if (data.role) localStorage.setItem("role", data.role);

      // Fetch user info to get more details and verify role
      try {
        const userRes = await axios.get("/users/me");
        const user = userRes.data;
        if (user?.role) localStorage.setItem("role", user.role);
        if (user?.role === "Student") router.push("/portal");
        else router.push("/");
      } catch (e) {
        // If user info not available, use role from login and go to homepage
        console.warn("Could not fetch user details, using role from login");
        if (data.role === "Student") router.push("/portal");
        else router.push("/");
      }
    
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-50">
      {/* ĐỔI BORDER TOP COLOR */}
      <Card className="w-full max-w-md shadow-xl border-t-4 border-t-teal-600">
        <CardHeader className="text-center pb-2">
          {/* ĐỔI MÀU ICON NỀN */}
          <div className="mx-auto w-12 h-12 bg-teal-50 rounded-lg flex items-center justify-center mb-4">
             <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-teal-600"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path></svg>
          </div>
          <CardTitle className="text-2xl font-bold text-slate-800">Đăng nhập Hệ thống</CardTitle>
          <p className="text-sm text-slate-500">Syllabus Management System</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
                <div className="flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded-md text-sm border border-red-100">
                    <AlertCircle className="w-4 h-4" /> {error}
                </div>
            )}
            
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Tên đăng nhập</label>
              <Input 
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
                placeholder="Ví dụ: gv1, hod1, sv1..." 
                required 
                className="h-10"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700">Mật khẩu</label>
              <Input 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="••••••" 
                required 
                className="h-10"
              />
            </div>

            {/* ĐỔI MÀU NÚT SUBMIT */}
            <Button type="submit" className="w-full bg-teal-600 hover:bg-teal-700 h-10 text-base" disabled={loading}>
              {loading ? "Đang xử lý..." : "Đăng nhập"}
            </Button>

            <div className="text-xs text-center text-slate-400 mt-6 pt-4 border-t">
                <p className="mb-1 font-semibold">Tài khoản mặc định:</p>
                Admin: <b>admin</b> | Trưởng bộ môn: <b>hod1</b><br/>
                Giảng viên: <b>gv1</b> | Sinh viên: <b>sv1</b> <br/>
                Phòng đào tạo: <b>aa1</b> <br/>
                (Mật khẩu chung: 123456)
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
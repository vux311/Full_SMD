"use client";

import React, { useEffect, useState } from "react";
import axios from "@/lib/axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { User, Shield, Key, Save } from "lucide-react";

interface UserProfile {
  id: number;
  username: string;
  full_name: string;
  role: string;
}

export default function ProfilePage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // State cho form đổi mật khẩu
  const [passData, setPassData] = useState({ current: "", new: "", confirm: "" });
  const [passLoading, setPassLoading] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
        try {
            const userRes = await axios.get('/users/me');
            const userData = userRes.data;
            setUser(userData);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    };
    fetchProfile();
  }, []);

  const handleChangePassword = async () => {
      // Validate cơ bản
      if (!passData.current || !passData.new) return alert("Vui lòng nhập đầy đủ thông tin");
      if (passData.new !== passData.confirm) return alert("Mật khẩu mới không khớp");
      if (passData.new.length < 6) return alert("Mật khẩu mới phải từ 6 ký tự trở lên");

      setPassLoading(true);
      try {
          await axios.post('/users/change-password', { currentPassword: passData.current, newPassword: passData.new });
          alert("Thành công! Mật khẩu đã được thay đổi.");
          setPassData({ current: "", new: "", confirm: "" }); // Reset form
      } catch (err: any) {
          console.error(err);
          const message = err?.response?.data?.detail || err?.message || "Lỗi kết nối server";
          alert("Lỗi: " + message);
      } finally {
          setPassLoading(false);
      }
  };

  if (loading) return <div className="p-8 text-center">Đang tải thông tin...</div>;
  if (!user) return <div className="p-8 text-center">Không tìm thấy thông tin người dùng.</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
        <h2 className="text-2xl font-bold tracking-tight">Hồ sơ cá nhân</h2>
        
        <div className="grid gap-6 md:grid-cols-3">
            {/* Cột trái: Avatar */}
            <Card className="md:col-span-1">
                <CardContent className="pt-6 flex flex-col items-center text-center">
                    <Avatar className="w-24 h-24 mb-4 border-4 border-slate-50">
                        <AvatarImage src={`https://ui-avatars.com/api/?name=${user.full_name}&background=0D8ABC&color=fff`} />
                        <AvatarFallback>User</AvatarFallback>
                    </Avatar>
                    <h3 className="font-bold text-xl">{user.full_name}</h3>
                    <div className="text-sm text-muted-foreground mb-4">@{user.username}</div>
                    <div className="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-medium border border-blue-200">
                        <Shield className="w-3 h-3 mr-1"/> {user.role}
                    </div>
                </CardContent>
            </Card>

            {/* Cột phải: Thông tin & Đổi Pass */}
            <div className="md:col-span-2 space-y-6">
                {/* Thông tin chung */}
                <Card>
                    <CardHeader>
                        <CardTitle>Thông tin tài khoản</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium flex items-center gap-2 text-slate-600"><User className="w-4 h-4"/> Họ và tên</label>
                            <Input value={user.full_name} readOnly className="bg-slate-50"/>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium flex items-center gap-2 text-slate-600"><Key className="w-4 h-4"/> Tên đăng nhập</label>
                            <Input value={user.username} readOnly className="bg-slate-50"/>
                        </div>
                    </CardContent>
                </Card>

                {/* Form đổi mật khẩu */}
                <Card>
                    <CardHeader>
                        <CardTitle>Đổi mật khẩu</CardTitle>
                        <CardDescription>Để bảo mật, vui lòng không chia sẻ mật khẩu cho người khác.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Mật khẩu hiện tại</label>
                            <Input 
                                type="password" 
                                value={passData.current}
                                onChange={e => setPassData({...passData, current: e.target.value})}
                                placeholder="••••••"
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Mật khẩu mới</label>
                                <Input 
                                    type="password"
                                    value={passData.new}
                                    onChange={e => setPassData({...passData, new: e.target.value})}
                                    placeholder="••••••"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Nhập lại mới</label>
                                <Input 
                                    type="password"
                                    value={passData.confirm}
                                    onChange={e => setPassData({...passData, confirm: e.target.value})}
                                    placeholder="••••••"
                                />
                            </div>
                        </div>
                        <div className="flex justify-end pt-2">
                            <Button onClick={handleChangePassword} disabled={passLoading}>
                                {passLoading ? "Đang xử lý..." : <><Save className="w-4 h-4 mr-2" /> Lưu thay đổi</>}
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    </div>
  );
}
"use client";

import React, { useEffect, useState } from "react";
import axios, { API_BASE } from "@/lib/axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { User, Shield, Key, Save, Mail, Building2, Edit2, Upload, History, AlertCircle } from "lucide-react";

interface Department {
  id: number;
  name: string;
  code: string;
  faculty?: {
    id: number;
    name: string;
    code: string;
  };
}

interface Role {
  id: number;
  name: string;
  description?: string;
}

interface UserProfile {
  id: number;
  username: string;
  email: string;
  fullName: string;
  isActive: boolean;
  avatarFileId?: number;
  department?: Department;
  roles?: Role[];
}

interface AuditLog {
  id: number;
  timestamp: string;
  action: string;
  resourceTarget: string;
  details?: string;
}

export default function ProfilePage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);

  // State cho form chỉnh sửa thông tin
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState({ fullName: "", email: "" });
  const [editLoading, setEditLoading] = useState(false);

  // State cho form đổi mật khẩu
  const [passData, setPassData] = useState({ current: "", new: "", confirm: "" });
  const [passLoading, setPassLoading] = useState(false);

  // State cho upload avatar
  const [avatarUploading, setAvatarUploading] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchProfile = async () => {
        try {
            const userRes = await axios.get('/users/me');
            const userData = userRes.data;
            setUser(userData);
            setEditData({ 
              fullName: userData.fullName || "", 
              email: userData.email || "" 
            });
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    };
    fetchProfile();
  }, []);

  const fetchAuditLogs = async () => {
    if (!user) return;
    setLogsLoading(true);
    try {
      const res = await axios.get(`/admin/logs?userId=${user.id}&limit=20`);
      setAuditLogs(res.data || []);
    } catch (e) { 
      console.error(e); 
    } finally {
      setLogsLoading(false);
    }
  };

  const handleEditProfile = async () => {
    if (!user || !editData.fullName || !editData.email) {
      return alert("Vui lòng nhập đầy đủ thông tin");
    }

    setEditLoading(true);
    try {
      await axios.put(`/users/${user.id}`, {
        fullName: editData.fullName,
        email: editData.email
      });
      
      // Cập nhật state local
      setUser({ ...user, fullName: editData.fullName, email: editData.email });
      setEditMode(false);
      alert("Cập nhật thông tin thành công!");
    } catch (err: any) {
      console.error(err);
      const message = err?.response?.data?.detail || "Lỗi khi cập nhật thông tin";
      alert("Lỗi: " + message);
    } finally {
      setEditLoading(false);
    }
  };

  const handleChangePassword = async () => {
      // Validate cơ bản
      if (!passData.current || !passData.new) return alert("Vui lòng nhập đầy đủ thông tin");
      if (passData.new !== passData.confirm) return alert("Mật khẩu mới không khớp");
      if (passData.new.length < 6) return alert("Mật khẩu mới phải từ 6 ký tự trở lên");

      setPassLoading(true);
      try {
          await axios.post('/auth/change-password', { 
            currentPassword: passData.current, 
            newPassword: passData.new 
          });
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

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !user) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      return alert("Vui lòng chọn file ảnh (JPG, PNG, GIF...)");
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      return alert("Kích thước file không được vượt quá 5MB");
    }

    setAvatarUploading(true);
    try {
      // 1. Upload file
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', user.id.toString());
      
      const uploadRes = await axios.post('/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const fileId = uploadRes.data.id;

      // 2. Update user avatar_file_id
      await axios.put(`/users/${user.id}`, {
        avatar_file_id: fileId
      });

      // 3. Update local state
      setUser({ ...user, avatarFileId: fileId });
      alert("Cập nhật avatar thành công!");
      
      // Refresh page để load avatar mới
      window.location.reload();
    } catch (err: any) {
      console.error(err);
      const message = err?.response?.data?.detail || "Lỗi khi upload avatar";
      alert("Lỗi: " + message);
    } finally {
      setAvatarUploading(false);
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getActionBadgeColor = (action: string) => {
    switch (action.toUpperCase()) {
      case 'LOGIN': return 'bg-green-100 text-green-700 border-green-200';
      case 'CREATE': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'UPDATE': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'DELETE': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  if (loading) return <div className="p-8 text-center">Đang tải thông tin...</div>;
  if (!user) return <div className="p-8 text-center">Không tìm thấy thông tin người dùng.</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight">Hồ sơ cá nhân</h2>
          {!user.isActive && (
            <Badge variant="destructive" className="gap-1">
              <AlertCircle className="w-3 h-3"/> Tài khoản bị vô hiệu hóa
            </Badge>
          )}
        </div>
        
        <div className="grid gap-6 md:grid-cols-3">
            {/* Cột trái: Avatar & Info Card */}
            <Card className="md:col-span-1">
                <CardContent className="pt-6 flex flex-col items-center text-center">
                    <div className="relative mb-4">
                      <Avatar className="w-28 h-28 border-4 border-slate-100 shadow-md">
                          <AvatarImage 
                            src={user.avatarFileId 
                              ? `${API_BASE}/files/${user.avatarFileId}` 
                              : `https://ui-avatars.com/api/?name=${user.fullName}&background=0D8ABC&color=fff&size=128`
                            } 
                          />
                          <AvatarFallback>{user.fullName?.substring(0, 2).toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <Button
                        size="sm"
                        variant="secondary"
                        className="absolute bottom-0 right-0 rounded-full w-8 h-8 p-0 shadow-lg"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={avatarUploading}
                        title="Thay đổi avatar"
                      >
                        {avatarUploading ? (
                          <span className="animate-spin">⏳</span>
                        ) : (
                          <Upload className="w-4 h-4" />
                        )}
                      </Button>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={handleAvatarUpload}
                      />
                    </div>
                    <h3 className="font-bold text-xl mb-1">{user.fullName}</h3>
                    <div className="text-sm text-muted-foreground mb-3">@{user.username}</div>
                    
                    {/* Roles */}
                    <div className="flex flex-wrap gap-2 justify-center mb-4">
                      {user.roles && user.roles.length > 0 ? (
                        user.roles.map((role, idx) => {
                          const roleId = role.id || (role as any).roleId || (role as any).role?.id || idx;
                          const roleName = role.name || (role as any).role?.name || "Unknown";
                          return (
                            <Badge key={`role-${roleId}-${idx}`} variant="outline" className="gap-1 bg-blue-50 text-blue-700 border-blue-200">
                              <Shield className="w-3 h-3"/> {roleName}
                            </Badge>
                          );
                        })
                      ) : (
                        <Badge variant="outline">Chưa có vai trò</Badge>
                      )}
                    </div>

                    <Separator className="my-4"/>

                    {/* Department & Faculty */}
                    {user.department && (
                      <div className="w-full space-y-2 text-sm">
                        <div className="flex items-start gap-2 text-left">
                          <Building2 className="w-4 h-4 mt-0.5 text-muted-foreground flex-shrink-0"/>
                          <div>
                            <div className="font-medium">{user.department.name}</div>
                            {user.department.faculty && (
                              <div className="text-xs text-muted-foreground">{user.department.faculty.name}</div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                </CardContent>
            </Card>

            {/* Cột phải: Tabs */}
            <div className="md:col-span-2">
              <Tabs defaultValue="info" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="info">Thông tin</TabsTrigger>
                  <TabsTrigger value="security">Bảo mật</TabsTrigger>
                  <TabsTrigger value="history" onClick={fetchAuditLogs}>Lịch sử</TabsTrigger>
                </TabsList>

                {/* Tab: Thông tin */}
                <TabsContent value="info" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle>Thông tin tài khoản</CardTitle>
                        {!editMode ? (
                          <Button variant="outline" size="sm" onClick={() => setEditMode(true)}>
                            <Edit2 className="w-4 h-4 mr-2"/> Chỉnh sửa
                          </Button>
                        ) : (
                          <div className="flex gap-2">
                            <Button variant="outline" size="sm" onClick={() => {
                              setEditMode(false);
                              setEditData({ fullName: user.fullName, email: user.email });
                            }}>
                              Hủy
                            </Button>
                            <Button size="sm" onClick={handleEditProfile} disabled={editLoading}>
                              <Save className="w-4 h-4 mr-2"/> {editLoading ? "Đang lưu..." : "Lưu"}
                            </Button>
                          </div>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="fullName" className="flex items-center gap-2">
                          <User className="w-4 h-4"/> Họ và tên
                        </Label>
                        <Input 
                          id="fullName"
                          value={editMode ? editData.fullName : user.fullName} 
                          onChange={e => editMode && setEditData({...editData, fullName: e.target.value})}
                          readOnly={!editMode}
                          className={!editMode ? "bg-slate-50" : ""}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="email" className="flex items-center gap-2">
                          <Mail className="w-4 h-4"/> Email
                        </Label>
                        <Input 
                          id="email"
                          type="email"
                          value={editMode ? editData.email : user.email} 
                          onChange={e => editMode && setEditData({...editData, email: e.target.value})}
                          readOnly={!editMode}
                          className={!editMode ? "bg-slate-50" : ""}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="username" className="flex items-center gap-2">
                          <Key className="w-4 h-4"/> Tên đăng nhập
                        </Label>
                        <Input 
                          id="username"
                          value={user.username} 
                          readOnly 
                          className="bg-slate-50"
                        />
                        <p className="text-xs text-muted-foreground">Tên đăng nhập không thể thay đổi</p>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Tab: Bảo mật */}
                <TabsContent value="security" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Đổi mật khẩu</CardTitle>
                      <CardDescription>Để bảo mật, vui lòng sử dụng mật khẩu mạnh và không chia sẻ cho người khác.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="currentPass">Mật khẩu hiện tại</Label>
                        <Input 
                          id="currentPass"
                          type="password" 
                          value={passData.current}
                          onChange={e => setPassData({...passData, current: e.target.value})}
                          placeholder="••••••"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="newPass">Mật khẩu mới</Label>
                          <Input 
                            id="newPass"
                            type="password"
                            value={passData.new}
                            onChange={e => setPassData({...passData, new: e.target.value})}
                            placeholder="••••••"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="confirmPass">Nhập lại mới</Label>
                          <Input 
                            id="confirmPass"
                            type="password"
                            value={passData.confirm}
                            onChange={e => setPassData({...passData, confirm: e.target.value})}
                            placeholder="••••••"
                          />
                        </div>
                      </div>
                      <div className="flex justify-end pt-2">
                        <Button onClick={handleChangePassword} disabled={passLoading}>
                          {passLoading ? "Đang xử lý..." : <><Save className="w-4 h-4 mr-2" /> Đổi mật khẩu</>}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Tab: Lịch sử hoạt động */}
                <TabsContent value="history" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <History className="w-5 h-5"/> Lịch sử hoạt động
                      </CardTitle>
                      <CardDescription>20 hoạt động gần nhất của bạn trong hệ thống</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {logsLoading ? (
                        <div className="text-center py-8 text-muted-foreground">Đang tải...</div>
                      ) : auditLogs.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">Chưa có lịch sử hoạt động</div>
                      ) : (
                        <div className="space-y-3">
                          {auditLogs.map((log, idx) => (
                            <div key={log.id || idx} className="flex items-start gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors">
                              <Badge key={`badge-${log.id || idx}`} className={`mt-0.5 ${getActionBadgeColor(log.action)}`}>
                                {log.action}
                              </Badge>
                              <div className="flex-1 min-w-0">
                                <div className="font-medium text-sm">{log.resourceTarget}</div>
                                {log.details && (
                                  <div className="text-xs text-muted-foreground mt-1 line-clamp-2">{log.details}</div>
                                )}
                                <div className="text-xs text-muted-foreground mt-1">{formatDateTime(log.timestamp)}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
        </div>
    </div>
  );
}
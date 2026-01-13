"use client";

import React, { useEffect, useState } from "react";
import axios from "@/lib/axios";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Trash2, Plus, Users, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface User {
  id: number;
  username: string;
  full_name: string;
  role: string;
}

export default function UserManagementPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false); // Modal state

  // Form state
  const [formData, setFormData] = useState({ username: "", password: "", full_name: "", email: "", role: "Lecturer" });

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/users/');
      const data = res.data;
      setUsers(data || []);
    } catch (e: any) {
      const status = e?.response?.status || e?.status;
      if (status === 403) alert("Bạn không có quyền truy cập trang này!");
      else console.error(e);
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleCreate = async () => {
    if (!formData.username || !formData.password || !formData.email) return alert("Vui lòng nhập đủ thông tin!");
    try {
        await axios.post('/users/', { 
            username: formData.username, 
            password: formData.password, 
            full_name: formData.full_name || formData.username,
            email: formData.email,
            is_active: true
        });
        alert("Tạo tài khoản thành công!");
        setOpen(false);
        setFormData({ username: "", password: "", full_name: "", email: "", role: "Lecturer" });
        fetchUsers();
    } catch (e: any) { const message = e?.response?.data?.detail || e?.message || "Lỗi kết nối server"; alert("Lỗi: " + message); }
  };

  const handleDelete = async (id: number) => {
      if (!confirm("Hành động này không thể hoàn tác. Bạn chắc chắn muốn xóa user này?")) return;
      try {
          await axios.delete(`/users/${id}`);
          alert("Đã xóa thành công!");
          fetchUsers();
      } catch (e: any) { const message = e?.response?.data?.detail || e?.message; alert("Lỗi: " + message); }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
            <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                <Users className="w-6 h-6 text-blue-600"/> Quản trị Người dùng
            </h2>
            <p className="text-sm text-muted-foreground mt-1">Quản lý danh sách tài khoản truy cập hệ thống</p>
        </div>
        
        {/* MODAL THÊM USER */}
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700">
                    <Plus className="w-4 h-4 mr-2"/> Thêm tài khoản
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader><DialogTitle>Tạo tài khoản mới</DialogTitle></DialogHeader>
                <div className="space-y-4 py-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Họ và tên</label>
                        <Input value={formData.full_name} onChange={e => setFormData({...formData, full_name: e.target.value})} placeholder="VD: Nguyễn Văn A" />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Email <span className="text-red-500">*</span></label>
                        <Input type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} placeholder="VD: gvmoi@example.com" required />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Username <span className="text-red-500">*</span></label>
                            <Input value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} placeholder="VD: gv_moi" required />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Password <span className="text-red-500">*</span></label>
                            <Input type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} placeholder="******" required />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Vai trò</label>
                        <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                            value={formData.role} 
                            onChange={e => setFormData({...formData, role: e.target.value})}
                        >
                            <option value="Lecturer">Giảng viên (Lecturer)</option>
                            <option value="Head of Dept">Trưởng bộ môn (Head of Dept)</option>
                            <option value="Student">Sinh viên (Student)</option>
                            <option value="Admin">Quản trị viên (Admin)</option>
                        </select>
                    </div>
                    <Button className="w-full mt-4 bg-blue-600 hover:bg-blue-700" onClick={handleCreate}>Xác nhận tạo</Button>
                </div>
            </DialogContent>
        </Dialog>
      </div>

      <Card>
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[80px]">ID</TableHead>
                    <TableHead>Tài khoản</TableHead>
                    <TableHead>Họ tên hiển thị</TableHead>
                    <TableHead>Vai trò</TableHead>
                    <TableHead className="text-right">Hành động</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {loading ? (
                    <TableRow><TableCell colSpan={5} className="text-center h-24"><Loader2 className="animate-spin w-4 h-4 inline mr-2"/> Đang tải danh sách...</TableCell></TableRow>
                ) : users.length === 0 ? (
                    <TableRow><TableCell colSpan={5} className="text-center h-24 text-muted-foreground">Chưa có người dùng nào.</TableCell></TableRow>
                ) : (
                    users.map(u => (
                        <TableRow key={u.id}>
                            <TableCell className="font-mono text-xs text-gray-500">#{u.id}</TableCell>
                            <TableCell className="font-bold">{u.username}</TableCell>
                            <TableCell>{u.full_name}</TableCell>
                            <TableCell>
                                <Badge variant="outline" className={
                                    u.role === 'Admin' ? 'border-red-200 bg-red-50 text-red-700' :
                                    u.role === 'Student' ? 'border-green-200 bg-green-50 text-green-700' : 
                                    'border-blue-200 bg-blue-50 text-blue-700'
                                }>
                                    {u.role}
                                </Badge>
                            </TableCell>
                            <TableCell className="text-right">
                                <Button variant="ghost" size="icon" onClick={() => handleDelete(u.id)} className="text-gray-400 hover:text-red-600 hover:bg-red-50" title="Xóa người dùng">
                                    <Trash2 className="w-4 h-4"/>
                                </Button>
                            </TableCell>
                        </TableRow>
                    ))
                )}
            </TableBody>
        </Table>
      </Card>
    </div>
  );
}
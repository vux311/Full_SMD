
/*

http://localhost:3000/admin/users
✅ FIXED: Thêm tài khoản với vai trò được lưu vào DB thông qua API /users/:id/roles
✅ FIXED: Đã thêm option chọn khoa (department) khi tạo user
✅ FIXED: Kiểm tra trùng username, email khi tạo user mới
✅ FIXED: Kiểm tra định dạng email với regex validation
✅ FIXED: Hiển thị đầy đủ họ tên và vai trò của user trong bảng (updated UserSchema to include roles)
✅ FIXED: Chọn vai trò bằng dropdown giống như chọn khoa
✅ FIXED: Họ tên hiển thị - updated interface to use camelCase (fullName) matching API response
✅ FIXED: Role assignment timing - Added 300ms delay + better error handling
✅ FIXED: Thêm tính năng Edit user với modal chỉnh sửa
✅ FIXED: SOLUTION FOR ROLE ASSIGNMENT:
- Sau khi gán role qua POST /users/:id/roles, đợi 300ms để database commit
- Sau đó fetch lại users để lấy roles mới
- Có error handling rõ ràng để báo lỗi nếu role assignment thất bại
- Hiển thị thông báo chi tiết nếu có lỗi từ API (vd: "method not allowed")

✅ FIXED: NOTE: Cần đảm bảo Flask API server đã restart để endpoint /users/:id/roles hoạt động
- Lỗi 500 khi xóa user
*/
"use client";

import React, { useEffect, useState } from "react";
import axios from "@/lib/axios";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Trash2, Plus, Users, Loader2, Pencil } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface Role {
  id: number;
  name: string;
  description?: string;
}

interface Department {
  id: number;
  name: string;
  code: string;
  faculty_id: number;
}

interface User {
  id: number;
  username: string;
  fullName: string;  // API trả về camelCase
  email: string;
  departmentId?: number;  // API trả về camelCase
  isActive: boolean;  // API trả về camelCase
  roles?: Array<{
    roleId: number;  // API trả về camelCase
    role: Role;
  }>;
}

export default function UserManagementPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false); // Create modal state
  const [editOpen, setEditOpen] = useState(false); // Edit modal state
  const [editingUser, setEditingUser] = useState<User | null>(null); // User being edited
  const [departments, setDepartments] = useState<Department[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);

  // Form state
  const [formData, setFormData] = useState({ 
    username: "", 
    password: "", 
    full_name: "", 
    email: "", 
    department_id: "",
    role_id: "" // Changed from role_ids array to single role_id
  });
  const [errors, setErrors] = useState<{username?: string; email?: string}>({});

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

  const fetchDepartments = async () => {
    try {
      const res = await axios.get('/departments/');
      setDepartments(res.data || []);
    } catch (e) {
      console.error("Failed to fetch departments:", e);
    }
  };

  const fetchRoles = async () => {
    try {
      const res = await axios.get('/roles/');
      setRoles(res.data || []);
    } catch (e) {
      console.error("Failed to fetch roles:", e);
    }
  };

  useEffect(() => { 
    fetchUsers(); 
    fetchDepartments();
    fetchRoles();
  }, []);

  const handleCreate = async () => {
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email || !emailRegex.test(formData.email)) {
      setErrors({ ...errors, email: "Email không hợp lệ" });
      return alert("Vui lòng nhập email hợp lệ!");
    }

    if (!formData.username || !formData.password || !formData.email) {
      return alert("Vui lòng nhập đủ thông tin bắt buộc!");
    }

    // Check for duplicate username and email
    const existingUser = users.find(u => 
      u.username.toLowerCase() === formData.username.toLowerCase() || 
      u.email.toLowerCase() === formData.email.toLowerCase()
    );
    if (existingUser) {
      if (existingUser.username.toLowerCase() === formData.username.toLowerCase()) {
        setErrors({ ...errors, username: "Username đã tồn tại" });
        return alert("Username đã tồn tại trong hệ thống!");
      }
      if (existingUser.email.toLowerCase() === formData.email.toLowerCase()) {
        setErrors({ ...errors, email: "Email đã tồn tại" });
        return alert("Email đã tồn tại trong hệ thống!");
      }
    }

    try {
        const userData: any = { 
            username: formData.username, 
            password: formData.password, 
            full_name: formData.full_name || formData.username,
            email: formData.email,
            is_active: true
        };
        
        // Add department_id if selected
        if (formData.department_id) {
          userData.department_id = parseInt(formData.department_id);
        }

        // Create user first
        const userResponse = await axios.post('/users/', userData);
        const newUser = userResponse.data;
        
        // Assign role if selected
        let roleAssigned = false;
        if (formData.role_id) {
          try {
            const roleResponse = await axios.post(`/users/${newUser.id}/roles`, {
              role_ids: [parseInt(formData.role_id)]
            });
            console.log("Role assigned successfully to user", newUser.id, roleResponse.data);
            roleAssigned = true;
            
            // Wait a bit for database to commit
            await new Promise(resolve => setTimeout(resolve, 300));
          } catch (roleError: any) {
            console.error("Could not assign role:", roleError);
            console.error("Error details:", roleError.response?.data);
            alert(`Tạo user thành công nhưng không thể gán vai trò: ${roleError.response?.data?.error || roleError.message}`);
          }
        }

        // Fetch users again to get updated roles BEFORE showing success message
        await fetchUsers();
        
        // Now show success and close modal
        if (roleAssigned || !formData.role_id) {
          alert("Tạo tài khoản thành công!");
        }
        setOpen(false);
        setFormData({ 
          username: "", 
          password: "", 
          full_name: "", 
          email: "", 
          department_id: "",
          role_id: ""
        });
        setErrors({});
    } catch (e: any) { 
      const message = e?.response?.data?.detail || e?.message || "Lỗi kết nối server"; 
      alert("Lỗi: " + message); 
    }
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      password: "", // Don't show password
      full_name: user.fullName,
      email: user.email,
      department_id: user.departmentId?.toString() || "",
      role_id: user.roles?.[0]?.roleId?.toString() || ""
    });
    setEditOpen(true);
  };

  const handleUpdate = async () => {
    if (!editingUser) return;
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email || !emailRegex.test(formData.email)) {
      setErrors({ ...errors, email: "Email không hợp lệ" });
      return alert("Vui lòng nhập email hợp lệ!");
    }

    // Check for duplicate email (excluding current user)
    const existingUser = users.find(u => 
      u.id !== editingUser.id && u.email.toLowerCase() === formData.email.toLowerCase()
    );
    if (existingUser) {
      setErrors({ ...errors, email: "Email đã tồn tại" });
      return alert("Email đã tồn tại trong hệ thống!");
    }

    try {
      const userData: any = {
        email: formData.email,
        full_name: formData.full_name || formData.username,
        is_active: true
      };

      // Add password if provided
      if (formData.password) {
        userData.password = formData.password;
      }

      // Add department_id if selected
      if (formData.department_id) {
        userData.department_id = parseInt(formData.department_id);
      }

      // Update user
      await axios.put(`/users/${editingUser.id}`, userData);

      // Update role if changed
      let roleUpdated = false;
      if (formData.role_id) {
        try {
          const roleResponse = await axios.post(`/users/${editingUser.id}/roles`, {
            role_ids: [parseInt(formData.role_id)]
          });
          console.log("Role updated successfully for user", editingUser.id, roleResponse.data);
          roleUpdated = true;
          
          // Wait a bit for database to commit
          await new Promise(resolve => setTimeout(resolve, 300));
        } catch (roleError: any) {
          console.error("Could not update role:", roleError);
          console.error("Error details:", roleError.response?.data);
          alert(`Cập nhật user thành công nhưng không thể gán vai trò: ${roleError.response?.data?.error || roleError.message}`);
        }
      }

      // Fetch users again to get updated data BEFORE showing success message
      await fetchUsers();

      // Now show success and close modal
      if (roleUpdated || !formData.role_id) {
        alert("Cập nhật tài khoản thành công!");
      }
      setEditOpen(false);
      setEditingUser(null);
      setFormData({
        username: "",
        password: "",
        full_name: "",
        email: "",
        department_id: "",
        role_id: ""
      });
      setErrors({});
    } catch (e: any) {
      const message = e?.response?.data?.detail || e?.message || "Lỗi kết nối server";
      alert("Lỗi: " + message);
    }
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
                        <Input 
                          type="email" 
                          value={formData.email} 
                          onChange={e => {
                            setFormData({...formData, email: e.target.value});
                            if (errors.email) setErrors({...errors, email: undefined});
                          }} 
                          placeholder="VD: gvmoi@example.com" 
                          className={errors.email ? "border-red-500" : ""}
                          required 
                        />
                        {errors.email && <p className="text-xs text-red-500">{errors.email}</p>}
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Username <span className="text-red-500">*</span></label>
                            <Input 
                              value={formData.username} 
                              onChange={e => {
                                setFormData({...formData, username: e.target.value});
                                if (errors.username) setErrors({...errors, username: undefined});
                              }} 
                              placeholder="VD: gv_moi" 
                              className={errors.username ? "border-red-500" : ""}
                              required 
                            />
                            {errors.username && <p className="text-xs text-red-500">{errors.username}</p>}
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Password <span className="text-red-500">*</span></label>
                            <Input type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} placeholder="******" required />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Khoa</label>
                        <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                            value={formData.department_id} 
                            onChange={e => setFormData({...formData, department_id: e.target.value})}
                        >
                            <option value="">-- Chọn khoa (không bắt buộc) --</option>
                            {departments.map(dept => (
                              <option key={dept.id} value={dept.id}>{dept.name} ({dept.code})</option>
                            ))}
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Vai trò</label>
                        <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                            value={formData.role_id} 
                            onChange={e => setFormData({...formData, role_id: e.target.value})}
                        >
                            <option value="">-- Chọn vai trò (không bắt buộc) --</option>
                            {roles.map(role => (
                              <option key={role.id} value={role.id}>{role.name}</option>
                            ))}
                        </select>
                    </div>
                    <Button className="w-full mt-4 bg-blue-600 hover:bg-blue-700" onClick={handleCreate}>Xác nhận tạo</Button>
                </div>
            </DialogContent>
        </Dialog>

        {/* MODAL EDIT USER */}
        <Dialog open={editOpen} onOpenChange={setEditOpen}>
            <DialogContent>
                <DialogHeader><DialogTitle>Chỉnh sửa thông tin tài khoản</DialogTitle></DialogHeader>
                <div className="space-y-4 py-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Username</label>
                        <Input value={formData.username} disabled className="bg-gray-100" />
                        <p className="text-xs text-gray-500">Username không thể thay đổi</p>
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Họ và tên</label>
                        <Input value={formData.full_name} onChange={e => setFormData({...formData, full_name: e.target.value})} placeholder="VD: Nguyễn Văn A" />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Email <span className="text-red-500">*</span></label>
                        <Input 
                          type="email" 
                          value={formData.email} 
                          onChange={e => {
                            setFormData({...formData, email: e.target.value});
                            if (errors.email) setErrors({...errors, email: undefined});
                          }} 
                          placeholder="VD: gvmoi@example.com" 
                          className={errors.email ? "border-red-500" : ""}
                          required 
                        />
                        {errors.email && <p className="text-xs text-red-500">{errors.email}</p>}
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Password mới (để trống nếu không đổi)</label>
                        <Input type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} placeholder="******" />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Khoa</label>
                        <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                            value={formData.department_id} 
                            onChange={e => setFormData({...formData, department_id: e.target.value})}
                        >
                            <option value="">-- Chọn khoa (không bắt buộc) --</option>
                            {departments.map(dept => (
                              <option key={dept.id} value={dept.id}>{dept.name} ({dept.code})</option>
                            ))}
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Vai trò</label>
                        <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                            value={formData.role_id} 
                            onChange={e => setFormData({...formData, role_id: e.target.value})}
                        >
                            <option value="">-- Chọn vai trò (không bắt buộc) --</option>
                            {roles.map(role => (
                              <option key={role.id} value={role.id}>{role.name}</option>
                            ))}
                        </select>
                    </div>
                    <Button className="w-full mt-4 bg-blue-600 hover:bg-blue-700" onClick={handleUpdate}>Cập nhật</Button>
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
                    users.map(u => {
                        // Get role names from user's roles array
                        const userRoles = u.roles?.map(ur => ur.role.name) || [];
                        const primaryRole = userRoles[0] || 'No Role';
                        
                        return (
                        <TableRow key={u.id}>
                            <TableCell className="font-mono text-xs text-gray-500">#{u.id}</TableCell>
                            <TableCell className="font-bold">{u.username}</TableCell>
                            <TableCell>{u.fullName || '-'}</TableCell>
                            <TableCell>
                                <div className="flex flex-wrap gap-1">
                                  {userRoles.length > 0 ? userRoles.map((roleName, idx) => (
                                    <Badge key={idx} variant="outline" className={
                                        roleName === 'Admin' ? 'border-red-200 bg-red-50 text-red-700' :
                                        roleName === 'Student' ? 'border-green-200 bg-green-50 text-green-700' : 
                                        'border-blue-200 bg-blue-50 text-blue-700'
                                    }>
                                        {roleName}
                                    </Badge>
                                  )) : (
                                    <span className="text-xs text-gray-400">Chưa gán vai trò</span>
                                  )}
                                </div>
                            </TableCell>
                            <TableCell className="text-right">
                                <div className="flex justify-end gap-2">
                                    <Button 
                                        variant="ghost" 
                                        size="icon" 
                                        onClick={() => handleEdit(u)} 
                                        className="text-gray-400 hover:text-blue-600 hover:bg-blue-50" 
                                        title="Chỉnh sửa người dùng"
                                    >
                                        <Pencil className="w-4 h-4"/>
                                    </Button>
                                    <Button 
                                        variant="ghost" 
                                        size="icon" 
                                        onClick={() => handleDelete(u.id)} 
                                        className="text-gray-400 hover:text-red-600 hover:bg-red-50" 
                                        title="Xóa người dùng"
                                    >
                                        <Trash2 className="w-4 h-4"/>
                                    </Button>
                                </div>
                            </TableCell>
                        </TableRow>
                        );
                    })
                )}
            </TableBody>
        </Table>
      </Card>
    </div>
  );
}
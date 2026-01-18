"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Plus, 
  Search, 
  Edit2, 
  Trash2, 
  Loader2, 
  GraduationCap, 
  Building2,
  BookOpen
} from "lucide-react";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter,
  DialogDescription
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import axios from "@/lib/axios";
import { useAuth } from "@/contexts/AuthContext";

interface Program {
  id: number;
  name: string;
  departmentId: number;
  totalCredits: number;
  department?: {
    id: number;
    name: string;
    code: string;
  };
}

interface Department {
  id: number;
  name: string;
  code: string;
}

export default function ProgramsPage() {
  const { role } = useAuth();
  const [programs, setPrograms] = useState<Program[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  
  // States for Create/Edit Dialog
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProgram, setEditingProgram] = useState<Program | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    departmentId: "",
    totalCredits: 0
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchPrograms = useCallback(async () => {
    setLoading(true);
    try {
      const [programsRes, departmentsRes] = await Promise.all([
        axios.get("/programs"),
        axios.get("/departments")
      ]);
      setPrograms(programsRes.data || []);
      setDepartments(departmentsRes.data || []);
    } catch (err) {
      console.error("Failed to fetch programs:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPrograms();
  }, [fetchPrograms]);

  const filteredPrograms = programs.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.department?.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleOpenDialog = (program?: Program) => {
    if (program) {
      setEditingProgram(program);
      setFormData({
        name: program.name,
        departmentId: String(program.departmentId),
        totalCredits: program.totalCredits || 0
      });
    } else {
      setEditingProgram(null);
      setFormData({
        name: "",
        departmentId: "",
        totalCredits: 0
      });
    }
    setDialogOpen(true);
  };

  const handleSubmit = async () => {
    if (!formData.name || !formData.departmentId) {
      alert("Vui lòng điền đầy đủ tên và bộ môn");
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        name: formData.name,
        departmentId: Number(formData.departmentId),
        totalCredits: Number(formData.totalCredits)
      };

      if (editingProgram) {
        await axios.put(`/programs/${editingProgram.id}`, payload);
        alert("Cập nhật chương trình đào tạo thành công!");
      } else {
        await axios.post("/programs", payload);
        alert("Thêm chương trình đào tạo thành công!");
      }
      setDialogOpen(false);
      fetchPrograms();
    } catch (err: any) {
      console.error("Submit error:", err);
      alert(err.response?.data?.message || "Có lỗi xảy ra khi lưu");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Bạn có chắc chắn muốn xóa chương trình đào tạo này không?")) return;
    
    try {
      await axios.delete(`/programs/${id}`);
      alert("Đã xóa thành công");
      fetchPrograms();
    } catch (err: any) {
      console.error("Delete error:", err);
      alert(err.response?.data?.message || "Có lỗi xảy ra khi xóa");
    }
  };

  const isAdmin = role === "Admin" || role === "Academic Affairs" || role === "AA";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Quản lý Chương trình đào tạo</h1>
          <p className="text-sm text-muted-foreground">
            Quản lý các chương trình đào tạo, chuyên ngành và cấu trúc tín chỉ của nhà trường.
          </p>
        </div>
        {isAdmin && (
          <Button className="bg-teal-600 hover:bg-teal-700" onClick={() => handleOpenDialog()}>
            <Plus className="w-4 h-4 mr-2" /> Thêm chương trình
          </Button>
        )}
      </div>

      <Card>
        <CardHeader className="pb-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Tìm kiếm chương trình hoặc bộ môn..."
              className="pl-8 max-w-sm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-teal-600" />
            </div>
          ) : (
            <div className="border rounded-md">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50">
                    <TableHead className="w-12">ID</TableHead>
                    <TableHead>Tên Chương trình</TableHead>
                    <TableHead>Bộ môn / Khoa</TableHead>
                    <TableHead className="text-center">Số tín chỉ</TableHead>
                    {isAdmin && <TableHead className="w-24 text-right">Thao tác</TableHead>}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPrograms.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={isAdmin ? 5 : 4} className="text-center py-10 text-muted-foreground">
                        Không tìm thấy chương trình nào phù hợp.
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredPrograms.map((p) => (
                      <TableRow key={p.id} className="hover:bg-slate-50/50">
                        <TableCell className="font-medium text-slate-500">{p.id}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div className="p-1.5 bg-teal-50 rounded text-teal-600">
                                <GraduationCap className="w-4 h-4" />
                            </div>
                            <span className="font-semibold text-slate-900">{p.name}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                           <div className="flex items-center gap-1.5 text-slate-600">
                              <Building2 className="w-4 h-4 text-slate-400" />
                              <span>{p.department?.name || "N/A"}</span>
                           </div>
                        </TableCell>
                        <TableCell className="text-center">
                           <Badge variant="outline" className="font-mono bg-blue-50 text-blue-700 border-blue-200">
                              {p.totalCredits} TC
                           </Badge>
                        </TableCell>
                        {isAdmin && (
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                className="h-8 w-8 p-0 text-teal-600 hover:text-teal-700 hover:bg-teal-50"
                                onClick={() => handleOpenDialog(p)}
                                title="Chỉnh sửa"
                              >
                                <Edit2 className="h-4 w-4" />
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                                onClick={() => handleDelete(p.id)}
                                title="Xóa"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        )}
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* CREATE/EDIT DIALOG */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>
              {editingProgram ? "Chỉnh sửa chương trình" : "Thêm chương trình đào tạo mới"}
            </DialogTitle>
            <DialogDescription>
              Nhập thông tin chi tiết cho chương trình đào tạo. Nhấn lưu khi hoàn tất.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Tên chương trình <span className="text-red-600">*</span></Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ví dụ: Công nghệ thông tin"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="department">Bộ môn trực thuộc <span className="text-red-600">*</span></Label>
              <select
                id="department"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={formData.departmentId}
                onChange={(e) => setFormData({ ...formData, departmentId: e.target.value })}
              >
                <option value="">-- Chọn bộ môn --</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.id}>{dept.name} ({dept.code})</option>
                ))}
              </select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="credits">Tổng số tín chỉ</Label>
              <Input
                id="credits"
                type="number"
                value={formData.totalCredits}
                onChange={(e) => setFormData({ ...formData, totalCredits: Number(e.target.value) })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={submitting}>Hủy</Button>
            <Button 
                onClick={handleSubmit} 
                disabled={submitting}
                className="bg-teal-600 hover:bg-teal-700"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              {editingProgram ? "Cập nhật" : "Lưu thay đổi"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

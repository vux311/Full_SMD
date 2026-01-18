"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { 
  Plus, 
  Search, 
  Edit2, 
  Trash2, 
  Loader2, 
  Building,
  School,
  Building2
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

interface Faculty {
  id: number;
  code: string;
  name: string;
  description?: string;
}

interface Department {
  id: number;
  facultyId: number;
  code: string;
  name: string;
  faculty?: {
    id: number;
    name: string;
    code: string;
  };
}

export default function DepartmentsPage() {
  const { role } = useAuth();
  const [faculties, setFaculties] = useState<Faculty[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("faculties");
  const [searchTerm, setSearchTerm] = useState("");

  // Dialog states
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [itemType, setItemType] = useState<"faculty" | "department">("faculty");
  const [submitting, setSubmitting] = useState(false);

  // Form states
  const [facultyFormData, setFacultyFormData] = useState({ code: "", name: "", description: "" });
  const [deptFormData, setDeptFormData] = useState({ code: "", name: "", facultyId: "" });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [facRes, deptRes] = await Promise.all([
        axios.get("/faculties"),
        axios.get("/departments")
      ]);
      setFaculties(facRes.data || []);
      setDepartments(deptRes.data || []);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleOpenDialog = (type: "faculty" | "department", item?: any) => {
    setItemType(type);
    if (item) {
      setEditingItem(item);
      if (type === "faculty") {
        setFacultyFormData({ 
          code: item.code, 
          name: item.name, 
          description: item.description || "" 
        });
      } else {
        setDeptFormData({ 
          code: item.code, 
          name: item.name, 
          facultyId: String(item.facultyId) 
        });
      }
    } else {
      setEditingItem(null);
      if (type === "faculty") {
        setFacultyFormData({ code: "", name: "", description: "" });
      } else {
        setDeptFormData({ code: "", name: "", facultyId: "" });
      }
    }
    setDialogOpen(true);
  };

  const handleSubmit = async () => {
    if (itemType === "faculty") {
      if (!facultyFormData.code || !facultyFormData.name) {
        alert("Vui lòng nhập mã và tên khoa");
        return;
      }
    } else {
      if (!deptFormData.code || !deptFormData.name || !deptFormData.facultyId) {
        alert("Vui lòng nhập đầy đủ thông tin bộ môn");
        return;
      }
    }

    setSubmitting(true);
    try {
      if (itemType === "faculty") {
        if (editingItem) {
          await axios.put(`/faculties/${editingItem.id}`, facultyFormData);
        } else {
          await axios.post("/faculties", facultyFormData);
        }
      } else {
        const payload = { 
          code: deptFormData.code,
          name: deptFormData.name,
          facultyId: Number(deptFormData.facultyId) 
        };
        if (editingItem) {
          await axios.put(`/departments/${editingItem.id}`, payload);
        } else {
          await axios.post("/departments", payload);
        }
      }
      setDialogOpen(false);
      fetchData();
      alert("Thao tác thành công!");
    } catch (err: any) {
      console.error("Submit error:", err);
      alert(err.response?.data?.message || "Có lỗi xảy ra");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (type: "faculty" | "department", id: number) => {
    if (!confirm(`Bạn có chắc chắn muốn xóa ${type === 'faculty' ? 'khoa' : 'bộ môn'} này?`)) return;
    try {
      const endpoint = type === "faculty" ? "/faculties" : "/departments";
      await axios.delete(`${endpoint}/${id}`);
      fetchData();
      alert("Xóa thành công!");
    } catch (err: any) {
      console.error("Delete error:", err);
      alert(err.response?.data?.message || "Có lỗi xảy ra khi xóa");
    }
  };

  const filteredFaculties = faculties.filter(f => 
    f.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    f.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredDepartments = departments.filter(d => 
    d.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    d.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.faculty?.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Quản lý Khoa & Bộ môn</h1>
          <p className="text-slate-500">Quản lý cơ cấu tổ chức của trường</p>
        </div>
        <Button 
          className="bg-teal-600 hover:bg-teal-700 text-white"
          onClick={() => handleOpenDialog(activeTab === "faculties" ? "faculty" : "department")}
        >
          <Plus className="w-4 h-4 mr-2" />
          Thêm {activeTab === "faculties" ? "Khoa" : "Bộ môn"}
        </Button>
      </div>

      <Card className="border-none shadow-sm overflow-hidden">
        <CardContent className="p-0">
          <Tabs defaultValue="faculties" value={activeTab} onValueChange={setActiveTab} className="w-full">
            <div className="px-6 pt-4 border-b bg-white flex justify-between items-center">
              <TabsList className="bg-slate-100 p-1 mb-2">
                <TabsTrigger value="faculties" className="data-[state=active]:bg-white data-[state=active]:text-teal-700 flex items-center gap-2">
                  <School className="w-4 h-4" /> Khoa
                </TabsTrigger>
                <TabsTrigger value="departments" className="data-[state=active]:bg-white data-[state=active]:text-teal-700 flex items-center gap-2">
                  <Building2 className="w-4 h-4" /> Bộ môn
                </TabsTrigger>
              </TabsList>
              <div className="relative w-64 mb-2">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input 
                  placeholder="Tìm kiếm..." 
                  className="pl-9 bg-slate-50 border-slate-200 focus:bg-white transition-all"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            <TabsContent value="faculties" className="m-0">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50/50">
                    <TableHead className="w-[100px]">ID</TableHead>
                    <TableHead>Mã Khoa</TableHead>
                    <TableHead>Tên Khoa</TableHead>
                    <TableHead>Mô tả</TableHead>
                    <TableHead className="text-right">Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={5} className="h-32 text-center text-slate-500">
                        <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                        Đang tải dữ liệu...
                      </TableCell>
                    </TableRow>
                  ) : filteredFaculties.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="h-32 text-center text-slate-500">
                        Không tìm thấy khoa nào
                      </TableCell>
                    </TableRow>
                  ) : filteredFaculties.map((f) => (
                    <TableRow key={f.id} className="hover:bg-slate-50/50 transition-colors">
                      <TableCell className="font-medium text-slate-500">{f.id}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="font-mono text-teal-700 border-teal-100 bg-teal-50/30">
                          {f.code}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-semibold text-slate-700">{f.name}</TableCell>
                      <TableCell className="text-slate-500 italic max-w-xs truncate">{f.description || "-"}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-8 w-8 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                            onClick={() => handleOpenDialog("faculty", f)}
                          >
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDelete("faculty", f.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TabsContent>

            <TabsContent value="departments" className="m-0">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50/50">
                    <TableHead className="w-[100px]">ID</TableHead>
                    <TableHead>Mã Bộ môn</TableHead>
                    <TableHead>Tên Bộ môn</TableHead>
                    <TableHead>Thuộc Khoa</TableHead>
                    <TableHead className="text-right">Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={5} className="h-32 text-center text-slate-500">
                        <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                        Đang tải dữ liệu...
                      </TableCell>
                    </TableRow>
                  ) : filteredDepartments.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="h-32 text-center text-slate-500">
                        Không tìm thấy bộ môn nào
                      </TableCell>
                    </TableRow>
                  ) : filteredDepartments.map((d) => (
                    <TableRow key={d.id} className="hover:bg-slate-50/50 transition-colors">
                      <TableCell className="font-medium text-slate-500">{d.id}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="font-mono text-blue-700 border-blue-100 bg-blue-50/30">
                          {d.code}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-semibold text-slate-700">{d.name}</TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="bg-slate-100 text-slate-600">
                          {d.faculty?.name || "N/A"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-8 w-8 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                            onClick={() => handleOpenDialog("department", d)}
                          >
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDelete("department", d.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{editingItem ? "Cập nhật" : "Thêm mới"} {itemType === "faculty" ? "Khoa" : "Bộ môn"}</DialogTitle>
            <DialogDescription>Nhập thông tin chi tiết dưới đây.</DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            {itemType === "faculty" ? (
              <>
                <div className="space-y-2">
                  <Label htmlFor="fac-code">Mã Khoa</Label>
                  <Input 
                    id="fac-code" 
                    value={facultyFormData.code} 
                    onChange={(e) => setFacultyFormData({...facultyFormData, code: e.target.value})}
                    placeholder="VD: CNTT, KTVT..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="fac-name">Tên Khoa</Label>
                  <Input 
                    id="fac-name" 
                    value={facultyFormData.name} 
                    onChange={(e) => setFacultyFormData({...facultyFormData, name: e.target.value})}
                    placeholder="VD: Khoa Công nghệ thông tin..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="fac-desc">Mô tả</Label>
                  <Input 
                    id="fac-desc" 
                    value={facultyFormData.description} 
                    onChange={(e) => setFacultyFormData({...facultyFormData, description: e.target.value})}
                  />
                </div>
              </>
            ) : (
              <>
                <div className="space-y-2">
                  <Label htmlFor="dept-faculty">Thuộc Khoa</Label>
                  <select 
                    id="dept-faculty"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    value={deptFormData.facultyId}
                    onChange={(e) => setDeptFormData({...deptFormData, facultyId: e.target.value})}
                  >
                    <option value="">-- Chọn Khoa --</option>
                    {faculties.map(f => (
                      <option key={f.id} value={f.id}>{f.name}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="dept-code">Mã Bộ môn</Label>
                  <Input 
                    id="dept-code" 
                    value={deptFormData.code} 
                    onChange={(e) => setDeptFormData({...deptFormData, code: e.target.value})}
                    placeholder="VD: KHMT, HTTT..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="dept-name">Tên Bộ môn</Label>
                  <Input 
                    id="dept-name" 
                    value={deptFormData.name} 
                    onChange={(e) => setDeptFormData({...deptFormData, name: e.target.value})}
                    placeholder="VD: Hệ thống thông tin..."
                  />
                </div>
              </>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={submitting}>Hủy</Button>
            <Button 
                onClick={handleSubmit} 
                disabled={submitting}
                className="bg-teal-600 hover:bg-teal-700 text-white"
            >
              {submitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Lưu thay đổi
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

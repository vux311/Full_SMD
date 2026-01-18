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
  BookOpen,
  Link2,
  GitBranch,
  X
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import axios from "@/lib/axios";
import { useAuth } from "@/contexts/AuthContext";

interface Subject {
  id: number;
  code: string;
  nameVi: string;
  nameEn: string;
  credits: number;
  departmentId: number;
  department?: {
    name: string;
  };
}

interface Relationship {
  id: number;
  subjectId: number;
  relatedSubjectId: number;
  type: string;
  relatedSubject?: Subject;
}

export default function SubjectsPage() {
  const { role } = useAuth();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  
  // States for Subject Dialog
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState<Subject | null>(null);
  const [formData, setFormData] = useState({
    code: "",
    nameVi: "",
    nameEn: "",
    credits: 0,
    departmentId: ""
  });
  const [departments, setDepartments] = useState<any[]>([]);
  const [submitting, setSubmitting] = useState(false);

  // States for Relationships
  const [relDialogOpen, setRelDialogOpen] = useState(false);
  const [targetSubject, setTargetSubject] = useState<Subject | null>(null);
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [newRel, setNewRel] = useState({ relatedSubjectId: "", type: "PREREQUISITE" });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [subjectsRes, deptsRes] = await Promise.all([
        axios.get("/subjects"),
        axios.get("/departments")
      ]);
      setSubjects(subjectsRes.data || []);
      setDepartments(deptsRes.data || []);
    } catch (err) {
      console.error("Failed to fetch subjects:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const filteredSubjects = subjects.filter(s => 
    s.nameVi.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleOpenDialog = (subject?: Subject) => {
    if (subject) {
      setEditingSubject(subject);
      setFormData({
        code: subject.code,
        nameVi: subject.nameVi,
        nameEn: subject.nameEn,
        credits: subject.credits,
        departmentId: String(subject.departmentId)
      });
    } else {
      setEditingSubject(null);
      setFormData({
        code: "",
        nameVi: "",
        nameEn: "",
        credits: 0,
        departmentId: ""
      });
    }
    setDialogOpen(true);
  };

  const handleSubmit = async () => {
    if (!formData.code || !formData.nameVi || !formData.departmentId) {
      alert("Vui lòng điền đủ thông tin bắt buộc");
      return;
    }

    setSubmitting(true);
    try {
      if (editingSubject) {
        await axios.put(`/subjects/${editingSubject.id}`, formData);
      } else {
        await axios.post("/subjects", formData);
      }
      setDialogOpen(false);
      fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Bạn có chắc chắn muốn xóa học phần này?")) return;
    try {
      await axios.delete(`/subjects/${id}`);
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.message || "Lỗi khi xóa học phần");
    }
  };

  const openRelDialog = async (subject: Subject) => {
    setTargetSubject(subject);
    try {
      const res = await axios.get(`/subject-relationships/subject/${subject.id}`);
      setRelationships(res.data || []);
      setRelDialogOpen(true);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddRel = async () => {
    if (!newRel.relatedSubjectId || !targetSubject) return;
    try {
      await axios.post("/subject-relationships", {
        subjectId: targetSubject.id,
        relatedSubjectId: Number(newRel.relatedSubjectId),
        type: newRel.type
      });
      // Refresh
      const res = await axios.get(`/subject-relationships/subject/${targetSubject.id}`);
      setRelationships(res.data || []);
      setNewRel({ ...newRel, relatedSubjectId: "" });
    } catch (err: any) {
      alert(err.response?.data?.error || "Lỗi khi thêm quan hệ");
    }
  };

  const handleRemoveRel = async (id: number) => {
    try {
      await axios.delete(`/subject-relationships/${id}`);
      const res = await axios.get(`/subject-relationships/subject/${targetSubject?.id}`);
      setRelationships(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const isAdmin = role === "Admin" || role === "Academic Affairs" || role === "AA";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Quản lý Học phần (Subjects)</h1>
          <p className="text-sm text-muted-foreground">
            Quản lý danh mục học phần và các mối quan hệ tiên quyết/song hành.
          </p>
        </div>
        {isAdmin && (
          <Button className="bg-teal-600 hover:bg-teal-700" onClick={() => handleOpenDialog()}>
            <Plus className="w-4 h-4 mr-2" /> Thêm học phần
          </Button>
        )}
      </div>

      <Card>
        <CardHeader className="pb-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Tìm theo tên hoặc mã học phần..."
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
                    <TableHead className="w-24">Mã HP</TableHead>
                    <TableHead>Tên Học Phần</TableHead>
                    <TableHead>Số TC</TableHead>
                    <TableHead>Bộ môn</TableHead>
                    <TableHead className="text-right">Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredSubjects.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-10 text-muted-foreground">
                        Không tìm thấy học phần nào.
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredSubjects.map((s) => (
                      <TableRow key={s.id} className="hover:bg-slate-50/50">
                        <TableCell className="font-mono font-bold text-teal-700">{s.code}</TableCell>
                        <TableCell>
                          <div>
                            <div className="font-semibold text-slate-900">{s.nameVi}</div>
                            <div className="text-xs text-slate-500 italic">{s.nameEn}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">{s.credits} TC</Badge>
                        </TableCell>
                        <TableCell className="text-sm text-slate-600">
                          {s.department?.name || "N/A"}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="text-blue-600 hover:bg-blue-50"
                              onClick={() => openRelDialog(s)}
                              title="Quản lý quan hệ (Tiên quyết/Song hành)"
                            >
                              <GitBranch className="h-4 w-4" />
                            </Button>
                            {isAdmin && (
                              <>
                                <Button 
                                  variant="ghost" 
                                  size="sm" 
                                  className="text-teal-600 hover:bg-teal-50"
                                  onClick={() => handleOpenDialog(s)}
                                >
                                  <Edit2 className="h-4 w-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm" 
                                  className="text-red-600 hover:bg-red-50"
                                  onClick={() => handleDelete(s.id)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Subject Create/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{editingSubject ? "Chỉnh sửa học phần" : "Thêm học phần mới"}</DialogTitle>
            <DialogDescription>
              Nhập các thông tin cơ bản cho học phần trong hệ thống.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">Mã HP</Label>
              <Input 
                className="col-span-3" 
                value={formData.code} 
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">Tên (Vi)</Label>
              <Input 
                className="col-span-3" 
                value={formData.nameVi} 
                onChange={(e) => setFormData({ ...formData, nameVi: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">Tên (En)</Label>
              <Input 
                className="col-span-3" 
                value={formData.nameEn} 
                onChange={(e) => setFormData({ ...formData, nameEn: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">Số TC</Label>
              <Input 
                type="number"
                className="col-span-3" 
                value={formData.credits} 
                onChange={(e) => setFormData({ ...formData, credits: Number(e.target.value) })}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">Bộ môn</Label>
              <Select 
                value={formData.departmentId} 
                onValueChange={(val: string) => setFormData({ ...formData, departmentId: val })}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Chọn bộ môn" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map((d) => (
                    <SelectItem key={d.id} value={String(d.id)}>{d.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Hủy</Button>
            <Button onClick={handleSubmit} disabled={submitting} className="bg-teal-600 hover:bg-teal-700 text-white">
              {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Lưu thay đổi
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Relationships Dialog */}
      <Dialog open={relDialogOpen} onOpenChange={setRelDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Mối quan hệ: {targetSubject?.nameVi}</DialogTitle>
            <DialogDescription>
              Thiết lập các học phần tiên quyết (Prerequisite) hoặc học trước (Co-requisite).
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="flex gap-2 items-end border p-3 rounded-md bg-slate-50">
              <div className="flex-1 space-y-1">
                <Label className="text-xs">Học phần liên quan</Label>
                <Select value={newRel.relatedSubjectId} onValueChange={(val: string) => setNewRel({...newRel, relatedSubjectId: val})}>
                  <SelectTrigger><SelectValue placeholder="Chọn môn..." /></SelectTrigger>
                  <SelectContent>
                    {subjects.filter(s => s.id !== targetSubject?.id).map(s => (
                      <SelectItem key={s.id} value={String(s.id)}>{s.code} - {s.nameVi}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="w-32 space-y-1">
                <Label className="text-xs">Loại quan hệ</Label>
                <Select value={newRel.type} onValueChange={(val: string) => setNewRel({...newRel, type: val})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="PREREQUISITE">Tiên quyết</SelectItem>
                    <SelectItem value="CO_REQUISITE">Học trước</SelectItem>
                    <SelectItem value="EQUIVALENT">Tương đương</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={handleAddRel} className="bg-blue-600 text-white">Thêm</Button>
            </div>

            <div className="border rounded-md max-h-[300px] overflow-y-auto">
              <Table>
                <TableHeader><TableRow><TableHead>Mã HP</TableHead><TableHead>Tên Học Phần</TableHead><TableHead>Loại</TableHead><TableHead className="w-10"></TableHead></TableRow></TableHeader>
                <TableBody>
                  {relationships.length === 0 ? (
                    <TableRow><TableCell colSpan={4} className="text-center py-4 text-xs text-slate-400 italic">Chưa có quan hệ nào được khai báo.</TableCell></TableRow>
                  ) : (
                    relationships.map((r: any) => (
                      <TableRow key={r.id}>
                        <TableCell className="font-mono text-xs">{r.relatedSubject?.code}</TableCell>
                        <TableCell className="text-xs">{r.relatedSubject?.name_vi || r.relatedSubject?.nameVi}</TableCell>
                        <TableCell><Badge className="text-[10px] scale-90" variant="outline">{r.type}</Badge></TableCell>
                        <TableCell><Button variant="ghost" size="icon" className="h-6 w-6 text-red-400" onClick={() => handleRemoveRel(r.id)}><X className="h-3 w-3"/></Button></TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

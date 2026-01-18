/*
fixed issues in Academic Year settings page:
- Khi tạo năm học mới, không bắt buộc phải nhập start_date và end_date nữa
- Thêm thông báo khi tạo năm học thành công
- Sau khi kích hoạt năm học mới, reload trang để Header cập nhật lại năm học hiện tại 
*/

"use client";

import React, { useEffect, useState } from "react";
import axios from "@/lib/axios";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { CheckCircle, Settings, Plus, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface AcademicYear {
  id: number;
  code: string;
  isActive: boolean;
}

export default function SettingsPage() {
  const [years, setYears] = useState<AcademicYear[]>([]);
  const [loading, setLoading] = useState(true);
  const [newYear, setNewYear] = useState({ code: "" });

  const fetchYears = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/academic-years/');
      const data = res.data;
      setYears(data || []);
    } catch (e) { console.error(e); } 
    finally { setLoading(false); }
  };

  useEffect(() => { fetchYears(); }, []);

  const handleCreate = async () => {
    if (!newYear.code) return alert("Vui lòng nhập mã năm học");
    try {
      await axios.post('/academic-years/', { code: newYear.code });
      alert("Thêm thành công!");
      setNewYear({ code: "" });
      fetchYears();
    } catch (e: any) { const message = e?.response?.data?.detail || e?.message || "Lỗi kết nối"; alert("Lỗi: " + message); }
  };

  const handleActivate = async (id: number) => {
      try {
          await axios.put(`/academic-years/${id}`, { isActive: true });
          alert("Đã kích hoạt năm học mới!");
          fetchYears();
          // Reload trang để Header cập nhật lại
          window.location.reload();
      } catch(e: any) { const message = e?.response?.data?.detail || e?.message || "Lỗi kết nối"; alert("Lỗi: " + message); }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Settings className="w-6 h-6 text-slate-700"/> Cấu hình Hệ thống
        </h2>
        <p className="text-sm text-muted-foreground mt-1">Quản lý năm học và các tham số hệ thống.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* FORM THÊM MỚI */}
        <Card className="md:col-span-1 h-fit">
            <CardHeader><CardTitle>Thêm Năm học mới</CardTitle></CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-2">
                    <label className="text-sm font-medium">Mã Năm học</label>
                    <Input placeholder="2026-2027" value={newYear.code} onChange={e => setNewYear({...newYear, code: e.target.value})} />
                    <p className="text-xs text-muted-foreground">VD: 2026-2027, HK1-2026</p>
                </div>
                <Button className="w-full mt-2" onClick={handleCreate}>
                    <Plus className="w-4 h-4 mr-2"/> Thêm mới
                </Button>
            </CardContent>
        </Card>

        {/* DANH SÁCH */}
        <Card className="md:col-span-2">
            <CardHeader><CardTitle>Danh sách Năm học</CardTitle></CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Mã năm học</TableHead>
                            <TableHead>Trạng thái</TableHead>
                            <TableHead className="text-right">Hành động</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow><TableCell colSpan={4} className="text-center h-24"><Loader2 className="animate-spin w-4 h-4 inline mr-2"/> Đang tải...</TableCell></TableRow>
                        ) : years.map(y => (
                            <TableRow key={y.id} className={y.isActive ? "bg-green-50" : ""}>
                                <TableCell className="font-mono font-bold">{y.code}</TableCell>
                                <TableCell>
                                    {y.isActive ? (
                                        <Badge className="bg-green-600 hover:bg-green-700">Đang kích hoạt</Badge>
                                    ) : (
                                        <Badge variant="outline">Không hoạt động</Badge>
                                    )}
                                </TableCell>
                                <TableCell className="text-right">
                                    {!y.isActive && (
                                        <Button size="sm" variant="outline" onClick={() => handleActivate(y.id)}>
                                            <CheckCircle className="w-4 h-4 mr-2 text-green-600"/> Kích hoạt
                                        </Button>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
      </div>
    </div>
  );
}
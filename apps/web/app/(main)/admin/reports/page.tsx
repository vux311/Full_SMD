"use client";

import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { 
  MessageSquareWarning, 
  Loader2, 
  User, 
  FileText, 
  Calendar,
  CheckCircle2,
  Clock
} from "lucide-react";
import { Button } from "@/components/ui/button";
import axios from "@/lib/axios";
import { useAuth } from "@/contexts/AuthContext";
import Link from "next/link";

interface Report {
  id: number;
  syllabusId: number;
  userId: number;
  content: string;
  createdAt: string;
  status: string;
  user?: {
    fullName: string;
    username: string;
  };
  syllabus?: {
    subjectCode: string;
    subjectNameVi: string;
    version: string;
  };
}

export default function ReportsPage() {
  const { role } = useAuth();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/student/reports');
      setReports(res.data || []);
    } catch (e: any) {
      console.error(e);
    } finally { setLoading(false); }
  };

  const handleResolve = async (id: number) => {
    try {
      await axios.post(`/student/report/${id}/resolve`, { status: 'RESOLVED' });
      fetchReports();
    } catch (e) {
      console.error(e);
      alert("Lỗi khi xử lý phản hồi");
    }
  };

  useEffect(() => { fetchReports(); }, []);

  const getStatusBadge = (status: string) => {
    if (status === "RESOLVED") return <Badge className="bg-green-100 text-green-700 border-green-200 gap-1"><CheckCircle2 className="w-3 h-3" /> Đã xử lý</Badge>;
    return <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200 gap-1"><Clock className="w-3 h-3" /> Chờ xử lý</Badge>;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
            <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                <MessageSquareWarning className="w-6 h-6 text-rose-500" /> Phản hồi & Báo lỗi từ Sinh viên
            </h2>
            <p className="text-muted-foreground">Theo dõi và xử lý các phản hồi của sinh viên về nội dung đề cương.</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchReports} className="gap-2">
            Làm mới
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center p-20">
              <Loader2 className="w-8 h-8 animate-spin text-teal-600" />
            </div>
          ) : (
            <div className="border rounded-md">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50">
                    <TableHead className="w-[180px]">Sinh viên</TableHead>
                    <TableHead className="w-[250px]">Học phần / Đề cương</TableHead>
                    <TableHead>Nội dung phản hồi</TableHead>
                    <TableHead className="w-[150px]">Ngày gửi</TableHead>
                    <TableHead className="text-right">Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {reports.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-20 text-muted-foreground italic text-lg">
                        Hiện chưa có phản hồi nào từ sinh viên.
                      </TableCell>
                    </TableRow>
                  ) : (
                    reports.map((r) => (
                      <TableRow key={r.id} className="hover:bg-slate-50 transition-colors">
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div className="p-2 bg-slate-100 rounded-full text-slate-500"><User className="w-4 h-4" /></div>
                            <div>
                                <div className="font-semibold text-sm">{r.user?.fullName || "Sinh viên"}</div>
                                <div className="text-[10px] text-muted-foreground">@{r.user?.username || "unknown"}</div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <div className="flex items-center gap-1.5 font-bold text-teal-700 text-xs">
                                <FileText className="w-3 h-3" />
                                <Link href={`/syllabus/${r.syllabusId}`} className="hover:underline">
                                    {r.syllabus?.subjectCode} - v{r.syllabus?.version}
                                </Link>
                            </div>
                            <div className="text-[11px] text-slate-500 truncate max-w-[220px]">
                                {r.syllabus?.subjectNameVi}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="max-w-[400px] text-sm text-slate-700 line-clamp-2 italic">
                            "{r.content}"
                          </div>
                        </TableCell>
                        <TableCell>
                           <div className="flex items-center gap-1.5 text-xs text-slate-500">
                              <Calendar className="w-3.5 h-3.5" />
                              {new Date(r.createdAt).toLocaleDateString('vi-VN')}
                           </div>
                        </TableCell>
                        <TableCell className="text-right">
                           <div className="flex items-center justify-end gap-2">
                             {getStatusBadge(r.status)}
                             {r.status === 'PENDING' && (
                               <Button size="sm" variant="ghost" className="h-8 text-teal-600 hover:text-teal-700 hover:bg-teal-50" onClick={() => handleResolve(r.id)}>
                                 Xử lý
                               </Button>
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
      
      <div className="bg-blue-50 border border-blue-100 p-4 rounded-lg flex gap-3">
          <div className="p-2 bg-blue-100 rounded-full text-blue-600 h-fit"><Clock className="w-4 h-4" /></div>
          <div>
              <h4 className="font-bold text-blue-800 text-sm">Ghi chú cho Quản trị viên</h4>
              <p className="text-xs text-blue-700 leading-relaxed max-w-2xl">
                  Khi sinh viên báo lỗi, thông báo sẽ được gửi đến Giảng viên biên soạn và Trưởng bộ môn. 
                  Bạn có thể liên hệ trực tiếp với sinh viên để làm rõ vấn đề hoặc yêu cầu giảng viên cập nhật nội dung đề cương.
              </p>
          </div>
      </div>
    </div>
  );
}

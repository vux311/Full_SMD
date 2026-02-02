"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { Edit, Eye, GitCompare, Loader2, RefreshCcw } from "lucide-react";
import SyllabusDeleteButton from "@/components/SyllabusDeleteButton"; 
import DashboardCharts from "@/components/DashboardCharts";
import axios from "@/lib/axios";

interface Syllabus {
  id: number;
  subjectNameVi: string;
  subjectNameEn: string;
  subjectCode: string;
  credits: number;
  status: string;
  version: string;
  lecturer: string;
  dateEdited: string;
}

export default function Dashboard() {
  const router = useRouter();
  
  const [syllabuses, setSyllabuses] = useState<Syllabus[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [statsData, setStatsData] = useState(null);
  
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  // Get user role
  const [userRole, setUserRole] = useState<string>("");
  
  useEffect(() => {
    if (typeof window !== "undefined") {
      const role = localStorage.getItem("role") || "";
      setUserRole(role);
    }
  }, []);

  const fetchData = useCallback(async (page: number, keyword: string) => {
    setLoading(true);

    try {
      const query = new URLSearchParams({ page: page.toString(), limit: "10", search: keyword });
      const listRes = await axios.get(`/syllabuses?${query.toString()}`);
      const list = listRes.data;
      setSyllabuses(list.data || []);
      setTotal(list.total || 0);
      setTotalPages(list.total_pages || 1);

      try {
        const statsRes = await axios.get(`/stats`);
        const stats = statsRes.data;
        setStatsData(stats);
      } catch (e) {
        // ignore stats error
      }

    } catch (err: any) {
      console.error(err);
      if (err?.response?.status === 401 || err?.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("role");
        router.push("/login");
        return;
      }
    } finally { setLoading(false); }
  }, [router]);

  useEffect(() => {
    const timer = setTimeout(() => fetchData(currentPage, searchTerm), 500);
    return () => clearTimeout(timer);
  }, [searchTerm, currentPage, fetchData]);

  const renderStatusBadge = (status: string) => {
    let color = "bg-gray-500";
    let label = status;
    
    switch (status) {
        case "Approved": color = "bg-green-600"; break;
        case "Pending": color = "bg-yellow-500"; label = "Pending Review"; break;
        case "Pending Approval": color = "bg-orange-500"; label = "Pending AA"; break; 
        case "Returned": color = "bg-red-500"; break;
        case "Draft": color = "bg-slate-500"; break;
    }
    return <Badge className={color}>{label}</Badge>;
  };

  return (
    <div className="space-y-8">
      
      <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold tracking-tight">Dashboard Overview</h2>
            <p className="text-sm text-muted-foreground">Tổng quan hệ thống thời gian thực</p>
          </div>
          <DashboardCharts data={statsData} />
      </section>

      <section className="space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-t pt-8">
            <div>
                <h3 className="text-xl font-bold tracking-tight">Quản lý Đề cương</h3>
                <p className="text-sm text-muted-foreground">Danh sách chi tiết các học phần</p>
            </div>
            <div className="w-full md:w-1/3 flex gap-2">
              <Input
                placeholder="Tìm kiếm theo tên hoặc mã HP..."
                value={searchTerm}
                onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                className="bg-white"
              />
              <Button variant="outline" size="icon" onClick={() => fetchData(currentPage, searchTerm)} title="Làm mới">
                  <RefreshCcw className="w-4 h-4"/>
              </Button>
            </div>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">Mã HP</TableHead>
                  <TableHead>Tên Học Phần</TableHead>
                  <TableHead>Phiên bản</TableHead>
                  <TableHead>Tín chỉ</TableHead>
                  <TableHead>Giảng viên</TableHead>
                  <TableHead>Trạng thái</TableHead>
                  <TableHead className="text-right">Hành động</TableHead> 
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading && syllabuses.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="h-24 text-center">
                      <div className="flex justify-center items-center gap-2">
                        <Loader2 className="animate-spin w-4 h-4" /> Đang tải dữ liệu...
                      </div>
                    </TableCell>
                  </TableRow>
                ) : syllabuses.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                      Không tìm thấy đề cương nào.
                    </TableCell>
                  </TableRow>
                ) : (
                  syllabuses.map((s) => (
                    <TableRow key={s.id}>
                      <TableCell className="font-bold">{s.subjectCode}</TableCell>
                      <TableCell>
                        <div className="font-medium">{s.subjectNameVi || "(Chưa có tên)"}</div>
                        <div className="text-xs text-muted-foreground truncate max-w-[200px]">{s.subjectNameEn}</div>
                      </TableCell>
                      <TableCell><Badge variant="outline" className="bg-slate-50">v{s.version || "1.0"}</Badge></TableCell>
                      <TableCell>{s.credits}</TableCell>
                      <TableCell className="text-sm text-gray-600">{s.lecturer}</TableCell>
                      <TableCell>{renderStatusBadge(s.status)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2 items-center">
                            <Link href={`/syllabus/compare?baseId=${s.id - 1}&targetId=${s.id}`}>
                                <Button variant="outline" size="icon" title="So sánh bản cũ"><GitCompare className="w-4 h-4 text-orange-600" /></Button>
                            </Link>
                            <Link href={`/syllabus/${s.id}`}>
                                <Button variant="ghost" size="icon" title="Xem chi tiết"><Eye className="w-4 h-4" /></Button>
                            </Link>
                            
                            {/* Edit - chỉ Lecturer và Admin, và chỉ khi Draft/Returned */}
                            {(userRole === "Lecturer" || userRole === "Admin") && 
                             (s.status.toUpperCase() === "DRAFT" || s.status.toUpperCase() === "RETURNED") && (
                                <Link href={`/syllabus/${s.id}/edit`}>
                                    <Button variant="ghost" size="icon" title="Chỉnh sửa"><Edit className="w-4 h-4 text-teal-600" /></Button>
                                </Link>
                            )}
                            
                            {/* Delete - chỉ Admin */}
                            {userRole === "Admin" && s.status.toUpperCase() === "DRAFT" && (
                                <div className="scale-90"><SyllabusDeleteButton id={s.id} /></div>
                            )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
            
            <div className="flex items-center justify-between px-4 py-4 border-t">
              <div className="text-sm text-muted-foreground">Trang {currentPage} / {totalPages}</div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage <= 1}>Trước</Button>
                <Button variant="outline" size="sm" onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage >= totalPages}>Sau</Button>
              </div>
            </div>
          </Card>
      </section>
    </div>
  );
}
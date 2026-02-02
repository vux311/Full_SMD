"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Loader2, FileSignature, CheckCircle, XCircle, ArrowRight } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import axios from "@/lib/axios";

interface Syllabus {
  id: number;
  subjectNameVi: string;
  subjectCode: string;
  lecturer: string;
  dateEdited: string;
  status: string;
  version: string;
  headDepartment?: string; // Tên trưởng bộ môn đã duyệt
}

export default function ReviewPage() {
  const [reviews, setReviews] = useState<Syllabus[]>([]);
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState("");
  
  // State cho Modal từ chối
  const [rejectId, setRejectId] = useState<number | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [processing, setProcessing] = useState(false);

  const fetchReviews = async () => {
    setLoading(true);
    const role = localStorage.getItem("role") || "";
    setUserRole(role);

    // Determine status to fetch based on role - Yuri Workflow Update
    let statusToFetch = "PENDING_REVIEW";
    if (role === "Academic Affairs" || role === "AA") statusToFetch = "PENDING_APPROVAL";
    else if (role === "Principal") statusToFetch = "APPROVED";
    else if (role === "Admin") statusToFetch = "";

    try {
      const url = statusToFetch ? `/syllabuses?status=${encodeURIComponent(statusToFetch)}&limit=100` : `/syllabuses?limit=100`;
      const res = await axios.get(url);
      const data = res.data;
      setReviews(data.data || []);
    } catch (err: any) {
      console.error(err);
      const status = err?.response?.status || err?.status;
      if (status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("role");
        window.location.href = "/login";
      }
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchReviews(); }, []);

  const handleApprove = async (id: number) => {
      // Đổi thông báo tùy theo role
      let msg = "Xác nhận duyệt?";
      if (userRole === "Head of Dept" || userRole === "HoD") {
          msg = "Xác nhận duyệt và chuyển lên Phòng Đào tạo?";
      } else if (userRole === "Academic Affairs" || userRole === "AA") {
          msg = "Xác nhận duyệt và chuyển lên Ban Giám hiệu phê duyệt cuối cùng?";
      } else {
          msg = "Xác nhận PHÊ DUYỆT CHIẾN LƯỢC CUỐI CÙNG và công bố?";
      }

      if(!confirm(msg)) return;
      
      setProcessing(true);
      try {
          await axios.post(`/syllabuses/${id}/evaluate`, { action: 'approve' });
          alert("✅ Phê duyệt thành công!");
          
          // QUAN TRỌNG: Cập nhật state cục bộ để biến khỏi danh sách ngay lập tức
          setReviews(prev => prev.filter(r => r.id !== id));
          
          // Vẫn gọi lại fetch để đảm bảo đồng bộ hoàn toàn với server (optional)
          // fetchReviews(); 
      } catch(e: any) {
          const status = e?.response?.status || e?.status;
          
          if (status === 401) { 
              alert("⚠️ Phiên đăng nhập hết hạn."); 
              window.location.href = "/login"; 
              return; 
          }
          
          if (status === 403) {
              const message = e?.response?.data?.message || "Bạn không có quyền phê duyệt đề cương này";
              alert("🚫 " + message);
              return;
          }
          
          if (status === 422) {
              const message = e?.response?.data?.message || "Đề cương không trong trạng thái phù hợp";
              alert("⚠️ " + message);
              return;
          }
          
          const message = e?.response?.data?.message || e?.message || "Lỗi kết nối";
          alert("❌ " + message);
      } finally {
          setProcessing(false);
      }
  };

  const handleRejectSubmit = async () => {
      if (!rejectId || !rejectReason.trim()) return alert("⚠️ Vui lòng nhập lý do từ chối!");
      
      setProcessing(true);
      try {
          await axios.post(`/syllabuses/${rejectId}/evaluate`, { action: 'reject', comment: rejectReason });
          alert("✅ Đã trả về yêu cầu sửa!");
          
          // QUAN TRỌNG: Cập nhật state cục bộ
          const idToRemove = rejectId;
          setRejectId(null);
          setRejectReason("");
          setReviews(prev => prev.filter(r => r.id !== idToRemove));
      } catch(e: any) {
          const status = e?.response?.status || e?.status;
          
          if (status === 403) {
              alert("🚫 Bạn không có quyền từ chối đề cương này");
              return;
          }
          
          if (status === 422) {
              const message = e?.response?.data?.message || "Đề cương không trong trạng thái phù hợp";
              alert("⚠️ " + message);
              return;
          }
          
          const message = e?.response?.data?.message || e?.message || "Lỗi kết nối";
          alert("❌ " + message);
      } finally { setProcessing(false); }
  };

  // Xác định tiêu đề trang dựa trên Role
  const isAA = userRole === "Academic Affairs" || userRole === "AA";
  const isHoD = userRole === "Head of Dept" || userRole === "HoD";
  const isPrincipal = userRole === "Principal";

  const pageTitle = isPrincipal
    ? "Phê duyệt Chiến lược (Ban Giám hiệu)"
    : isAA
    ? "Phê duyệt cấp Trường (Phòng Đào tạo)" 
    : "Phê duyệt cấp Bộ môn";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
            <h2 className="text-2xl font-bold tracking-tight">{pageTitle}</h2>
            <p className="text-sm text-muted-foreground">
                {isPrincipal
                    ? "Danh sách đề cương đã qua kiểm duyệt chuyên môn và nghiệp vụ, chờ phê duyệt cuối cùng."
                    : isAA 
                    ? "Danh sách các đề cương đã được Trưởng bộ môn thông qua." 
                    : "Danh sách các đề cương đang chờ duyệt."}
            </p>
        </div>
        <Badge variant="secondary" className="text-base px-4 py-2 bg-yellow-100 text-yellow-800 hover:bg-yellow-200">
          Chờ xử lý: {reviews.length}
        </Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileSignature className="w-5 h-5"/> Danh sách chờ duyệt
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Mã HP</TableHead>
                <TableHead>Tên Học Phần</TableHead>
                <TableHead>Phiên bản</TableHead>
                <TableHead>Người gửi</TableHead>
                {(isAA || isPrincipal) && <TableHead>Trạng thái duyệt</TableHead>}
                <TableHead>Ngày cập nhật</TableHead>
                <TableHead className="text-right">Hành động</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow><TableCell colSpan={7} className="text-center h-24"><Loader2 className="animate-spin w-4 h-4 inline mr-2"/> Đang tải...</TableCell></TableRow>
              ) : reviews.length === 0 ? (
                <TableRow><TableCell colSpan={7} className="text-center h-24 text-muted-foreground">Hiện tại không có yêu cầu nào cần duyệt.</TableCell></TableRow>
              ) : (
                reviews.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell className="font-bold">{s.subjectCode}</TableCell>
                    <TableCell>
                        <div className="font-medium">{s.subjectNameVi}</div>
                        {(s.status || "").toUpperCase() === "PENDING_APPROVAL" && <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200 mt-1">Đã qua BM</Badge>}
                        {(s.status || "").toUpperCase() === "APPROVED" && <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-200 mt-1">Đã qua PĐT</Badge>}
                        {(s.status || "").toUpperCase() === "PENDING_REVIEW" && <Badge variant="outline" className="text-xs bg-orange-50 text-orange-700 border-orange-200 mt-1">Chờ BM duyệt</Badge>}
                    </TableCell>
                    <TableCell><Badge variant="outline">v{s.version}</Badge></TableCell>
                    <TableCell className="text-gray-600">{s.lecturer}</TableCell>
                    
                    {(isAA || isPrincipal) && (
                        <TableCell className="text-green-600 font-medium">
                            <div className="flex items-center gap-1">
                                <CheckCircle className="w-3 h-3"/> 
                                {isPrincipal ? "PĐT Approved" : (s.headDepartment || "BM Approved")}
                            </div>
                        </TableCell>
                    )}
                    
                    <TableCell>{s.dateEdited}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Link href={`/syllabus/${s.id}/edit`}>
                             <Button variant="outline" size="sm">Xem chi tiết</Button>
                        </Link>
                        
                        <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={() => handleApprove(s.id)} title="Duyệt">
                            {isHoD ? <ArrowRight className="w-4 h-4"/> : <CheckCircle className="w-4 h-4"/>}
                        </Button>
                        
                        <Button size="sm" variant="destructive" onClick={() => setRejectId(s.id)} title="Trả về">
                            <XCircle className="w-4 h-4"/>
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* MODAL NHẬP LÝ DO TỪ CHỐI */}
      <Dialog open={!!rejectId} onOpenChange={(open) => !open && setRejectId(null)}>
        <DialogContent>
            <DialogHeader>
                <DialogTitle>Trả về yêu cầu sửa đổi</DialogTitle>
                <DialogDescription>
                    {isAA 
                        ? "Đề cương sẽ bị trả về trạng thái 'Returned' cho Giảng viên (và thông báo cho Trưởng BM)." 
                        : "Vui lòng nhập lý do để Giảng viên chỉnh sửa lại."}
                </DialogDescription>
            </DialogHeader>
            <div className="py-4">
                <Textarea 
                    placeholder="Nhập lý do cụ thể..." 
                    rows={4}
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                />
            </div>
            <DialogFooter>
                <Button variant="outline" onClick={() => setRejectId(null)}>Hủy bỏ</Button>
                <Button variant="destructive" onClick={handleRejectSubmit} disabled={processing}>
                    {processing ? "Đang gửi..." : "Xác nhận Trả về"}
                </Button>
            </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
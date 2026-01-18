"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Bell, Flag, Sparkles, Loader2, CheckCircle2 } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import axios from "@/lib/axios";
import { useAuth } from "@/contexts/AuthContext";

interface StudentActionButtonsProps {
  syllabusId: number;
  subjectId: number;
  subjectCode: string;
}

export default function StudentActionButtons({ syllabusId, subjectId, subjectCode }: StudentActionButtonsProps) {
  const { role } = useAuth();
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [reportContent, setReportContent] = useState("");
  const [loading, setLoading] = useState<string | null>(null);
  const [aiSummary, setAiSummary] = useState<string | null>(null);
  const [subscribed, setSubscribed] = useState(false);

  const isStudent = role === "Student" || role === "Admin";

  const handleSubscribe = async () => {
    if (!isStudent) return alert("Bạn cần đăng nhập với vai trò Sinh viên để sử dụng tính năng này.");
    setLoading("sub");
    try {
      // Giả sử API lấy student_id từ token hoặc g.user_id ở backend
      // Ở đây controller đang yêu cầu student_id trong body, cần check lại backend
      await axios.post("/student/subscribe", { subject_id: subjectId });
      setSubscribed(true);
      alert("✅ Đăng ký theo dõi môn học thành công!");
    } catch (err) {
      console.error(err);
      alert("❌ Có lỗi xảy ra khi đăng ký theo dõi.");
    } finally { setLoading(null); }
  };

  const handleReport = async () => {
    if (!reportContent.trim()) return;
    setLoading("report");
    try {
      await axios.post("/student/report", { syllabus_id: syllabusId, content: reportContent });
      alert("✅ Cảm ơn bạn đã phản hồi! Chúng tôi sẽ kiểm tra sớm nhất.");
      setShowReportDialog(false);
      setReportContent("");
    } catch (err) {
      console.error(err);
      alert("❌ Lỗi khi gửi phản hồi.");
    } finally { setLoading(null); }
  };

  const handleAiSummary = async () => {
    setLoading("ai");
    try {
        // Gọi AI Summary - Cần triển khai endpoint này ở backend
        const res = await axios.post(`/ai/summary`, { syllabus_id: syllabusId });
        setAiSummary(res.data.summary);
    } catch (err) {
        console.error(err);
        setAiSummary("Đã có lỗi xảy ra khi tạo tóm tắt AI. Vui lòng thử lại sau.");
    } finally { setLoading(null); }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-2">
        <Button 
          variant={subscribed ? "secondary" : "outline"} 
          className={`flex-1 gap-2 ${subscribed ? "text-green-600 bg-green-50" : "text-teal-600 border-teal-200"}`}
          onClick={handleSubscribe}
          disabled={loading === "sub"}
        >
          {loading === "sub" ? <Loader2 className="w-4 h-4 animate-spin" /> : subscribed ? <CheckCircle2 className="w-4 h-4" /> : <Bell className="w-4 h-4" />}
          {subscribed ? "Đang theo dõi" : "Theo dõi môn này"}
        </Button>

        <Button 
          variant="outline" 
          className="flex-1 gap-2 text-rose-600 border-rose-200 hover:bg-rose-50"
          onClick={() => isStudent ? setShowReportDialog(true) : alert("Bạn cần đăng nhập để gửi phản hồi.")}
        >
          <Flag className="w-4 h-4" /> Báo lỗi/Phản hồi
        </Button>

        <Button 
          className="flex-1 gap-2 bg-gradient-to-r from-teal-600 to-blue-600 hover:from-teal-700 hover:to-blue-700 text-white shadow-md shadow-teal-100"
          onClick={handleAiSummary}
          disabled={loading === "ai"}
        >
          {loading === "ai" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          Tóm tắt AI
        </Button>
      </div>

      {aiSummary && (
        <div className="bg-teal-50 border border-teal-100 rounded-lg p-4 animate-in fade-in slide-in-from-top-2">
            <h4 className="font-bold text-teal-800 mb-2 flex items-center gap-2">
                <Sparkles className="w-4 h-4" /> Tóm tắt AI (Sơ lược môn học)
            </h4>
            <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">{aiSummary}</p>
        </div>
      )}

      <Dialog open={showReportDialog} onOpenChange={setShowReportDialog}>
        <DialogContent>
            <DialogHeader>
                <DialogTitle>Gửi phản hồi về đề cương</DialogTitle>
                <DialogDescription>Giúp chúng tôi cải thiện chất lượng dữ liệu. Hãy mô tả lỗi bạn phát hiện (Mã môn: {subjectCode})</DialogDescription>
            </DialogHeader>
            <Textarea 
                placeholder="Nhập nội dung phản hồi của bạn..." 
                className="min-h-[120px]"
                value={reportContent}
                onChange={(e) => setReportContent(e.target.value)}
            />
            <DialogFooter>
                <Button variant="outline" onClick={() => setShowReportDialog(false)}>Hủy</Button>
                <Button 
                    variant="destructive" 
                    onClick={handleReport}
                    disabled={loading === "report" || !reportContent.trim()}
                >
                    {loading === "report" && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                    Gửi phản hồi
                </Button>
            </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

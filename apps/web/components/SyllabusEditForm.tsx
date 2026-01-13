"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { 
    Save, 
    Send, 
    FileDiff, 
    ArrowLeft, 
    MessageSquareWarning, 
    Sparkles, 
    Loader2   
} from "lucide-react";
import { SyllabusData } from "./Types";
import MaterialsTab from "./syllabus-form/MaterialsTab";
import axios from "@/lib/axios";

interface ExtendedSyllabusData extends SyllabusData {
    feedback?: string | null;
}

export default function SyllabusEditForm({ initial }: { initial: SyllabusData }) {
  const router = useRouter();
  
  const [data, setData] = useState<ExtendedSyllabusData>(initial);
  const [lastSavedString, setLastSavedString] = useState(JSON.stringify(initial));
  const [submitting, setSubmitting] = useState(false);
  const [userRole, setUserRole] = useState<string>("");
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    const role = localStorage.getItem("role") || "";
    setUserRole(role);
  }, []);

  const hasUnsavedChanges = useMemo(() => {
    return JSON.stringify(data) !== lastSavedString;
  }, [data, lastSavedString]);

  const isEditable = !data.id || data.status === "Draft" || data.status === "Returned";


  const updateField = (field: keyof SyllabusData, value: any) => {
    if (isEditable) setData((prev) => ({ ...prev, [field]: value }));
  };

  const updateTime = (key: keyof SyllabusData["timeAllocation"], val: number) => {
    if (isEditable) setData((prev) => ({
      ...prev,
      timeAllocation: { ...prev.timeAllocation, [key]: val },
    }));
  }; 

  const addArrayItem = <T,>(field: keyof SyllabusData, newItem: T) => {
    if (isEditable) setData((prev) => ({
      ...prev,
      [field]: [...(prev[field] as T[]), newItem],
    }));
  };

  const removeArrayItem = (field: keyof SyllabusData, index: number) => {
    if (isEditable) setData((prev) => ({
      ...prev,
      [field]: (prev[field] as any[]).filter((_, i) => i !== index),
    }));
  };

  const updateArrayItem = <T,>(field: keyof SyllabusData, index: number, newItem: Partial<T>) => {
    if (isEditable) {
      const arr = [...(data[field] as T[])];
      arr[index] = { ...arr[index], ...newItem };
      setData((prev) => ({ ...prev, [field]: arr }));
    }
  };

  const handleAIGenerate = async () => {
    if (!data.subjectNameVi) return alert("Vui lòng nhập Tên môn học (Tiếng Việt) để AI hiểu ý bạn!");

    if (!confirm(`AI sẽ tự động soạn thảo nội dung cho môn "${data.subjectNameVi}". Dữ liệu hiện tại sẽ bị ghi đè. Bạn có chắc không?`)) return; 

    setAiLoading(true);
    try {
        const res = await axios.post("/ai/generate", { subject_name: data.subjectNameVi }, { skipSnake: true } as any);
        const aiData = res.data;
        setData(prev => ({
            ...prev,
            ...aiData,
            id: prev.id,
            status: prev.status,
            version: prev.version
        }));
        alert("AI đã soạn thảo xong! Vui lòng kiểm tra lại các Tab.");
    } catch (e: any) {
        console.error(e);
        const msg = e?.response?.data?.detail || e?.message || "Lỗi kết nối đến AI Server.";
        alert(msg);
    } finally {
        setAiLoading(false);
    }
  };

  const handleSave = async () => {
    setSubmitting(true);
    try {
      const isEdit = !!data.id;

      if (!isEdit) {
        // Create parent syllabus first (axios will convert camelCase -> snake_case on POST)
        const parentPayload: any = { ...data };
        delete parentPayload.clos;
        delete parentPayload.teachingPlan;
        delete parentPayload.materials;

        const res = await axios.post("/syllabuses", parentPayload);
        const resJson = res.data;
        if (!resJson?.id) throw new Error("No id returned from server");

        const syllabusId = resJson.id;

        // Create children (CLOs, Teaching Plans, Materials) using Promise.all
        const closPromises = (data.clos || []).map((clo) => axios.post("/syllabus-clos", { syllabus_id: syllabusId, ...clo }));
        const planPromises = (data.teachingPlan || []).map((p) => axios.post("/teaching-plans", { syllabus_id: syllabusId, ...p }));
        const matPromises = (data.materials || []).map((m) => axios.post("/syllabus-materials", { syllabus_id: syllabusId, ...m }));

        await Promise.all([...closPromises, ...planPromises, ...matPromises]);

        const newData = { ...data, id: syllabusId };
        setData(newData);
        setLastSavedString(JSON.stringify(newData));
        router.push(`/syllabus/${syllabusId}/edit`);
        alert("Tạo mới thành công!");
        return;
      }

      // Edit existing syllabus
      await axios.patch(`/syllabuses/${data.id}`, data);
      setLastSavedString(JSON.stringify(data));
      router.refresh();
      alert("Đã lưu bản nháp!");

    } catch (error: any) {
      console.error("Save Error:", error);
      if (error?.status === 401) {
        alert("Phiên đăng nhập hết hạn.");
        router.push("/login");
        return;
      }
      alert(error?.message || "Lỗi khi lưu dữ liệu.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleWorkflow = async (action: "submit" | "approve" | "revise") => {
    if (!data.id) return;

    let confirmMsg = "";
    if (action === "submit") confirmMsg = "Gửi đề cương đi phê duyệt? Bạn sẽ không thể chỉnh sửa trong lúc chờ.";
    if (action === "approve") confirmMsg = "Xác nhận PHÊ DUYỆT đề cương này?";
    if (action === "revise") confirmMsg = "Hệ thống sẽ tạo phiên bản MỚI (Draft) từ bản này để bạn chỉnh sửa. Tiếp tục?";

    if (!confirm(confirmMsg)) return;

    setSubmitting(true);
    try {
      const res = await axios.post(`/syllabuses/${data.id}/${action}`);
      const resData = res.data;

      if (action === "revise") {
        alert(`Đã tạo phiên bản mới: ${resData.version}`);
        router.push(`/syllabus/${resData.id}/edit`);
        return;
      }
      alert("Thao tác thành công!");
      router.refresh();
    } catch (e: any) {
      console.error(e);
      const msg = e?.response?.data?.detail || e?.message || "Lỗi kết nối server.";
      alert(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const totalPeriods = (data.timeAllocation.theory || 0) + (data.timeAllocation.exercises || 0) + (data.timeAllocation.practice || 0);

  const renderStatusBadge = () => {
    const status = data.status || "Draft";
    let colorClass = "bg-gray-500";
    let label = "Bản nháp";

    if (status === "Pending") { colorClass = "bg-yellow-500"; label = "Chờ duyệt (BM)"; }
    else if (status === "Pending Approval") { colorClass = "bg-orange-500"; label = "Chờ duyệt (PĐT)"; }
    else if (status === "Approved") { colorClass = "bg-green-600"; label = "Đã công bố"; }
    else if (status === "Returned") { colorClass = "bg-red-500"; label = "Yêu cầu sửa"; }

    return <Badge className={`${colorClass} hover:${colorClass} ml-3 text-sm px-3 py-1`}>{label}</Badge>;
  };

  return (
    <div className="w-full max-w-6xl mx-auto py-6 px-4">
      {data.status === "Returned" && data.feedback && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3 items-start shadow-sm animate-in slide-in-from-top-2">
             <MessageSquareWarning className="w-6 h-6 text-red-600 mt-0.5 shrink-0" />
             <div>
                <h3 className="font-bold text-red-700 text-lg">Yêu cầu chỉnh sửa</h3>
                <p className="text-red-600 mt-1 whitespace-pre-wrap">{data.feedback}</p>
             </div>
          </div>
      )}

      <Card className="shadow-lg border-t-4 border-t-primary">
        <CardHeader className="flex flex-col md:flex-row justify-between items-start md:items-center border-b pb-4 mb-4 bg-slate-50/50 rounded-t-lg gap-4">
          <div>
            <div className="flex items-center gap-2">
              <CardTitle className="text-xl">
                {data.id ? `Biên soạn: ${data.subjectCode}` : "Tạo Đề Cương Mới"}
              </CardTitle>
              {data.version && <Badge variant="outline" className="border-primary text-primary font-bold">v{data.version}</Badge>}
              {renderStatusBadge()}
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {isEditable ? "Bạn đang ở chế độ chỉnh sửa" : "Chế độ xem (Read-only)"}
            </p>
          </div>

          <div className="flex flex-wrap gap-2 items-center">
            <Button variant="outline" onClick={() => router.back()} size="sm">
                <ArrowLeft className="w-4 h-4 mr-2"/> Thoát
            </Button>

            {isEditable && (
              <Button onClick={handleSave} disabled={submitting || aiLoading} variant="secondary" className="border border-slate-300 relative" size="sm">
                <Save className="w-4 h-4 mr-2" /> Lưu Nháp
                {hasUnsavedChanges && (
                    <span className="absolute -top-1 -right-1 flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                    </span>
                )}
              </Button>
            )}

            {data.id && (
              <>
                {(data.status === "Draft" || data.status === "Returned") && (
                  <div className="flex flex-col items-end">
                      {/* SỬA: bg-blue-600 -> bg-teal-600 */}
                      <Button 
                        className="bg-teal-600 hover:bg-teal-700 text-white disabled:opacity-50 disabled:cursor-not-allowed" 
                        size="sm" 
                        onClick={() => handleWorkflow("submit")}
                        disabled={hasUnsavedChanges || submitting || aiLoading}
                        title={hasUnsavedChanges ? "Bạn cần lưu nháp trước khi gửi duyệt" : "Gửi đi phê duyệt"}
                      >
                        <Send className="w-4 h-4 mr-2" /> Gửi Duyệt
                      </Button>
                  </div>
                )}

                {(data.status === "Pending" || data.status === "Pending Approval") && (userRole === "Head of Dept" || userRole === "Academic Affairs" || userRole === "Admin") && (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => router.push("/reviews")}>
                         Xử lý yêu cầu này (Duyệt/Trả về)
                    </Button>
                  </div>
                )}

                {data.status === "Approved" && (
                    <Button className="bg-purple-600 hover:bg-purple-700 text-white border-purple-800" size="sm" onClick={() => handleWorkflow("revise")}>
                        <FileDiff className="w-4 h-4 mr-2" /> Tạo phiên bản mới
                    </Button>
                )}
              </>
            )}
          </div>
        </CardHeader>

        <CardContent className={!isEditable ? "opacity-95 pointer-events-none" : ""}>
          <Tabs defaultValue="general" className="w-full">
            <TabsList className="grid w-full grid-cols-7 mb-6 h-auto p-1 bg-slate-100">
              <TabsTrigger value="general">1. Thông tin chung</TabsTrigger>
              <TabsTrigger value="clos">2-4. Mục tiêu & CĐR</TabsTrigger>
              <TabsTrigger value="plo">PLO Map</TabsTrigger>
              <TabsTrigger value="assessment">5-6. Đánh giá</TabsTrigger>
              <TabsTrigger value="plan">7. Kế hoạch</TabsTrigger>
              <TabsTrigger value="materials">8. Tài liệu</TabsTrigger>
              <TabsTrigger value="others">9. Khác</TabsTrigger>
            </TabsList>

            <TabsContent value="general" className="space-y-6 animate-in fade-in-50">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label className="text-sm font-semibold flex justify-between items-center">
                        Tên HP (Tiếng Việt)
                        {isEditable && (
                            <button 
                                onClick={handleAIGenerate} 
                                disabled={aiLoading}
                                className="text-xs flex items-center gap-1 text-purple-600 hover:text-purple-800 font-bold transition-all hover:scale-105 border border-purple-200 px-2 py-1 rounded-full bg-purple-50"
                                title="Tự động điền nội dung bằng AI"
                            >
                                {aiLoading ? <Loader2 className="w-3 h-3 animate-spin"/> : <Sparkles className="w-3 h-3"/>}
                                {aiLoading ? "AI đang viết..." : "AI Soạn thảo"}
                            </button>
                        )}
                    </label>
                    <Input value={data.subjectNameVi} onChange={(e) => updateField("subjectNameVi", e.target.value)} placeholder="VD: Nhập môn Trí tuệ Nhân tạo"/>
                </div>
                <div className="space-y-2"><label className="text-sm font-semibold">Tên HP (Tiếng Anh)</label><Input value={data.subjectNameEn} onChange={(e) => updateField("subjectNameEn", e.target.value)} /></div>
                <div className="space-y-2"><label className="text-sm font-semibold">Mã Học Phần</label><Input value={data.subjectCode} onChange={(e) => updateField("subjectCode", e.target.value)} /></div>
                <div className="space-y-2"><label className="text-sm font-semibold">Số tín chỉ</label><Input type="number" value={data.credits} onChange={(e) => updateField("credits", Number(e.target.value))} /></div>
              </div>
              <div className="border p-4 rounded-md bg-slate-50">
                <h3 className="font-bold mb-4 text-sm uppercase text-slate-600">Phân bổ thời gian (Tiết)</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 items-end">
                  <label className="text-sm">Lý thuyết <Input type="number" className="mt-1 bg-white" value={data.timeAllocation.theory} onChange={(e) => updateTime("theory", Number(e.target.value))} /></label>
                  <label className="text-sm">Bài tập/Dự án <Input type="number" className="mt-1 bg-white" value={data.timeAllocation.exercises} onChange={(e) => updateTime("exercises", Number(e.target.value))} /></label>
                  <label className="text-sm">Thực hành <Input type="number" className="mt-1 bg-white" value={data.timeAllocation.practice} onChange={(e) => updateTime("practice", Number(e.target.value))} /></label>
                  <label className="text-sm">Tự học <Input type="number" className="mt-1 bg-white" value={data.timeAllocation.selfStudy} onChange={(e) => updateTime("selfStudy", Number(e.target.value))} /></label>
                  <div className="text-sm font-bold pb-2 text-right md:text-left">Tổng trên lớp: <span className="text-lg text-primary ml-2">{totalPeriods}</span></div>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <label className="text-sm font-semibold">HP Tiên quyết <Input className="mt-1" value={data.prerequisites} onChange={(e) => updateField("prerequisites", e.target.value)} /></label>
                <label className="text-sm font-semibold">HP Học trước <Input className="mt-1" value={data.preCourses} onChange={(e) => updateField("preCourses", e.target.value)} /></label>
                <label className="text-sm font-semibold">HP Song hành <Input className="mt-1" value={data.coCourses} onChange={(e) => updateField("coCourses", e.target.value)} /></label>
              </div>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <label className="text-sm font-semibold">Loại học phần <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background mt-1" value={data.courseType} onChange={(e) => updateField("courseType", e.target.value)}><option value="Bắt buộc">Bắt buộc</option><option value="Tự chọn bắt buộc">Tự chọn bắt buộc</option><option value="Tự chọn tự do">Tự chọn tự do</option></select></label>
                <label className="text-sm font-semibold">Thuộc thành phần <Input className="mt-1" value={data.componentType} onChange={(e) => updateField("componentType", e.target.value)} /></label>
              </div>
              <div className="border-t pt-4 grid grid-cols-1 md:grid-cols-4 gap-6">
                <label className="text-sm font-semibold">Ngày biên soạn <Input type="date" className="mt-1" value={data.datePrepared} onChange={(e) => updateField("datePrepared", e.target.value)} /></label>
                <label className="text-sm font-semibold">Ngày chỉnh sửa <Input type="date" className="mt-1" value={data.dateEdited} onChange={(e) => updateField("dateEdited", e.target.value)} /></label>
                <label className="text-sm font-semibold">Trưởng khoa/QL CTĐT <Input className="mt-1" value={data.dean} onChange={(e) => updateField("dean", e.target.value)} /></label>
                <label className="text-sm font-semibold">GV Biên soạn <Input className="mt-1 bg-gray-100" value={data.lecturer} disabled /></label>
              </div>
            </TabsContent>

            {/* Các TabsContent khác (clos, plo, assessment, plan, materials, others) giữ nguyên code cũ vì không có màu cứng, nó sẽ tự ăn theo màu Primary mới */}
            <TabsContent value="clos" className="space-y-6 animate-in fade-in-50">
              <div><label className="font-bold block mb-2">2. Mô tả tóm tắt học phần</label><Textarea rows={4} value={data.description} onChange={(e) => updateField("description", e.target.value)} /></div>
              <div className="bg-slate-50 p-4 rounded-md">
                <label className="font-bold block mb-2">3. Mục tiêu học phần (Course Objectives)</label>
                {data.objectives.map((obj, i) => (
                  <div key={i} className="flex gap-2 mb-2"><Input value={obj} onChange={(e) => { const newObj = [...data.objectives]; newObj[i] = e.target.value; updateField("objectives", newObj); }} /><Button variant="ghost" onClick={() => { const newObj = data.objectives.filter((_, idx) => idx !== i); updateField("objectives", newObj); }}>✕</Button></div>
                ))}
                <Button variant="outline" size="sm" className="mt-2 border-dashed" onClick={() => updateField("objectives", [...data.objectives, `CO${data.objectives.length + 1}: `])}>+ Thêm Mục Tiêu (CO)</Button>
              </div>
              <div>
                <label className="font-bold block mb-2">4. Chuẩn đầu ra học phần (CLOs)</label>
                <Table>
                  <TableHeader><TableRow><TableHead className="w-24">Mã CĐR</TableHead><TableHead>Mô tả chuẩn đầu ra</TableHead><TableHead className="w-12"></TableHead></TableRow></TableHeader>
                  <TableBody>{data.clos.map((clo, i) => (
                    <TableRow key={i}><TableCell><Input className="font-bold" value={clo.code} onChange={(e) => updateArrayItem("clos", i, { code: e.target.value })} /></TableCell><TableCell><Input value={clo.description} onChange={(e) => updateArrayItem("clos", i, { description: e.target.value })} /></TableCell><TableCell><Button variant="ghost" size="icon" onClick={() => removeArrayItem("clos", i)}>✕</Button></TableCell></TableRow>
                  ))}</TableBody>
                </Table>
                <Button variant="outline" className="w-full mt-2 border-dashed" onClick={() => addArrayItem("clos", { code: `CLO${data.clos.length + 1}`, description: "" })}>+ Thêm CLO Mới</Button>
              </div>
            </TabsContent>

            <TabsContent value="plo" className="animate-in fade-in-50">
               {/* SỬA: Alert bg-blue-50 -> bg-teal-50 */}
               <div className="alert bg-teal-50 text-teal-700 p-3 mb-4 text-sm rounded-md border border-teal-100"><strong>Hướng dẫn:</strong> Điền các ký tự (I, R, M, A) vào các ô tương ứng.</div>
               <div className="border rounded-md overflow-x-auto"><Table><TableHeader><TableRow><TableHead className="w-24 bg-gray-100">CLO \ PLO</TableHead>{[1, 2, 3, 4, 5, 6, 7].map((p) => (<TableHead key={p} className="text-center w-16 bg-gray-50">PLO{p}</TableHead>))}</TableRow></TableHeader><TableBody>{data.clos.map((clo, i) => { const rowMap = data.ploMapping.find((p) => p.cloCode === clo.code) || { cloCode: clo.code, plos: {} }; return (<TableRow key={i}><TableCell className="font-bold bg-gray-50">{clo.code}</TableCell>{[1, 2, 3, 4, 5, 6, 7].map((p) => (<TableCell key={p} className="p-1"><Input className="h-9 text-center uppercase" value={rowMap.plos[`PLO${p}`] || ""} onChange={(e) => { const val = e.target.value; const newMapping = [...data.ploMapping]; const existIdx = newMapping.findIndex((m) => m.cloCode === clo.code); if (existIdx >= 0) { newMapping[existIdx] = { ...newMapping[existIdx], plos: { ...newMapping[existIdx].plos, [`PLO${p}`]: val } } } else { newMapping.push({ cloCode: clo.code, plos: { [`PLO${p}`]: val } }); } updateField("ploMapping", newMapping); }} /></TableCell>))}</TableRow>); })}</TableBody></Table></div>
            </TabsContent>

            <TabsContent value="assessment" className="space-y-6 animate-in fade-in-50">
               <div><label className="font-bold block mb-2">5. Nhiệm vụ của sinh viên</label><Textarea rows={4} value={data.studentDuties} onChange={(e) => updateField("studentDuties", e.target.value)} /></div>
               <div><div className="flex justify-between items-center mb-2"><label className="font-bold block">6. Phương pháp kiểm tra, đánh giá</label><div className="text-sm">Tổng trọng số: <span className={`font-bold ml-2 ${data.assessmentScheme.reduce((sum, item) => sum + (item.weight || 0), 0) === 100 ? 'text-green-600' : 'text-red-600'}`}>{data.assessmentScheme.reduce((sum, item) => sum + (item.weight || 0), 0)}%</span></div></div><div className="border rounded-md"><Table><TableHeader><TableRow><TableHead>Thành phần</TableHead><TableHead>Phương pháp / Hình thức</TableHead><TableHead className="w-24">CĐR HP</TableHead><TableHead className="w-20">Tiêu chí</TableHead><TableHead className="w-20">Trọng số (%)</TableHead><TableHead className="w-10"></TableHead></TableRow></TableHeader><TableBody>{data.assessmentScheme.map((item, i) => (<TableRow key={i}><TableCell><Input value={item.component} onChange={(e) => updateArrayItem("assessmentScheme", i, { component: e.target.value })} /></TableCell><TableCell><Input value={item.method} onChange={(e) => updateArrayItem("assessmentScheme", i, { method: e.target.value })} /></TableCell><TableCell><Input value={item.clos} onChange={(e) => updateArrayItem("assessmentScheme", i, { clos: e.target.value })} /></TableCell><TableCell><Input value={item.criteria} onChange={(e) => updateArrayItem("assessmentScheme", i, { criteria: e.target.value })} /></TableCell><TableCell><Input type="number" value={item.weight} onChange={(e) => updateArrayItem("assessmentScheme", i, { weight: Number(e.target.value) })} /></TableCell><TableCell><Button variant="ghost" size="icon" onClick={() => removeArrayItem("assessmentScheme", i)}>✕</Button></TableCell></TableRow>))}</TableBody></Table></div><Button variant="outline" className="w-full mt-2 border-dashed" onClick={() => addArrayItem("assessmentScheme", { component: "", method: "", clos: "", criteria: "", weight: 0 })}>+ Thêm thành phần đánh giá</Button></div>
            </TabsContent>

            <TabsContent value="plan" className="animate-in fade-in-50">
               <div className="mb-2"><label className="font-bold">7. Kế hoạch giảng dạy và học tập</label></div><div className="border rounded-md overflow-hidden"><Table><TableHeader><TableRow><TableHead className="w-20">Tuần</TableHead><TableHead className="w-1/3">Nội dung</TableHead><TableHead className="w-24">CLOs</TableHead><TableHead>Hoạt động Dạy/Học</TableHead><TableHead className="w-32">Đánh giá</TableHead><TableHead className="w-10"></TableHead></TableRow></TableHeader><TableBody>{data.teachingPlan.map((row, i) => (<TableRow key={i}><TableCell className="align-top"><Input value={row.week} onChange={(e) => updateArrayItem("teachingPlan", i, { week: e.target.value })} /></TableCell><TableCell className="align-top"><Textarea className="min-h-[80px]" value={row.content} onChange={(e) => updateArrayItem("teachingPlan", i, { content: e.target.value })} /></TableCell><TableCell className="align-top"><Input value={row.clos} onChange={(e) => updateArrayItem("teachingPlan", i, { clos: e.target.value })} /></TableCell><TableCell className="align-top"><Textarea className="min-h-[80px]" value={row.activity} onChange={(e) => updateArrayItem("teachingPlan", i, { activity: e.target.value })} /></TableCell><TableCell className="align-top"><Input value={row.assessment} onChange={(e) => updateArrayItem("teachingPlan", i, { assessment: e.target.value })} /></TableCell><TableCell className="align-top"><Button variant="ghost" size="icon" onClick={() => removeArrayItem("teachingPlan", i)}>✕</Button></TableCell></TableRow>))}</TableBody></Table></div><Button variant="outline" className="w-full mt-2 border-dashed" onClick={() => addArrayItem("teachingPlan", { week: "", content: "", clos: "", activity: "", assessment: "" })}>+ Thêm Tuần / Chương</Button>
            </TabsContent>

            <TabsContent value="materials">
                <MaterialsTab data={data} readOnly={!isEditable} onUpdate={(idx, val) => updateArrayItem("materials", idx, { content: val })} onAdd={(type) => addArrayItem("materials", { type: type, content: "" })} onRemove={(idx) => removeArrayItem("materials", idx)}/>
            </TabsContent>

            <TabsContent value="others" className="space-y-6 animate-in fade-in-50">
              <div className="bg-white p-6 rounded-md border shadow-sm"><label className="font-bold block mb-3 text-lg">9. Yêu cầu khác về học phần</label><Textarea rows={8} className="resize-y" value={data.otherRequirements} onChange={(e) => updateField("otherRequirements", e.target.value)} placeholder="Ví dụ: Sinh viên phải chuẩn bị Laptop cá nhân..." /></div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
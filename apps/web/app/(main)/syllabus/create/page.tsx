"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// --- Types ---
type CLO = { id: string; code: string; description: string };
type Assessment = { id: string; component: string; weight: number; description: string };
type Material = { id: string; type: "Main" | "Ref"; author: string; title: string; publisher: string; year: string };

export default function CreateSyllabusPage() {
  const router = useRouter();
  const [tab, setTab] = useState("general");

  // --- State ---
  const [title, setTitle] = useState("");
  const [code, setCode] = useState("");
  const [credits, setCredits] = useState<number | "">(3);
  const [description, setDescription] = useState("");
  
  const [prerequisites, setPrerequisites] = useState("");
  const [preCourses, setPreCourses] = useState("");
  const [courseType, setCourseType] = useState("Bắt buộc");
  const [studentTasks, setStudentTasks] = useState("");

  // MỚI: State cho Time Allocation
  const [timeAllocation, setTimeAllocation] = useState({ theory: 0, exercises: 0, practice: 0, self_study: 0 });

  const [clos, setClos] = useState<CLO[]>([{ id: crypto.randomUUID(), code: "G1", description: "" }]);
  const [assessments, setAssessments] = useState<Assessment[]>([
    { id: crypto.randomUUID(), component: "Quá trình", weight: 50, description: "" },
    { id: crypto.randomUUID(), component: "Cuối kỳ", weight: 50, description: "" },
  ]);
  const [materials, setMaterials] = useState<Material[]>([]);

  const [submitting, setSubmitting] = useState(false);

  // --- Helpers ---
  function addCLO() { setClos(s => [...s, { id: crypto.randomUUID(), code: `G${s.length + 1}`, description: "" }]); }
  function updateCLO(id: string, f: Partial<CLO>) { setClos(s => s.map(c => c.id === id ? { ...c, ...f } : c)); }
  function removeCLO(id: string) { setClos(s => s.filter(c => c.id !== id)); }

  function addAssessment() { setAssessments(s => [...s, { id: crypto.randomUUID(), component: "", weight: 0, description: "" }]); }
  function updateAssessment(id: string, f: Partial<Assessment>) { setAssessments(s => s.map(a => a.id === id ? { ...a, ...f } : a)); }
  function removeAssessment(id: string) { setAssessments(s => s.filter(a => a.id !== id)); }

  function addMaterial() { setMaterials(s => [...s, { id: crypto.randomUUID(), type: "Main", author: "", title: "", publisher: "", year: "" }]); }
  function updateMaterial(id: string, f: Partial<Material>) { setMaterials(s => s.map(m => m.id === id ? { ...m, ...f } : m)); }
  function removeMaterial(id: string) { setMaterials(s => s.filter(m => m.id !== id)); }

  const totalWeight = assessments.reduce((sum, item) => sum + (Number(item.weight) || 0), 0);

  // --- Submit ---
  async function handleSubmit() {
    const payload = {
      subject_name: title,
      subject_code: code,
      credits: credits === "" ? 0 : credits,
      description,
      prerequisites,
      pre_courses: preCourses,
      course_type: courseType,
      student_tasks: studentTasks,
      time_allocation: timeAllocation, // Thêm vào payload
      clos: clos.map(c => ({ code: c.code, description: c.description })),
      assessment_scheme: assessments.map(a => ({ component: a.component, weight: Number(a.weight), description: a.description })),
      materials: materials.map(m => ({ type: m.type, title: m.title, author: m.author, publisher: m.publisher, year: m.year })),
    };

    setSubmitting(true);
    try {
      // Use the centralized client so base URL, Authorization header and snake_case conversion are handled automatically
      // Example usage (client-side):
      // const resJson = await (await import("@/lib/apiClient")).apiFetch("/syllabuses", { method: "POST", body: payload });
      // router.push("/");

      // (Legacy direct fetch removed from source; keep example above for reference)
    } catch (err) { alert("Lỗi: " + err); } 
    finally { setSubmitting(false); }
  }

  const selectClass = "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";

  return (
    <div className="flex justify-center py-12 px-4">
      <Card className="w-full max-w-4xl">
        <CardHeader><CardTitle>Thêm Đề Cương Mới</CardTitle></CardHeader>
        <CardContent>
          <Tabs value={tab} onValueChange={setTab}>
            <TabsList className="w-full grid grid-cols-4">
              <TabsTrigger value="general">Thông tin chung</TabsTrigger>
              <TabsTrigger value="clos">CĐR (CLOs)</TabsTrigger>
              <TabsTrigger value="materials">Tài liệu</TabsTrigger>
              <TabsTrigger value="assessments">Đánh giá</TabsTrigger>
            </TabsList>

            <TabsContent value="general" className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <label className="flex flex-col gap-1"><span className="text-sm font-medium">Tên học phần</span><Input value={title} onChange={e => setTitle(e.target.value)} /></label>
                <label className="flex flex-col gap-1"><span className="text-sm font-medium">Mã học phần</span><Input value={code} onChange={e => setCode(e.target.value)} /></label>
              </div>
              <div className="grid grid-cols-2 gap-4">
                 <label className="flex flex-col gap-1"><span className="text-sm font-medium">Số tín chỉ</span><Input type="number" value={credits} onChange={e => setCredits(e.target.value === "" ? "" : Number(e.target.value))} /></label>
                 <label className="flex flex-col gap-1"><span className="text-sm font-medium">Loại học phần</span>
                    <select className={selectClass} value={courseType} onChange={e => setCourseType(e.target.value)}>
                        <option value="Bắt buộc">Bắt buộc</option>
                        <option value="Tự chọn">Tự chọn</option>
                    </select>
                 </label>
              </div>

              {/* KHUNG NHẬP PHÂN BỔ THỜI GIAN */}
              <div className="border p-4 rounded-md bg-gray-50">
                <span className="text-sm font-bold mb-2 block">Phân bổ thời gian (Tiết)</span>
                <div className="grid grid-cols-4 gap-2">
                    <label className="flex flex-col gap-1">
                        <span className="text-xs text-gray-500">Lý thuyết</span>
                        <Input type="number" value={timeAllocation.theory} onChange={e => setTimeAllocation({...timeAllocation, theory: Number(e.target.value)})} />
                    </label>
                    <label className="flex flex-col gap-1">
                        <span className="text-xs text-gray-500">Bài tập/Dự án</span>
                        <Input type="number" value={timeAllocation.exercises} onChange={e => setTimeAllocation({...timeAllocation, exercises: Number(e.target.value)})} />
                    </label>
                    <label className="flex flex-col gap-1">
                        <span className="text-xs text-gray-500">Thực hành</span>
                        <Input type="number" value={timeAllocation.practice} onChange={e => setTimeAllocation({...timeAllocation, practice: Number(e.target.value)})} />
                    </label>
                    <label className="flex flex-col gap-1">
                        <span className="text-xs text-gray-500">Tự học</span>
                        <Input type="number" value={timeAllocation.self_study} onChange={e => setTimeAllocation({...timeAllocation, self_study: Number(e.target.value)})} />
                    </label>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <label className="flex flex-col gap-1"><span className="text-sm font-medium">HP Tiên quyết</span><Input value={prerequisites} onChange={e => setPrerequisites(e.target.value)} /></label>
                <label className="flex flex-col gap-1"><span className="text-sm font-medium">HP Học trước</span><Input value={preCourses} onChange={e => setPreCourses(e.target.value)} /></label>
              </div>
              <label className="flex flex-col gap-1"><span className="text-sm font-medium">Mô tả tóm tắt</span><Textarea value={description} onChange={e => setDescription(e.target.value)} /></label>
              <label className="flex flex-col gap-1"><span className="text-sm font-medium">Nhiệm vụ SV</span><Textarea value={studentTasks} onChange={e => setStudentTasks(e.target.value)} /></label>
            </TabsContent>

            {/* Các Tab khác giữ nguyên logic cũ */}
            <TabsContent value="clos" className="mt-4 space-y-4">
                {clos.map((c, idx) => (
                    <div key={c.id} className="flex gap-2"><Input className="w-24" value={c.code} onChange={e => updateCLO(c.id, {code: e.target.value})} /><Input value={c.description} onChange={e => updateCLO(c.id, {description: e.target.value})} /><Button variant="ghost" onClick={() => removeCLO(c.id)}>✕</Button></div>
                ))}
                <Button variant="outline" onClick={addCLO} className="w-full border-dashed">+ Thêm CLO</Button>
            </TabsContent>
            <TabsContent value="materials" className="space-y-4 mt-4">
                {materials.map((m, idx) => (
                    <div key={m.id} className="border p-3 rounded-md space-y-2 relative bg-gray-50">
                        <Button variant="ghost" size="sm" className="absolute top-2 right-2 text-red-500" onClick={() => removeMaterial(m.id)}>✕</Button>
                        <div className="flex gap-4">
                             <div className="w-1/4">
                                <span className="text-xs text-muted-foreground">Loại</span>
                                <select className={`${selectClass} h-9 mt-1`} value={m.type} onChange={e => updateMaterial(m.id, { type: e.target.value as any })}><option value="Main">Giáo trình</option><option value="Ref">Tham khảo</option></select>
                             </div>
                             <div className="w-3/4"><span className="text-xs text-muted-foreground">Tên tài liệu</span><Input className="h-9 mt-1" value={m.title} onChange={e => updateMaterial(m.id, { title: e.target.value })} /></div>
                        </div>
                        <div className="grid grid-cols-3 gap-2">
                             <Input className="h-8 text-sm" value={m.author} onChange={e => updateMaterial(m.id, { author: e.target.value })} placeholder="Tác giả" />
                             <Input className="h-8 text-sm" value={m.publisher} onChange={e => updateMaterial(m.id, { publisher: e.target.value })} placeholder="NXB" />
                             <Input className="h-8 text-sm" value={m.year} onChange={e => updateMaterial(m.id, { year: e.target.value })} placeholder="Năm" />
                        </div>
                    </div>
                ))}
                <Button variant="outline" onClick={addMaterial} className="w-full border-dashed">+ Thêm Tài liệu</Button>
            </TabsContent>
            <TabsContent value="assessments" className="mt-4 space-y-4">
                <div className="flex justify-between"><h3 className="font-medium">Điểm số</h3><Badge variant={totalWeight===100?"default":"destructive"}>{totalWeight}%</Badge></div>
                {assessments.map(a => (
                    <div key={a.id} className="flex gap-2"><Input className="w-1/3" value={a.component} onChange={e=>updateAssessment(a.id, {component:e.target.value})} /><Input className="w-20" type="number" value={a.weight} onChange={e=>updateAssessment(a.id, {weight:Number(e.target.value)})} /><Input className="flex-1" value={a.description} onChange={e=>updateAssessment(a.id, {description:e.target.value})} /><Button variant="ghost" onClick={()=>removeAssessment(a.id)}>✕</Button></div>
                ))}
                <Button variant="outline" onClick={addAssessment} className="w-full border-dashed">+ Thêm điểm</Button>
                <div className="pt-4 mt-4 border-t"><Button className="w-full" onClick={handleSubmit} disabled={submitting || totalWeight !== 100}>Lưu Đề Cương</Button></div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}

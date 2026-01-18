"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { useReactToPrint } from "react-to-print";
import { Printer, ArrowLeft, Pencil, BrainCircuit, CheckCircle2, AlertCircle, History } from "lucide-react";
import { Button } from "@/components/ui/button";
import VisualSubjectTree from "./VisualSubjectTree";
import StudentActionButtons from "./StudentActionButtons";
import SyllabusHistory from "./SyllabusHistory";
import axios from "@/lib/axios";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";

// QUAN TRỌNG: Import đúng đường dẫn
import { SyllabusData } from "./Types"; 

export default function SyllabusDetailView({ 
  syllabus, 
  hideManagementButtons = false,
  hideStudentActions = false
}: { 
  syllabus: SyllabusData, 
  hideManagementButtons?: boolean,
  hideStudentActions?: boolean
}) {
  const contentRef = useRef<HTMLDivElement>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  
  const handlePrint = useReactToPrint({
    contentRef: contentRef,
    documentTitle: `${syllabus.subjectCode}_Syllabus`,
  });

  const analyzeAlignment = async () => {
    setAnalyzing(true);
    try {
      const res = await axios.post("/ai/analyze-alignment", { syllabus_id: syllabus.id });
      setAnalysisResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Lỗi khi phân tích: " + (err as any).message);
    } finally {
      setAnalyzing(false);
    }
  };

  const printStyle = `
    @page { size: A4; margin: 20mm 20mm 20mm 20mm; } 
    @media print { 
        body { -webkit-print-color-adjust: exact; } 
        .print-break-avoid { break-inside: avoid; }
    }
    .word-table { width: 100%; border-collapse: collapse; font-size: 11pt; }
    .word-table td, .word-table th { border: 1px solid black; padding: 4px; vertical-align: top; }
    .word-header { font-family: "Times New Roman", serif; text-align: center; }
  `;

  return (
    <div className="p-6 bg-gray-100 min-h-screen font-sans">
      <style>{printStyle}</style>
      
      <div className="max-w-[210mm] mx-auto mb-4 flex justify-between print:hidden">
         {!hideManagementButtons ? (
           <Link href="/"><Button variant="ghost"><ArrowLeft className="mr-2 h-4 w-4" /> Quay lại</Button></Link>
         ) : <div></div>}
         <div className="flex gap-2">
            {!hideManagementButtons && (
              <>
              <Link href={`/syllabus/${syllabus.id}/edit`}><Button variant="outline"><Pencil className="mr-2 h-4 w-4" /> Chỉnh sửa</Button></Link>
              
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="secondary" onClick={analyzeAlignment} disabled={analyzing}>
                    <BrainCircuit className="mr-2 h-4 w-4" /> 
                    {analyzing ? "Đang phân tích..." : "AI Alignment"}
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle className="flex items-center gap-2">
                        <BrainCircuit className="w-5 h-5 text-purple-600" />
                        Phân tích ma trận CLO-PLO (AI)
                      </DialogTitle>
                    </DialogHeader>
                    
                    {analysisResult ? (
                      <div className="space-y-4 py-4">
                        <div className="flex items-center justify-between bg-slate-50 p-4 rounded-lg border">
                          <div className="font-semibold">Điểm phù hợp tổng quát:</div>
                          <div className={`text-2xl font-bold ${analysisResult.overall_score > 70 ? 'text-green-600' : 'text-amber-500'}`}>
                            {analysisResult.overall_score}%
                          </div>
                        </div>

                        <div>
                          <h4 className="font-bold flex items-center gap-1 mb-2">
                             <CheckCircle2 className="w-4 h-4 text-green-500" /> Điểm mạnh
                          </h4>
                          <ul className="list-disc pl-5 text-sm space-y-1">
                            {analysisResult.strengths?.map((s: string, i: number) => <li key={i}>{s}</li>)}
                          </ul>
                        </div>

                        <div>
                          <h4 className="font-bold flex items-center gap-1 mb-2">
                             <AlertCircle className="w-4 h-4 text-amber-500" /> Điểm cần cải thiện
                          </h4>
                          <ul className="list-disc pl-5 text-sm space-y-1">
                            {analysisResult.weaknesses?.map((w: string, i: number) => <li key={i}>{w}</li>)}
                          </ul>
                        </div>

                        <div className="bg-blue-50 p-4 rounded-lg text-sm italic border-l-4 border-blue-400">
                          {analysisResult.analysis}
                        </div>

                        <div className="space-y-2">
                          <h4 className="font-bold text-sm">Gợi ý từ chuyên gia AI:</h4>
                          {analysisResult.suggestions?.map((s: any, i: number) => (
                            <div key={i} className="p-3 bg-white border rounded text-xs">
                              {s.clo && <Badge variant="outline" className="mb-1">{s.clo}</Badge>}
                              {s.plo && <Badge variant="outline" className="mb-1 bg-purple-50">{s.plo}</Badge>}
                              <p className="text-gray-700">{s.suggestion || s.issue}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="py-12 text-center animate-pulse">
                        Đang lấy ý kiến từ chuyên gia AI...
                      </div>
                    )}
                </DialogContent>
              </Dialog>
              </>
            )}
            <Button onClick={() => handlePrint()}><Printer className="mr-2 h-4 w-4" /> Xuất PDF / In</Button>
            {syllabus.id && <SyllabusHistory syllabusId={syllabus.id} />}
         </div>
      </div>

      <div className="flex justify-center">
        <div ref={contentRef} className="bg-white w-[210mm] min-h-[297mm] px-[15mm] py-[15mm] shadow-lg print:shadow-none text-black leading-snug" style={{ fontFamily: '"Times New Roman", Times, serif', fontSize: '12pt' }}>
            
            <div className="text-center font-bold mb-4">
                <div className="uppercase text-[11pt]">TRƯỜNG ĐH GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH</div>
                <div className="uppercase text-[14pt] mt-2">ĐỀ CƯƠNG CHI TIẾT HỌC PHẦN</div>
                <div className="italic font-normal text-[12pt]">(COURSE SYLLABUS)</div>
            </div>

            {/* Workflow & Deadline Banner */}
            {syllabus.status !== 'Draft' && syllabus.status !== 'Approved' && syllabus.status !== 'Published' && (
              <div className="mb-6 p-4 rounded-lg border bg-slate-50 flex items-center justify-between print:hidden">
                <div className="flex items-center gap-4">
                  <div>
                    <div className="text-xs text-muted-foreground uppercase font-semibold">Trạng thái</div>
                    <Badge variant={syllabus.status === 'Returned' ? 'destructive' : 'secondary'}>
                      {syllabus.status}
                    </Badge>
                  </div>
                  {syllabus.dueDate && (
                    <div>
                      <div className="text-xs text-muted-foreground uppercase font-semibold flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> Hạn duyệt
                      </div>
                      <div className={`text-sm font-bold ${new Date(syllabus.dueDate) < new Date() ? 'text-red-600' : 'text-amber-600'}`}>
                        {new Date(syllabus.dueDate).toLocaleDateString('vi-VN')}
                      </div>
                    </div>
                  )}
                  {syllabus.assignedTo && (
                    <div>
                      <div className="text-xs text-muted-foreground uppercase font-semibold">Đang chờ xử lý bởi</div>
                      <div className="text-sm font-medium">{syllabus.assignedTo}</div>
                    </div>
                  )}
                </div>
                {new Date(syllabus.dueDate || '') < new Date() && (
                   <Badge variant="destructive" className="animate-pulse">QUÁ HẠN</Badge>
                )}
              </div>
            )}

            {/* 1. THÔNG TIN CHUNG */}
            <div className="mb-4">
                <h3 className="font-bold mb-2">1. Tổng quát về học phần (General course information)</h3>
                <table className="word-table">
                    <tbody>
                        <tr>
                            <td className="w-[140px]">Tên học phần</td>
                            <td colSpan={5}>
                                <div>Tiếng Việt: <b>{syllabus.subjectNameVi}</b></div>
                                <div>Tiếng Anh: <b>{syllabus.subjectNameEn}</b></div>
                                <div>Mã HP: <b>{syllabus.subjectCode}</b></div>
                            </td>
                        </tr>
                        <tr>
                            <td>Số tín chỉ</td>
                            <td colSpan={5} className="font-bold">{syllabus.credits || 0} ({syllabus.credits || 0}, 0, {syllabus.credits || 0})</td>
                        </tr>
                        <tr className="text-center font-semibold">
                            <td>Phân bổ thời gian</td><td>Lý thuyết</td><td>Bài tập/Dự án</td><td>Thực hành</td><td>Tổng</td><td>Tự học</td>
                        </tr>
                        <tr className="text-center">
                            <td></td>
                            <td>{syllabus.timeAllocation?.theory || 0}</td>
                            <td>{syllabus.timeAllocation?.exercises || 0}</td>
                            <td>{syllabus.timeAllocation?.practice || 0}</td>
                            <td className="font-bold">{((syllabus.timeAllocation?.theory || 0) + (syllabus.timeAllocation?.exercises || 0) + (syllabus.timeAllocation?.practice || 0))}</td>
                            <td>{syllabus.timeAllocation?.selfStudy || 0}</td>
                        </tr>
                        <tr><td>Thang điểm</td><td colSpan={5}>10</td></tr>
                        <tr><td>HP tiên quyết</td><td colSpan={5}>{syllabus.prerequisites || 'N/A'}</td></tr>
                        <tr><td>HP học trước</td><td colSpan={5}>{syllabus.preCourses || 'N/A'}</td></tr>
                        <tr><td>HP song hành</td><td colSpan={5}>{syllabus.coCourses || 'N/A'}</td></tr>
                        <tr>
                            <td>Loại học phần</td>
                            <td colSpan={5}>
                                <span className="mr-8">{syllabus.courseType === 'Bắt buộc' ? '☒' : '☐'} Bắt buộc</span>
                                <span className="mr-8">{syllabus.courseType === 'Tự chọn bắt buộc' ? '☒' : '☐'} Tự chọn bắt buộc</span>
                                <span>{syllabus.courseType === 'Tự chọn tự do' ? '☒' : '☐'} Tự chọn tự do</span>
                            </td>
                        </tr>
                        <tr><td>Thuộc thành phần</td><td colSpan={5}>{syllabus.componentType}</td></tr>
                    </tbody>
                </table>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs italic mb-6">
                <div>
                   <p><b>Chương trình đào tạo:</b> {syllabus.programName || "Chưa xác định"}</p>
                   <p><b>Năm học áp dụng:</b> {syllabus.academicYearName || "Chưa xác định"}</p>
                </div>
                <div>
                   <p><b>Giảng viên biên soạn:</b> {syllabus.lecturer || "Giảng viên"}</p>
                   <p><b>Phiên bản:</b> {syllabus.version || "1.0"}</p>
                </div>
            </div>

            {/* BẢN ĐỒ MÔN HỌC (Visual Subject Tree) */}
            <div className="mb-4 space-y-4 print:hidden">
                {/* Tính năng sinh viên: Tóm tắt AI, Theo dõi, Báo lỗi */}
                {!hideStudentActions && (
                    <StudentActionButtons 
                        syllabusId={syllabus.id!} 
                        subjectId={syllabus.subjectId!} 
                        subjectCode={syllabus.subjectCode}
                    />
                )}

                <VisualSubjectTree 
                    subjectId={syllabus.subjectId!} 
                    currentSubjectName={syllabus.subjectNameVi} 
                />
            </div>

            {/* 2. MÔ TẢ */}
            <div className="mb-4">
                <h3 className="font-bold mb-1">2. Mô tả tóm tắt học phần (Course description)</h3>
                <p className="text-justify whitespace-pre-line">{syllabus.description}</p>
            </div>

            {/* 3. MỤC TIÊU */}
            <div className="mb-4">
                 <h3 className="font-bold mb-1">3. Mục tiêu học phần (Course Objectives)</h3>
                 <p className="mb-1">Học phần này trang bị cho sinh viên:</p>
                 <ul className="list-none pl-0">
                    {syllabus.objectives.map((obj, i) => <li key={i}>{obj}</li>)}
                 </ul>
            </div>

            {/* 4. CLOs & PLO Mapping */}
            <div className="mb-4">
                <h3 className="font-bold mb-1">4. Chuẩn đầu ra học phần (Course Learning Outcomes - CLO)</h3>
                <p className="mb-2">Sau khi học xong học phần này sinh viên có khả năng:</p>
                {syllabus.clos.map((c, i) => (
                    <div key={i} className="mb-1 text-justify flex">
                        <span className="font-bold min-w-[60px]">{c.code} :</span>
                        <span>{c.description}</span>
                    </div>
                ))}
                
                <p className="mt-2 mb-1 italic">Liên hệ giữa CĐR học phần (CLOs) và CĐR CTĐT (PLOs):</p>
                <table className="word-table text-center">
                    <thead>
                        <tr className="bg-gray-100">
                            <th>PLO/CLO</th>{[1,2,3,4,5,6,7].map(n => <th key={n}>PLO{n}</th>)}
                        </tr>
                    </thead>
                    <tbody>
                        {syllabus.clos.map((clo, i) => {
                             const map = syllabus.ploMapping.find(m => m.cloCode === clo.code)?.plos || {};
                             return (
                                <tr key={i}>
                                    <td className="font-bold">{clo.code}</td>
                                    {[1,2,3,4,5,6,7].map(n => <td key={n}>{map[`PLO${n}`] || ""}</td>)}
                                </tr>
                             )
                        })}
                    </tbody>
                </table>
            </div>

            {/* 5. NHIỆM VỤ */}
            <div className="mb-4">
                <h3 className="font-bold mb-1">5. Nhiệm vụ của sinh viên (Students duties)</h3>
                <div className="whitespace-pre-line pl-4">{syllabus.studentDuties}</div>
            </div>

            {/* 6. ĐÁNH GIÁ */}
            <div className="mb-4 print-break-avoid">
                <h3 className="font-bold mb-1">6. Phương pháp kiểm tra, đánh giá (Assessment methods):</h3>
                <p className="mb-2">Phương pháp kiểm tra đánh giá của HP đảm bảo người học đạt được CĐR mong đợi</p>
                <table className="word-table">
                    <thead>
                        <tr className="bg-gray-100 font-bold text-center">
                            <td>Thành phần đánh giá</td><td>Phương pháp/ Hình thức đánh giá</td><td>CĐR HP (CLOs)</td><td>Tiêu chí đánh giá</td><td>Trọng số (%)</td>
                        </tr>
                    </thead>
                    <tbody>
                        {syllabus.assessmentScheme.map((item, i) => (
                             <tr key={i} className="text-center">
                                 <td className="text-left">{item.component}</td><td className="text-left">{item.method}</td><td>{item.clos}</td><td>{item.criteria}</td><td>{item.weight}</td>
                             </tr>
                        ))}
                        <tr className="font-bold text-center"><td colSpan={4}>Tổng cộng</td><td>100</td></tr>
                    </tbody>
                </table>
            </div>

            {/* 7. KẾ HOẠCH */}
            <div className="mb-4">
                <h3 className="font-bold mb-2">7. Kế hoạch giảng dạy và học tập (Teaching and learning plan/outline)</h3>
                <table className="word-table">
                    <thead>
                        <tr className="bg-gray-100 font-bold text-center">
                            <td className="w-[10%]">Tuần / Chương</td><td className="w-[40%]">Nội dung</td><td className="w-[10%]">CLOs</td><td className="w-[25%]">Hoạt động dạy và học</td><td className="w-[15%]">Dạng bài đánh giá</td>
                        </tr>
                    </thead>
                    <tbody>
                         <tr className="font-bold bg-gray-50"><td colSpan={5}>PHẦN LÝ THUYẾT</td></tr>
                        {syllabus.teachingPlan.map((row, i) => (
                            <tr key={i}>
                                <td className="text-center">{row.week}</td><td className="whitespace-pre-line">{row.topic}</td><td className="text-center">{row.clos}</td><td className="text-center whitespace-pre-line">{row.activity}</td><td className="text-center">{row.assessment}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* 8. TÀI LIỆU */}
            <div className="mb-4 print-break-avoid">
                <h3 className="font-bold mb-1">8. Tài liệu học tập (Course materials)</h3>
                <div className="font-bold pl-0">8.1. Tài liệu chính (Main materials)</div>
                <div className="pl-4 mb-2">
                    {syllabus.materials.filter(m => m.type === 'Main').map((m, i) => <div key={i}>[{i+1}] {m.title}</div>)}
                </div>
                <div className="font-bold pl-0">8.2. Tài liệu tham khảo (References materials)</div>
                <div className="pl-4">
                    {syllabus.materials.filter(m => m.type === 'Ref').map((m, i) => <div key={i}>[{i+1}] {m.title}</div>)}
                </div>
            </div>

            {/* 9. YÊU CẦU KHÁC (ĐÃ CÓ) */}
            <div className="mb-4">
                 <h3 className="font-bold mb-1">9. Yêu cầu khác về học phần (Other course requirements and expectations)</h3>
                 <div className="pl-4 whitespace-pre-line">{syllabus.otherRequirements || "Không"}</div>
            </div>

            {/* 10. CHỮ KÝ */}
            <div className="mb-4 print-break-avoid">
                <h3 className="font-bold mb-2">10. Biên soạn và cập nhật đề cương</h3>
                <div className="pl-4">
                    <div>- Ngày biên soạn lần đầu: {syllabus.datePrepared}</div>
                    <div>- Ngày chỉnh sửa: {syllabus.dateEdited}</div>
                </div>
                
                <table className="w-full mt-6 text-center font-bold border-none uppercase">
                    <tbody>
                        <tr><td className="w-1/3 align-top pb-24">PHÒNG ĐÀO TẠO</td><td className="w-1/3 align-top pb-24">QUẢN LÝ CTĐT</td><td className="w-1/3 align-top pb-24">GV LẬP ĐỀ CƯƠNG</td></tr>
                        <tr><td></td><td>(Đã ký)</td><td>(Đã ký)</td></tr>
                        <tr><td></td><td>{syllabus.dean}</td><td>{syllabus.lecturer}</td></tr>
                    </tbody>
                </table>
            </div>

        </div>
      </div>
    </div>
  );
}
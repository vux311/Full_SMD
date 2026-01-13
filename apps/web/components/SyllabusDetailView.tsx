"use client";

import React, { useRef } from "react";
import Link from "next/link";
import { useReactToPrint } from "react-to-print";
import { Printer, ArrowLeft, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
// QUAN TRỌNG: Import đúng đường dẫn
import { SyllabusData } from "./Types"; 

export default function SyllabusDetailView({ syllabus }: { syllabus: SyllabusData }) {
  const contentRef = useRef<HTMLDivElement>(null);
  
  const handlePrint = useReactToPrint({
    contentRef: contentRef,
    documentTitle: `${syllabus.subjectCode}_Syllabus`,
  });

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
         <Link href="/"><Button variant="ghost"><ArrowLeft className="mr-2 h-4 w-4" /> Quay lại</Button></Link>
         <div className="flex gap-2">
            <Link href={`/syllabus/${syllabus.id}/edit`}><Button variant="outline"><Pencil className="mr-2 h-4 w-4" /> Chỉnh sửa</Button></Link>
            <Button onClick={() => handlePrint()}><Printer className="mr-2 h-4 w-4" /> Xuất PDF / In</Button>
         </div>
      </div>

      <div className="flex justify-center">
        <div ref={contentRef} className="bg-white w-[210mm] min-h-[297mm] px-[15mm] py-[15mm] shadow-lg print:shadow-none text-black leading-snug" style={{ fontFamily: '"Times New Roman", Times, serif', fontSize: '12pt' }}>
            
            <div className="text-center font-bold mb-4">
                <div className="uppercase text-[11pt]">TRƯỜNG ĐH GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH</div>
                <div className="uppercase text-[14pt] mt-2">ĐỀ CƯƠNG CHI TIẾT HỌC PHẦN</div>
                <div className="italic font-normal text-[12pt]">(COURSE SYLLABUS)</div>
            </div>

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
                                <td className="text-center">{row.week}</td><td className="whitespace-pre-line">{row.content}</td><td className="text-center">{row.clos}</td><td className="text-center whitespace-pre-line">{row.activity}</td><td className="text-center">{row.assessment}</td>
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
                    {syllabus.materials.filter(m => m.type === 'Main').map((m, i) => <div key={i}>[{i+1}] {m.content}</div>)}
                </div>
                <div className="font-bold pl-0">8.2. Tài liệu tham khảo (References materials)</div>
                <div className="pl-4">
                    {syllabus.materials.filter(m => m.type === 'Ref').map((m, i) => <div key={i}>[{i+1}] {m.content}</div>)}
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
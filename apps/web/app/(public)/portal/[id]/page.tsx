import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import SyllabusDetailView from "@/components/SyllabusDetailView";
import StudentActionButtons from "@/components/StudentActionButtons";
import { SyllabusData, defaultSyllabus } from "@/components/Types";

export default async function StudentViewPage(props: { params: Promise<{ id: string }> }) {
  const { id } = await props.params;

  try {
    // Gọi API lấy chi tiết đề cương (SỬA: sử dụng endpoint public để lọc trạng thái Approved/Published)
    // Sử dụng API_URL (nội bộ docker) nếu có, fallback về NEXT_PUBLIC_API_URL
    const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";
    const res = await fetch(`${apiUrl}/public/syllabus/${id}`, { cache: "no-store" });

    if (!res.ok) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
                <div className="text-xl font-bold text-gray-500">Không tìm thấy đề cương này.</div>
                <Link href="/portal"><Button>Quay lại trang chủ</Button></Link>
            </div>
        );
    }

    const rawData = await res.json();
    
    // Merge dữ liệu an toàn (convert backend camelCase to frontend camelCase model)
    const syllabus: SyllabusData = {
        ...defaultSyllabus,
        ...rawData,
        objectives: rawData.objectives || [],
        clos: rawData.clos || [],
        
        // Chuyển đổi ploMapping từ cấu trúc lồng nhau của backend
        ploMapping: Array.isArray(rawData.clos) 
            ? rawData.clos.map((clo: any) => {
                const plos: { [key: string]: string } = {};
                const mappings = clo.ploMappings || [];
                if (Array.isArray(mappings)) {
                    mappings.forEach((m: any) => {
                        const code = m.programPloCode;
                        if (code) plos[code] = m.level;
                    });
                }
                return { cloCode: clo.code, plos };
            })
            : [],

        // Chuyển đổi assessmentScheme từ cấu trúc đa cấp (Scheme -> Component)
        assessmentScheme: Array.isArray(rawData.assessmentSchemes)
            ? rawData.assessmentSchemes.flatMap((scheme: any) => 
                (scheme.components || []).map((comp: any) => ({
                    component: scheme.name,
                    method: comp.name,
                    clos: Array.isArray(comp.clos) 
                        ? comp.clos.map((ac: any) => ac.syllabusCloCode).filter(Boolean).join(', ') 
                        : (comp.cloIds || ''),
                    criteria: comp.criteria || (comp.rubrics && comp.rubrics.length > 0 ? comp.rubrics[0].criteria : ''),
                    weight: comp.weight
                }))
              )
            : [],

        teachingPlan: rawData.teachingPlans || [],
        materials: rawData.materials || [],
        timeAllocation: rawData.timeAllocation || { theory: 0, exercises: 0, practice: 0, selfStudy: 0 }
    };

    return (
        <div className="container mx-auto pb-10 max-w-6xl px-4">
            {/* Nút quay lại & Actions */}
            <div className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 py-4 border-b">
                <Link href="/portal">
                    <Button variant="ghost" className="gap-2 hover:bg-slate-100 text-slate-600">
                        <ArrowLeft className="w-4 h-4" /> Quay lại tìm kiếm
                    </Button>
                </Link>

                <div className="w-full md:w-auto min-w-[320px]">
                    {/* Giữ ActionButtons ở đây để giao diện portal chuyên nghiệp hơn */}
                    <StudentActionButtons 
                        syllabusId={syllabus.id!} 
                        subjectId={syllabus.subjectId!} 
                        subjectCode={syllabus.subjectCode} 
                    />
                </div>
            </div>

            {/* Hiển thị nội dung đề cương */}
            <div className="bg-white shadow-xl rounded-xl border-t-4 border-teal-600 overflow-hidden">
                <SyllabusDetailView 
                    syllabus={syllabus} 
                    hideManagementButtons={true} 
                    hideStudentActions={true} 
                />
            </div>
        </div>
    );

  } catch (err) {
    return <div className="p-12 text-center text-red-500">Lỗi kết nối server. Vui lòng thử lại sau.</div>;
  }
}
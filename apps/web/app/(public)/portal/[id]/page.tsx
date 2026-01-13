import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import SyllabusDetailView from "@/components/SyllabusDetailView";
import { SyllabusData, defaultSyllabus } from "@/components/Types";

export default async function StudentViewPage(props: { params: Promise<{ id: string }> }) {
  const { id } = await props.params;

  try {
    // Gọi API lấy chi tiết đề cương (use public env var and plural resource)
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/syllabuses/${id}`, { cache: "no-store" });

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
        ploMapping: rawData.ploMapping || [],
        assessmentScheme: rawData.assessmentScheme || [],
        teachingPlan: rawData.teachingPlan || [],
        materials: rawData.materials || [],
        timeAllocation: rawData.timeAllocation || { theory: 0, exercises: 0, practice: 0, selfStudy: 0 }
    };

    return (
        <div className="container mx-auto pb-10">
            {/* Nút quay lại */}
            <div className="mb-6">
                <Link href="/portal">
                    <Button variant="outline" className="gap-2 bg-white hover:bg-slate-100">
                        <ArrowLeft className="w-4 h-4" /> Quay lại tìm kiếm
                    </Button>
                </Link>
            </div>

            {/* Hiển thị nội dung đề cương */}
            <div className="bg-white shadow-sm rounded-lg border overflow-hidden">
                <SyllabusDetailView syllabus={syllabus} />
            </div>
        </div>
    );

  } catch (err) {
    return <div className="p-12 text-center text-red-500">Lỗi kết nối server. Vui lòng thử lại sau.</div>;
  }
}
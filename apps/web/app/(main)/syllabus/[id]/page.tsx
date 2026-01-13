// import Link from "next/link";
// import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
// import SyllabusDetailView from "@/components/SyllabusDetailView"; // Import component vừa tạo

// interface Syllabus {
//   id: number;
//   subject_name: string;
//   subject_code: string;
//   credits: number;
//   description?: string;
//   clos?: Array<{ code: string; description: string }>;
// }

// export default async function Page(props: { params: Promise<{ id: string }> }) {
//   const { id } = await props.params;

//   if (!id) return renderNotFound();

//   try {
//     // Server-side example using environment variable:
//     // const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/syllabuses/${id}`, { cache: "no-store" });

//     if (res.status === 404) return renderNotFound();
    
//     if (!res.ok) {
//       console.error("Failed to fetch syllabus", res.status);
//       return renderError();
//     }

//     const syllabus: Syllabus = await res.json();

//     // Render component giao diện (Client Component)
//     return <SyllabusDetailView syllabus={syllabus} />;

//   } catch (err) {
//     console.error("Error fetching syllabus:", err);
//     return renderError();
//   }
// }

// // --- Các hàm render lỗi giữ nguyên ---

// function renderNotFound() {
//   return (
//     <div className="flex items-center justify-center p-12">
//       <Card className="w-full max-w-md text-center">
//         <CardHeader>
//           <CardTitle className="text-xl">Syllabus not found</CardTitle>
//         </CardHeader>
//         <CardContent>
//           <p className="text-sm text-muted-foreground mb-4">The requested syllabus does not exist or has been removed.</p>
//           <Link className="text-sm font-medium text-primary hover:underline" href="/">Back to Dashboard</Link>
//         </CardContent>
//       </Card>
//     </div>
//   );
// }

// function renderError() {
//   return (
//     <div className="flex items-center justify-center p-12">
//       <Card className="w-full max-w-md text-center border-destructive/50">
//         <CardHeader>
//           <CardTitle className="text-xl text-destructive">Unable to load</CardTitle>
//         </CardHeader>
//         <CardContent>
//           <p className="text-sm text-muted-foreground mb-4">There was an error loading the details. Please ensure the backend server is running.</p>
//           <Link className="text-sm font-medium text-primary hover:underline" href="/">Back to Dashboard</Link>
//         </CardContent>
//       </Card>
//     </div>
//   );
// }

import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import SyllabusDetailView from "@/components/SyllabusDetailView";
// Import Type từ file types (nếu anh đã tạo) hoặc định nghĩa trực tiếp ở đây để nhanh gọn
import { SyllabusData, defaultSyllabus } from "@/components/Types"; 

// Nếu anh chưa tạo file types.ts, hãy uncomment đoạn dưới đây để dùng tạm:
/*
interface SyllabusData {
  id?: number;
  subject_name_vi: string;
  subject_name_en: string;
  subject_code: string;
  credits: number;
  time_allocation: { theory: number; exercises: number; practice: number; self_study: number; };
  prerequisites: string; pre_courses: string; co_courses: string;
  course_type: string; component_type: string;
  description: string;
  objectives: string[];
  clos: { code: string; description: string }[];
  plo_mapping: { clo_code: string; plos: { [key: string]: string } }[];
  student_duties: string;
  assessment_scheme: { component: string; method: string; clos: string; criteria: string; weight: number; }[];
  teaching_plan: { week: string; content: string; clos: string; activity: string; assessment: string; }[];
  materials: { type: "Main" | "Ref"; content: string; }[];
  date_prepared: string; date_edited: string; lecturer: string; head_department: string; dean: string;
}
*/

export default async function Page(props: { params: Promise<{ id: string }> }) {
  const { id } = await props.params;

  if (!id) return renderNotFound();

  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/syllabuses/${id}`, { cache: "no-store" });

    if (res.status === 404) return renderNotFound();
    
    if (!res.ok) {
      console.error("Failed to fetch syllabus", res.status);
      return renderError();
    }

    const rawData = await res.json();

    // MERGE dữ liệu từ API với dữ liệu mặc định để tránh lỗi "undefined" khi render
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

    return <SyllabusDetailView syllabus={syllabus} />;

  } catch (err) {
    console.error("Error fetching syllabus:", err);
    return renderError();
  }
}

function renderNotFound() {
  return (
    <div className="flex items-center justify-center p-12">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle className="text-xl">Syllabus not found</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">The requested syllabus does not exist or has been removed.</p>
          <Link className="text-sm font-medium text-primary hover:underline" href="/">Back to Dashboard</Link>
        </CardContent>
      </Card>
    </div>
  );
}

function renderError() {
  return (
    <div className="flex items-center justify-center p-12">
      <Card className="w-full max-w-md text-center border-destructive/50">
        <CardHeader>
          <CardTitle className="text-xl text-destructive">Unable to load</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">There was an error loading the details. Please ensure the backend server is running.</p>
          <Link className="text-sm font-medium text-primary hover:underline" href="/">Back to Dashboard</Link>
        </CardContent>
      </Card>
    </div>
  );
}
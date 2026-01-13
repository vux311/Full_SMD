import React from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import SyllabusEditForm from "@/components/SyllabusEditForm";
import { SyllabusData, defaultSyllabus } from "@/components/Types";

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

    // Merge dữ liệu API với dữ liệu mặc định để tránh lỗi undefined
    const syllabus: SyllabusData = {
        ...defaultSyllabus,
        ...rawData,
        objectives: Array.isArray(rawData.objectives) ? rawData.objectives : [],
        clos: Array.isArray(rawData.clos) ? rawData.clos : [],
        ploMapping: Array.isArray(rawData.ploMapping) ? rawData.ploMapping : [],
        assessmentScheme: Array.isArray(rawData.assessmentScheme) ? rawData.assessmentScheme : [],
        teachingPlan: Array.isArray(rawData.teachingPlan) ? rawData.teachingPlan : [],
        materials: Array.isArray(rawData.materials) ? rawData.materials : [],
        timeAllocation: rawData.timeAllocation || defaultSyllabus.timeAllocation
    };

    return <SyllabusEditForm initial={syllabus} />;

  } catch (err) {
    console.error("Error fetching syllabus:", err);
    return renderError();
  }
}

function renderNotFound() {
    return (
        <div className="flex items-center justify-center min-h-[50vh]">
            <Card className="w-full max-w-md text-center p-6">
                <CardHeader>
                    <CardTitle className="text-xl">Không tìm thấy đề cương</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-muted-foreground mb-4">Đề cương này không tồn tại hoặc đã bị xóa.</p>
                    <Link href="/" className="text-blue-600 hover:underline">Quay về trang chủ</Link>
                </CardContent>
            </Card>
        </div>
    );
}

function renderError() {
    return (
        <div className="flex items-center justify-center min-h-[50vh]">
            <Card className="w-full max-w-md text-center p-6 border-red-200 bg-red-50">
                <CardHeader>
                    <CardTitle className="text-xl text-red-600">Lỗi kết nối</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-red-500 mb-4">Không thể tải dữ liệu từ Backend. Vui lòng kiểm tra lại server API.</p>
                    <Link href="/" className="text-red-700 font-bold hover:underline">Quay về trang chủ</Link>
                </CardContent>
            </Card>
        </div>
    );
}
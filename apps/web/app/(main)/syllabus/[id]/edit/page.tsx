"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import SyllabusEditForm from "@/components/SyllabusEditForm";
import { SyllabusData, defaultSyllabus } from "@/components/Types";
import axios from "@/lib/axios";

export default function Page() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [syllabus, setSyllabus] = useState<SyllabusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setError("not_found");
      setLoading(false);
      return;
    }

    const fetchSyllabus = async () => {
      try {
        const res = await axios.get(`/syllabuses/${id}/details`);
        const rawData = res.data;

        // Map backend plural names to frontend singular names used in Types.ts/Form
        const syllabusData: SyllabusData = {
            ...defaultSyllabus,
            id: rawData.id,
            subjectId: rawData.subjectId,
            program_id: rawData.programId,
            academicYearId: rawData.academicYearId,
            lecturerId: rawData.lecturerId,
            status: rawData.status || "Draft",
            version: rawData.version || "1.0",
            
            // Content fields
            description: rawData.description || "",
            objectives: Array.isArray(rawData.objectives) ? rawData.objectives : [],
            studentDuties: rawData.studentDuties || "",
            otherRequirements: rawData.otherRequirements || "",
            
            // Foreign Keys for Dropdowns (already mapped to camelCase by axios interceptor)
            headDepartmentId: rawData.headDepartmentId,
            deanId: rawData.deanId,
            
            // Additional metadata
            preCourses: rawData.preCourses || "",
            coCourses: rawData.coCourses || "",
            courseType: rawData.courseType || "Bắt buộc",
            componentType: rawData.componentType || "",
            datePrepared: rawData.datePrepared || "",
            dateEdited: rawData.dateEdited || "",
            dean: rawData.dean || "",
            headDepartment: rawData.headDepartment || "",
            
            // These come from Subject relationship (read-only display)
            // Robust check to handle both flattened and nested objects from backend
            subjectNameVi: typeof rawData.subjectNameVi === 'object' ? rawData.subjectNameVi?.nameVi : (rawData.subjectNameVi || ""),
            subjectNameEn: typeof rawData.subjectNameEn === 'object' ? rawData.subjectNameEn?.nameEn : (rawData.subjectNameEn || ""),
            subjectCode: typeof rawData.subjectCode === 'object' ? rawData.subjectCode?.code : (rawData.subjectCode || ""),
            credits: typeof rawData.credits === 'object' ? rawData.credits?.credits : (rawData.credits || 3),
            lecturer: typeof rawData.lecturer === 'object' ? rawData.lecturer?.fullName : (rawData.lecturer || ""),
            
            // Arrays - Backend plural vs Frontend singular
            clos: Array.isArray(rawData.clos) ? rawData.clos : [],
            ploMapping: Array.isArray(rawData.clos) 
                ? rawData.clos.map((clo: any) => {
                    const plos: { [key: string]: string } = {};
                    if (Array.isArray(clo.ploMappings)) {
                        clo.ploMappings.forEach((m: any) => {
                            if (m.programPloCode) plos[m.programPloCode] = m.level;
                        });
                    }
                    return { cloCode: clo.code, plos };
                })
                : [],
            
            // Mapping Assessment Systems
            assessmentScheme: Array.isArray(rawData.assessmentSchemes) && rawData.assessmentSchemes.length > 0 
                ? (rawData.assessmentSchemes[0].components || []).map((c: any) => ({
                    component: c.name || "",
                    weight: c.weight || 0,
                    method: c.method || "Tự luận",
                    criteria: c.criteria || "Theo đáp án",
                    // Map nested CLO objects back to string for the form
                    clos: Array.isArray(c.clos) 
                      ? c.clos.map((cls: any) => cls.syllabusCloCode || cls.syllabus_clo_code).join(", ") 
                      : (c.cloIds || "")
                }))
                : [],
                
            // Mapping Teaching Plans
            teachingPlan: Array.isArray(rawData.teachingPlans) 
                ? rawData.teachingPlans.map((p: any) => ({
                    week: p.week || 0,
                    topic: p.topic || "",
                    activity: p.activity || "",
                    assessment: p.assessment || "",
                    clos: Array.isArray(p.clos) ? p.clos.join(", ") : (p.clos || "")
                }))
                : [],
                
            materials: Array.isArray(rawData.materials) ? rawData.materials : [],
            timeAllocation: (() => {
                let ta = rawData.timeAllocation;
                if (typeof ta === 'string') {
                    try { ta = JSON.parse(ta); } catch(e) { ta = defaultSyllabus.timeAllocation; }
                }
                return ta || defaultSyllabus.timeAllocation;
            })(),
            prerequisites: rawData.prerequisites || "",
        };

        setSyllabus(syllabusData);
        setLoading(false);

      } catch (err: any) {
        console.error("Error fetching syllabus:", err);
        if (err?.response?.status === 404) {
          setError("not_found");
        } else if (err?.response?.status === 401) {
          router.push("/login");
        } else {
          setError("error");
        }
        setLoading(false);
      }
    };

    fetchSyllabus();
  }, [id, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Đang tải đề cương...</p>
        </div>
      </div>
    );
  }

  if (error === "not_found") {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Card className="w-full max-w-md text-center p-6">
          <CardHeader>
            <CardTitle className="text-xl">Không tìm thấy đề cương</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">Đề cương này không tồn tại hoặc đã bị xóa.</p>
            <Link href="/dashboard" className="text-primary hover:underline">Quay về Dashboard</Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Card className="w-full max-w-md text-center p-6 border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-xl text-red-600">Lỗi kết nối</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-600 mb-4">Không thể tải dữ liệu đề cương. Vui lòng thử lại sau.</p>
            <Link href="/dashboard" className="text-primary hover:underline">Quay về Dashboard</Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!syllabus) return null;

  return <SyllabusEditForm initial={syllabus} />;
}
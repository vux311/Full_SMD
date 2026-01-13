"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, BookOpen, User, Clock, GraduationCap, Loader2 } from "lucide-react";

interface SyllabusPublic {
  id: number;
  subjectNameVi: string;
  subjectNameEn: string;
  subjectCode: string;
  credits: number;
  lecturer: string;
  version: string;
  description: string;
  dateEdited: string;
}

export default function StudentHomePage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [results, setResults] = useState<SyllabusPublic[]>([]);
  const [loading, setLoading] = useState(false);
  const [debouncedTerm, setDebouncedTerm] = useState(searchTerm);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedTerm(searchTerm), 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  useEffect(() => {
    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/public/syllabus?search=${encodeURIComponent(debouncedTerm)}`);
            const data = await res.json();
            setResults(data.data || []);
        } catch(e) { console.error(e); } 
        finally { setLoading(false); }
    };
    fetchData();
  }, [debouncedTerm]);

  return (
    <div className="space-y-12 pb-20">
      {/* ĐỔI GRADIENT BACKGROUND */}
      <div className="text-center space-y-6 py-16 bg-gradient-to-b from-teal-50 to-white rounded-3xl border border-teal-100 px-4">
        <div className="inline-flex items-center px-3 py-1 rounded-full bg-teal-100 text-teal-700 text-xs font-bold mb-2">
            <GraduationCap className="w-4 h-4 mr-2"/> Cổng thông tin Đào tạo
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight">Tra cứu Đề cương Học phần</h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">Hệ thống dữ liệu số hóa chính thức. Tìm kiếm thông tin chi tiết, chuẩn đầu ra và tài liệu học tập mới nhất.</p>
        
        <div className="max-w-xl mx-auto relative mt-8">
            <Search className="absolute left-4 top-3.5 h-5 w-5 text-teal-500" />
            <Input 
                className="pl-12 h-12 text-lg shadow-xl border-teal-100 focus-visible:ring-teal-500 rounded-full transition-all" 
                placeholder="Nhập mã môn (VD: IT001) hoặc tên môn học..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            {loading && <div className="absolute right-4 top-4"><Loader2 className="w-4 h-4 animate-spin text-gray-400"/></div>}
        </div>
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6 px-2">
            <h2 className="text-xl font-bold text-slate-800">{searchTerm ? `Kết quả tìm kiếm cho "${searchTerm}"` : "Đề cương mới cập nhật"}</h2>
            <span className="text-sm text-slate-500">{results.length} kết quả</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {loading && results.length === 0 ? ([1,2,3].map(i => <div key={i} className="h-64 bg-gray-100 rounded-xl animate-pulse"></div>)) : results.length === 0 ? (
                <div className="col-span-full text-center py-16 text-gray-400 italic bg-slate-50 rounded-xl border border-dashed">Không tìm thấy đề cương nào phù hợp.</div>
            ) : (
                results.map((item) => (
                    /* ĐỔI BORDER TOP CARD */
                    <Card key={item.id} className="group hover:shadow-lg transition-all duration-300 border-t-4 border-t-teal-500 flex flex-col h-full">
                        <CardHeader className="pb-3">
                            <div className="flex justify-between items-start mb-2">
                                <Badge variant="secondary" className="bg-teal-50 text-teal-700 hover:bg-teal-100 border-teal-200 font-mono">{item.subjectCode}</Badge>
                                <span className="text-[10px] font-bold bg-green-100 text-green-700 px-2 py-0.5 rounded-full border border-green-200">v{item.version}</span>
                            </div>
                            <CardTitle className="text-lg leading-snug group-hover:text-teal-700 transition-colors min-h-[3.5rem] line-clamp-2">{item.subjectNameVi}</CardTitle>
                            <p className="text-xs text-muted-foreground line-clamp-1 italic">{item.subjectNameEn}</p>
                        </CardHeader>
                        <CardContent className="flex-1 pb-4">
                            <p className="text-sm text-gray-600 line-clamp-3 mb-4 h-[4.5em]">{item.description || "Chưa có mô tả tóm tắt cho học phần này."}</p>
                            <div className="space-y-2 pt-4 border-t border-dashed">
                                <div className="flex items-center gap-2 text-xs text-gray-500"><BookOpen className="w-3.5 h-3.5 text-teal-500" /> <span className="font-medium">{item.credits} tín chỉ</span></div>
                                <div className="flex items-center gap-2 text-xs text-gray-500"><User className="w-3.5 h-3.5 text-purple-500" /> <span>GV: {item.lecturer}</span></div>
                                <div className="flex items-center gap-2 text-xs text-gray-500"><Clock className="w-3.5 h-3.5 text-orange-500" /> <span>Cập nhật: {item.dateEdited}</span></div>
                            </div>
                        </CardContent>
                        <CardFooter className="pt-0 pb-6 px-6">
                            <Link href={`/portal/${item.id}`} className="w-full">
                                {/* ĐỔI NÚT ACTION */}
                                <Button className="w-full bg-teal-700 hover:bg-teal-800 text-white transition-colors shadow-lg shadow-teal-100">Xem chi tiết</Button>
                            </Link>
                        </CardFooter>
                    </Card>
                ))
            )}
        </div>
      </div>
    </div>
  );
}
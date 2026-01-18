"use client";

import React, { useEffect, useState } from "react";
import axios from "@/lib/axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowDown, ArrowUp, Link2, Loader2, BookOpen } from "lucide-react";

interface TreeNode {
  relatedSubjectId?: number;
  subjectId?: number;
  relatedSubjectCode?: string;
  subjectCode?: string;
  relatedSubjectName?: string;
  subjectName?: string;
  type: string;
}

export default function VisualSubjectTree({ subjectId, currentSubjectName }: { subjectId: number, currentSubjectName: string }) {
  const [data, setData] = useState<{ prerequisites: TreeNode[], successors: TreeNode[] } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTree = async () => {
      try {
        const res = await axios.get(`/subject-relationships/tree/${subjectId}`);
        setData(res.data);
      } catch (err) {
        console.error("Error fetching subject tree:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTree();
  }, [subjectId]);

  if (loading) return <div className="flex justify-center p-8"><Loader2 className="animate-spin text-teal-600" /></div>;
  if (!data || (data.prerequisites.length === 0 && data.successors.length === 0)) {
    return (
        <div className="text-center p-8 text-slate-400 italic bg-slate-50 rounded-xl border border-dashed">
            Môn học này không có học phần liên quan (tiên quyết/song hành) được khai báo.
        </div>
    );
  }

  return (
    <div className="space-y-4 py-4">
      <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 mb-4">
        <Link2 className="w-5 h-5 text-teal-600" /> Bản đồ môn học (Subject Pathway)
      </h3>

      <div className="flex flex-col items-center gap-6">
        {/* Prerequisites */}
        {data.prerequisites.length > 0 && (
          <div className="w-full">
            <div className="flex flex-wrap justify-center gap-3">
              {data.prerequisites.map((item, i) => (
                <div key={i} className="flex flex-col items-center">
                    <Card className="bg-amber-50 border-amber-200 min-w-[150px] shadow-sm">
                        <CardContent className="p-3 text-center">
                            <div className="text-[10px] font-bold text-amber-600 uppercase mb-1">{item.type}</div>
                            <div className="font-bold text-sm">{item.relatedSubjectCode}</div>
                            <div className="text-[11px] text-slate-600 line-clamp-1">{item.relatedSubjectName}</div>
                        </CardContent>
                    </Card>
                    <ArrowDown className="text-amber-400 w-4 h-4 mt-2" />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Current Subject */}
        <div className="relative">
            <Card className="bg-teal-600 text-white border-teal-700 w-[220px] shadow-lg ring-4 ring-teal-100">
                <CardContent className="p-4 text-center">
                    <BookOpen className="w-6 h-6 mx-auto mb-2 opacity-80" />
                    <div className="font-bold">{currentSubjectName}</div>
                    <div className="text-xs opacity-80 mt-1">(Đang xem)</div>
                </CardContent>
            </Card>
        </div>

        {/* Successors */}
        {data.successors.length > 0 && (
          <div className="w-full">
            <div className="flex flex-wrap justify-center gap-3">
              {data.successors.map((item, i) => (
                <div key={i} className="flex flex-col items-center">
                    <ArrowDown className="text-blue-400 w-4 h-4 mb-2" />
                    <Card className="bg-blue-50 border-blue-200 min-w-[150px] shadow-sm">
                        <CardContent className="p-3 text-center">
                            <div className="text-[10px] font-bold text-blue-600 uppercase mb-1">MÔN TIẾP THEO</div>
                            <div className="font-bold text-sm">{item.subjectCode}</div>
                            <div className="text-[11px] text-slate-600 line-clamp-1">{item.subjectName}</div>
                        </CardContent>
                    </Card>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

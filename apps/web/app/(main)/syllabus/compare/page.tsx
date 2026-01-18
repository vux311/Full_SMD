"use client";

import React, { useEffect, useState } from "react";
import axios from "@/lib/axios";
import { useSearchParams, useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Sparkles, Scale, Info, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface DiffItem {
  field: string;
  old_value: string;
  new_value: string;
  type: string;
}

interface AiReport {
    summary?: string;
    impact_assessment?: string;
    is_significant_change?: boolean;
    detailed_analysis?: { category: string; description: string; change_type: string }[];
    error?: string;
}

export default function ComparePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const baseId = searchParams.get("baseId");
  const targetId = searchParams.get("targetId");

  const [data, setData] = useState<{ 
    base_version: string; 
    target_version: string; 
    diffs: DiffItem[];
    ai_report?: AiReport;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDiff = async () => {
      if (!baseId || !targetId) return;

      try {
        const query = new URLSearchParams({ base_id: baseId, target_id: targetId }).toString();
        const res = await axios.get(`/syllabus/compare?${query}`);
        const data = res.data;
        setData(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchDiff();
  }, [baseId, targetId]);

  if (!baseId || !targetId) return <div className="p-8 text-center">Missing IDs to compare</div>;
  if (loading) return <div className="p-8 text-center">Analyzing changes...</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => router.back()}><ArrowLeft className="w-4 h-4 mr-2"/> Back</Button>
        <h1 className="text-2xl font-bold">So sánh Phiên bản</h1>
      </div>

      <div className="grid grid-cols-2 gap-4">
         <Card className="bg-slate-50 border-slate-200 shadow-sm">
            <CardHeader className="py-3 px-4 bg-slate-100/50 border-b">
                <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Phiên bản gốc (v{data?.base_version})</CardTitle>
            </CardHeader>
         </Card>
         <Card className="bg-teal-50 border-teal-200 shadow-sm">
            <CardHeader className="py-3 px-4 bg-teal-100/50 border-b">
                <CardTitle className="text-sm font-bold text-teal-600 uppercase tracking-wider">Phiên bản mới (v{data?.target_version})</CardTitle>
            </CardHeader>
         </Card>
      </div>

      {/* AI CHANGE DETECTION REPORT */}
      {data?.ai_report && !data.ai_report.error && (
          <Card className="border-teal-200 bg-gradient-to-br from-teal-50 to-white overflow-hidden shadow-md">
              <CardHeader className="bg-teal-600 text-white py-3 flex flex-row items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  <CardTitle className="text-lg">AI Change Detection & Impact Analysis</CardTitle>
                  {data.ai_report.is_significant_change && (
                      <Badge className="ml-auto bg-amber-400 text-amber-900 border-none">Thay đổi đáng kể</Badge>
                  )}
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                  {data.ai_report.summary && (
                      <div className="bg-white p-4 rounded-lg border border-teal-100 shadow-sm">
                          <h3 className="font-bold text-teal-800 flex items-center gap-2 mb-2">
                              <Info className="w-4 h-4" /> Tóm tắt thay đổi
                          </h3>
                          <p className="text-slate-700 leading-relaxed">{data.ai_report.summary}</p>
                      </div>
                  )}

                  <div className="grid md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <h3 className="font-bold text-slate-800 flex items-center gap-2">
                            <Scale className="w-4 h-4 text-teal-600" /> Phân tích chi tiết
                        </h3>
                        <div className="space-y-3">
                            {data.ai_report.detailed_analysis?.map((item, idx) => (
                                <div key={idx} className="p-3 bg-white rounded-md border border-slate-100 shadow-sm text-sm">
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="font-bold text-slate-700">{item.category}</span>
                                        <Badge variant="outline" className="text-[10px] py-0">{item.change_type}</Badge>
                                    </div>
                                    <p className="text-slate-500 text-xs">{item.description}</p>
                                </div>
                            ))}
                        </div>
                      </div>

                      <div className="bg-amber-50/50 p-4 rounded-lg border border-amber-100 self-start">
                          <h3 className="font-bold text-amber-800 flex items-center gap-2 mb-2">
                              <CheckCircle2 className="w-4 h-4" /> Đánh giá tác động
                          </h3>
                          <p className="text-amber-900/80 text-sm whitespace-pre-line leading-relaxed italic">
                              "{data.ai_report.impact_assessment}"
                          </p>
                      </div>
                  </div>
              </CardContent>
          </Card>
      )}

      {data?.ai_report?.error && (
          <div className="p-4 bg-red-50 text-red-600 rounded-lg border border-red-100 text-sm italic">
            ⚠️ AI Analysis: {data.ai_report.error}
          </div>
      )}

      <div className="space-y-4 pt-4 border-t">
        <h2 className="text-xl font-bold text-slate-700">Dữ liệu thô (Field Comparison)</h2>
        {data?.diffs.length === 0 ? (
            <Card className="p-8 text-center text-green-600 font-bold border-green-200 bg-green-50">
                ✅ Không có sự thay đổi nào giữa 2 phiên bản này.
            </Card>
        ) : (
            data?.diffs.map((diff, idx) => (
                <Card key={idx} className="overflow-hidden">
                    <div className="bg-gray-100 px-4 py-2 font-mono text-sm font-bold border-b uppercase text-gray-600">
                        Field: {diff.field}
                    </div>
                    <div className="grid grid-cols-2">
                        <div className="p-4 bg-red-50 text-red-700 border-r break-words">
                            <div className="text-xs font-bold text-red-400 mb-1">OLD</div>
                            {diff.old_value}
                        </div>
                        <div className="p-4 bg-green-50 text-green-700 break-words">
                            <div className="text-xs font-bold text-green-400 mb-1">NEW</div>
                            {diff.new_value}
                        </div>
                    </div>
                </Card>
            ))
        )}
      </div>
    </div>
  );
}
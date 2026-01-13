"use client";

import React, { useEffect, useState } from "react";
import axios from "@/lib/axios";
import { useSearchParams, useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

interface DiffItem {
  field: string;
  old_value: string;
  new_value: string;
  type: string;
}

export default function ComparePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const baseId = searchParams.get("baseId");
  const targetId = searchParams.get("targetId");

  const [data, setData] = useState<{ base_version: string; target_version: string; diffs: DiffItem[] } | null>(null);
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
         <Card className="bg-slate-50 border-slate-200">
            <CardHeader><CardTitle className="text-lg text-slate-500">Phiên bản gốc (v{data?.base_version})</CardTitle></CardHeader>
         </Card>
         <Card className="bg-blue-50 border-blue-200">
            <CardHeader><CardTitle className="text-lg text-blue-600">Phiên bản mới (v{data?.target_version})</CardTitle></CardHeader>
         </Card>
      </div>

      <div className="space-y-4">
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
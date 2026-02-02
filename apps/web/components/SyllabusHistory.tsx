"use client";

import React, { useEffect, useState } from "react";
import axios from "@/lib/axios";
import { 
    Sheet, 
    SheetContent, 
    SheetHeader, 
    SheetTitle, 
    SheetTrigger,
    SheetDescription
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { History, Diff, Loader2, Calendar, User, ChevronRight, CheckCircle2, AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface SnapshotItem {
    id: number;
    version: string;
    createdAt: string;
    createdBy: string;
}

interface DiffAnalysis {
    summary: string;
    detailed_analysis: {
        category: string;
        change_type: string;
        description: string;
    }[];
    impact_assessment: string;
    is_significant_change: boolean;
}

export default function SyllabusHistory({ syllabusId }: { syllabusId: number }) {
    const [history, setHistory] = useState<SnapshotItem[]>([]);
    const [loading, setLoading] = useState(false);
    const [comparing, setComparing] = useState(false);
    const [diffResult, setDiffResult] = useState<DiffAnalysis | null>(null);
    const [selectedId, setSelectedId] = useState<number | null>(null);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`/syllabuses/${syllabusId}/history`);
            setHistory(res.data);
        } catch (err) {
            console.error("Failed to fetch history:", err);
        } finally {
            setLoading(false);
        }
    };

    const compareWithCurrent = async (snapshotId: number) => {
        setComparing(true);
        setDiffResult(null);
        setSelectedId(snapshotId);
        try {
            const res = await axios.get(`/syllabuses/compare-versions`, {
                params: {
                    s1: snapshotId,
                    s2: 'current',
                    syllabus_id: syllabusId
                }
            });
            setDiffResult(res.data);
        } catch (err) {
            console.error("Comparison failed:", err);
            alert("Lỗi khi so sánh phiên bản");
        } finally {
            setComparing(false);
        }
    };

    return (
        <Sheet>
            <SheetTrigger asChild>
                <Button variant="outline" size="sm" onClick={fetchHistory}>
                    <History className="w-4 h-4 mr-2" /> Lịch sử & So sánh
                </Button>
            </SheetTrigger>
            <SheetContent className="w-[400px] sm:w-[540px] md:w-[650px]">
                <SheetHeader>
                    <SheetTitle className="flex items-center gap-2">
                        <History className="w-5 h-5 text-blue-600" />
                        Lịch sử phiên bản đề cương
                    </SheetTitle>
                    <SheetDescription>
                        Xem lại các bản copy bất biến (Snapshot) và so sánh sự thay đổi bằng AI.
                    </SheetDescription>
                </SheetHeader>

                <div className="grid grid-cols-2 gap-4 mt-6 h-[calc(100vh-150px)]">
                    {/* Left side: History list */}
                    <div className="border-r pr-4">
                        <h4 className="font-bold text-sm mb-4 uppercase text-slate-500">Danh sách Snapshots</h4>
                        {loading ? (
                            <div className="flex justify-center p-8"><Loader2 className="animate-spin text-blue-600" /></div>
                        ) : history.length === 0 ? (
                            <div className="text-center p-8 text-slate-400 italic text-sm">Chưa có bản lưu lịch sử nào.</div>
                        ) : (
                            <div className="h-full overflow-y-auto pr-2 custom-scrollbar">
                                <div className="space-y-3">
                                    {history.map((s) => (
                                        <div 
                                            key={s.id} 
                                            className={`p-3 border rounded-lg cursor-pointer transition-colors ${selectedId === s.id ? 'bg-blue-50 border-blue-200' : 'hover:bg-slate-50'}`}
                                            onClick={() => compareWithCurrent(s.id)}
                                        >
                                            <div className="flex justify-between items-start mb-1">
                                                <Badge variant="outline">v{s.version}</Badge>
                                                <div className="text-[10px] text-slate-400 flex items-center gap-1">
                                                    <Calendar className="w-3 h-3" /> {s.createdAt && !isNaN(Date.parse(s.createdAt)) ? new Date(s.createdAt).toLocaleDateString() : 'N/A'}
                                                </div>
                                            </div>
                                            <div className="text-xs text-slate-600 flex items-center gap-1 mt-2">
                                                <User className="w-3 h-3" /> {s.createdBy}
                                            </div>
                                            <div className="mt-2 text-[11px] text-blue-600 font-medium flex items-center gap-1">
                                                So sánh với hiện tại <ChevronRight className="w-3 h-3" />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right side: Diff result */}
                    <div className="pl-2 overflow-y-auto">
                        <h4 className="font-bold text-sm mb-4 uppercase text-slate-500">So sánh (AI Analysis)</h4>
                        {comparing ? (
                            <div className="flex flex-col items-center justify-center h-48 gap-3">
                                <Loader2 className="animate-spin text-blue-600" />
                                <span className="text-xs text-slate-400 animate-pulse">AI đang phân tích sự thay đổi...</span>
                            </div>
                        ) : diffResult ? (
                            <div className="space-y-4">
                                <div className="bg-slate-100 p-3 rounded-lg text-sm border-l-4 border-blue-500 italic">
                                    "{diffResult.summary}"
                                </div>

                                {diffResult.is_significant_change && (
                                    <Badge className="bg-amber-100 text-amber-700 hover:bg-amber-100 border-amber-200 gap-1">
                                        <AlertCircle className="w-3 h-3" /> Thay đổi đáng kể
                                    </Badge>
                                )}

                                <div className="space-y-3">
                                    {diffResult.detailed_analysis.map((item, i) => (
                                        <div key={i} className="p-3 border rounded-md bg-white shadow-sm">
                                            <div className="flex justify-between items-center mb-1">
                                                <span className="font-bold text-xs text-slate-800">{item.category}</span>
                                                <Badge variant={
                                                    item.change_type === 'Added' ? 'default' : 
                                                    item.change_type === 'Removed' ? 'destructive' : 
                                                    item.change_type === 'Modified' ? 'secondary' : 'outline'
                                                } className="text-[9px] px-1 h-4">
                                                    {item.change_type}
                                                </Badge>
                                            </div>
                                            <p className="text-[11px] text-slate-600 leading-relaxed">{item.description}</p>
                                        </div>
                                    ))}
                                </div>

                                <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                                    <h5 className="text-xs font-bold text-blue-800 flex items-center gap-1 mb-1">
                                        <CheckCircle2 className="w-3 h-3" /> Đánh giá tác động:
                                    </h5>
                                    <p className="text-xs text-blue-700 leading-relaxed">{diffResult.impact_assessment}</p>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-64 text-slate-300 gap-2">
                                <Diff className="w-12 h-12 opacity-20" />
                                <span className="text-xs italic">Chọn một phiên bản để so sánh</span>
                            </div>
                        )}
                    </div>
                </div>
            </SheetContent>
        </Sheet>
    );
}

"use client";

import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Users, CheckCircle, Clock } from "lucide-react";

interface StatsData {
  totalSyllabus: number;
  totalUsers: number;
  statusBreakdown: { name: string; value: number; fill: string }[];
}

export default function DashboardCharts({ data }: { data: StatsData | null }) {
  if (!data) return <div className="h-48 flex items-center justify-center text-gray-400">Đang tải thống kê...</div>;

  const breakdown = data.statusBreakdown || [];
  const approvedCount = breakdown.find(i => i.name === "Đã xuất bản")?.value || 0;
  const pendingCount = breakdown.find(i => i.name === "Chờ duyệt")?.value || 0;

  return (
    <div className="space-y-6 mb-8 animate-in fade-in-50 slide-in-from-top-5 duration-500">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* SỬA: Card này đổi từ Blue -> Teal */}
        <Card className="bg-teal-50 border-teal-200 shadow-sm">
            <CardContent className="p-4 flex items-center gap-4">
                <div className="p-3 bg-teal-100 rounded-full text-teal-600"><FileText className="w-6 h-6" /></div>
                <div>
                    <p className="text-sm text-gray-500 font-medium">Tổng đề cương</p>
                    <h3 className="text-2xl font-bold text-teal-700">{data.totalSyllabus}</h3>
                </div>
            </CardContent>
        </Card>

        {/* Các Card khác giữ nguyên màu để phân biệt trạng thái (Xanh lá, Vàng, Tím) */}
        <Card className="bg-green-50 border-green-200 shadow-sm">
            <CardContent className="p-4 flex items-center gap-4">
                <div className="p-3 bg-green-100 rounded-full text-green-600"><CheckCircle className="w-6 h-6" /></div>
                <div>
                    <p className="text-sm text-gray-500 font-medium">Đã công bố</p>
                    <h3 className="text-2xl font-bold text-green-700">{approvedCount}</h3>
                </div>
            </CardContent>
        </Card>

        <Card className="bg-yellow-50 border-yellow-200 shadow-sm">
            <CardContent className="p-4 flex items-center gap-4">
                <div className="p-3 bg-yellow-100 rounded-full text-yellow-600"><Clock className="w-6 h-6" /></div>
                <div>
                    <p className="text-sm text-gray-500 font-medium">Đang chờ duyệt</p>
                    <h3 className="text-2xl font-bold text-yellow-700">{pendingCount}</h3>
                </div>
            </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200 shadow-sm">
            <CardContent className="p-4 flex items-center gap-4">
                <div className="p-3 bg-purple-100 rounded-full text-purple-600"><Users className="w-6 h-6" /></div>
                <div>
                    <p className="text-sm text-gray-500 font-medium">Người dùng</p>
                    <h3 className="text-2xl font-bold text-purple-700">{data.totalUsers}</h3>
                </div>
            </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="shadow-sm">
            <CardHeader><CardTitle className="text-lg">Tỷ lệ trạng thái đề cương</CardTitle></CardHeader>
            <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={breakdown}
                            cx="50%" cy="50%"
                            innerRadius={60} outerRadius={100}
                            paddingAngle={5}
                            dataKey="value"
                        >
                            {breakdown.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.fill} stroke="none"/>
                            ))}
                        </Pie>
                        <Tooltip />
                        <Legend verticalAlign="bottom" height={36}/>
                    </PieChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>

        <Card className="shadow-sm">
            <CardHeader><CardTitle className="text-lg">Thống kê số lượng</CardTitle></CardHeader>
            <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={breakdown} margin={{top: 20, right: 30, left: 0, bottom: 5}}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="name" tick={{fontSize: 12}} />
                        <YAxis allowDecimals={false} />
                        <Tooltip cursor={{fill: 'transparent'}} />
                        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                            {breakdown.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.fill} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
      </div>
    </div>
  );
}
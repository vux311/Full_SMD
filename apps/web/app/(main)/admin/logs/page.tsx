"use client";

import React, { useEffect, useState } from "react";
import axios from "@/lib/axios";
import { Card } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { FileClock, Loader2, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Log {
  id: number;
  timestamp: string;
  username: string;
  action: string;
  details: string;
}

export default function SystemLogsPage() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/admin/logs?limit=50');
      const data = res.data;
      setLogs(data || []);
    } catch (e: any) {
      const status = e?.response?.status || e?.status;
      if (status === 403) alert("Bạn không có quyền truy cập!");
      else console.error(e);
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchLogs(); }, []);

  const getActionColor = (action: string) => {
      if (action === "LOGIN") return "bg-blue-100 text-blue-700 border-blue-200";
      if (action.includes("DELETE")) return "bg-red-100 text-red-700 border-red-200";
      if (action.includes("APPROVE")) return "bg-green-100 text-green-700 border-green-200";
      if (action.includes("CREATE")) return "bg-purple-100 text-purple-700 border-purple-200";
      return "bg-gray-100 text-gray-700";
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
            <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                <FileClock className="w-6 h-6 text-orange-600"/> Nhật ký Hệ thống
            </h2>
            <p className="text-sm text-muted-foreground mt-1">Theo dõi hoạt động của người dùng (50 bản ghi gần nhất)</p>
        </div>
        <Button variant="outline" onClick={fetchLogs}><RefreshCcw className="w-4 h-4 mr-2"/> Làm mới</Button>
      </div>

      <Card>
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[180px]">Thời gian</TableHead>
                    <TableHead>Người thực hiện</TableHead>
                    <TableHead>Hành động</TableHead>
                    <TableHead>Chi tiết</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {loading ? (
                    <TableRow><TableCell colSpan={4} className="text-center h-24"><Loader2 className="animate-spin w-4 h-4 inline mr-2"/> Đang tải dữ liệu...</TableCell></TableRow>
                ) : logs.length === 0 ? (
                    <TableRow><TableCell colSpan={4} className="text-center h-24 text-muted-foreground">Chưa có nhật ký nào.</TableCell></TableRow>
                ) : (
                    logs.map(log => (
                        <TableRow key={log.id}>
                            <TableCell className="text-xs text-gray-500 font-mono">
                                {new Date(log.timestamp).toLocaleString('vi-VN')}
                            </TableCell>
                            <TableCell className="font-bold text-sm">{log.username}</TableCell>
                            <TableCell>
                                <Badge variant="outline" className={getActionColor(log.action)}>
                                    {log.action}
                                </Badge>
                            </TableCell>
                            <TableCell className="text-sm text-gray-600">{log.details}</TableCell>
                        </TableRow>
                    ))
                )}
            </TableBody>
        </Table>
      </Card>
    </div>
  );
}
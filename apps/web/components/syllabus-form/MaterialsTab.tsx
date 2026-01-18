// apps/web/components/syllabus-form/MaterialsTab.tsx
"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SyllabusData } from "../Types";

interface MaterialsTabProps {
  data: SyllabusData;
  readOnly: boolean;
  onUpdate: (index: number, val: string) => void;
  onAdd: (type: "Main" | "Ref") => void;
  onRemove: (index: number) => void;
}

export default function MaterialsTab({ data, readOnly, onUpdate, onAdd, onRemove }: MaterialsTabProps) {
  
  const renderSection = (type: "Main" | "Ref", label: string) => (
    <div className="bg-slate-50 p-4 rounded-md mb-4 border border-slate-200">
      <h3 className="font-bold mb-3 text-slate-700">{label}</h3>
      <div className="space-y-3">
        {data.materials.map((m, originalIndex) => ({ m, originalIndex }))
          .filter(item => item.m.type === type)
          .map(({ m, originalIndex }, i) => (
            <div key={originalIndex} className="flex gap-2 items-center">
              <span className="text-sm font-bold w-8 text-gray-500">[{i + 1}]</span>
              <Input 
                value={m.title} 
                onChange={(e) => onUpdate(originalIndex, e.target.value)} 
                placeholder="Ví dụ: Tên tác giả, Năm xuất bản, Tên sách, Nhà xuất bản..." 
                disabled={readOnly}
                className="bg-white flex-1"
              />
              {!readOnly && (
                <Button variant="ghost" size="icon" onClick={() => onRemove(originalIndex)} className="text-red-500 hover:text-red-700 hover:bg-red-50">✕</Button>
              )}
            </div>
        ))}
        {/* Hiển thị thông báo nếu chưa có tài liệu nào */}
        {data.materials.filter(m => m.type === type).length === 0 && (
            <div className="text-sm text-gray-400 italic pl-8">Chưa có tài liệu nào.</div>
        )}
      </div>
      {!readOnly && (
        <Button variant="outline" size="sm" className="mt-3 ml-8 border-dashed bg-white" onClick={() => onAdd(type)}>
          + Thêm tài liệu
        </Button>
      )}
    </div>
  );

  return (
    <div className="animate-in fade-in-50 space-y-4">
      {renderSection("Main", "8.1. Tài liệu chính")}
      {renderSection("Ref", "8.2. Tài liệu tham khảo")}
    </div>
  );
}
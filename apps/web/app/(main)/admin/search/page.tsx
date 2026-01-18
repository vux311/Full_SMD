"use client";

import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Search, 
  FileSearch, 
  Cpu, 
  Upload, 
  FileText, 
  Loader2,
  CheckCircle2,
  AlertTriangle,
  History
} from "lucide-react";
import axios from "@/lib/axios";
import { Badge } from "@/components/ui/badge";

export default function AdvancedSearchPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  
  const [isUploading, setIsUploading] = useState(false);
  const [ocrText, setOcrText] = useState("");
  const [isReindexing, setIsReindexing] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery) return;
    setIsSearching(true);
    try {
      const res = await axios.get(`/search/syllabuses?q=${encodeURIComponent(searchQuery)}`);
      setSearchResults(res.data || []);
    } catch (e) {
      console.error(e);
    } finally { setIsSearching(false); }
  };

  const handleOCR = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setOcrText("");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("/search/ocr", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setOcrText(res.data.text);
    } catch (e: any) {
      setOcrText("Lỗi: " + (e.response?.data?.message || e.message));
    } finally { setIsUploading(false); }
  };

  const handleReindex = async () => {
    setIsReindexing(true);
    try {
      await axios.post("/search/reindex");
      alert("Đã bắt đầu lập lại chỉ mục thành công!");
    } catch (e) {
      alert("Lỗi reindex.");
    } finally { setIsReindexing(false); }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-3">
             <Cpu className="w-8 h-8 text-indigo-600" /> Công nghệ Số hóa & Tìm kiếm AI
          </h2>
          <p className="text-muted-foreground">Sử dụng Tesseract OCR và Elasticsearch để quản lý dữ liệu đề cương cũ.</p>
        </div>
        <Button variant="outline" size="sm" onClick={handleReindex} disabled={isReindexing} className="gap-2 border-indigo-200 text-indigo-700 hover:bg-indigo-50">
          {isReindexing ? <Loader2 className="w-4 h-4 animate-spin" /> : <History className="w-4 h-4" />}
          Lập lại chỉ mục (Reindex)
        </Button>
      </div>

      <Tabs defaultValue="search" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-8 h-12">
          <TabsTrigger value="search" className="gap-2 text-lg"><Search className="w-5 h-5"/> Tìm kiếm thông minh (Elasticsearch)</TabsTrigger>
          <TabsTrigger value="ocr" className="gap-2 text-lg"><FileText className="w-5 h-5"/> Số hóa tài liệu cũ (OCR)</TabsTrigger>
        </TabsList>

        <TabsContent value="search">
          <Card className="border-indigo-100 shadow-sm">
            <CardHeader className="pb-4">
               <div className="flex gap-2">
                 <Input 
                   placeholder="Nhập từ khóa tìm kiếm (Ví dụ: Lập trình C#, Cơ sở dữ liệu...)" 
                   className="h-12 text-lg" 
                   value={searchQuery}
                   onChange={(e) => setSearchQuery(e.target.value)}
                   onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                 />
                 <Button className="h-12 px-8 bg-indigo-600 hover:bg-indigo-700 gap-2" onClick={handleSearch} disabled={isSearching}>
                    {isSearching ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                    Tìm kiếm
                 </Button>
               </div>
            </CardHeader>
            <CardContent>
              {searchResults.length > 0 ? (
                <div className="space-y-4">
                  {searchResults.map((hit, idx) => (
                    <div key={idx} className="p-4 border rounded-lg hover:bg-slate-50 transition-colors border-slate-200">
                       <div className="flex justify-between items-start mb-2">
                         <h4 className="font-bold text-indigo-800 text-lg">
                           [{hit.source.subject_code}] {hit.source.subject_name_vi}
                         </h4>
                         <Badge variant="secondary">Độ khớp: {(hit.score * 10).toFixed(1)}%</Badge>
                       </div>
                       <div className="text-sm text-slate-600 line-clamp-3 italic bg-white p-2 border-l-4 border-indigo-300 rounded">
                         ...{hit.highlight?.description || hit.source.description}...
                       </div>
                       <div className="mt-3 flex items-center gap-4 text-xs text-slate-400">
                          <span className="flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5 text-green-500" /> Version: {hit.source.version}</span>
                          <span className="flex items-center gap-1"><FileSearch className="w-3.5 h-3.5 text-blue-500" /> Trạng thái: {hit.source.status}</span>
                       </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-20 bg-slate-50 rounded-lg border-2 border-dashed border-slate-200">
                   <Search className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                   <p className="text-slate-500 font-medium">Nhập từ khóa để tìm kiếm trong kho dữ liệu đề cương.</p>
                   <p className="text-xs text-slate-400 mt-1">Hệ thống hỗ trợ tìm kiếm mờ (fuzzy) và đánh trọng số theo mã môn học.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ocr">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             <Card>
               <CardHeader>
                 <CardTitle className="flex items-center gap-2"><Upload className="w-5 h-5 text-indigo-600" /> Tải tài liệu lên</CardTitle>
                 <CardDescription>Hỗ trợ file PDF, PNG, JPG từ các đề cương cũ bản cứng.</CardDescription>
               </CardHeader>
               <CardContent>
                 <div className="border-2 border-dashed border-indigo-200 rounded-xl p-10 text-center bg-indigo-50/30">
                    <input type="file" id="ocr-upload" hidden onChange={handleOCR} accept=".pdf,image/*" />
                    <label htmlFor="ocr-upload" className="cursor-pointer">
                       <div className="bg-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm border border-indigo-100 group-hover:scale-110 transition-transform">
                          {isUploading ? <Loader2 className="w-8 h-8 animate-spin text-indigo-600" /> : <Upload className="w-8 h-8 text-indigo-600" />}
                       </div>
                       <p className="font-bold text-indigo-900">Click để chọn file hoặc kéo thả</p>
                       <p className="text-xs text-indigo-600 mt-2">Dung lượng tối đa 10MB</p>
                    </label>
                 </div>

                 <div className="mt-6 space-y-3">
                   <div className="flex items-start gap-2 text-xs text-amber-700 bg-amber-50 p-3 rounded-lg border border-amber-100">
                      <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <div>
                        <strong>Ghi chú:</strong> Độ chính xác của OCR phụ thuộc vào chất lượng ảnh quét.
                        Hệ thống ưu tiên hỗ trợ ngôn ngữ Việt/Anh.
                      </div>
                   </div>
                 </div>
               </CardContent>
             </Card>

             <Card className="flex flex-col">
               <CardHeader className="flex flex-row items-center justify-between space-y-0">
                 <div>
                   <CardTitle className="flex items-center gap-2"><FileText className="w-5 h-5 text-indigo-600" /> Kết quả trích xuất</CardTitle>
                   <CardDescription>Nội dung số được chuyển đổi từ ảnh quét.</CardDescription>
                 </div>
                 {ocrText && <Button variant="ghost" size="sm" onClick={() => { navigator.clipboard.writeText(ocrText); alert("Đã copy!"); }}>Sao chép</Button>}
               </CardHeader>
               <CardContent className="flex-1">
                 <div className="h-full min-h-[300px] w-full bg-slate-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-auto max-h-[500px]">
                    {ocrText ? (
                      <pre className="whitespace-pre-wrap">{ocrText}</pre>
                    ) : (
                      <div className="h-full flex flex-col items-center justify-center text-slate-500 italic opacity-50">
                        <Loader2 className={`w-8 h-8 mb-2 ${isUploading ? 'animate-spin' : 'hidden'}`} />
                        {isUploading ? "Đang xử lý OCR..." : "Kết quả sẽ hiển thị tại đây..."}
                      </div>
                    )}
                 </div>
               </CardContent>
             </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

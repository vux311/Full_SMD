/*
khi vào trang http://localhost:3000/syllabus/create để tạo đề cương mới, sau khi đã biên soạn hoàn tất mình ấn lưu nháp
chuyện xảy ra là khi ấn lưu nháp những gì mình đã biên soạn không được lưu
hãy kiểm tra và sửa lỗi này giúp mình, mức độ ưu tiên rất cao ảnh hưởng đến toàn bộ dự án 
và nếu không thể sửa lỗi này thì viết lại từ đầu là điều chắc chắn xảy ra 
*/
"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { 
    Save, 
    Send, 
    FileDiff, 
    ArrowLeft, 
    MessageSquareWarning, 
    Sparkles, 
    Loader2,
    BookOpen,
    LineChart,
    Trash2,
    Check,
    ChevronsUpDown,
    Search
} from "lucide-react";
import { SyllabusData } from "./Types";
import MaterialsTab from "./syllabus-form/MaterialsTab";
import axios from "@/lib/axios";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

function SearchableSelect({ 
  options, 
  value, 
  onChange, 
  placeholder, 
  searchPlaceholder = "Tìm kiếm...",
  disabled = false,
  className = ""
}: {
  options: { value: string | number, label: string }[],
  value: string | number,
  onChange: (val: string | number) => void,
  placeholder: string,
  searchPlaceholder?: string,
  disabled?: boolean,
  className?: string
}) {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState("");

  const selectedOption = options.find(opt => opt.value === value);

  const filteredOptions = options.filter(opt => 
    opt.label.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild disabled={disabled}>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn("w-full justify-between font-normal bg-white", className)}
        >
          <span className="truncate">{selectedOption ? selectedOption.label : placeholder}</span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="p-0 w-[--radix-popover-trigger-width]" align="start">
        <div className="flex items-center border-b px-3">
          <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
          <input
            className="flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
            placeholder={searchPlaceholder}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="max-h-[300px] overflow-y-auto p-1">
          {filteredOptions.length === 0 && (
            <div className="py-6 text-center text-sm">Không tìm thấy kết quả.</div>
          )}
          {filteredOptions.map((option) => (
            <div
              key={option.value}
              className={cn(
                "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 px-2 text-sm outline-none hover:bg-slate-100 hover:text-slate-900 transition-colors",
                value === option.value && "bg-slate-100 text-slate-900"
              )}
              onClick={() => {
                onChange(option.value);
                setOpen(false);
                setSearch(""); // Reset search on select
              }}
            >
              <Check
                className={cn(
                  "mr-2 h-4 w-4",
                  value === option.value ? "opacity-100" : "opacity-0"
                )}
              />
              {option.label}
            </div>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}

export default function SyllabusEditForm({ initial }: { initial: SyllabusData }) {
  const router = useRouter();
  
  const [data, setData] = useState<SyllabusData>(initial);
  const [lastSavedString, setLastSavedString] = useState(JSON.stringify(initial));
  const [submitting, setSubmitting] = useState(false);
  const [userRole, setUserRole] = useState<string>("");
  const [aiLoading, setAiLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  
  // Dropdown data
  const [subjects, setSubjects] = useState<any[]>([]);
  const [programs, setPrograms] = useState<any[]>([]);
  const [academicYears, setAcademicYears] = useState<any[]>([]);
  const [lecturers, setLecturers] = useState<any[]>([]);
  const [loadingDropdowns, setLoadingDropdowns] = useState(true);
  const [plos, setPlos] = useState<any[]>([]);

  useEffect(() => {
    setMounted(true);
    const role = localStorage.getItem("role") || "";
    setUserRole(role);
    
    // Load dropdown data
    const loadDropdowns = async () => {
      try {
        console.log("[DEBUG] Fetching dropdown data...");
        const [subjectsRes, programsRes, yearsRes, usersRes] = await Promise.all([
          axios.get('/subjects'),
          axios.get('/programs'),
          axios.get('/academic-years'),
          axios.get('/users')
        ]);
        
        console.log("[DEBUG] Fetched users:", usersRes.data);
        
        setSubjects(Array.isArray(subjectsRes.data) ? subjectsRes.data : []);
        setPrograms(Array.isArray(programsRes.data) ? programsRes.data : []);
        setAcademicYears(Array.isArray(yearsRes.data) ? yearsRes.data : []);
        
        // Populate lecturers/users list for selection
        let allUsers: any[] = [];
        if (usersRes.data && Array.isArray(usersRes.data)) {
          allUsers = usersRes.data;
        } else if (usersRes.data && usersRes.data.data && Array.isArray(usersRes.data.data)) {
          // Alternative format check
          allUsers = usersRes.data.data;
        }
        
        // Get current user info from token
        const userId = localStorage.getItem("user_id");
        const userName = localStorage.getItem("full_name") || localStorage.getItem("username");
        
        // Ensure the current user is in the list even if server list is empty/fails
        if (userId) {
          const currentId = Number(userId);
          const exists = allUsers.some(u => u.id === currentId);
          if (!exists) {
            allUsers.push({ 
              id: currentId, 
              fullName: userName,
              full_name: userName,
              username: userName
            });
          }
        }
        
        setLecturers(allUsers);

        // Auto-select current user as lecturer for new syllabus
        if (userId && !data.id && !data.lecturerId) {
            updateField("lecturerId", Number(userId));
            updateField("lecturer", userName || "");
        }
      } catch (error) {
        console.error("[ERROR] loadDropdowns failed:", error);
        alert("Không thể tải dữ liệu dropdown. Vui lòng refresh trang.");
      } finally {
        setLoadingDropdowns(false);
      }
    };
    
    loadDropdowns();
  }, []);

  // Fetch PLOs when program changes
  useEffect(() => {
    if (data.program_id) {
      const fetchPLOs = async () => {
        try {
          console.log(`[DEBUG] Fetching PLOs for program: ${data.program_id}`);
          // Bỏ /api/ ở phía trước vì baseURL đã có rồi
          // SỬA: Route đúng của PLO là /program-outcomes/program/{id}
          const res = await axios.get(`/program-outcomes/program/${data.program_id}`);
          setPlos(Array.isArray(res.data) ? res.data : []);
        } catch (err) {
          console.error("Lỗi khi tải PLO:", err);
          setPlos([]);
        }
      };
      fetchPLOs();
    } else {
      setPlos([]);
    }
  }, [data.program_id]);

  const hasUnsavedChanges = useMemo(() => {
    return JSON.stringify(data) !== lastSavedString;
  }, [data, lastSavedString]);

  const isEditable = !data.id || 
                     (data.status?.toUpperCase() === "DRAFT" || data.status?.toUpperCase() === "RETURNED");


  const updateField = (field: keyof SyllabusData, value: any) => {
    if (isEditable || userRole === "Admin") setData((prev) => ({ ...prev, [field]: value }));
  };

  const updateTime = (key: keyof SyllabusData["timeAllocation"], val: number) => {
    if (isEditable || userRole === "Admin") setData((prev) => ({
      ...prev,
      timeAllocation: { ...prev.timeAllocation, [key]: val },
    }));
  }; 

  const addArrayItem = <T,>(field: keyof SyllabusData, newItem: T) => {
    if (isEditable || userRole === "Admin") setData((prev) => ({
      ...prev,
      [field]: [...(prev[field] as T[]), newItem],
    }));
  };

  const removeArrayItem = (field: keyof SyllabusData, index: number) => {
    if (isEditable || userRole === "Admin") setData((prev) => ({
      ...prev,
      [field]: (prev[field] as any[]).filter((_, i) => i !== index),
    }));
  };

  const updateArrayItem = <T,>(field: keyof SyllabusData, index: number, newItem: Partial<T>) => {
    if (isEditable || userRole === "Admin") {
      setData((prev) => {
        const arr = [...(prev[field] as T[])];
        arr[index] = { ...arr[index], ...newItem };
        return { ...prev, [field]: arr };
      });
    }
  };

  const handleAIGenerate = async () => {
    if (!data.subjectNameVi) {
      alert("Vui lòng nhập Tên môn học (Tiếng Việt) để AI hiểu ý bạn!");
      return;
    }

    if (!confirm(`AI sẽ tự động soạn thảo nội dung cho môn "${data.subjectNameVi}".\n\nDữ liệu hiện tại sẽ bị ghi đè. Bạn có chắc không?`)) {
      return;
    }

    setAiLoading(true);
    try {
        // Send subjectName in camelCase, axios will convert to snake_case
        const res = await axios.post("/ai/generate", { subjectName: data.subjectNameVi });
        const aiData = res.data;
        
        if (!aiData || typeof aiData !== 'object') {
          throw new Error("Dữ liệu AI trả về không hợp lệ");
        }
        
        // Merge AI data with existing data
        setData(prev => ({
            ...prev,
            ...aiData,
            id: prev.id,
            status: prev.status,
            version: prev.version,
            subjectNameVi: prev.subjectNameVi, // Keep the original name
        }));
        
        alert("✅ AI đã soạn thảo xong! Vui lòng kiểm tra lại các Tab.");
    } catch (e: any) {
        console.error("AI Generate Error:", e);
        
        let errorMsg = "Lỗi kết nối đến AI Server.";
        
        if (e?.response?.data?.message) {
          errorMsg = e.response.data.message;
        } else if (e?.response?.status === 404) {
          errorMsg = "Endpoint AI không tồn tại. Vui lòng kiểm tra backend.";
        } else if (e?.message?.includes("Network Error")) {
          errorMsg = "Không thể kết nối đến backend. Vui lòng kiểm tra server có đang chạy không.";
        } else if (e?.message) {
          errorMsg = e.message;
        }
        
        alert(`❌ Lỗi AI Generate:\n${errorMsg}\n\nVui lòng điền thông tin thủ công.`);
    } finally {
        setAiLoading(false);
    }
  };

  const handleSave = async () => {
    // 1. Validation for weights
    const totalWeight = data.assessmentScheme.reduce((sum, item) => sum + (Number(item.weight) || 0), 0);
    if (totalWeight !== 100) {
        if (!confirm(`⚠️ Tổng trọng số hiện tại là ${totalWeight}%, không bằng 100%.\n\nBạn có chắc chắn muốn lưu bản nháp này không? (Để được duyệt, tổng phải bằng 100%)`)) {
            return;
        }
    }

    setSubmitting(true);
    try {
      const isEdit = !!data.id;

      if (!isEdit) {
        // Validate required IDs before creating
        if (!data.subjectId || !data.program_id || !data.academicYearId || !data.lecturerId) {
          alert("⚠️ Vui lòng điền đầy đủ các ID bắt buộc:\n\n" +
            `- Subject ID: ${data.subjectId || 'THIẾU'}\n` +
            `- Program ID: ${data.program_id || 'THIẾU'}\n` +
            `- Academic Year ID: ${data.academicYearId || 'THIẾU'}\n` +
            `- Lecturer ID: ${data.lecturerId || 'THIẾU'}\n\n` +
            "Các ID này phải được nhập thủ công hoặc chọn từ dropdown.");
          setSubmitting(false);
          return;
        }
        
        console.log("[DEBUG] Starting create syllabus with IDs:", {
          subjectId: data.subjectId,
          program_id: data.program_id,
          academicYearId: data.academicYearId,
          lecturerId: data.lecturerId
        });

        // Create parent syllabus first (axios will convert camelCase -> snake_case on POST)
        const parentPayload: any = {
          subjectId: data.subjectId,
          program_id: data.program_id,
          academicYearId: data.academicYearId,
          lecturerId: data.lecturerId,
          headDepartmentId: data.headDepartmentId,
          deanId: data.deanId,
          version: data.version || "1.0",
          timeAllocation: data.timeAllocation,
          prerequisites: data.prerequisites ?? null,
          
          // Content fields
          description: data.description ?? null,
          objectives: data.objectives || [],
          studentDuties: data.studentDuties ?? null,
          otherRequirements: data.otherRequirements ?? null,
          
          // Additional metadata
          preCourses: data.preCourses ?? null,
          coCourses: data.coCourses ?? null,
          courseType: data.courseType ?? null,
          componentType: data.componentType ?? null,
          datePrepared: data.datePrepared ?? null,
          dateEdited: data.dateEdited ?? null,
          dean: data.dean ?? null,
          headDepartment: data.headDepartment ?? null,
        };

        // Add child entities to payload - backend service handles them atomically
        parentPayload.clos = (data.clos || [])
          .filter((clo) => clo.code && clo.description)
          .map(clo => {
            // Merge PLO mappings for this CLO if they exist
            const mapping = data.ploMapping?.find(m => m.cloCode === clo.code);
            return {
              ...clo,
              ploMappings: mapping ? Object.entries(mapping.plos).map(([code, level]) => ({ code, level })) : []
            };
          });

        parentPayload.teachingPlans = data.teachingPlan?.filter((p) => p.week && p.topic) || [];
        parentPayload.materials = data.materials?.filter((m) => m.type && m.title) || [];
        
        // Convert assessment scheme to nested structure expected by backend
        if (data.assessmentScheme && data.assessmentScheme.length > 0) {
          parentPayload.assessmentSchemes = [{
            name: "Default Scheme",
            components: data.assessmentScheme.map(item => ({
              name: item.component,
              method: item.method,
              weight: item.weight,
              criteria: item.criteria,
              cloIds: item.clos // CLO codes/IDs reference
            }))
          }];
        }

        console.log("[DEBUG] Creating syllabus with full payload (header + children):", parentPayload);
        const res = await axios.post("/syllabuses", parentPayload);
        const resJson = res.data;
        console.log("[DEBUG] Server response:", resJson);
        
        if (!resJson?.id) {
          console.error("[ERROR] No ID returned from server. Full response:", resJson);
          throw new Error("Server không trả về ID. Vui lòng kiểm tra logs backend.");
        }

        const syllabusId = resJson.id;
        const childCounts = {
          clos: parentPayload.clos.length,
          plans: parentPayload.teachingPlans.length,
          materials: parentPayload.materials.length
        };
        
        console.log("[DEBUG] Syllabus created successfully with children:", childCounts);

        const newData = { ...data, id: syllabusId };
        setData(newData);
        setLastSavedString(JSON.stringify(newData));
        console.log("[DEBUG] Create completed successfully. Redirecting...");
        alert(`✅ Tạo mới thành công!\n\nĐề cương ID: ${syllabusId}\n` +
              `📚 CLOs: ${childCounts.clos}\n` +
              `📅 Kế hoạch: ${childCounts.plans}\n` +
              `📖 Tài liệu: ${childCounts.materials}`);
        router.push(`/syllabus/${syllabusId}/edit`);
        return;
      }

      // Edit existing syllabus
      // Syncing payload with create logic to preserve children
      const updatePayload: any = {
        subjectId: data.subjectId,
        program_id: data.program_id,
        academicYearId: data.academicYearId,
        lecturerId: data.lecturerId,
        headDepartmentId: data.headDepartmentId,
        deanId: data.deanId,
        version: data.version,
        timeAllocation: data.timeAllocation,
        prerequisites: data.prerequisites ?? null,
        
        // Content fields
        description: data.description ?? null,
        objectives: data.objectives || [],
        studentDuties: data.studentDuties ?? null,
        otherRequirements: data.otherRequirements ?? null,
        
        // Additional metadata
        preCourses: data.preCourses ?? null,
        coCourses: data.coCourses ?? null,
        courseType: data.courseType ?? null,
        componentType: data.componentType ?? null,
        datePrepared: data.datePrepared ?? null,
        dateEdited: data.dateEdited ?? null,
        dean: data.dean ?? null,
        headDepartment: data.headDepartment ?? null,
      };

      // Synchronize child entities saving logic
      updatePayload.clos = (data.clos || [])
        .filter((clo) => clo.code && clo.description)
        .map(clo => {
          // Merge PLO mappings for this CLO
          const mapping = data.ploMapping?.find(m => m.cloCode === clo.code);
          return {
            ...clo,
            ploMappings: mapping ? Object.entries(mapping.plos).map(([code, level]) => ({ code, level })) : []
          };
        });

      updatePayload.teachingPlans = data.teachingPlan?.filter((p) => p.week && p.topic) || [];
      updatePayload.materials = data.materials?.filter((m) => m.type && m.title) || [];
      
      if (data.assessmentScheme && data.assessmentScheme.length > 0) {
        updatePayload.assessmentSchemes = [{
          name: "Default Scheme",
          components: data.assessmentScheme.map(item => ({
            name: item.component,
            method: item.method,
            weight: item.weight,
            criteria: item.criteria,
            cloIds: item.clos
          }))
        }];
      }
      
      console.log("[DEBUG] Updating syllabus with full synchronzed payload:", updatePayload);
      const updateRes = await axios.patch(`/syllabuses/${data.id}`, updatePayload);
      console.log("[DEBUG] Update response:", updateRes.data);
      setLastSavedString(JSON.stringify(data));
      router.refresh();
      alert(`✅ Đã lưu bản nháp!\n\nĐề cương ID: ${data.id}\nThời gian: ${new Date().toLocaleTimeString()}`);

    } catch (error: any) {
      console.error("[ERROR] Save Error:", error);
      console.error("[ERROR] Error details:", {
        message: error.message,
        status: error?.response?.status,
        data: error?.response?.data,
        config: error?.config?.url
      });
      
      // Check for CORS or network errors
      if (error?.message?.includes('Network Error') || error?.code === 'ERR_NETWORK') {
        alert("❌ Không thể kết nối đến backend.\n\nVui lòng kiểm tra:\n1. Backend có đang chạy không?\n2. Đúng port chưa? (mặc định: 9999)\n3. CORS đã được cấu hình chưa?");
        setSubmitting(false);
        return;
      }
      
      if (error?.response?.status === 401) {
        alert("⚠️ Phiên đăng nhập hết hạn.");
        router.push("/login");
        return;
      }
      
      if (error?.response?.status === 403) {
        const message = error?.response?.data?.message || "Bạn không có quyền thực hiện thao tác này";
        alert(`🚫 ${message}\n\nChỉ Lecturer và Admin có thể tạo/sửa đề cương.`);
        setSubmitting(false);
        return;
      }
      
      if (error?.response?.status === 422) {
        const message = error?.response?.data?.message || "Dữ liệu không hợp lệ";
        const details = error?.response?.data?.details || error?.response?.data?.error || "";
        alert(`⚠️ ${message}\n\nChi tiết: ${details}\n\nVui lòng kiểm tra lại các trường bắt buộc.`);
        setSubmitting(false);
        return;
      }
      
      const errorMsg = error?.response?.data?.error || error?.response?.data?.message || error?.message || "Lỗi khi lưu dữ liệu.";
      const statusCode = error?.response?.status || "N/A";
      const url = error?.config?.url || "Unknown endpoint";
      
      alert(`❌ Lỗi khi lưu đề cương\n\n` +
        `Mã lỗi: ${statusCode}\n` +
        `Endpoint: ${url}\n` +
        `Chi tiết: ${errorMsg}\n\n` +
        `Vui lòng kiểm tra Console (F12) để xem log chi tiết.`);
      
      console.log("[ERROR] Full error object:", error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleWorkflow = async (action: "submit" | "approve" | "revise") => {
    if (!data.id) return;

    let confirmMsg = "";
    if (action === "submit") confirmMsg = "Gửi đề cương đi phê duyệt? Bạn sẽ không thể chỉnh sửa trong lúc chờ.";
    if (action === "approve") confirmMsg = "Xác nhận PHÊ DUYỆT đề cương này?";
    if (action === "revise") confirmMsg = "Hệ thống sẽ tạo phiên bản MỚI (Draft) từ bản này để bạn chỉnh sửa. Tiếp tục?";

    if (!confirm(confirmMsg)) return;

    setSubmitting(true);
    try {
      let res;
      if (action === "approve") {
          res = await axios.post(`/syllabuses/${data.id}/evaluate`, { action: 'approve' });
      } else {
          res = await axios.post(`/syllabuses/${data.id}/${action}`);
      }
      const resData = res.data;

      if (action === "revise") {
        alert(`✅ Đã tạo phiên bản mới: ${resData.version}`);
        router.push(`/syllabus/${resData.id}/edit`);
        return;
      }
      alert("✅ Thao tác thành công!");
      router.refresh();
    } catch (e: any) {
      console.error(e);
      
      const status = e?.response?.status;
      
      if (status === 403) {
        const message = e?.response?.data?.message || "Bạn không có quyền thực hiện thao tác này";
        alert(`🚫 ${message}`);
        return;
      }
      
      if (status === 422) {
        const message = e?.response?.data?.message || "Đề cương không trong trạng thái phù hợp";
        alert(`⚠️ ${message}`);
        return;
      }
      
      const msg = e?.response?.data?.message || e?.response?.data?.detail || e?.message || "Lỗi kết nối server.";
      alert(`❌ ${msg}`);
    } finally {
      setSubmitting(false);
    }
  };

  const totalPeriods = (data.timeAllocation?.theory || 0) + (data.timeAllocation?.exercises || 0) + (data.timeAllocation?.practice || 0);

  const renderStatusBadge = () => {
    const status = (data.status || "DRAFT").toUpperCase();
    let colorClass = "bg-slate-500";
    let label = "Bản nháp";

    switch (status) {
      case "PENDING_REVIEW":
        colorClass = "bg-yellow-500";
        label = "Đang chờ BM duyệt";
        break;
      case "PENDING_APPROVAL":
        colorClass = "bg-blue-500";
        label = "Đang chờ PĐT duyệt";
        break;
      case "APPROVED":
        colorClass = "bg-teal-600";
        label = "Đã phê duyệt (Chờ XB)";
        break;
      case "PUBLISHED":
        colorClass = "bg-green-600";
        label = "Đã xuất bản";
        break;
      case "RETURNED":
      case "REJECTED":
        colorClass = "bg-red-500";
        label = "Yêu cầu chỉnh sửa";
        break;
      case "DRAFT":
      default:
        colorClass = "bg-slate-500";
        label = "Bản nháp";
        break;
    }

    return <Badge className={`${colorClass} hover:${colorClass} ml-3 text-sm px-3 py-1`}>{label}</Badge>;
  };

  if (!mounted) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-2 text-slate-500 font-medium">Đang chuẩn bị biểu mẫu...</span>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto py-6 px-4">
      {(data.status?.toUpperCase() === "RETURNED" || data.status?.toUpperCase() === "REJECTED") && data.feedback && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3 items-start shadow-sm animate-in slide-in-from-top-2">
             <MessageSquareWarning className="w-6 h-6 text-red-600 mt-0.5 shrink-0" />
             <div>
                <h3 className="font-bold text-red-700 text-lg">Yêu cầu chỉnh sửa</h3>
                <p className="text-red-600 mt-1 whitespace-pre-wrap">{data.feedback}</p>
             </div>
          </div>
      )}
       {/* DoI bUN jQK #dm #fucklife #ttt #ttql #huhuhuuhu #cuocdoithatbun #nttoiqua */}
      <Card className="shadow-lg border-t-4 border-t-primary">
        <CardHeader className="flex flex-col md:flex-row justify-between items-start md:items-center border-b pb-4 mb-4 bg-slate-50/50 rounded-t-lg gap-4">
          <div>
            <div className="flex items-center gap-2">
              <CardTitle className="text-xl">
                {data.id ? `Biên soạn: ${data.subjectCode}` : "Tạo Đề Cương Mới"}
              </CardTitle>
              {data.version && <Badge variant="outline" className="border-primary text-primary font-bold">v{data.version}</Badge>}
              {renderStatusBadge()}
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {isEditable ? "Bạn đang ở chế độ chỉnh sửa" : "Chế độ xem (Read-only)"}
            </p>
          </div>

          <div className="flex flex-wrap gap-2 items-center">
            <Button variant="outline" onClick={() => router.back()} size="sm">
                <ArrowLeft className="w-4 h-4 mr-2"/> Thoát
            </Button>

            {isEditable && (
              <Button onClick={handleSave} disabled={submitting || aiLoading} variant="secondary" className="border border-slate-300 relative" size="sm">
                <Save className="w-4 h-4 mr-2" /> Lưu Nháp
                {hasUnsavedChanges && (
                    <span className="absolute -top-1 -right-1 flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                    </span>
                )}
              </Button>
            )}

            {data.id && (
              <>
                {(data.status?.toUpperCase() === "DRAFT" || data.status?.toUpperCase() === "RETURNED") && (
                  <div className="flex flex-col items-end">
                      {/* SỬA: bg-blue-600 -> bg-teal-600 */}
                      <Button 
                        className="bg-teal-600 hover:bg-teal-700 text-white disabled:opacity-50 disabled:cursor-not-allowed" 
                        size="sm" 
                        onClick={() => handleWorkflow("submit")}
                        disabled={hasUnsavedChanges || submitting || aiLoading}
                        title={hasUnsavedChanges ? "Bạn cần lưu nháp trước khi gửi duyệt" : "Gửi đi phê duyệt"}
                      >
                        <Send className="w-4 h-4 mr-2" /> Gửi Duyệt
                      </Button>
                  </div>
                )}

                {(data.status?.toUpperCase() === "PENDING_REVIEW" || 
                  data.status?.toUpperCase() === "PENDING_APPROVAL" || 
                  data.status?.toUpperCase() === "APPROVED") && 
                  (userRole === "Head of Dept" || userRole === "HoD" || userRole === "Academic Affairs" || userRole === "AA" || userRole === "Principal" || userRole === "Admin") && (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => router.push("/reviews")}>
                         Xử lý yêu cầu này (Duyệt/Trả về)
                    </Button>
                  </div>
                )}

                {(data.status?.toUpperCase() === "APPROVED" || data.status?.toUpperCase() === "PUBLISHED") && (
                    <Button className="bg-purple-600 hover:bg-purple-700 text-white border-purple-800" size="sm" onClick={() => handleWorkflow("revise")}>
                        <FileDiff className="w-4 h-4 mr-2" /> Tạo phiên bản mới
                    </Button>
                )}
              </>
            )}
          </div>
        </CardHeader>

        <CardContent>
          <Tabs defaultValue="general" className="w-full">
            <TabsList className="grid w-full grid-cols-7 mb-6 h-auto p-1 bg-slate-100 italic">
              <TabsTrigger value="general">1. Thông tin chung</TabsTrigger>
              <TabsTrigger value="clos">2-4. Mục tiêu & CĐR</TabsTrigger>
              <TabsTrigger value="plo">PLO Map</TabsTrigger>
              <TabsTrigger value="assessment">5-6. Đánh giá</TabsTrigger>
              <TabsTrigger value="plan">7. Kế hoạch</TabsTrigger>
              <TabsTrigger value="materials">8. Tài liệu</TabsTrigger>
              <TabsTrigger value="others">9. Khác</TabsTrigger>
            </TabsList>

            <div className={(!isEditable && userRole !== "Admin") ? "opacity-90 pointer-events-none" : ""}>
                <TabsContent value="general" className="space-y-6 animate-in fade-in-50">
                  {/* ... contents continue ... */}
                  <div className="bg-slate-50 border-2 border-slate-200 rounded-lg p-4 mb-6 shadow-sm">
                <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2">
                  <span className="text-lg">⚙️</span> Cấu trúc thực thi & Phân quyền
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-900">
                      Môn học (Subject) <span className="text-red-600">*</span>
                    </label>
                    {loadingDropdowns ? (
                      <div className="text-sm text-gray-500">Đang tải...</div>
                    ) : (
                      <SearchableSelect 
                        options={subjects.map(s => ({ value: s.id, label: `${s.code} - ${s.nameVi || s.name_vi}` }))}
                        value={data.subjectId || ""}
                        placeholder="-- Chọn môn học --"
                        disabled={!!data.id && userRole !== "Admin"}
                        className={data.id && userRole !== "Admin" ? "bg-gray-100 border-gray-300" : "border-blue-300"}
                        onChange={(val) => {
                          const subjectId = Number(val);
                          const subject = subjects.find(s => s.id === subjectId);
                          if (subject) {
                            updateField("subjectId", subjectId);
                            updateField("subjectCode", subject.code);
                            updateField("subjectNameVi", subject.nameVi || subject.name_vi);
                            updateField("subjectNameEn", subject.nameEn || subject.name_en);
                            updateField("credits", subject.credits);
                          }
                        }}
                      />
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-900">
                      Năm học (Academic Year) <span className="text-red-600">*</span>
                    </label>
                    {loadingDropdowns ? (
                      <div className="text-sm text-gray-500">Đang tải...</div>
                    ) : (
                      <SearchableSelect 
                        options={academicYears.map(y => ({ value: y.id, label: y.code }))}
                        value={data.academicYearId || ""}
                        placeholder="-- Chọn năm học --"
                        onChange={(val) => updateField("academicYearId", Number(val))}
                      />
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-900">
                      Trưởng Bộ môn <span className="text-red-600">*</span>
                    </label>
                    {loadingDropdowns ? (
                      <div className="text-sm text-gray-500">Đang tải...</div>
                    ) : (
                      <SearchableSelect 
                        options={lecturers.map(l => ({ value: l.id, label: l.fullName || l.full_name || l.username }))}
                        value={data.headDepartmentId || ""}
                        placeholder="-- Chọn Trưởng Bộ môn --"
                        onChange={(val) => {
                          const id = Number(val);
                          const user = lecturers.find(l => l.id === id);
                          updateField("headDepartmentId", id);
                          updateField("headDepartment", user ? (user.fullName || user.full_name || user.username) : "");
                        }}
                      />
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-900">
                      Ban Giám hiệu (Ký duyệt) <span className="text-red-600">*</span>
                    </label>
                    {loadingDropdowns ? (
                      <div className="text-sm text-gray-500">Đang tải...</div>
                    ) : (
                      <SearchableSelect 
                        options={lecturers.map(l => ({ value: l.id, label: l.fullName || l.full_name || l.username }))}
                        value={data.deanId || ""}
                        placeholder="-- Chọn người ký --"
                        onChange={(val) => {
                          const id = Number(val);
                          const user = lecturers.find(l => l.id === id);
                          updateField("deanId", id);
                          updateField("dean", user ? (user.fullName || user.full_name || user.username) : "");
                        }}
                      />
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-900">
                      Chương trình (Program) <span className="text-red-600">*</span>
                    </label>
                    {loadingDropdowns ? (
                      <div className="text-sm text-gray-500">Đang tải...</div>
                    ) : (
                      <SearchableSelect 
                        options={programs.map(p => ({ value: p.id, label: p.name || p.nameVi || p.name_vi }))}
                        value={data.program_id || ""}
                        disabled={!!data.id && userRole !== "Admin"}
                        className={data.id && userRole !== "Admin" ? "bg-gray-100 border-gray-300" : "border-slate-300"}
                        placeholder="-- Chọn chương trình --"
                        onChange={(val) => updateField("program_id", Number(val))}
                      />
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-slate-900">
                      Người biên soạn (Lecturer) <span className="text-red-600">*</span>
                    </label>
                    {loadingDropdowns ? (
                      <div className="text-sm text-gray-500">Đang tải...</div>
                    ) : (
                      <SearchableSelect 
                        options={lecturers.map(l => ({ value: l.id, label: l.fullName || l.full_name || l.username }))}
                        value={data.lecturerId || ""}
                        disabled={!!data.id && userRole !== "Admin"}
                        className={data.id && userRole !== "Admin" ? "bg-gray-100 border-gray-300" : "border-slate-300"}
                        placeholder="-- Chọn giảng viên --"
                        onChange={(val) => {
                          const id = Number(val);
                          const user = lecturers.find(l => l.id === id);
                          updateField("lecturerId", id);
                          updateField("lecturer", user ? (user.fullName || user.full_name || user.username) : "");
                        }}
                      />
                    )}
                  </div>
                </div>
                {!data.id && (
                  <p className="text-xs text-amber-700 mt-2 font-medium">
                    💡 Lưu ý: Các trường này giúp định danh đề cương và phân quyền phê duyệt.
                  </p>
                )}
              </div>
              
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label className="text-sm font-semibold flex justify-between items-center">
                        Tên HP (Tiếng Việt)
                        {isEditable && (
                            <button 
                                onClick={handleAIGenerate} 
                                disabled={aiLoading}
                                className="text-xs flex items-center gap-1 text-purple-600 hover:text-purple-800 font-bold transition-all hover:scale-105 border border-purple-200 px-2 py-1 rounded-full bg-purple-50"
                                title="Tự động điền nội dung bằng AI"
                            >
                                {aiLoading ? <Loader2 className="w-3 h-3 animate-spin"/> : <Sparkles className="w-3 h-3"/>}
                                {aiLoading ? "AI đang viết..." : "AI Soạn thảo"}
                            </button>
                        )}
                    </label>
                    <Input value={data.subjectNameVi} onChange={(e) => updateField("subjectNameVi", e.target.value)} placeholder="VD: Nhập môn Trí tuệ Nhân tạo"/>
                </div>
                <div className="space-y-2"><label className="text-sm font-semibold">Tên HP (Tiếng Anh)</label><Input value={data.subjectNameEn} onChange={(e) => updateField("subjectNameEn", e.target.value)} /></div>
                <div className="space-y-2"><label className="text-sm font-semibold">Mã Học Phần</label><Input value={data.subjectCode} onChange={(e) => updateField("subjectCode", e.target.value)} /></div>
                <div className="space-y-2"><label className="text-sm font-semibold">Số tín chỉ</label><Input type="number" value={data.credits} onChange={(e) => updateField("credits", Number(e.target.value))} /></div>
              </div>
              <div className="border p-4 rounded-md bg-slate-50">
                <h3 className="font-bold mb-4 text-sm uppercase text-slate-600">Phân bổ thời gian (Tiết)</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 items-end">
                  <label className="text-sm">Lý thuyết <Input type="number" className="mt-1 bg-white" value={data.timeAllocation?.theory || 0} onChange={(e) => updateTime("theory", Number(e.target.value))} /></label>
                  <label className="text-sm">Bài tập/Dự án <Input type="number" className="mt-1 bg-white" value={data.timeAllocation?.exercises || 0} onChange={(e) => updateTime("exercises", Number(e.target.value))} /></label>
                  <label className="text-sm">Thực hành <Input type="number" className="mt-1 bg-white" value={data.timeAllocation?.practice || 0} onChange={(e) => updateTime("practice", Number(e.target.value))} /></label>
                  <label className="text-sm">Tự học <Input type="number" className="mt-1 bg-white" value={data.timeAllocation?.selfStudy || 0} onChange={(e) => updateTime("selfStudy", Number(e.target.value))} /></label>
                  <div className="text-sm font-bold pb-2 text-right md:text-left">Tổng trên lớp: <span className="text-lg text-primary ml-2">{totalPeriods}</span></div>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-1">
                  <label className="text-sm font-semibold uppercase text-slate-500 text-[11px]">HP Tiên quyết</label>
                  <SearchableSelect 
                    options={[
                      { value: "", label: "-- Không có --" },
                      ...subjects.map(s => ({ value: s.code, label: `${s.code} - ${s.nameVi || s.name_vi}` }))
                    ]}
                    value={data.prerequisites || ""}
                    placeholder="Chọn môn học..."
                    onChange={(val) => updateField("prerequisites", String(val))}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-semibold uppercase text-slate-500 text-[11px]">HP Học trước</label>
                  <SearchableSelect 
                    options={[
                      { value: "", label: "-- Không có --" },
                      ...subjects.map(s => ({ value: s.code, label: `${s.code} - ${s.nameVi || s.name_vi}` }))
                    ]}
                    value={data.preCourses || ""}
                    placeholder="Chọn môn học..."
                    onChange={(val) => updateField("preCourses", String(val))}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-semibold uppercase text-slate-500 text-[11px]">HP Song hành</label>
                  <SearchableSelect 
                    options={[
                      { value: "", label: "-- Không có --" },
                      ...subjects.map(s => ({ value: s.code, label: `${s.code} - ${s.nameVi || s.name_vi}` }))
                    ]}
                    value={data.coCourses || ""}
                    placeholder="Chọn môn học..."
                    onChange={(val) => updateField("coCourses", String(val))}
                  />
                </div>
              </div>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <label className="text-sm font-semibold">Loại học phần <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background mt-1" value={data.courseType || ""} onChange={(e) => updateField("courseType", e.target.value)}><option value="Bắt buộc">Bắt buộc</option><option value="Tự chọn bắt buộc">Tự chọn bắt buộc</option><option value="Tự chọn tự do">Tự chọn tự do</option></select></label>
                <label className="text-sm font-semibold">Thuộc thành phần <Input className="mt-1" value={data.componentType || ""} onChange={(e) => updateField("componentType", e.target.value)} /></label>
              </div>
              <div className="border-t pt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                <label className="text-sm font-semibold">Ngày biên soạn <Input type="date" className="mt-1" value={data.datePrepared || ""} onChange={(e) => updateField("datePrepared", e.target.value)} /></label>
                <label className="text-sm font-semibold">Ngày chỉnh sửa <Input type="date" className="mt-1" value={data.dateEdited || ""} onChange={(e) => updateField("dateEdited", e.target.value)} /></label>
              </div>
            </TabsContent>

            {/* Các TabsContent khác (clos, plo, assessment, plan, materials, others) giữ nguyên code cũ vì không có màu cứng, nó sẽ tự ăn theo màu Primary mới */}
            <TabsContent value="clos" className="space-y-6 animate-in fade-in-50">
              <div><label className="font-bold block mb-2">2. Mô tả tóm tắt học phần</label><Textarea rows={4} value={data.description || ""} onChange={(e) => updateField("description", e.target.value)} /></div>
              <div className="bg-slate-50 p-4 rounded-md">
                <label className="font-bold block mb-2">3. Mục tiêu học phần (Course Objectives)</label>
                {data.objectives.map((obj, i) => (
                  <div key={i} className="flex gap-2 mb-2"><Input value={obj} onChange={(e) => { const newObj = [...data.objectives]; newObj[i] = e.target.value; updateField("objectives", newObj); }} /><Button variant="ghost" onClick={() => { const newObj = data.objectives.filter((_, idx) => idx !== i); updateField("objectives", newObj); }}>✕</Button></div>
                ))}
                <Button variant="outline" size="sm" className="mt-2 border-dashed" onClick={() => updateField("objectives", [...data.objectives, `CO${data.objectives.length + 1}: `])}>+ Thêm Mục Tiêu (CO)</Button>
              </div>
              <div>
                <label className="font-bold block mb-2">4. Chuẩn đầu ra học phần (CLOs)</label>
                <Table>
                  <TableHeader><TableRow><TableHead className="w-24">Mã CĐR</TableHead><TableHead>Mô tả chuẩn đầu ra</TableHead><TableHead className="w-12"></TableHead></TableRow></TableHeader>
                  <TableBody>{data.clos.map((clo, i) => (
                    <TableRow key={i}><TableCell><Input className="font-bold" value={clo.code} onChange={(e) => updateArrayItem("clos", i, { code: e.target.value })} /></TableCell><TableCell><Input value={clo.description} onChange={(e) => updateArrayItem("clos", i, { description: e.target.value })} /></TableCell><TableCell><Button variant="ghost" size="icon" onClick={() => removeArrayItem("clos", i)}>✕</Button></TableCell></TableRow>
                  ))}</TableBody>
                </Table>
                <Button variant="outline" className="w-full mt-2 border-dashed" onClick={() => addArrayItem("clos", { code: `CLO${data.clos.length + 1}`, description: "" })}>+ Thêm CLO Mới</Button>
              </div>
            </TabsContent>

            <TabsContent value="plo" className="animate-in fade-in-50">
               <div className="alert bg-teal-50 text-teal-700 p-3 mb-4 text-sm rounded-md border border-teal-100 flex items-start gap-3">
                  <span className="text-lg">💡</span>
                  <div>
                    <strong className="block mb-1">Hướng dẫn PLO Mapping:</strong>
                    <p className="opacity-90 leading-relaxed">
                      Điền các mức độ đóng góp của CLO vào PLO: <strong>I</strong> (Introduced), 
                      <strong>R</strong> (Reinforced), <strong>M</strong> (Mastered), <strong>A</strong> (Assessed).
                    </p>
                  </div>
               </div>
               
               {!data.program_id || data.clos.length === 0 ? (
                 <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-xl p-12 text-center">
                    <div className="text-4xl mb-4">📋</div>
                    <h3 className="text-lg font-bold text-slate-700 mb-2">Bảng PLO Mapping chưa sẵn sàng</h3>
                    <p className="text-slate-500 max-w-md mx-auto">
                      Vui lòng chọn <strong>Chương trình đào tạo</strong> (Tab 1) và 
                      thêm ít nhất một <strong>CLO</strong> (Tab 2) để bắt đầu ánh xạ.
                    </p>
                 </div>
               ) : (
                 <div className="border rounded-xl overflow-hidden shadow-sm bg-white">
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow className="bg-slate-50">
                          <TableHead className="w-32 bg-slate-100 font-bold border-r">CLO \ PLO</TableHead>
                          {plos.length > 0 ? (
                            plos.map((plo) => (
                              <TableHead key={plo.id} className="text-center min-w-[80px] font-bold text-teal-700 bg-teal-50/30">
                                {plo.code}
                                <div className="text-[9px] font-normal text-slate-400 uppercase truncate px-1" title={plo.nameVi}>
                                  {plo.nameVi || plo.name_vi}
                                </div>
                              </TableHead>
                            ))
                          ) : (
                            <TableHead className="text-center text-slate-400 italic font-normal">
                              Đang tải danh sách PLO...
                            </TableHead>
                          )}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {data.clos.map((clo, i) => {
                          const rowMap = data.ploMapping?.find((p) => p.cloCode === clo.code) || { cloCode: clo.code, plos: {} };
                          
                          return (
                            <TableRow key={i} className="hover:bg-slate-50/50">
                              <TableCell className="font-bold bg-slate-50/50 border-r">{clo.code}</TableCell>
                              {plos.map((plo) => (
                                <TableCell key={plo.id} className="p-1 text-center">
                                  <input 
                                    className="w-full h-10 text-center uppercase border-none focus:ring-2 focus:ring-teal-500 rounded-md transition-all font-medium bg-transparent"
                                    placeholder="-"
                                    value={rowMap.plos[plo.code] || ""} 
                                    onChange={(e) => {
                                      const val = e.target.value.toUpperCase();
                                      // Only allows I, R, M, A or empty
                                      if (val !== "" && !["I", "R", "M", "A"].includes(val)) return;
                                      
                                      const newMapping = [...(data.ploMapping || [])];
                                      const existIdx = newMapping.findIndex((m) => m.cloCode === clo.code);
                                      
                                      if (existIdx >= 0) {
                                        newMapping[existIdx] = { 
                                          ...newMapping[existIdx], 
                                          plos: { ...newMapping[existIdx].plos, [plo.code]: val } 
                                        };
                                      } else {
                                        newMapping.push({ 
                                          cloCode: clo.code, 
                                          plos: { [plo.code]: val } 
                                        });
                                      }
                                      updateField("ploMapping", newMapping);
                                    }} 
                                  />
                                </TableCell>
                              ))}
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </div>
                 </div>
               )}
            </TabsContent>

            <TabsContent value="assessment" className="space-y-6 animate-in fade-in-50">
               <div className="bg-slate-50 p-4 rounded-md border border-slate-200 shadow-inner">
                  <label className="font-bold flex items-center gap-2 mb-2 text-slate-700">
                    <BookOpen className="w-4 h-4" /> 5. Nhiệm vụ của sinh viên
                  </label>
                  <Textarea 
                    rows={4} 
                    className="bg-white"
                    placeholder="VD: Dự lớp tối thiểu 80% thời gian; hoàn thành các bài tập..."
                    value={data.studentDuties || ""} 
                    onChange={(e) => updateField("studentDuties", e.target.value)} 
                  />
               </div>

               <div className="space-y-4">
                  <div className="flex justify-between items-center bg-teal-50 p-3 rounded-md border border-teal-100">
                    <div>
                      <h3 className="font-bold text-teal-800 flex items-center gap-2">
                        <LineChart className="w-5 h-5" /> 6. Phương pháp kiểm tra, đánh giá
                      </h3>
                      <p className="text-xs text-teal-600 mt-1">Hệ thống sẽ tự động tính tổng trọng số.</p>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <div className="text-[10px] uppercase text-slate-500 font-semibold mb-0.5">Tổng trọng số</div>
                        <div className={`text-2xl font-black transition-colors ${data.assessmentScheme.reduce((sum: number, item: any) => sum + (item.weight || 0), 0) === 100 ? 'text-green-600' : 'text-rose-500'}`}>
                          {data.assessmentScheme.reduce((sum: number, item: any) => sum + (item.weight || 0), 0)}%
                        </div>
                      </div>
                      <Button 
                        type="button" 
                        variant="default" 
                        size="sm" 
                        className="bg-teal-600 hover:bg-teal-700 shadow-sm"
                        onClick={() => addArrayItem("assessmentScheme", { component: "", method: "", clos: "", criteria: "", weight: 10 })}
                      >
                         + Thêm Thành Phần
                      </Button>
                    </div>
                  </div>

                  <div className="overflow-hidden border rounded-xl shadow-sm bg-white">
                    <Table>
                      <TableHeader>
                        <TableRow className="bg-slate-50 hover:bg-slate-50">
                          <TableHead className="w-[180px] font-bold">Thành phần đánh giá</TableHead>
                          <TableHead className="font-bold">Phương pháp / Hình thức</TableHead>
                          <TableHead className="w-[180px] font-bold">Đáp ứng CLO</TableHead>
                          <TableHead className="w-[100px] font-bold">Trọng số</TableHead>
                          <TableHead className="w-[10px]"></TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {data.assessmentScheme.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={5} className="text-center py-10 text-slate-400 italic">
                              Chưa có thành phần đánh giá nào.
                            </TableCell>
                          </TableRow>
                        ) : (
                          data.assessmentScheme.map((item: any, i: number) => (
                            <TableRow key={i} className="group hover:bg-slate-50/50">
                              <TableCell className="align-top">
                                <select 
                                  className="w-full h-10 px-3 py-2 rounded-md border border-input bg-background text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                  value={item.component} 
                                  onChange={(e) => updateArrayItem("assessmentScheme", i, { component: e.target.value })}
                                >
                                  <option value="">-- Chọn --</option>
                                  <optgroup label="Thường xuyên">
                                    <option value="Đánh giá quá trình">Đánh giá quá trình</option>
                                    <option value="Tham gia lớp">Tham gia lớp</option>
                                    <option value="Bài tập về nhà">Bài tập về nhà</option>
                                  </optgroup>
                                  <optgroup label="Định kỳ">
                                    <option value="Kiểm tra lần 1">Kiểm tra lần 1</option>
                                    <option value="Kiểm tra giữa kỳ">Kiểm tra giữa kỳ</option>
                                    <option value="Thực hành">Thực hành</option>
                                  </optgroup>
                                  <optgroup label="Tổng kết">
                                    <option value="Thi cuối kỳ">Thi cuối kỳ</option>
                                    <option value="Đồ án/Báo cáo">Đồ án/Báo cáo</option>
                                  </optgroup>
                                </select>
                              </TableCell>
                              <TableCell className="align-top">
                                <Input 
                                  placeholder="Ví dụ: Trắc nghiệm / Vấn đáp" 
                                  value={item.method} 
                                  onChange={(e) => updateArrayItem("assessmentScheme", i, { method: e.target.value })} 
                                />
                                <div className="mt-2">
                                  <Input 
                                    className="h-8 text-[11px] bg-slate-50/50" 
                                    placeholder="Tiêu chí đánh giá..." 
                                    value={item.criteria || ""} 
                                    onChange={(e) => updateArrayItem("assessmentScheme", i, { criteria: e.target.value })} 
                                  />
                                </div>
                              </TableCell>
                              <TableCell className="align-top">
                                <div className="flex flex-wrap gap-1.5 p-1 min-h-[40px]">
                                  {(data.clos || []).length > 0 ? (
                                    (data.clos || []).map((clo: any) => {
                                      const isSelected = item.clos?.split(',').map((s: string) => s.trim()).includes(clo.code);
                                      return (
                                        <Badge 
                                          key={clo.code} 
                                          variant={isSelected ? "default" : "outline"}
                                          className={`cursor-pointer transition-all select-none font-bold py-1 ${isSelected ? 'scale-105' : 'opacity-60 hover:opacity-100 hover:bg-slate-100'}`}
                                          onClick={() => {
                                            const currentClosArr = item.clos ? item.clos.split(',').map((s: string) => s.trim()).filter((s: string) => s) : [];
                                            const newClosArr = isSelected 
                                                ? currentClosArr.filter((c: string) => c !== clo.code)
                                                : [...currentClosArr, clo.code];
                                            updateArrayItem("assessmentScheme", i, { clos: newClosArr.join(', ') });
                                          }}
                                        >
                                          {clo.code}
                                        </Badge>
                                      );
                                    })
                                  ) : (
                                    <span className="text-[10px] text-slate-400 italic">Vui lòng tạo CLO trước</span>
                                  )}
                                </div>
                              </TableCell>
                              <TableCell className="align-top">
                                <div className="relative">
                                  <Input 
                                    type="number" 
                                    className="pr-8 font-bold text-center"
                                    value={item.weight} 
                                    onChange={(e) => updateArrayItem("assessmentScheme", i, { weight: Number(e.target.value) })} 
                                  />
                                  <span className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 text-xs shadow-none">%</span>
                                </div>
                              </TableCell>
                              <TableCell className="align-top pt-3">
                                <Button 
                                  variant="ghost" 
                                  size="icon" 
                                  className="opacity-0 group-hover:opacity-100 transition-opacity hover:bg-rose-50 hover:text-rose-600"
                                  onClick={() => removeArrayItem("assessmentScheme", i)}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </div>
               </div>
            </TabsContent>

            <TabsContent value="plan" className="animate-in fade-in-50">
               <div className="mb-2"><label className="font-bold">7. Kế hoạch giảng dạy và học tập</label></div><div className="border rounded-md overflow-hidden"><Table><TableHeader><TableRow><TableHead className="w-20">Tuần</TableHead><TableHead className="w-1/3">Nội dung</TableHead><TableHead className="w-24">CLOs</TableHead><TableHead>Hoạt động Dạy/Học</TableHead><TableHead className="w-32">Đánh giá</TableHead><TableHead className="w-10"></TableHead></TableRow></TableHeader><TableBody>{data.teachingPlan.map((row, i) => (<TableRow key={i}><TableCell className="align-top"><Input type="number" value={row.week} onChange={(e) => updateArrayItem("teachingPlan", i, { week: Number(e.target.value) })} /></TableCell><TableCell className="align-top"><Textarea className="min-h-[80px]" value={row.topic || ""} onChange={(e) => updateArrayItem("teachingPlan", i, { topic: e.target.value })} /></TableCell><TableCell className="align-top"><Input value={row.clos || ""} onChange={(e) => updateArrayItem("teachingPlan", i, { clos: e.target.value })} /></TableCell><TableCell className="align-top"><Textarea className="min-h-[80px]" value={row.activity || ""} onChange={(e) => updateArrayItem("teachingPlan", i, { activity: e.target.value })} /></TableCell><TableCell className="align-top"><Input value={row.assessment || ""} onChange={(e) => updateArrayItem("teachingPlan", i, { assessment: e.target.value })} /></TableCell><TableCell className="align-top"><Button variant="ghost" size="icon" onClick={() => removeArrayItem("teachingPlan", i)}>✕</Button></TableCell></TableRow>))}</TableBody></Table></div><Button variant="outline" className="w-full mt-2 border-dashed" onClick={() => addArrayItem("teachingPlan", { week: 1, topic: "", clos: "", activity: "", assessment: "" })}>+ Thêm Tuần / Chương</Button>
            </TabsContent>

            <TabsContent value="materials">
                <MaterialsTab data={data} readOnly={!isEditable} onUpdate={(idx, val) => updateArrayItem("materials", idx, { title: val })} onAdd={(type) => addArrayItem("materials", { type: type, title: "" })} onRemove={(idx) => removeArrayItem("materials", idx)}/>
            </TabsContent>

            <TabsContent value="others" className="space-y-6 animate-in fade-in-50">
              <div className="bg-white p-6 rounded-md border shadow-sm"><label className="font-bold block mb-3 text-lg">9. Yêu cầu khác về học phần</label><Textarea rows={8} className="resize-y" value={data.otherRequirements || ""} onChange={(e) => updateField("otherRequirements", e.target.value)} placeholder="Ví dụ: Sinh viên phải chuẩn bị Laptop cá nhân..." /></div>
            </TabsContent>
            </div>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { 
  Settings, 
  Bell, 
  Info, 
  Clock, 
  Building2, 
  Globe, 
  Image as ImageIcon,
  Loader2,
  CheckCircle2
} from "lucide-react";
import axios from "@/lib/axios";
import { Badge } from "@/components/ui/badge";

// Helper for notifications since sonner is not installed
const toast = {
  success: (msg: string) => alert(msg),
  error: (msg: string) => alert(msg),
};

interface SystemSetting {
  key: string;
  value: string;
  data_type: string;
  description: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SystemSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingKey, setUpdatingKey] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await axios.get("/settings");
      setSettings(response.data);
    } catch (error) {
      console.error("Failed to fetch settings", error);
      toast.error("Không thể tải cấu hình hệ thống");
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = async (key: string, value: string) => {
    setUpdatingKey(key);
    try {
      await axios.put(/settings/ + key, { value });
      toast.success("Cập nhật thành công");
      // Update local state without refetching
      setSettings(prev => prev.map(s => s.key === key ? { ...s, value } : s));
    } catch (error) {
      console.error("Update failed", error);
      toast.error("Lỗi khi cập nhật " + key);
    } finally {
      setUpdatingKey(null);
    }
  };

  const getSettingValue = (key: string) => settings.find(s => s.key === key)?.value || "";

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <p className="text-muted-foreground">Đang tải cấu hình hệ thống...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Cấu hình hệ thống</h1>
          <p className="text-muted-foreground"> Quản lý các tham số vận hành và thông tin tổ chức của SMD. </p>
        </div>
      </div>

      <Tabs defaultValue="workflow" className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:w-[400px] bg-white border">
          <TabsTrigger value="workflow" className="flex items-center gap-2">
            <Settings className="w-4 h-4" /> Cấu hình
          </TabsTrigger>
          <TabsTrigger value="info" className="flex items-center gap-2">
            <Building2 className="w-4 h-4" /> Thông tin
          </TabsTrigger>
        </TabsList>

        <TabsContent value="workflow" className="mt-6 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-600" /> Vận hành hệ thống
              </CardTitle>
              <CardDescription>Các tham số ảnh hưởng đến quy trình phê duyệt và thông báo.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="workflow_deadline_days" className="font-semibold">Hạn chót phê duyệt (ngày)</Label>
                  {updatingKey === "workflow_deadline_days" && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
                </div>
                <div className="flex gap-4 items-center">
                  <Input
                    id="workflow_deadline_days"
                    type="number"
                    defaultValue={getSettingValue("workflow_deadline_days")}
                    className="max-w-[120px]"
                    onBlur={(e) => {
                      if (e.target.value !== getSettingValue("workflow_deadline_days")) {
                        updateSetting("workflow_deadline_days", e.target.value);
                      }
                    }}
                  />
                  <p className="text-sm text-muted-foreground italic">Số ngày tối đa để người duyệt hoàn thành 1 bước trong quy trình phê duyệt 5 bước.</p>
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="current_academic_year" className="font-semibold">Năm học hiện hành</Label>
                <div className="flex gap-4 items-center">
                  <Input
                    id="current_academic_year"
                    defaultValue={getSettingValue("current_academic_year")}
                    className="max-w-[200px]"
                    onBlur={(e) => {
                      if (e.target.value !== getSettingValue("current_academic_year")) {
                        updateSetting("current_academic_year", e.target.value);
                      }
                    }}
                  />
                  <Badge variant="outline" className="text-blue-600 bg-blue-50">Active</Badge>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg bg-gray-50/50">
                <div className="space-y-1">
                  <Label className="text-base font-semibold flex items-center gap-2">
                    <Bell className="w-4 h-4 text-orange-500" /> Bật/tắt thông báo Email
                  </Label>
                  <p className="text-sm text-muted-foreground">Hệ thống sẽ gửi email tự động khi có đề cương cần duyệt hoặc bình luận mới.</p>
                </div>
                <Button 
                  variant={getSettingValue("enable_email_notifications") === "true" ? "default" : "outline"}
                  className={getSettingValue("enable_email_notifications") === "true" ? "bg-green-600 hover:bg-green-700" : ""}
                  onClick={() => updateSetting("enable_email_notifications", getSettingValue("enable_email_notifications") === "true" ? "true" : "false")}
                >
                  {getSettingValue("enable_email_notifications") === "true" ? "Đang bật" : "Đang tắt"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="info" className="mt-6 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="w-5 h-5 text-green-600" /> Thông tin Đơn vị
              </CardTitle>
              <CardDescription>Thông tin này được sử dụng trong xuất bản Đề cương học phần (Syllabus).</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-6">
                <div className="grid gap-2">
                  <Label htmlFor="UNIVERSITY_NAME" className="font-semibold">Tên trường / Học viện</Label>
                  <Input 
                    id="UNIVERSITY_NAME" 
                    defaultValue={getSettingValue("UNIVERSITY_NAME")}
                    onBlur={(e) => e.target.value !== getSettingValue("UNIVERSITY_NAME") && updateSetting("UNIVERSITY_NAME", e.target.value)}
                    placeholder="VD: Trường Đại học Công nghệ"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="UNIVERSITY_WEBSITE" className="font-semibold flex items-center gap-2">
                      <Globe className="w-4 h-4 text-gray-500" /> Website chính thức
                    </Label>
                    <Input 
                      id="UNIVERSITY_WEBSITE" 
                      defaultValue={getSettingValue("UNIVERSITY_WEBSITE")}
                      onBlur={(e) => e.target.value !== getSettingValue("UNIVERSITY_WEBSITE") && updateSetting("UNIVERSITY_WEBSITE", e.target.value)}
                      placeholder="https://example.edu.vn"
                    />
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="UNIVERSITY_LOGO_URL" className="font-semibold flex items-center gap-2">
                      <ImageIcon className="w-4 h-4 text-gray-500" /> Đường dẫn Logo (URL)
                    </Label>
                    <Input 
                      id="UNIVERSITY_LOGO_URL" 
                      defaultValue={getSettingValue("UNIVERSITY_LOGO_URL")}
                      onBlur={(e) => e.target.value !== getSettingValue("UNIVERSITY_LOGO_URL") && updateSetting("UNIVERSITY_LOGO_URL", e.target.value)}
                      placeholder="https://example.edu.vn/logo.png"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      
      <div className="flex items-center gap-2 text-sm text-muted-foreground bg-blue-50 p-3 rounded-lg border border-blue-100 italic">
        <CheckCircle2 className="w-4 h-4 text-blue-500" />
        Lưu ý: Các thay đổi sẽ được hệ thống tự động lưu lại khi bạn rời khỏi ô nhập liệu (onBlur).
      </div>
    </div>
  );
}

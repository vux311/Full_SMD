// apps/web/app/(main)/layout.tsx
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";

export default function MainLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="min-h-screen">
      {/* Sidebar cố định */}
      <div>
        <Sidebar />
      </div>

      {/* Khu vực nội dung chính */}
      <div className="md:pl-64 min-h-screen flex flex-col">
        <Header />
        <main className="p-6 flex-1 bg-gray-50/50">
          {children}
        </main>
      </div>
    </div>
  );
}
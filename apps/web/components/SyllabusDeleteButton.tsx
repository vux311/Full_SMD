"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogAction,
  AlertDialogCancel,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import axios from "@/lib/axios";

interface SyllabusDeleteButtonProps {
  id: number;
  onDeleteSuccess?: () => void;
}

export default function SyllabusDeleteButton({ id, onDeleteSuccess }: SyllabusDeleteButtonProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleDelete() {
    setLoading(true);
    try {
      await axios.delete(`/syllabuses/${id}`);
      alert("Xóa thành công!");
      if (onDeleteSuccess) {
        onDeleteSuccess();
      } else {
        router.push("/");
      }
    } catch (err: any) {
      console.error("Network error deleting syllabus:", err);
      const status = err?.response?.status || err?.status;
      const message = err?.response?.data?.detail || err?.message;
      if (status === 401) {
        alert("Phiên đăng nhập hết hạn.");
        router.push("/login");
        return;
      }
      alert(message || "Delete failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">Delete</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone. The syllabus will be permanently deleted.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction asChild>
            <Button variant="destructive" onClick={handleDelete} disabled={loading}>
              {loading ? "Deleting..." : "Confirm"}
            </Button>
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
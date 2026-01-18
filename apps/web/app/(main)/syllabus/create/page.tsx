"use client";

import React from "react";
import SyllabusEditForm from "@/components/SyllabusEditForm";
import { defaultSyllabus } from "@/components/Types";

export default function CreateSyllabusPage() {
  return <SyllabusEditForm initial={defaultSyllabus} />;
}

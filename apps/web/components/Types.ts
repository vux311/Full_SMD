export type SyllabusStatus = "DRAFT" | "PENDING_REVIEW" | "PENDING_APPROVAL" | "APPROVED" | "PUBLISHED" | "REJECTED" | "RETURNED";

export interface SyllabusData {
  id?: number;
  // Required backend IDs
  subjectId?: number;
  program_id?: number;
  academicYearId?: number;
  lecturerId?: number;
  headDepartmentId?: number;
  deanId?: number;
  
  status: SyllabusStatus;
  version?: string;
  dueDate?: string | null;
  assignedTo?: string | null;
  subjectNameVi: string;
  subjectNameEn: string;
  subjectCode: string;
  credits: number;
  lecturer?: string | null;
  programName?: string | null;
  academicYearName?: string | null;
  feedback?: string | null;
  timeAllocation: {
    theory: number;
    exercises: number;
    practice: number;
    selfStudy: number;
  };
  prerequisites: string | null;
  preCourses: string | null;
  coCourses: string | null;
  courseType: string | null;
  componentType: string | null;
  description: string | null;
  objectives: string[];
  clos: { code: string; description: string }[];
  ploMapping: {
    cloCode: string;
    plos: { [key: string]: string };
  }[];
  studentDuties: string | null;
  assessmentScheme: {
    component: string;
    method: string;
    clos: string;
    criteria: string;
    weight: number;
  }[];
  teachingPlan: {
    week: number;
    topic: string;
    clos: string;
    activity: string;
    assessment: string;
  }[];
  materials: {
    type: "Main" | "Ref";
    title: string;
  }[];
  otherRequirements: string | null;
  datePrepared: string | null;
  dateEdited: string | null;
  headDepartment?: string | null;
  dean?: string | null;
}

export const defaultSyllabus: SyllabusData = {
  status: "DRAFT",
  // Set default IDs to undefined - user MUST select these
  subjectId: undefined,
  program_id: undefined,
  academicYearId: undefined,
  lecturerId: undefined,
  headDepartmentId: undefined,
  deanId: undefined,
  
  subjectNameVi: "",
  subjectNameEn: "",
  subjectCode: "",
  credits: 3,
  timeAllocation: { theory: 0, exercises: 0, practice: 0, selfStudy: 0 },
  prerequisites: "",
  preCourses: "",
  coCourses: "",
  courseType: "Bắt buộc",
  componentType: "Cơ sở ngành",
  description: "",
  objectives: [],
  clos: [],
  ploMapping: [],
  studentDuties: "",
  assessmentScheme: [],
  teachingPlan: [],
  materials: [],
  otherRequirements: "Không",
  datePrepared: new Date().toISOString().split('T')[0],
  dateEdited: new Date().toISOString().split('T')[0],
  lecturer: "",
  headDepartment: "",
  dean: ""
};
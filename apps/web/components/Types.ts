export type SyllabusStatus = "Draft" | "Pending" | "Approved" | "Returned" | "Pending Approval";

export interface SyllabusData {
  id?: number;
  status: SyllabusStatus;
  version?: string;
  subjectNameVi: string;
  subjectNameEn: string;
  subjectCode: string;
  credits: number;
  timeAllocation: {
    theory: number;
    exercises: number;
    practice: number;
    selfStudy: number;
  };
  prerequisites: string;
  preCourses: string;
  coCourses: string;
  courseType: string;
  componentType: string;
  description: string;
  objectives: string[];
  clos: { code: string; description: string }[];
  ploMapping: {
    cloCode: string;
    plos: { [key: string]: string };
  }[];
  studentDuties: string;
  assessmentScheme: {
    component: string;
    method: string;
    clos: string;
    criteria: string;
    weight: number;
  }[];
  teachingPlan: {
    week: string;
    content: string;
    clos: string;
    activity: string;
    assessment: string;
  }[];
  materials: {
    type: "Main" | "Ref";
    content: string;
  }[];
  otherRequirements: string;
  datePrepared: string;
  dateEdited: string;
  lecturer: string;
  headDepartment: string;
  dean: string;
}

export const defaultSyllabus: SyllabusData = {
  status: "Draft",
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
# Syllabus Management & Digitalization (SMD) - UML Designs

## 1. Overall Use Case Diagram
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Student" as student
actor "Lecturer" as lecturer
actor "Head of Department (HoD)" as hod
actor "Academic Affairs (AA)" as aa
actor "Principal" as principal
actor "System Admin" as admin

rectangle "SMD - Syllabus Management & Digitalization" {
    package "Public & Search" {
        (Search Syllabus) as UC1
        (View Syllabus Detail) as UC2
        (AI Summary) as UC3
        (Semantic Search) as UC4
    }
    
    package "Syllabus Authoring" {
        (Create/Edit Syllabus) as UC5
        (AI Generation Support) as UC6
        (Import via OCR) as UC7
        (Submit for Review) as UC8
    }
    
    package "Review & Workflow" {
        (Collaborative Review) as UC9
        (HOD Approval - Level 1) as UC10
        (AA Approval - Level 2) as UC11
        (Principal Final Approval) as UC12
        (AI Change Detection) as UC13
        (Reject & Feedback) as UC14
    }
    
    package "System & Data Management" {
        (User & Role Management) as UC15
        (Subject & Program Config) as UC16
        (System Monitoring/Audit) as UC17
        (Report & KPI Dashboard) as UC18
    }
}

student --> UC1
student --> UC2
student --> UC3
student --> UC4

lecturer --> UC1
lecturer --> UC2
lecturer --> UC5
lecturer --> UC6
lecturer --> UC7
lecturer --> UC8

hod --> UC9
hod --> UC10
hod --> UC13
hod --> UC14

aa --> UC11
aa --> UC16
aa --> UC18

principal --> UC12
principal --> UC18

admin --> UC15
admin --> UC16
admin --> UC17

@enduml

---

## 2. Screen Flow Diagram
@startuml
skinparam state {
  BackgroundColor White
  BorderColor Black
}

[*] --> Login

state Login {
  [*] --> LoginForm
}

Login --> Dashboard : Authenticated

state Dashboard {
  [*] --> Overview
  Overview --> SearchSyllabus : Click Search
  Overview --> MySyllabus : Click My List (Lecturer)
  Overview --> ApprovalQueue : Click Pending (HoD/AA)
  Overview --> AdminPanel : Click Settings (Admin)
}

state SearchSyllabus {
    [*] --> SearchBar
    SearchBar --> SearchResults
    SearchResults --> SyllabusDetail : View
}

state MySyllabus {
    [*] --> List
    List --> SyllabusEdit : Create/Edit
    SyllabusEdit --> AISupport : Open Generate
    SyllabusEdit --> OCRUpload : Import PDF
    SyllabusEdit --> SubmitConfirm : Submit
}

state ApprovalQueue {
    [*] --> PendingList
    PendingList --> ComparisonView : Check AI Changes
    ComparisonView --> ApprovalAction : Approve/Reject
}

state SyllabusDetail {
    [*] --> DetailView
    DetailView --> AISummaryView : Request AI
    DetailView --> RelationshipTree : View Subject Map
}

Dashboard --> [*] : Logout
@enduml

---

## 3. Sequence Diagram (Syllabus Submission & AI Processing)
@startuml
actor Lecturer
boundary "Web App" as Web
control "Syllabus Controller" as Ctrl
control "Celery Worker" as Task
entity "Syllabus Service" as Svc
entity "AI Service" as AI
database "SQL Server" as DB
database "Redis/Elasticsearch" as ES

Lecturer -> Web : Submit Syllabus
Web -> Ctrl : POST /syllabuses/{id}/submit
Ctrl -> Svc : submit_syllabus(id)

Svc -> DB : Update status to PENDING
Svc -> ES : index_syllabus() (Sync/Async)

group AI Processing (Async)
    Svc -> Task : Dispatch generate_summary_task
    Task -> AI : summarize_syllabus(content)
    AI --> Task : summary_result
    Task -> DB : Store result in SyllabusSnapshot
    Task -> Web : SocketIO Notify Progress
end

Svc --> Ctrl : Success
Ctrl --> Web : 202 Accepted / 200 OK
Web --> Lecturer : Show "In Review" status
@enduml

---

## 4. Activity Diagram (Syllabus Workflow)
@startuml
|Lecturer|
start
:Draft Syllabus;
:Use AI Support / OCR;
if (Data Valid?) then (yes)
  :Submit for Review;
else (no)
  :Fix Data;
  detach
endif

|HoD|
:Receive Notification;
:Review Academic Content;
:Use AI Change Detection;
if (Approved?) then (yes)
  :Forward to AA;
else (no)
  :Return to Lecturer (Feedback);
  |Lecturer|
  :Edit based on Feedback;
  stop
endif

|Academic Affairs|
:Review PLO Mapping/Standards;
if (Standards met?) then (yes)
  :Approve for Final Release;
else (no)
  :Reject;
  |HoD|
endif

|Principal|
:Final Strategy Review;
:Public Release;
stop
@enduml

---

## 5. Package Diagram (Architecture)

### Frontend (Next.js)
@startuml
package "Frontend (React/Next.js)" {
    [app/] <<Routes>>
    [components/] <<UI/Logic>>
    [contexts/] <<State Management>>
    [lib/] <<API Clients/Utils>>
    [hooks/] <<Shared Logic>>
    
    [app/] ..> [components/]
    [app/] ..> [contexts/]
    [components/] ..> [lib/]
    [components/] ..> [ui/] : shadcn/ui
}
@enduml

### Backend (Python/Flask)
@startuml
package "Backend (Flask/Clean Architecture)" {
    [api/controllers] <<Handlers>>
    [services] <<Business Logic>>
    [domain/models] <<Entities>>
    [infrastructure/repositories] <<Data Access>>
    [infrastructure/databases] <<DB Config>>
    
    [api/controllers] ..> [services]
    [services] ..> [infrastructure/repositories]
    [infrastructure/repositories] ..> [domain/models]
    [infrastructure/repositories] ..> [infrastructure/databases]
    
    package "AI & Task Modules" {
        [tasks] <<Celery>>
        [ocr_service]
        [search_service]
    }
}
@enduml

Context:
○ Syllabus Management and Digitalization System of the University (SMD) project was developed to address the current challenges in managing textbooks across university courses and programs.
○ In traditional textbook management, universities often face problems such as decentralized textbook file storage (PDF/Word), inconsistent formatting, difficulty tracking version updates, and lack of transparent workflows for review and approval. Students and lecturers also face difficulties in accessing, comparing, or analyzing textbooks effectively across courses and academic years.
○ To overcome these challenges, the SMD system integrates a web platform that centralizes version control and workflow management. A key innovation of the project is the automated textbook management features, including AI-powered change detection, CLO–PLO mapping, and content summarization. These tools help standardize course content, track changes over time, and facilitate easy comparison between versions and courses.
○ The project aims to improve efficiency, accuracy, and transparency in course management, providing instructors, departments, and students with a streamlined system for accessing, reviewing, and analyzing course content, while supporting future expansion and potential integration with learning management systems.


● Proposed Solutions: The project “Syllabus Management and Digitization System (SMD)” aims to build a centralized platform to serve the management, lookup and analysis of syllabus for faculties, lecturers and students in the university. Currently, syllabuses are stored separately in PDF/Word files in many different sources, difficult to update and lack system connectivity. SMD aims to:
o Centralized Syllabus Digitization and Management: Allowing lecturers and departments to enter, edit and standardize syllabus content on a unified Web App. The system supports attaching standard metadata such as CLO (Input Standards), PLO (Output Standards), assessment weights, prerequisite knowledge, teaching content and learning materials. In addition, syllabuses can establish relationships with each other such as: “replace”, “update”, “new version”, supporting scientific management by school year.
o Flexible review workflow: Provides a syllabus review process in the following steps: Draft → Pending Review→ Pending Approval → Approved → Published, with the Reviewer/Approver role ensuring the quality of academic content and clear version history. The system stores the entire edit history to help the auditing or accreditation department easily look up.

3 Syllabus Management View, search, filter, and compare syllabus versions; access CLO–PLO mapping and module relationship tree; follow syllabus to receive update notifications.
4 Collaborative Review syllabus during the collaboration period, add comments, edit or delete your feedback, and report detected errors quickly.
5 Notification Receive real-time alerts about syllabus submissions, review deadlines, feedback, or rejection from higher authorities.authorities (for prompt action).



Student

No. Function Description
1 Search Search syllabus by Subject Name, Subject Code or Filter by Major/Semester.
2 View Detail View the entire syllabus content. Supports visual tools: AI Summary, Subject Tree (Which subject is studied first/last), and Output Standard Map.
3 Subscribe Click the "Follow" button to receive emails/notifications when the syllabus changes.
4 Feedback Send a quick report if you detect errors in the syllabus content.





Head of Department - HoD

No. Function Description
1 Syllabus
Review/ Approval Official Level 1 Approval. Verifies academic content, CLOs, and Syllabus compliance. Uses AI Change Detection for quick revision tracking. Decides to Approve (forward to Academic Affairs) or Reject/Require Edit (return to Lecturer with mandatory reason).
2 Collaborative
Review Management Manages the collaborative consultation among Department Lecturers. Monitor feedback within the set timeframe. Compiles input, finalizes the draft, and officially moves the Syllabus into the HOD's review pipeline.
3 Lookup &
Analysis Searches, filters, and looks up all Syllabus within the Department. Includes the Syllabus Version Comparison feature across years/courses to ensure consistency.
4 Notification Receives real-time notifications for critical events: Syllabus submission, end of Collaborative Review period, or Syllabus rejection by higher authorities (for prompt action).


Academic Affairs - AA

No. Function Description
1 Academic Approval Level 2 Official Approval. Verifies Syllabus alignment with Program Learning Outcomes (PLO Mapping) and overall institutional standards (Credit, Rubrics). Decides to Approve (send to Final Approver/Publish) or Reject (return to HOD/Lecturer).
2 Course/Program Management Manages high-level academic standards and structural data. Includes managing PLO standards, Program structure, and prerequisite/corequisite rules (Module Relationships) for the entire Faculty/Program.
3 Lookup &
Analysis Searches, filters, and looks up all Syllabus within the Department. Includes the Syllabus Version Comparison feature across years/courses to ensure consistency.
4 Notification Receives real-time notifications for critical events: Syllabus submission, end of Collaborative Review period, or Syllabus rejection by higher authorities (for prompt action).


Principal - Final Approver/Strategic Flow

No. Function Description

1 Final Strategic Approval Final approval of important academic documents/proposals.
2 System Oversight View system overview, reports and operational status.






● Non-functional requirement:
● Performance:
+ Response Time:
● The system ensures smooth response to basic user tasks (login, page change, list view) under stable network conditions.
● The Syllabus search function returns results within an acceptable time for the current database.
+ AI Processing:
● Tasks that require high computing resources (such as text comparison, CLO-PLO checking, content summarization) are designed to run in the background (background processing/asynchronous) so as not to interrupt the user experience.
● The system will send notifications to users after the AI processing is completed.
+ Concurrency:
● The system operates stably with the expected concurrent access volume serving the Faculty/School level (about 50-100 concurrent users).
● Reliability / Availability:
+ Data Safety:
● The system has a periodic database backup mechanism to prevent the risk of data loss.
● Ensure data integrity during the approval process status transition (Workflow).
+ Error Handling:
● The system has a mechanism to catch errors and display friendly, clear notifications to users when an incident occurs, avoiding sudden application crashes.
● System error logs are recorded to serve maintenance and error correction.
● Security:
+ Access Control:
● The system requires authentication for all users accessing management functions.
● Role-based authorization (RBAC): Ensures users can only access authorized resources and functions (e.g., Students cannot access Lecturer functions).
+ Data security:
● User passwords are one-way encrypted (Hashing) before being stored in the database.
● The system complies with basic Web security principles to prevent common errors such as SQL Injection and XSS.
● Usability:
+ User Interface:
● The interface is designed to be intuitive, consistent, and easy to use for non-technical users.
● Supports good display on popular browsers today (Chrome, Edge, Firefox).
+ Mobile Experience:
● The Student subsystem supports a Responsive or Mobile App interface, optimized for searching and reading information on mobile devices.
● Maintainability & Scalability
+ System architecture:
● The system is built according to the basic Service-oriented or Microservices architecture, clearly separating the Web application (Web App) and the intelligent processing module (AI Service).
● Allows upgrading or replacing AI models without significantly affecting the core structure of the management application.
+ Source code organization:
● The source code complies with programming conventions, is clearly organized to facilitate future development and maintenance.

(*) 3.2. Main proposal content (including result and product)
a. Theory and practice (document):

● Students should apply the software development process and UML 2.0 in the modeling system.
● The documents include User Requirements, Software Requirement Specifications, Architecture Design, Detail Design, System Implementation, Testing Document, Installation Guide, source code, and deployable software packages.
● Server-side technologies:
○ Server: Python
○ Database Design: MySQL + Redis
● Client-side technologies:
○ Web Client: ReactJS/NextJs
○ Mobile App: React native.
● AI & Crawler Module:
○ Architecture: Python Microservice (FastAPI + Celery) following Event-driven model (Redis/RabbitMQ).
○ AI Core & NLP:
■ Orchestration: LangChain.
■ Models: Hugging Face (PhoBERT/ViBERT), SentenceTransformers (Semantic check), KeyBERT & VnCoreNLP (Keyword/Relation).
■ GenAI: Llama 3 (Ollama) hoặc OpenAI/Gemini API (Summarization).
○ Data Processing:
■ Crawler: Selenium, BeautifulSoup.
■ OCR: VietOCR/Tesseract (xử lý PDF/Image)
○ Storage & Search:
■ DB: PostgreSQL + pgvector (Vector & Relational Data).
■ Search: Elasticsearch (Full-text).
■ Cache: Redis.
b. Products:
○ Web App for System Admin: – User Management, Workflow Config, System Parameters and Final Publishing.
○ Web App for Lecturer: – Create, edit and update Syllabus, Submit for Review, track feedback status and search for reference resources.
○ Web App for Reviewer & Approver (HOD & Academic Affairs): – Collaborative Review, use AI to detect changes, CLO-PLO Mapping and manage curriculum framework.
○ Web App for Strategic Approver (Rector): – Approve high-level strategic decisions, view Impact Analysis reports and monitor system performance indicators (Audit/KPIs).

# AUDIT: Missing OPTIONS for CORS Preflight

## ❌ Endpoints THIẾU OPTIONS (Cần sửa ngay)

### 1. Teaching Plan Controller
- ❌ POST `/teaching-plans/`
- ❌ PUT `/teaching-plans/<id>`
- ❌ DELETE `/teaching-plans/<id>`

### 2. System Settings Controller
- ❌ POST `/system-settings/`

### 3. Syllabus Material Controller
- ❌ POST `/syllabus-materials/`
- ❌ DELETE `/syllabus-materials/<id>`

### 4. Syllabus Comment Controller
- ❌ POST `/syllabus-comments/`
- ❌ PUT `/syllabus-comments/<id>/resolve`
- ❌ DELETE `/syllabus-comments/<id>`

### 5. Syllabus CLO Controller
- ❌ POST `/syllabus-clos/`
- ❌ PUT `/syllabus-clos/<id>`
- ❌ DELETE `/syllabus-clos/<id>`

### 6. Subject Relationship Controller
- ❌ POST `/subject-relationships/`
- ❌ DELETE `/subject-relationships/<id>`

### 7. Subject Controller
- ❌ POST `/subjects/`
- ❌ PUT `/subjects/<id>`
- ❌ DELETE `/subjects/<id>`

### 8. Student Controller
- ❌ POST `/student/subscribe`
- ❌ POST `/student/report`

### 9. Rubric Controller
- ❌ POST `/rubrics/`
- ❌ PUT `/rubrics/<id>`
- ❌ DELETE `/rubrics/<id>`

### 10. Role Controller
- ❌ POST `/roles/`

### 11. Program Outcome Controller
- ❌ POST `/program-outcomes/`
- ❌ PUT `/program-outcomes/<id>`
- ❌ DELETE `/program-outcomes/<id>`

### 12. Program Controller
- ❌ POST `/programs/`
- ❌ PUT `/programs/<id>`
- ❌ DELETE `/programs/<id>`

### 13. File Controller
- ❌ POST `/files/upload`

### 14. Faculty Controller
- ❌ POST `/faculties/`
- ❌ PUT `/faculties/<id>`
- ❌ DELETE `/faculties/<id>`

### 15. Department Controller
- ❌ POST `/departments/`
- ❌ PUT `/departments/<id>`
- ❌ DELETE `/departments/<id>`

### 16. CLO-PLO Mapping Controller
- ❌ POST `/clo-plo-mappings/`
- ❌ DELETE `/clo-plo-mappings/<id>`

### 17. Assessment Scheme Controller
- ❌ POST `/assessment-schemes/`
- ❌ PUT `/assessment-schemes/<id>`
- ❌ DELETE `/assessment-schemes/<id>`

### 18. Assessment Component Controller
- ❌ POST `/assessment-components/`
- ❌ PUT `/assessment-components/<id>`
- ❌ DELETE `/assessment-components/<id>`

### 19. Assessment CLO Controller
- ❌ POST `/assessment-clos/`
- ❌ DELETE `/assessment-clos/`

### 20. Academic Year Controller
- ❌ POST `/academic-years/`
- ❌ PUT `/academic-years/<id>`
- ❌ DELETE `/academic-years/<id>`

### 21. AI Controller
- ❌ POST `/ai/generate`

### 22. Syllabus Controller (Workflow endpoints)
- ❌ POST `/syllabuses/<id>/submit`
- ❌ POST `/syllabuses/<id>/evaluate`

## ✅ Endpoints ĐÃ CÓ OPTIONS (OK)

### User Controller
- ✅ GET `/users/`
- ✅ GET `/users/<id>`
- ✅ GET `/users/me`
- ✅ POST `/users/`
- ✅ PUT `/users/<id>`
- ✅ DELETE `/users/<id>`

### Syllabus Controller
- ✅ GET `/syllabuses/`
- ✅ GET `/syllabuses/<id>`
- ✅ GET `/syllabuses/<id>/details`
- ✅ GET `/syllabuses/compare`
- ✅ POST `/syllabuses/`
- ✅ PUT `/syllabuses/<id>`
- ✅ DELETE `/syllabuses/<id>`

### Dashboard Controller
- ✅ GET `/stats/`

### Notification Controller
- ✅ GET `/notifications/`
- ✅ PUT `/notifications/<id>/read`

### Auth Controller
- ✅ POST `/auth/login`

### Public Controller
- ✅ GET `/public/syllabus`
- ✅ GET `/public/syllabus/<id>`

## 🔍 Frontend Field Name Issues

### User Management (FIXED)
- ❌ **WAS:** Frontend gửi `fullName` (camelCase)
- ✅ **NOW:** Sửa thành `full_name` (snake_case)
- ✅ **NOW:** Thêm `email` field (required)

### Potential Issues To Check
- Kiểm tra các form create/update khác có đang gửi đúng field names không
- Kiểm tra các schema có field nào required mà frontend không gửi không

## 📊 Summary

**Total Endpoints:** 93
**Missing OPTIONS:** ~60 endpoints
**Has OPTIONS:** ~20 endpoints
**Coverage:** ~21%

## 🚨 Priority Fix

**High Priority (User-facing features):**
1. Subject CRUD
2. Faculty CRUD  
3. Department CRUD
4. Program CRUD
5. Academic Year CRUD
6. Syllabus workflow (submit, evaluate)

**Medium Priority:**
7. Assessment components
8. Rubrics
9. CLO/PLO mappings

**Low Priority:**
10. File upload
11. Student features

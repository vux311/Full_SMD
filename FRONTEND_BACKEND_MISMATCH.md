# AUDIT: Frontend-Backend Endpoint Mismatches

## ❌ Endpoints SAI PATH

### 1. Profile Page
**File:** `app/(main)/profile/page.tsx`
- ❌ Frontend: `POST /users/change-password`
- ⚠️ Backend: **KHÔNG TỒN TẠI**
- 🔧 **Fix:** Cần thêm endpoint change password hoặc sửa frontend

### 2. Admin Settings Page  
**File:** `app/(main)/admin/settings/page.tsx`
- ❌ Frontend: `GET /admin/academic-years`
- ✅ Backend: `GET /academic-years/`
- 🔧 **Fix:** Đổi frontend thành `/academic-years/`

- ❌ Frontend: `POST /admin/academic-years`
- ✅ Backend: `POST /academic-years/`
- 🔧 **Fix:** Đổi frontend thành `/academic-years/`

- ❌ Frontend: `POST /admin/academic-years/:id/activate`
- ⚠️ Backend: **KHÔNG TỒN TẠI endpoint activate**
- 🔧 **Fix:** Cần thêm endpoint activate hoặc dùng PUT `/academic-years/:id`

### 3. Admin Logs Page
**File:** `app/(main)/admin/logs/page.tsx`  
- ❌ Frontend: `GET /admin/logs`
- ⚠️ Backend: **KHÔNG TỒN TẠI**
- 🔧 **Fix:** Cần tạo logs controller hoặc xóa trang này

### 4. Reviews Page
**File:** `app/(main)/reviews/page.tsx`
- ❌ Frontend: `POST /syllabuses/:id/approve`
- ⚠️ Backend: **KHÔNG TỒN TẠI** (có `/syllabuses/:id/evaluate`)
- 🔧 **Fix:** Đổi frontend dùng `/syllabuses/:id/evaluate` với action="approve"

- ❌ Frontend: `POST /syllabuses/:id/reject`
- ⚠️ Backend: **KHÔNG TỒN TẠI** (có `/syllabuses/:id/evaluate`)
- 🔧 **Fix:** Đổi frontend dùng `/syllabuses/:id/evaluate` với action="reject"

## ✅ DANH SÁCH ENDPOINTS BACKEND (Reference)

### Users
- GET `/users/`
- GET `/users/<id>`
- GET `/users/me`
- POST `/users/`
- PUT `/users/<id>`
- DELETE `/users/<id>`

### Academic Years
- GET `/academic-years/`
- POST `/academic-years/`
- PUT `/academic-years/<id>`
- DELETE `/academic-years/<id>`

### Syllabuses
- GET `/syllabuses/`
- GET `/syllabuses/<id>`
- POST `/syllabuses/`
- PUT `/syllabuses/<id>`
- DELETE `/syllabuses/<id>`
- POST `/syllabuses/<id>/submit`
- POST `/syllabuses/<id>/evaluate` - Có thể approve hoặc reject

## 🚨 PRIORITY FIXES

### HIGH (Blocking features)
1. ✅ **FIXED:** `/admin/users` paths → `/users/` 
2. ❌ **TODO:** `/admin/academic-years` → `/academic-years/`
3. ❌ **TODO:** `/syllabuses/:id/approve` → `/syllabuses/:id/evaluate?action=approve`
4. ❌ **TODO:** `/syllabuses/:id/reject` → `/syllabuses/:id/evaluate?action=reject`

### MEDIUM (Optional features)
5. ❌ **TODO:** Add `/users/change-password` endpoint
6. ❌ **TODO:** Add `/academic-years/:id/activate` endpoint or use PUT

### LOW (Admin only)
7. ❌ **TODO:** Create `/admin/logs` endpoint or remove logs page

## 📋 FIELD NAME ISSUES (FIXED)

### User Management ✅
- WAS: `fullName` (camelCase)
- NOW: `full_name` (snake_case) + added `email` field

## 🔍 NEXT STEPS

1. Restart Flask app để load tất cả OPTIONS endpoints mới
2. Fix frontend paths cho academic years
3. Fix frontend approve/reject để dùng evaluate endpoint
4. Test tất cả CRUD operations
5. Add missing endpoints nếu cần

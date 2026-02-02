import os
import json
import re
from datetime import datetime

# SEC-004: Prompt Injection Mitigation
def sanitize_prompt_input(text):
    """Basic sanitizer for AI prompts"""
    if not isinstance(text, str):
        return text
    # Pattern to detect common injection attempts
    patterns = [
        r"(?i)ignore\s+previous\s+(instructions|prompts)",
        r"(?i)forget\s+all\s+previous",
        r"(?i)system\s*:",
        r"(?i)###\s*instruction",
        r"(?i)\[INST\]",
        r"(?i)[\w\s]*you\s+are\s+now\s+a"
    ]
    for pattern in patterns:
        text = re.sub(pattern, "[INJECTION_ATTEMPT_FILTERED]", text)
    return text

# Prefer the new `google-genai` package
try:
    from google import genai
    _NEW_GENAI = True
except ImportError:
    try:
        import google.generativeai as genai
        _NEW_GENAI = False
    except ImportError:
        genai = None
        _NEW_GENAI = False


class AiService:
    def __init__(self, api_key: str = None, audit_repository=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.audit_repository = audit_repository

    def _validate_response_schema(self, data, required_keys):
        """SEC-005: Basic schema validation for AI responses"""
        if not isinstance(data, dict):
            return False
        return all(key in data for key in required_keys)

    def _log_usage(self, syllabus_id, action, in_tok, out_tok):
        if self.audit_repository and syllabus_id:
            try:
                self.audit_repository.create(syllabus_id, action, in_tok, out_tok)
            except Exception as e:
                print(f'Failed to log AI usage: {e}')

    def compare_syllabuses(self, base_data: dict, target_data: dict):
        """Analyze changes between two syllabus versions using AI"""
        if not self.api_key:
            return {"error": "Chưa cấu hình GEMINI_API_KEY"}

        prompt = f"""
        Bạn là một chuyên gia khảo thí và kiểm định chất lượng giáo dục. 
        Hãy phân tích sự thay đổi giữa hai phiên bản đề cương học phần dưới đây.
        
        Phiên bản 1 (Cũ): {sanitize_prompt_input(json.dumps(base_data, ensure_ascii=False))}
        Phiên bản 2 (Mới): {sanitize_prompt_input(json.dumps(target_data, ensure_ascii=False))}
        
        Hãy cung cấp báo cáo so sánh chi tiết bằng tiếng Việt, tập trung vào:
        1. Các thay đổi về cấu trúc (Số tín chỉ, phân bổ thời gian).
        2. Sự thay đổi về Chuẩn đầu ra (CLO) - có thêm/bớt hay thay đổi động từ Bloom không?
        3. Sự thay đổi về Nội dung giảng dạy và Hình thức đánh giá.
        4. Đánh giá tác động: Việc thay đổi này có làm tăng/giảm độ khó hay khối lượng học tập không?
        
        Trả về kết quả dưới dạng JSON với cấu trúc:
        {{
            "summary": "Tóm tắt ngắn gọn thay đổi chính (2-3 câu)",
            "detailed_analysis": [
                {{"category": "Tên hạng mục", "change_type": "Added/Removed/Modified/Unchanged", "description": "Mô tả chi tiết sự thay đổi"}}
            ],
            "impact_assessment": "Đánh giá chuyên môn về tác động của các thay đổi này",
            "is_significant_change": true/false
        }}
        """

        try:
            model_name = os.getenv('AI_MODEL', 'gemini-3-flash-preview')
            if model_name.startswith('models/'):
                model_name = model_name.replace('models/', '')

            if _NEW_GENAI:
                client = genai.Client(api_key=self.api_key)
                # Config with JSON mode if supported
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                text = response.text
            else:
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = response.text

            # Parse JSON from response
            try:
                # Remove markdown code blocks if any
                if text.startswith("```json"):
                    text = text.replace("```json", "", 1).replace("```", "", 1).strip()
                elif text.startswith("```"):
                    text = text.replace("```", "", 2).strip()
                
                result = json.loads(text)
                
                # SEC-005: Validate schema
                required = ["summary", "detailed_analysis", "impact_assessment", "is_significant_change"]
                if not self._validate_response_schema(result, required):
                    return {"summary": text, "error": "AI response missing required schema fields"}
                return result
            except Exception as pe:
                print(f"JSON Parse Error in AI Compare: {pe}")
                return {"summary": text, "error": "AI returned non-JSON response"}

        except Exception as e:
            print(f"AI Compare Error: {e}")
            return {"error": f"Lỗi AI: {str(e)}"}

    def analyze_clo_plo_alignment(self, clos_data: list, plos_data: list, mappings_data: list):
        """Phân tích mức độ đóng góp của CLO vào PLO giúp kiểm định chất lượng"""
        if not self.api_key:
            return {"error": "Chưa cấu hình GEMINI_API_KEY"}

        prompt = f"""
        Bạn là một chuyên gia về thiết kế chương trình đào tạo theo chuẩn đầu ra (Outcome-Based Education - OBE).
        Hãy phân tích ma trận thuận nghịch giữa Chuẩn đầu ra Học phần (CLO) và Chuẩn đầu ra Chương trình đào tạo (PLO).

        Danh sách CLOs: {sanitize_prompt_input(json.dumps(clos_data, ensure_ascii=False))}
        Danh sách PLOs: {sanitize_prompt_input(json.dumps(plos_data, ensure_ascii=False))}
        Ma trận Mapping hiện tại: {sanitize_prompt_input(json.dumps(mappings_data, ensure_ascii=False))}
        (Ghi chú: Mapping level I=Introduced, R=Reinforced, M=Mastered, A=Assessed)

        Hãy thực hiện:
        1. Đánh giá xem các CLO có nội dung phù hợp để hỗ trợ các PLO tương ứng không?
        2. Các động từ Bloom trong CLO đã đủ mức độ để đáp ứng yêu cầu của PLO chưa?
        3. Phát hiện các "điểm mù": Có PLO nào quan trọng mà không được hỗ trợ đủ bởi các CLO không?
        4. Đề xuất cải thiện Mapping hoặc cải thiện cách phát biểu CLO.

        Trả về kết quả JSON:
        {{
            "overall_score": 0-100,
            "analysis": "Nhận xét tổng quát",
            "strengths": ["Điểm mạnh 1", "Điểm mạnh 2"],
            "weaknesses": ["Điểm yếu 1", "Điểm yếu 2"],
            "suggestions": [
                {{"clo": "CLO code", "suggestion": "Đề xuất sửa nội dung hoặc mức độ Bloom"}},
                {{"plo": "PLO code", "issue": "PLO này đang thiếu đóng góp từ môn học này"}}
            ],
            "is_valid": true/false
        }}
        """

        try:
            model_name = os.getenv('AI_MODEL', 'gemini-3-flash-preview')
            if model_name.startswith('models/'):
                model_name = model_name.replace('models/', '')

            if _NEW_GENAI:
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                text = response.text
            else:
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = response.text

            try:
                if text.startswith("```json"):
                    text = text.replace("```json", "", 1).replace("```", "", 1).strip()
                
                result = json.loads(text)
                # SEC-005: Validate schema
                required = ["overall_score", "analysis", "suggestions", "is_valid"]
                if not self._validate_response_schema(result, required):
                    return {"analysis": text, "error": "AI response missing required schema fields"}
                return result
            except:
                return {"analysis": text, "error": "AI returned non-JSON response"}
        except Exception as e:
            return {"error": f"Lỗi AI: {str(e)}"}

    def generate(self, subject_name: str, syllabus_id: int = None):
        if not self.api_key:
            return {"error": "Chưa cấu hình GEMINI_API_KEY"}

        if genai is None:
            return {"error": "No generative AI client installed (install google-genai)"}

        # Complete Template matching frontend SyllabusData interface
        json_template = {
            "subject_name_vi": sanitize_prompt_input(subject_name),
            "subject_name_en": "...",
            "subject_code": "XXX101",
            "credits": 3,
            "time_allocation": { 
                "theory": 30, 
                "exercises": 15, 
                "practice": 15, 
                "self_study": 90 
            },
            "prerequisites": "Không có yêu cầu tiên quyết",
            "pre_courses": "Không",
            "co_courses": "Không",
            "course_type": "Bắt buộc",
            "component_type": "Cơ sở ngành",
            "description": "Mô tả chi tiết về môn học, mục tiêu, nội dung chính...",
            "objectives": [
                "Mục tiêu 1: Sinh viên hiểu được...",
                "Mục tiêu 2: Sinh viên vận dụng được...",
                "Mục tiêu 3: Sinh viên phân tích được..."
            ],
            "clos": [
                { "code": "CLO1", "description": "Trình bày được kiến thức cơ bản về..." },
                { "code": "CLO2", "description": "Vận dụng được kỹ năng..." },
                { "code": "CLO3", "description": "Phân tích được vấn đề..." },
                { "code": "CLO4", "description": "Đánh giá được..." },
                { "code": "CLO5", "description": "Thiết kế được..." }
            ],
            "plo_mapping": [
                { "clo_code": "CLO1", "plos": { "PLO1": "H", "PLO2": "M" } },
                { "clo_code": "CLO2", "plos": { "PLO3": "H", "PLO4": "M" } }
            ],
            "student_duties": "Sinh viên cần tham gia đầy đủ các buổi học, hoàn thành bài tập, đọc tài liệu trước buổi học...",
            "assessment_scheme": [
                { 
                    "component": "Điểm quá trình", 
                    "method": "Bài tập, thảo luận, kiểm tra nhỏ", 
                    "clos": "CLO1, CLO2", 
                    "criteria": "Độ chính xác, kỹ năng trình bày", 
                    "weight": 40 
                },
                { 
                    "component": "Kiểm tra giữa kỳ", 
                    "method": "Bài kiểm tra viết", 
                    "clos": "CLO1, CLO2, CLO3", 
                    "criteria": "Kiến thức lý thuyết, vận dụng", 
                    "weight": 20 
                },
                { 
                    "component": "Thi cuối kỳ", 
                    "method": "Bài thi viết hoặc project", 
                    "clos": "CLO3, CLO4, CLO5", 
                    "criteria": "Tổng hợp kiến thức, ứng dụng thực tế", 
                    "weight": 40 
                }
            ],
            "teaching_plan": [
                { "week": "1", "topic": "Giới thiệu môn học", "clos": "CLO1", "activity": "Giảng, thảo luận", "assessment": "Không" },
                { "week": "2", "topic": "Chủ đề 1", "clos": "CLO1", "activity": "Giảng, bài tập", "assessment": "Bài tập nhóm" },
                { "week": "3-15", "topic": "...", "clos": "...", "activity": "...", "assessment": "..." }
            ],
            "materials": [
                { "type": "Main", "title": "Tên tác giả, Năm xuất bản, Tên sách, Nhà xuất bản, ISBN (nếu có)" },
                { "type": "Main", "title": "..." },
                { "type": "Main", "title": "..." },
                { "type": "Ref", "title": "..." },
                { "type": "Ref", "title": "..." }
            ],
            "other_requirements": "Sinh viên cần có máy tính cá nhân cài đặt các phần mềm liên quan. Yêu cầu tham gia đầy đủ các buổi thực hành tại phòng lab. Cần chuẩn bị tài liệu và hoàn thành bài tập trước mỗi buổi học.",
            "date_prepared": "2026-01-15",
            "date_edited": "2026-01-15",
            "lecturer": "TS. Nguyễn Văn A",
            "head_department": "PGS.TS. Trần Văn B",
            "dean": "GS.TS. Lê Văn C"
        }

        prompt = f"""
Bạn là chuyên gia thiết kế chương trình đào tạo đại học tại Việt Nam. Hãy tạo một ĐỀ CƯƠNG HỌC PHẦN HOÀN CHỈNH cho môn học: "{subject_name}"

⚠️ YÊU CẦU BẮT BUỘC - PHẢI TUÂN THỦ 100%:
1. Trả về ĐÚNG format JSON như template, KHÔNG thêm markdown (```json) hay giải thích
2. ⭐ QUAN TRỌNG NHẤT: Điền ĐẦY ĐỦ TẤT CẢ 9 MỤC, KHÔNG được bỏ trống hay để "..."
3. Nội dung phải phù hợp với giáo dục đại học Việt Nam
4. Các mục còn ĐANG TRỐNG cần đặc biệt chú ý điền đầy đủ: MỤC 1 (subject_code, time_allocation, course_type), MỤC 5 (student_duties CHI TIẾT), MỤC 6 (assessment_scheme ĐẦY ĐỦ 3 items), MỤC 7 (teaching_plan ĐỦ 15 TUẦN), MỤC 9 (dates, lecturer, head_department, dean, other_requirements)

CHI TIẾT TỪNG MỤC:

📚 1. THÔNG TIN CHUNG:
- subject_name_en: Dịch chuẩn học thuật sang tiếng Anh
- subject_code: Mã HP 6-7 ký tự (VD: IT101, MATH201, PHY301)
- credits: Số tín chỉ (thường 2-4)
- time_allocation: theory (30-45 tiết), exercises (0-15), practice (0-30), self_study (90-180)
- prerequisites: "Không" hoặc tên HP cụ thể
- pre_courses: HP học trước (nếu có)
- co_courses: HP học song song (nếu có)
- course_type: "Bắt buộc" hoặc "Tự chọn"
- component_type: "Cơ sở ngành", "Chuyên ngành", "Đại cương"

🎯 2-4. MỤC TIÊU & CĐR:
- description: 3-5 câu mô tả tổng quan môn học
- objectives: Mảng 3-5 mục tiêu cụ thể, rõ ràng
- clos: TỐI THIỂU 5 CLOs, mỗi CLO:
  * code: "CLO1", "CLO2"...
  * description: Bắt đầu động từ hành động (Trình bày, Giải thích, Vận dụng, Phân tích, Đánh giá, Thiết kế...)
- plo_mapping: Map từng CLO với PLO1-PLO6, giá trị: "H" (Cao), "M" (Trung bình), "L" (Thấp)

👤 5. SINH VIÊN:
- student_duties: 3-5 câu về trách nhiệm SV (tham gia lớp, làm bài tập, tự học...)

📊 6. ĐÁNH GIÁ:
- assessment_scheme: TỐI THIỂU 3 thành phần, tổng weight = 100:
  * Quá trình (30-50%): Bài tập, thảo luận, kiểm tra nhỏ
  * Giữa kỳ (15-30%): Kiểm tra viết
  * Cuối kỳ (30-50%): Thi cuối kỳ hoặc project
  * Mỗi item có đầy đủ: component, method, clos, criteria, weight

📅 7. KẾ HOẠCH:
- teaching_plan: ĐỦ 15 TUẦN, mỗi tuần có:
  * week: "1", "2"... đến "15"
  * topic: Nội dung cụ thể của tuần đó
  * clos: CLO liên quan
  * activity: "Giảng", "Thảo luận", "Thực hành", "Bài tập nhóm"...
  * assessment: "Bài tập", "Kiểm tra", "Không"...

📖 8. TÀI LIỆU:
- materials: TỐI THIỂU 6 items (3 Main + 3 Ref):
  * type: "Main" hoặc "Ref"
  * title: "Tác giả (năm). Tên sách. Nhà xuất bản. ISBN (nếu có)"
  * Dùng tên sách THẬT hoặc hợp lý với môn học

🔧 9. KHÁC (BẮT BUỘC ĐIỀN ĐẦY ĐỦ):
- other_requirements: Yêu cầu khác (máy tính, phần mềm, thiết bị...) - ĐIỀN CỤ THỂ
- date_prepared: "2026-01-15" (định dạng YYYY-MM-DD)
- date_edited: "2026-01-15" (định dạng YYYY-MM-DD)
- lecturer: "TS. Nguyễn Văn A" (tên giả định với học hàm học vị)
- head_department: "PGS.TS. Trần Văn B" (PHẢI CÓ)
- dean: "GS.TS. Lê Văn C" (PHẢI CÓ)

⚠️⚠️⚠️ KIỂM TRA TRƯỚC KHI TRẢ VỀ:
✅ Mục 1: subject_code, credits, time_allocation (4 fields), course_type, component_type - CÓ HẾT CHƯA?
✅ Mục 5: student_duties ít nhất 3 câu - CÓ CHƯA?
✅ Mục 6: assessment_scheme có ĐỦ 3 items, tổng weight = 100 - CÓ CHƯA?
✅ Mục 7: teaching_plan có ĐỦ 15 tuần - CÓ CHƯA?
✅ Mục 9: dates, lecturer, head_department, dean, other_requirements - CÓ HẾT CHƯA?

TEMPLATE JSON CHUẨN (PHẢI ĐIỀN HẾT TẤT CẢ CÁC TRƯỜNG NÀY):
{json.dumps(json_template, ensure_ascii=False, indent=2)}

🚨🚨🚨 CẢNH BÁO CUỐI CÙNG: Output cuối cùng PHẢI là JSON hoàn chỉnh với TẤT CẢ các trường được điền, KHÔNG có "...", KHÔNG bỏ trống bất kỳ trường nào!
        """

        try:
            model_name = os.getenv('AI_MODEL', 'gemini-3-flash-preview')
            if model_name.startswith('models/'):
                model_name = model_name.replace('models/', '')
            
            max_tokens = int(os.getenv('AI_MAX_TOKENS', 16384))
            temperature = float(os.getenv('AI_TEMPERATURE', 1.0))

            if _NEW_GENAI:
                # Initialize client
                client = genai.Client(api_key=self.api_key)
                
                # In some versions of google-genai, the method is client.models.generate_content
                # and for others it might be slightly different. 
                # According to latest docs, it's client.models.generate_content(model='...', contents='...')
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "max_output_tokens": max_tokens,
                        "temperature": temperature
                    }
                )
                resp_text = response.text
            else:

                # Legacy package behavior
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(model_name)
                generation_config = {
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                    "response_mime_type": "application/json"
                }
                response = model.generate_content(prompt, generation_config=generation_config)
                resp_text = getattr(response, "text", "")

            # Clean markdown formatting if present
            clean_text = resp_text
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1].split("```")[0].strip()
            clean_text = clean_text.strip()
            
            # Log to file for debugging
            try:
                log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = os.path.join(log_dir, f"ai_response_{timestamp}.txt")
                
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
                    f.write(f"SUBJECT NAME: {subject_name}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    f.write("PROMPT:\n")
                    f.write("-" * 80 + "\n")
                    f.write(prompt + "\n")
                    f.write("-" * 80 + "\n\n")
                    
                    f.write("RAW RESPONSE:\n")
                    f.write("-" * 80 + "\n")
                    f.write(resp_text + "\n")
                    f.write("-" * 80 + "\n\n")
                    
                    f.write("CLEANED JSON:\n")
                    f.write("-" * 80 + "\n")
                    f.write(clean_text + "\n")
                    f.write("-" * 80 + "\n")
                    
                print(f"[AI LOG] Response saved to: {log_file}")
            except Exception as log_err:
                print(f"[AI LOG ERROR] Failed to write log: {log_err}")
            
            # Simple token estimation
            input_tokens = len(prompt.split())
            output_tokens = len(clean_text.split())

            # Log usage if syllabus_id provided
            self._log_usage(syllabus_id, 'GENERATE', input_tokens, output_tokens)

            return json.loads(clean_text)
        except Exception as e:
            print(f"AI Generate Error: {e}")
            # Attempt to log error usage
            try:
                self._log_usage(syllabus_id, 'ERROR', 0, 0)
            except: pass
            return {"error": str(e)}

    def summarize_syllabus(self, syllabus_data: dict, syllabus_id: int = None):
        """Summarize an existing syllabus using AI"""
        if not self.api_key:
            return {"error": "Chưa cấu hình GEMINI_API_KEY"}

        prompt = f"""
Bạn là một cố vấn học tập. Hãy tóm tắt đề cương học phần sau đây một cách ngắn gọn, dễ hiểu cho sinh viên.
Nội dung tóm tắt khoảng 150-200 từ, tập trung vào:
1. Môn học này dạy về cái gì nổi bật?
2. Kỹ năng quan trọng nhất sinh viên sẽ đạt được?
3. Lưu ý quan trọng về cách học hoặc đánh giá?

Dữ liệu đề cương:
Tên môn: {syllabus_data.get('subject_name_vi')}
Mô tả: {syllabus_data.get('description')}
Mục tiêu: {json.dumps(syllabus_data.get('objectives', []), ensure_ascii=False)}
CLOs: {json.dumps([c.get('description') for c in syllabus_data.get('clos', [])], ensure_ascii=False)}

YÊU CẦU: Trả về kết quả là chuỗi văn bản thuần túy, có xuống dòng hợp lý, KHÔNG CÓ định dạng Markdown (như bold, heading) hay JSON.
"""

        try:
            model_name = os.getenv('AI_MODEL', 'gemini-3-flash-preview')
            if model_name.startswith('models/'):
                model_name = model_name.replace('models/', '')

            if _NEW_GENAI:
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                resp_text = response.text
            else:
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                resp_text = getattr(response, "text", "")

            # Log usage
            try:
                self._log_usage(syllabus_id, 'SUMMARIZE', len(prompt.split()), len(resp_text.split()))
            except: pass

            return {"summary": resp_text.strip()}
        except Exception as e:
            print(f"AI Summarize Error: {e}")
            return {"error": str(e)}


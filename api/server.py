import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai_api_key = os.getenv("GENAI_API_KEY")
client = genai.Client(api_key=genai_api_key)

# Create FastAPI app
app = FastAPI(title="Logic Lens API")

# Add CORS middleware to allow requests from Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class CriterionResponse(BaseModel):
    name: str
    result: Literal["Đúng", "Sai", "Cần xem xét"]
    explanation: str
    points: float


class FactCheckResponse(BaseModel):
    criteria: List[CriterionResponse]
    sentiment: Literal["Trung lập", "Tiêu cực", "Tích cực"]


class TextRequest(BaseModel):
    text: str


# Create the model configuration
generation_config = types.GenerateContentConfig(
    system_instruction="""Bạn là trợ lý kiểm tra thông tin khách quan cho một tiện ích mở rộng Chrome. Nhiệm vụ của bạn là đánh giá văn bản được làm nổi bật dựa trên các tiêu chí được xác định trước và cho điểm trên thang điểm 20. Đối với mỗi tiêu chí, phân loại kết quả là:
- Đúng (đáp ứng tiêu chuẩn)
- Sai (không đáp ứng tiêu chuẩn)
- Cần xem xét (không chắc chắn, cần phân tích sâu hơn)

Đưa ra lời giải thích ngắn gọn bằng tiếng Việt cho mỗi phân loại. Không đưa ra ý kiến cá nhân hoặc đồng ý với người dùng; chỉ dựa trên văn bản và các nguồn đáng tin cậy (ví dụ: Bộ Y tế, Bộ Nông nghiệp, WHO, FDA, NCBI). Ngoài ra, phân loại cảm xúc của văn bản là Trung lập, Tiêu cực hoặc Tích cực để phản ánh giọng điệu của nó.

QUAN TRỌNG: Phản hồi phải là một đối tượng JSON hoàn chỉnh và hợp lệ.""",
    temperature=1,
    top_p=0.95,
    top_k=64,
    max_output_tokens=2000,
    response_mime_type="application/json",
    response_schema=FactCheckResponse,
)


@app.post("/api/fact-check", response_model=FactCheckResponse)
async def fact_check(request: TextRequest):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=f"""Đánh giá văn bản sau dựa trên các tiêu chí:

1. Nguồn gốc thông tin (3 điểm)
   - Nguồn được xác định rõ ràng?
   - Nguồn đáng tin cậy?
   - Có thể xác minh được?

2. Tính chính xác và logic (5 điểm)
   - Thông tin có chính xác không?
   - Có sai lầm logic không?
   - Có mâu thuẫn nội bộ không?
   - Có phù hợp với kiến thức khoa học không?

3. Ngôn ngữ và cách trình bày (3 điểm)
   - Văn phạm và chính tả có đúng không?
   - Cách viết có rõ ràng, mạch lạc không?
   - Có sử dụng từ ngữ không phù hợp không?

4. Tính khách quan (3 điểm)
   - Có thiên vị không?
   - Có cố tình gây hiểu lầm không?
   - Có đưa ra đầy đủ các khía cạnh không?

5. Thao túng cảm xúc (3 điểm)
   - Có sử dụng ngôn ngữ kích động không?
   - Có tạo ra nỗi sợ hãi vô cớ không?
   - Có gợi ý không có căn cứ không?

6. Bằng chứng và dẫn chứng (3 điểm)
   - Có cung cấp bằng chứng cụ thể không?
   - Bằng chứng có đáng tin cậy không?
   - Có thể kiểm chứng được không?

Văn bản cần đánh giá: {request.text}""",
            config=generation_config,
        )

        if not response.text:
            raise HTTPException(
                status_code=500, detail="Không nhận được phản hồi từ mô hình"
            )

        fact_check = FactCheckResponse.model_validate_json(response.text)
        return fact_check

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

import os
import json
import google.genai as genai
from google.genai import types
from langsmith import traceable
from dotenv import load_dotenv
from typing import List, Literal
from pydantic import BaseModel

load_dotenv()
genai_api_key = os.getenv("GENAI_API_KEY")
client = genai.Client(api_key=genai_api_key)


class CriterionResponse(BaseModel):
    name: str
    result: Literal["Đúng", "Sai", "Cần xem xét"]  # Vietnamese values
    explanation: str
    points: float


class FactCheckResponse(BaseModel):
    criteria: List[CriterionResponse]
    sentiment: Literal["Trung lập", "Tiêu cực", "Tích cực"]  # Vietnamese values


# Create the model
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


# Setup LangSmith trace
@traceable
def basic_score(user_input: str) -> FactCheckResponse:
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

Văn bản cần đánh giá: {user_input}

QUAN TRỌNG: Phản hồi phải là một đối tượng JSON hoàn chỉnh và hợp lệ, không có văn bản ở cuối.""",
            config=generation_config,
        )

        if (response.text is None) or (response.text == ""):
            raise ValueError("Không nhận được phản hồi từ mô hình")

        try:
            # Parse the response into our Pydantic model
            data = json.loads(response.text)
            fact_check = FactCheckResponse.model_validate(data)

            # Calculate and print total score
            total_score = sum(criterion.points for criterion in fact_check.criteria)
            print(f"\nTổng điểm: {total_score}/20")

            return fact_check
        except json.JSONDecodeError as e:
            print(f"\nLỗi phân tích JSON: {str(e)}")
            print("Nội dung phản hồi gây lỗi:")
            print(
                response.text[max(0, e.pos - 50) : min(len(response.text), e.pos + 50)]
            )
            raise
        except Exception as e:
            print(f"\nLỗi xử lý phản hồi: {str(e)}")
            raise

    except Exception as e:
        print(f"\nLỗi tạo phản hồi: {str(e)}")
        raise


text = """🪴🪴THÍ NGHIỆM ĐẶT 2 TRÁI BẮP GẦN NƠI CÓ SÓC
Sóc chê bắp biến đổi gen (GMO), gặm có mấy nhát là nó bỏ, trái bắp organic (thuần chủng) thì nó ăn gần hết.
Đến cả loài vật hoang dã còn tránh xa thức ăn biến đổi gen, sao con người chúng ta lại tạo ra nó và tiêu thụ nó?
"Đây là một dự án mà con trai tôi đã thực hiện khi lấy bằng Nông nghiệp bền vững năm 2005 tại Cao đẳng cộng đồng Central Carolina ở Pittsboro, NC.
Nó nói khá nhiều về tất cả những gì chúng ta cần biết về các sản phẩm GMO. Ngay cả những con sóc cũng không ăn nó. Chúng biết rằng có điều gì đó không ổn với nó".
~ Russell Turner
P/S: Dành cho ai chưa biết thì bắp biển đổi gen phổ biến mà chúng ta hay ăn, rồi làm sữa bắp, chính là bắp Mỹ (bắp ngọt) nhé!
Ngoài ra có bạn sẽ thắc mắc trong hình này sao bắp GMO lại nhỏ hơn bắp thường? Thì bạn hãy tìm hiểu lại những mục đích của các loại thực phẩm biến đổi gen nhé. 
Không phải cứ GMO thì sẽ to hơn loại thường đâu, có thể là sản phẩm GMO chống chịu sâu bệnh hay kháng thuốc bảo vệ thực vật tốt hơn, ngắn ngày hơn, ăn thơm và ngọt hơn chẳng hạn. 
Hoặc là bạn nghĩ đi, nếu sóc còn chê thì chắc là côn trùng cũng sẽ chê, đồng nghĩa nó sẽ được bảo quản dễ dàng và lâu hơn nữa.
"""

result = basic_score(text)
print("\nKết quả kiểm tra:")
print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))

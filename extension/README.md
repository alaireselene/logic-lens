# Logic Lens - Chrome Extension

Chrome extension để kiểm tra độ tin cậy của thông tin trên web.

## Cài đặt

### Backend API

1. Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

2. Tạo file `.env`:

```
GENAI_API_KEY=your_api_key_here
```

3. Chạy server:

```bash
cd api
uvicorn server:app --reload
```

### Chrome Extension

1. Mở `chrome://extensions/`
2. Bật "Developer mode"
3. Click "Load unpacked" và chọn thư mục `extension`

## Cách sử dụng

1. Chọn đoạn văn bản trên web
2. Đợi tooltip hiện kết quả phân tích:
   - Tổng điểm đánh giá (/20)
   - Đánh giá từng tiêu chí
   - Chi tiết giải thích
   - Tone cảm xúc

## Tiêu chí đánh giá

- Nguồn gốc thông tin (3đ)
- Tính chính xác và logic (5đ)
- Ngôn ngữ và cách trình bày (3đ)
- Tính khách quan (3đ)
- Thao túng cảm xúc (3đ)
- Bằng chứng và dẫn chứng (3đ)

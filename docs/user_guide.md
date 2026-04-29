# Hướng dẫn Cập nhật Dữ liệu & Huấn luyện lại Mô hình

Để tự cập nhật dữ liệu từ một file Excel mới và huấn luyện lại mô hình AI, bạn hãy thực hiện theo các bước sau:

## Bước 1: Chuẩn bị file dữ liệu
Đảm bảo file Excel của bạn có cấu trúc các sheet giống như file mẫu (`SmartLogistics_TrainingData.xlsx`). Các sheet cần có:
*   `🏭 Warehouses`
*   `🏍️ Shippers`
*   `🛒 Orders`
*   `📦 Delivery Records`

## Bước 2: Đưa file vào hệ thống (Docker)
Giả sử file của bạn tên là `NewData.xlsx` và đang ở thư mục hiện tại:

```bash
docker cp NewData.xlsx web_-backend-1:/app/NewData.xlsx
```

## Bước 3: Nạp dữ liệu vào Cơ sở dữ liệu (Seeding)
Chạy lệnh sau để xóa dữ liệu cũ và nạp dữ liệu từ file mới:

```bash
docker compose exec -e XLSX_PATH=/app/NewData.xlsx backend python scripts/seed.py
```

## Bước 4: Huấn luyện lại mô hình AI
Sau khi nạp dữ liệu, bạn cần chạy script huấn luyện để mô hình học từ dữ liệu mới:

```bash
docker compose exec backend python scripts/train.py
```

## Bước 5: Cập nhật dịch vụ
Cuối cùng, hãy khởi động lại backend để nó sử dụng mô hình vừa được huấn luyện:

```bash
docker compose restart backend
```

---

### Mẹo: Kiểm tra kết quả
Bạn có thể kiểm tra xem dữ liệu đã lên chưa bằng lệnh:
```bash
curl -s http://localhost:8000/api/v1/stats
```
Lệnh này sẽ trả về số lượng đơn hàng và shipper hiện có trong hệ thống.

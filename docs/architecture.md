# Kiến Trúc Hệ Thống & Thuật Toán Hybrid

LogiSense AI không chỉ sử dụng các thuật toán truyền thống mà còn kết hợp Machine Learning để tối ưu hóa hiệu quả thực tế dựa trên dữ liệu lịch sử và điều kiện thời gian thực.

---

## 🧠 Sự kết hợp giữa AdaBoost và A* (The Hybrid Logic)

Thách thức lớn nhất trong logistics đô thị là sự biến động của giao thông. **Đường ngắn nhất (Dijkstra) thường xuyên bị kẹt xe.**

### 1. Dự đoán ETA với AdaBoost Regressor
Chúng tôi chọn **AdaBoost** (Adaptive Boosting) vì khả năng hội tụ nhanh và xử lý cực tốt các đặc trưng phi tuyến tính (như mối quan hệ giữa giờ tan tầm và tốc độ di chuyển).

- **Input Features:** `Distance`, `Traffic_Level (0-3)`, `Hour_of_Day (Cyclic)`, `Day_of_Week`, `Number_of_Stops`.
- **Inference Speed:** < 5ms (nhờ nạp mô hình vào bộ nhớ đệm Singleton).
- **Mục tiêu:** Tính toán "Chi phí thời gian" dự kiến cho mỗi cạnh (edge) trên bản đồ.

### 2. Tối ưu lộ trình với A* Pathfinding
Thay vì sử dụng hàm Heuristic $h(n)$ là khoảng cách Euclid (chim bay), chúng tôi sử dụng kết quả từ AdaBoost làm **AI-driven Heuristic**.

- **$g(n)$:** Thời gian thực tế đã đi qua từ điểm xuất phát đến node hiện tại.
- **$h(n)$:** Thời gian dự kiến (ETA) từ node hiện tại đến đích, được dự báo bởi AdaBoost.
- **$f(n) = g(n) + h(n)$:** Thuật toán luôn ưu tiên mở rộng các node có tổng thời gian dự kiến thấp nhất.

---

## 🔄 Luồng dữ liệu (Data Pipeline)

1. **Ingestion:** Thu thập tọa độ GPS và mức độ giao thông từ API.
2. **Preprocessing:** Feature Engineering (Encoding thời gian tuần hoàn để mô hình hiểu được sự lặp lại của các khung giờ trong ngày).
3. **Inference Layer:** 
   - Bước 1: **KMeans Clustering** gán các đơn hàng gần nhau cho cùng một shipper.
   - Bước 2: **A* + AdaBoost** sắp xếp thứ tự giao hàng tối ưu trong mỗi cụm.
4. **Monitoring:** Kết quả được đẩy về Dashboard và cập nhật liên tục qua WebSocket.

---

## 🛠️ Hạ tầng kỹ thuật (Infrastructure Stack)

- **Backend Logic:** FastAPI xử lý đồng thời (Concurrency) tốt các yêu cầu tính toán lộ trình.
- **Caching Layer (Redis):** Lưu trữ các kết quả dự đoán cho các cung đường phổ biến để giảm tải cho mô hình ML.
- **Retraining Loop (MLflow + Celery):** Hệ thống tự động thu thập dữ liệu giao hàng thực tế để tái huấn luyện (Retrain) mô hình AdaBoost hàng tuần, đảm bảo độ chính xác không bị "drifting" theo thời gian.

---

## 🗺️ Lộ trình phát triển (Roadmap)

- [ ] **Giai đoạn 1:** Tích hợp dữ liệu thời tiết (Mưa/Ngập) vào mô hình AdaBoost.
- [ ] **Giai đoạn 2:** Hỗ trợ tối ưu hóa đa phương tiện (Xe máy, Xe tải, Robot giao hàng).
- [ ] **Giai đoạn 3:** Áp dụng Reinforcement Learning (Học tăng cường) để shipper tự tối ưu hóa dựa trên kinh nghiệm thực tế.

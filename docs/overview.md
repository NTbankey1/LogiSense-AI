# Tổng Quan Dự Án LogiSense AI (Smart Logistics)

**LogiSense AI** là một hệ thống quản lý logistics thông minh, kết hợp giữa trí tuệ nhân tạo (Machine Learning) và các thuật toán tối ưu hóa để giải quyết bài toán giao hàng hiệu quả.

---

## 🎯 Mục tiêu dự án

Hệ thống được thiết kế để giải quyết bài toán cốt lõi trong vận tải: **Làm thế nào để giao hàng nhanh nhất trong điều kiện giao thông biến động?**

- **Dự đoán thời gian giao hàng (ETA):** Sử dụng mô hình **AdaBoost** để dự đoán chính xác thời gian giao hàng dựa trên khoảng cách, mật độ giao thông, thời gian trong ngày và số điểm dừng.
- **Tối ưu hóa lộ trình:** Kết hợp thuật toán **A*** với heuristic từ mô hình AdaBoost để tìm ra lộ trình nhanh nhất (về mặt thời gian) cho shipper thay vì chỉ dựa trên khoảng cách địa lý.
- **Quản lý vận hành:** Theo dõi đơn hàng, shipper và hiệu suất hệ thống trong thời gian thực thông qua bộ công cụ giám sát trực quan.

---

## 🚀 Các tính năng chính (Visual Highlights)

1. **Dashboard Điều Hành:** Cung cấp cái nhìn tổng thể về hiệu suất, số lượng đơn hàng và trạng thái shipper.
   > ![Dashboard](assets/dashboard.png)
2. **Quản lý Đơn hàng:** Tạo mới, theo dõi và ưu tiên các yêu cầu giao hàng.
   > ![Orders](assets/orders.png)
3. **Bộ não Tối ưu hóa:** Sử dụng AI để phân cụm đơn hàng (KMeans) và tìm lộ trình tối ưu bằng A*.
   > ![Optimization](assets/optimization.png)
4. **Giám sát Thời gian thực:** Hiển thị vị trí shipper và tiến độ đơn hàng trên bản đồ nhiệt.
   > ![Monitor](assets/monitor.png)

---

## 🛠️ Công nghệ cốt lõi

### Backend Layer
- **Framework:** FastAPI (Python 3.12) - Đảm bảo hiệu năng cao và hỗ trợ async.
- **Machine Learning:** Scikit-learn với mô hình **AdaBoost Regressor** chuyên biệt cho ETA.
- **Database:** PostgreSQL (Lưu trữ nghiệp vụ) & Redis (Caching kết quả dự báo).
- **MLOps:** MLflow để quản lý vòng đời mô hình và Celery để chạy job huấn luyện lại.

### Frontend Layer
- **Framework:** React + TypeScript (Vite).
- **Styling:** Vanilla CSS hiện đại với thiết kế Dark-mode/Premium.
- **Real-time:** WebSockets/Axios cho cập nhật dữ liệu liên tục.

---

## 📈 Giá trị mang lại

- **Tiết kiệm 15-20% thời gian** di chuyển của shipper nhờ tránh các điểm kẹt xe dự báo.
- **Tăng độ chính xác ETA lên 90%** so với các phương pháp tính toán truyền thống.
- **Tự động hóa hoàn toàn** khâu phân chia đơn hàng, giảm tải cho bộ phận điều phối.

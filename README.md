# Phân tích dữ liệu bán lẻ trực tuyến (Online Retail)

Bài tập lớn học phần **Lập trình Python – PTIT**. Đề tài: *Doanh thu và xu hướng bán hàng*.
Dữ liệu: **Online Retail (UCI)**, giao dịch của một cửa hàng quà tặng trực tuyến ở Anh, 01/12/2010 – 09/12/2011
(541.909 dòng, 8 cột). Chi tiết nguồn và ý nghĩa các trường xem [docs/mo_ta_du_lieu.md](docs/mo_ta_du_lieu.md).

## Cài đặt và chạy

Cần Python 3.10 trở lên. Mở terminal trong thư mục dự án:

```bash
pip install -r requirements.txt
python main.py
```

Chương trình chạy **không cần Internet** (khoảng 15 giây) và lưu kết quả vào `outputs/`.
Kiểm thử phần làm sạch dữ liệu: `python kiem_thu.py`.

## Cấu trúc thư mục

```
BTL_python1/
├── main.py           # Chương trình chính: gọi lần lượt các bước
├── du_lieu.py        # Lớp RetailData: đọc, kiểm tra, làm sạch, tạo cột mới, lọc, tìm kiếm, sắp xếp, lưu
├── phan_tich.py      # Thống kê mô tả + 7 hàm trả lời 7 câu hỏi phân tích
├── bieu_do.py        # 4 hàm vẽ biểu đồ Matplotlib
├── kiem_thu.py       # Kiểm thử đơn giản bằng assert
├── requirements.txt
├── data/
│   ├── raw/Online_Retail.csv              # Dữ liệu gốc
│   └── processed/online_retail_clean.csv  # Dữ liệu sau làm sạch (chương trình tạo ra)
├── outputs/          # Bảng kết quả (.csv) và biểu đồ (.png)
└── docs/
    ├── mo_ta_du_lieu.md         # Nguồn dữ liệu, ý nghĩa các trường, chất lượng dữ liệu
    ├── bang_phan_cong.md        # Phân công công việc, khai báo dùng AI
    └── hoc_python_qua_du_an.md  # Tài liệu học Python qua dự án (cho người mới)
```

## Chức năng chính

1. **Đọc và kiểm tra dữ liệu:** đọc CSV, kiểm tra đủ cột, in kiểu dữ liệu, số ô trống, số dòng trùng.
2. **Làm sạch (7 bước):** đổi kiểu ngày giờ, xóa trùng, bỏ mã không phải sản phẩm, tách đơn hủy,
   bỏ số lượng/đơn giá ≤ 0, xử lý ô trống, bỏ 2 dòng số lượng bất thường. Kết quả: 522.567 dòng.
3. **Tạo cột mới:** `Revenue = Quantity × UnitPrice`, `Month`, `Weekday`, `Hour`.
4. **Lọc / tìm kiếm / sắp xếp:** lọc theo quốc gia, tìm sản phẩm theo từ khóa, sắp xếp theo doanh thu.
5. **Phân tích bằng Pandas:** 7 câu hỏi trong bảng dưới.
6. **Biểu đồ:** 4 biểu đồ thuộc 3 loại (đường, cột ngang, histogram).

| # | Câu hỏi | Kỹ thuật | Biểu đồ |
|---|---|---|---|
| 1 | Doanh thu thay đổi thế nào theo tháng? | `groupby` + `sum` | Đường |
| 2 | Quốc gia nào đem lại nhiều doanh thu nhất? | `groupby` + `agg` | Cột ngang |
| 3 | 10 sản phẩm doanh thu cao nhất? | `groupby` + `agg` | Cột ngang |
| 4 | Khách mua nhiều vào thứ mấy, giờ nào? | **`pivot_table`** (thứ × giờ) | – |
| 5 | Một đơn hàng thường trị giá bao nhiêu? | `groupby` + `describe` | Histogram |
| 6 | Khách có quay lại mua không? | `groupby` + `agg` | – |
| 7 | Tỷ lệ hủy đơn bao nhiêu? | `groupby` + `nunique` | – |

**Vì sao dùng `pivot_table` ở câu 4:** để trải doanh thu thành bảng 2 chiều (mỗi hàng là một thứ trong tuần,
mỗi cột là một giờ), nhìn một bảng là thấy ngay khung giờ bán chạy.

## Hạn chế

- Tháng 12/2011 chỉ có dữ liệu đến ngày 09.
- Khoảng 25% dòng không có `CustomerID`, nên câu 6 chỉ xét khách có mã.
- Không có giá vốn nên chỉ phân tích doanh thu, không tính được lợi nhuận.
- Bước 7 dùng ngưỡng số lượng 10.000 cho đơn giản. Cách chính xác hơn là ghép từng dòng bán với dòng hủy tương ứng.


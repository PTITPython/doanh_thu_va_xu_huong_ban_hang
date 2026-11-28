# Doanh thu và xu hướng bán hàng

Bài tập lớn học phần **Lập trình Python – PTIT**. Đề tài 03: *Doanh thu và xu hướng bán hàng*.

Chương trình đọc dữ liệu bán hàng, làm sạch, tạo cột mới, trả lời 7 câu hỏi phân tích bằng Pandas
và vẽ biểu đồ tương tác bằng Plotly trong Jupyter Notebook.

## 1. Dữ liệu

| Mục | Nội dung |
|---|---|
| Tên | Sample Sales Data |
| Nguồn | Kaggle – https://www.kaggle.com/datasets/kyanyoga/sample-sales-data |
| Thời điểm truy cập | *(nhóm điền ngày tải dữ liệu)* |
| Nội dung | Đơn hàng bán sỉ mô hình sưu tầm (xe hơi, mô tô, máy bay, tàu, xe lửa…) của một công ty cho các cửa hàng ở 19 nước |
| Thời gian | 06/01/2003 – 31/05/2005 (năm 2005 chỉ có 5 tháng) |
| Quy mô | 2.823 dòng × 25 cột, file CSV 518 KB. Mỗi dòng là **1 sản phẩm trong 1 đơn hàng** |
| Tệp | `Data/raw_data.csv` (gốc), `Data/clean_data.csv` (sau làm sạch, do chương trình tạo) |

### Ý nghĩa các trường

| Trường | Ý nghĩa |
|---|---|
| `ORDERNUMBER` | Mã đơn hàng |
| `ORDERLINENUMBER` | Số thứ tự sản phẩm trong đơn |
| `QUANTITYORDERED` | Số lượng đặt |
| `PRICEEACH` | Đơn giá (bị giới hạn tối đa 100 trong dữ liệu gốc) |
| `SALES` | Thành tiền của dòng (USD) |
| `ORDERDATE` | Ngày đặt hàng (dạng `tháng/ngày/năm giờ:phút`) |
| `STATUS` | Trạng thái: Shipped, Resolved, Cancelled, On Hold, In Process, Disputed |
| `QTR_ID`, `MONTH_ID`, `YEAR_ID` | Quý, tháng, năm của ngày đặt |
| `PRODUCTLINE` | Dòng sản phẩm (7 dòng: Classic Cars, Vintage Cars, Motorcycles, Planes, Trucks and Buses, Ships, Trains) |
| `MSRP` | Giá bán lẻ đề xuất của nhà sản xuất |
| `PRODUCTCODE` | Mã sản phẩm |
| `CUSTOMERNAME` | Tên khách hàng (cửa hàng) |
| `PHONE` | Số điện thoại khách |
| `ADDRESSLINE1`, `ADDRESSLINE2` | Địa chỉ |
| `CITY`, `STATE`, `POSTALCODE`, `COUNTRY` | Thành phố, bang, mã bưu chính, quốc gia |
| `TERRITORY` | Vùng: NA (Bắc Mỹ), EMEA, APAC, Japan |
| `CONTACTLASTNAME`, `CONTACTFIRSTNAME` | Họ, tên người liên hệ |
| `DEALSIZE` | Quy mô dòng hàng: Small, Medium, Large |

## 2. Cài đặt và chạy

Cần Python 3.10 trở lên. Mở terminal ở thư mục dự án:

```bash
pip install -r requirements.txt
python main.py                 # đọc, làm sạch, phân tích, lưu kết quả CSV vào Outputs/
python -m Process.kiem_thu     # kiểm thử tự động phần làm sạch dữ liệu
```

Biểu đồ: mở từng notebook `Outputs/cauN_*.ipynb` trong VS Code hoặc Jupyter, chọn kernel Python rồi **Run All**.
Chương trình chạy **không cần Internet**.

## 3. Cấu trúc thư mục

```
doanh_thu_va_xu_huong_ban_hang/
├── main.py                  # Chương trình chính: gọi lần lượt các bước
├── requirements.txt
├── README.md
├── Data/
│   ├── raw_data.csv         # Dữ liệu gốc
│   └── clean_data.csv       # Dữ liệu sau làm sạch (main.py tạo ra)
├── Process/
│   ├── xu_li_du_lieu.py     # Lớp RetailData: đọc, kiểm tra, làm sạch, tạo cột, lọc, tìm, sắp xếp, lưu
│   ├── cau_hoi.py           # Thống kê mô tả + 7 hàm trả lời 7 câu hỏi
│   ├── bieu_do.py           # 7 hàm vẽ biểu đồ Plotly (mỗi câu 1 hàm)
│   └── kiem_thu.py          # Kiểm thử bằng assert
└── Outputs/
    ├── cau1_*.ipynb ... cau7_*.ipynb   # Mỗi câu hỏi 1 notebook: phân tích + biểu đồ + nhận xét
    ├── cau1_*.csv ... cau7_*.csv       # Bảng kết quả 7 câu (main.py tạo ra)
    └── thong_ke_mo_ta.csv
```

## 4. Chức năng chính

1. **Đọc và kiểm tra:** đọc CSV, kiểm tra đủ 19 cột bắt buộc, báo lỗi dễ hiểu khi sai đường dẫn / file rỗng / sai định dạng;
   in nguồn, phạm vi thời gian, dung lượng file, kiểu dữ liệu, các cột có ô trống, số dòng trùng.
2. **Làm sạch (7 bước):** đổi `ORDERDATE` sang ngày giờ → xóa dòng trùng → chuẩn hóa chữ (khoảng trắng, `NYC`, vùng Singapore)
   → tách 60 dòng đơn hủy → lọc số lượng/đơn giá/doanh thu ≤ 0 → xử lý ô trống → đếm (giữ lại) đơn giá trị lớn.
   Kết quả: 2.823 → 2.763 dòng.
3. **Tạo cột mới:** `Revenue`, `UnitPriceReal` (đơn giá thực = SALES / số lượng), `Month`, `Weekday`, `IsCompleted`, `IsOutlier`.
4. **Lọc / tìm kiếm / sắp xếp:** lọc theo quốc gia, tìm sản phẩm theo từ khóa, sắp xếp theo cột bất kỳ.
5. **Phân tích bằng Pandas:** 7 câu hỏi dưới đây.
6. **Biểu đồ:** 7 biểu đồ Plotly thuộc 5 loại (đường, cột ngang, cột đứng, heatmap, histogram).

| # | Câu hỏi | Kỹ thuật | Biểu đồ |
|---|---|---|---|
| 1 | Doanh thu từng tháng ra sao, năm sau tăng bao nhiêu %? | `groupby` + `sum`, so cùng kỳ | Đường |
| 2 | Quốc gia nào mang lại nhiều doanh thu nhất? | `groupby` + `agg` | Cột ngang |
| 3 | Sản phẩm nào bán chạy, dòng sản phẩm nào tăng/giảm? | `groupby` + **`pivot_table`** (dòng SP × năm) | Cột ngang |
| 4 | Tháng nào, quý nào bán nhiều nhất (mùa vụ)? | **`pivot_table`** (năm × tháng) | Heatmap |
| 5 | Một đơn hàng thường trị giá bao nhiêu? | `groupby` + `describe`, tứ phân vị | Histogram |
| 6 | Doanh thu phụ thuộc vào bao nhiêu khách lớn? | `groupby` + `agg` | Cột ngang |
| 7 | Hủy đơn làm mất bao nhiêu doanh thu? | `groupby` + `nunique` | Cột đứng |

**Vì sao dùng `pivot_table`:** trải dữ liệu thành bảng 2 chiều. Ở câu 3, các năm thành cột nên tính tăng trưởng
chỉ bằng một phép chia `bang[2004] / bang[2003]`. Ở câu 4, bảng năm × tháng cho thấy ngay tháng 11 năm nào cũng cao nhất
và là đầu vào trực tiếp cho heatmap.

## 5. Hạn chế

- Năm 2005 chỉ có dữ liệu đến 31/05, nên so sánh năm 2005 phải dùng cùng kỳ 5 tháng.
- `PRICEEACH` bị chặn ở 100 nên dùng `SALES` làm doanh thu thay vì số lượng × đơn giá.
- Chỉ có 4 đơn bị hủy, mẫu quá nhỏ để kết luận chắc chắn ở câu 7.
- Không có giá vốn nên chỉ phân tích doanh thu, không tính được lợi nhuận.

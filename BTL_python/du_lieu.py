"""Mô-đun du_lieu: lớp RetailData lo việc đọc, kiểm tra, làm sạch, tạo cột mới, lọc, tìm kiếm, lưu."""

import pandas as pd

# Các cột bắt buộc phải có trong file dữ liệu
COT_BAT_BUOC = [
    "ORDERNUMBER", "ORDERLINENUMBER", "QUANTITYORDERED", "PRICEEACH", "SALES",
    "ORDERDATE", "STATUS", "PRODUCTLINE", "PRODUCTCODE", "CUSTOMERNAME", "COUNTRY",
]

# Trạng thái bị coi là HỦY -> tách ra bảng riêng 
# 'Disputed' (tranh chấp), 'On Hold' (tạm giữ), 'In Process' (đang xử lý) CHƯA hủy nên được giữ lại.
# Trạng thái coi là đơn bị hủy
TRANG_THAI_HUY = ["Cancelled"]

# Trạng thái coi là đơn đã hoàn tất
TRANG_THAI_HOAN_TAT = ["Shipped", "Resolved"]

def gioi_han_outlier(cot_so):
    """Ngưỡng giá trị lớn bất thường theo quy tắc IQR: Q3 + 1.5 x (Q3 - Q1)."""
    q1, q3 = cot_so.quantile([0.25, 0.75])
    return q3 + 1.5 * (q3 - q1)

class RetailData:
    """Quản lý bộ dữ liệu bán hàng: đọc, kiểm tra, làm sạch, tạo cột mới, lọc, tìm kiếm, lưu."""

    def __init__(self, duong_dan):
        self.duong_dan = duong_dan  # đường dẫn tới file CSV
        self.df = None              # bảng dữ liệu bán hàng (có sau khi gọi doc())
        self.don_huy = None         # bảng các dòng hủy đơn (có sau khi gọi lam_sach())

    def doc(self):
        """Đọc file CSV. Nếu không có file, pandas tự báo lỗi FileNotFoundError."""
        # [SỬA 1] encoding="cp850": file này KHÔNG phải UTF-8. cp850 đọc đúng ä, ñ, í
        #         (latin-1 sẽ ra 'Catalu¤a', 'Mart¡n').
        # [SỬA 2] keep_default_na=False + na_values=[""]: giữ nguyên chữ "NA" ở cột TERRITORY
        #         (North America). Mặc định pandas hiểu "NA" là ô trống -> 1.074 dòng mất vùng.
        # dtype=str: giữ các mã ở dạng chữ, tránh 10107 hay mã bưu điện bị đổi kiểu.
        self.df = pd.read_csv(
            self.duong_dan,
            encoding="cp850",
            keep_default_na=False,
            na_values=[""],
            dtype={"ORDERNUMBER": str, "PRODUCTCODE": str, "POSTALCODE": str, "PHONE": str},
        )
        for cot in COT_BAT_BUOC:
            if cot not in self.df.columns:
                raise ValueError(f"File dữ liệu thiếu cột '{cot}'")
        print(f"Đã đọc {len(self.df)} dòng, {len(self.df.columns)} cột")

    def kiem_tra(self):
        """In cấu trúc dữ liệu: kiểu của từng cột, số ô trống, số dòng trùng."""
        if self.df is None:
            raise ValueError("Chưa đọc dữ liệu! Hãy gọi doc() trước.")
        
        print("Kiểu dữ liệu của từng cột:")
        print(self.df.dtypes)
        print("\nSố ô trống ở mỗi cột:")
        print(self.df.isnull().sum())
        print("\nSố dòng trùng lặp:", self.df.duplicated().sum())

    def lam_sach(self):
        """Làm sạch dữ liệu từng bước, in số dòng còn lại sau mỗi bước."""
        if self.df is None:
            raise ValueError("Chưa đọc dữ liệu! Hãy gọi doc() trước.")
        
        df = self.df
        print("Ban đầu:", len(df), "dòng")

        # B1. Sai kiểu: cột ngày đang là chữ ('2/24/2003 0:00') -> đổi sang kiểu ngày giờ.
        #     Không dùng errors="coerce": nếu có ngày sai định dạng thì để chương trình báo lỗi ngay.
        df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"], format="%m/%d/%Y %H:%M")
        print("B1 - Đổi ORDERDATE sang kiểu ngày giờ, còn:", len(df))
        
        # B2. Trùng lặp: xóa dòng giống hệt nhau, và kiểm tra thêm khóa (đơn hàng + số dòng) có bị lặp không.
        df = df.drop_duplicates()
        so_trung_khoa = df.duplicated(subset=["ORDERNUMBER", "ORDERLINENUMBER"]).sum()
        print(f"B2 - Xóa dòng trùng lặp, còn: {len(df)} (trùng khóa đơn + dòng: {so_trung_khoa})")
       
        # B3. Chuẩn hóa giá trị chữ .
        so_khoang_trang = df["ADDRESSLINE1"].str.contains(r"\s{2,}", na=False).sum()
        for cot in df.columns:
            if pd.api.types.is_string_dtype(df[cot]):
                # strip(): bỏ khoảng trắng đầu/cuối; replace: gộp nhiều khoảng trắng liền nhau thành 1
                df[cot] = df[cot].str.strip().str.replace(r"\s{2,}", " ", regex=True)
        so_nyc = (df["CITY"] == "NYC").sum()
        df["CITY"] = df["CITY"].replace({"NYC": "New York"})
        # Singapore đang bị gán 2 vùng ('Japan' và 'APAC') -> thống nhất là APAC
        sai_vung = (df["COUNTRY"] == "Singapore") & (df["TERRITORY"] != "APAC")
        so_singapore = sai_vung.sum()
        df.loc[sai_vung, "TERRITORY"] = "APAC"
        print(f"B3 - Chuẩn hóa chữ: sửa {so_khoang_trang} địa chỉ thừa khoảng trắng, "
              f"{so_nyc} dòng NYC, {so_singapore} dòng Singapore, còn: {len(df)}")
        
        # B4. Tách đơn hủy (STATUS nằm trong TRANG_THAI_HUY) ra bảng riêng để dùng ở phần phân tích hủy đơn
        la_don_huy = df["STATUS"].isin(TRANG_THAI_HUY)
        self.don_huy = df[la_don_huy].copy()
        df = df[~la_don_huy]  # dấu ~ nghĩa là "KHÔNG": giữ các dòng không phải đơn hủy
        print("B4 - Tách", len(self.don_huy), "dòng hủy đơn, còn:", len(df))

        # B5. Giá trị sai: số lượng, đơn giá, doanh thu <= 0 là lỗi nhập liệu (dữ liệu này chưa có dòng nào lỗi,
        #     nhưng vẫn phải kiểm tra để chắc chắn)
        df = df[(df["QUANTITYORDERED"] > 0) & (df["PRICEEACH"] > 0) & (df["SALES"] > 0)]
        print("B5 - Bỏ số lượng/đơn giá/doanh thu <= 0, còn:", len(df))

        # B6. Giá trị thiếu:
        #     - bỏ dòng thiếu tên khách hàng hoặc dòng sản phẩm (cột quan trọng cho phân tích)
        #     - STATE trống vì nhiều nước không có bang -> điền 'Not applicable' (KHÔNG xóa dòng)
        #     - POSTALCODE trống ở một số dòng của Mỹ -> điền 'Unknown'
        #     - ADDRESSLINE2 trống 89% -> bỏ cả cột
        df = df.dropna(subset=["CUSTOMERNAME", "PRODUCTLINE"])
        df["STATE"] = df["STATE"].fillna("Not applicable")
        df["POSTALCODE"] = df["POSTALCODE"].fillna("Unknown")
        df = df.drop(columns="ADDRESSLINE2")
        print(f"B6 - Xử lý giá trị thiếu, còn: {len(df)} (ô trống còn lại: {int(df.isnull().sum().sum())})")

        # B7. Bất thường: KHÔNG xóa. Đơn lớn ở đây là hợp lệ (SALES tối đa ~14.000, khớp với DEALSIZE = Large),
        #     chỉ đánh dấu ở them_cot() để ai cần thì lọc ra. (Online Retail thì khác: có dòng 80.995 sản phẩm là nhập nhầm.)
        gioi_han = gioi_han_outlier(df["SALES"])
        so_lon = int((df["SALES"] > gioi_han).sum())
        print(f"B7 - Có {so_lon} dòng SALES > {gioi_han:,.0f}: giữ lại và đánh dấu, còn: {len(df)}")

        self.df = df.copy()  # tạo bản sao độc lập để bước sau thêm cột không bị pandas cảnh báo

    def them_cot(self):
        """Tạo các cột mới phục vụ phân tích."""
        if self.df is None:
            raise ValueError("Chưa đọc dữ liệu! Hãy gọi doc() trước.")
        
        df = self.df
        # Doanh thu lấy từ cột SALES gốc. KHÔNG dùng QUANTITYORDERED * PRICEEACH vì PRICEEACH bị chặn trần ở 100
        # (1.304 dòng) nên cách tính đó thấp hơn thực tế khoảng 17,5%.
        df["Revenue"] = df["SALES"]
        # Đơn giá thực tế mỗi sản phẩm = doanh thu / số lượng (có thể lớn hơn 100)
        df["UnitPriceReal"] = (df["SALES"] / df["QUANTITYORDERED"]).round(2)
        df["Month"] = df["ORDERDATE"].dt.strftime("%Y-%m")   # tháng, ví dụ '2003-02'
        df["Weekday"] = df["ORDERDATE"].dt.day_of_week       # thứ trong tuần: 0 = Thứ 2 ... 6 = Chủ nhật
        df["IsCompleted"] = df["STATUS"].isin(TRANG_THAI_HOAN_TAT)          # True nếu đơn đã hoàn tất
        df["IsOutlier"] = df["SALES"] > gioi_han_outlier(df["SALES"])   # True nếu là đơn lớn bất thường
        print("Đã thêm 6 cột: Revenue, UnitPriceReal, Month, Weekday, IsCompleted, IsOutlier")

    def loc_theo_quoc_gia(self, quoc_gia):
        """Lọc: trả về các dòng của một quốc gia (không phân biệt chữ hoa/thường)."""
        if self.df is None:
            raise ValueError("Chưa đọc dữ liệu! Hãy gọi doc() trước.")
        
        return self.df[self.df["COUNTRY"].str.lower() == quoc_gia.strip().lower()]

    def tim_san_pham(self, tu_khoa):
        """Tìm kiếm: trả về các dòng có dòng sản phẩm HOẶC mã sản phẩm chứa từ khóa.

        Dữ liệu này không có tên sản phẩm chi tiết nên tìm trên PRODUCTLINE (vd 'Classic Cars')
        và PRODUCTCODE (vd 'S18_1749').
        """
        if self.df is None:
            raise ValueError("Chưa đọc dữ liệu! Hãy gọi doc() trước.")
        tu_khoa = tu_khoa.strip()
        if tu_khoa == "":
            raise ValueError("Từ khóa tìm kiếm không được để trống")
        trong_dong_sp = self.df["PRODUCTLINE"].str.contains(tu_khoa, case=False, regex=False)
        trong_ma_sp = self.df["PRODUCTCODE"].str.contains(tu_khoa, case=False, regex=False)
        return self.df[trong_dong_sp | trong_ma_sp]

    def sap_xep(self, cot, tang_dan=False, so_dong=10):
        """Sắp xếp theo một cột (mặc định giảm dần) và lấy vài dòng đầu."""
        if self.df is None:
            raise ValueError("Chưa đọc dữ liệu! Hãy gọi doc() trước.")
        if cot not in self.df.columns:
            raise ValueError(f"Không có cột '{cot}'. Các cột hiện có: {list(self.df.columns)}")
        return self.df.sort_values(cot, ascending=tang_dan).head(so_dong)

    def luu(self, duong_dan):
        """Xuất dữ liệu đã làm sạch ra file CSV."""
        if self.df is None:
            raise ValueError("Chưa đọc dữ liệu! Hãy gọi doc() trước.")
        self.df.to_csv(duong_dan, index=False, encoding="utf-8-sig")
        print("Đã lưu dữ liệu sạch vào:", duong_dan)


if __name__ == "__main__":
    du_lieu = RetailData("sales_data_sample.csv")
    du_lieu.doc()
    print("\n--- LÀM SẠCH ---")
    du_lieu.lam_sach()
    print("\n--- TẠO CỘT MỚI ---")
    du_lieu.them_cot()
    du_lieu.luu("du_lieu_da_lam_sach.csv")

    print("\n--- LỌC - TÌM KIẾM - SẮP XẾP ---")
    duc = du_lieu.loc_theo_quoc_gia("Germany")
    print(f"Lọc nước Germany: {len(duc)} dòng, doanh thu {duc['Revenue'].sum():,.0f}")
    xe_co = du_lieu.tim_san_pham("Classic")
    print(f"Tìm 'Classic': {len(xe_co)} dòng, doanh thu {xe_co['Revenue'].sum():,.0f}")
    print("\n5 dòng có doanh thu lớn nhất:")
    print(du_lieu.sap_xep("Revenue", so_dong=5)[
        ["ORDERNUMBER", "CUSTOMERNAME", "PRODUCTLINE", "QUANTITYORDERED", "UnitPriceReal", "Revenue"]])
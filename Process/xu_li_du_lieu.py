"""Mô-đun du_lieu: quản lý dữ liệu bán hàng (đọc, kiểm tra, làm sạch, tạo cột, lọc, tìm, lưu)."""

import pandas as pd

# Các cột bắt buộc phải có trong file đầu vào
COT_BAT_BUOC = [
    "ORDERNUMBER", "ORDERLINENUMBER", "QUANTITYORDERED", "PRICEEACH", "SALES",
    "ORDERDATE", "STATUS", "PRODUCTLINE", "PRODUCTCODE", "CUSTOMERNAME", "COUNTRY",
]

# Chỉ tách đơn đã hủy ('Cancelled'); giữ lại 'Disputed', 'On Hold', 'In Process' vì chưa hủy hẳn
TRANG_THAI_HUY = ["Cancelled"]

# Các trạng thái được coi là đơn hoàn tất
TRANG_THAI_HOAN_TAT = ["Shipped", "Resolved"]


def gioi_han_outlier(cot_so):
    """Tính ngưỡng trên bất thường theo quy tắc IQR: Q3 + 1.5 * (Q3 - Q1)."""
    q1, q3 = cot_so.quantile([0.25, 0.75])
    return q3 + 1.5 * (q3 - q1)


class RetailData:
    """Xử lý vòng đời dữ liệu bán hàng từ lúc đọc file thô đến khi xuất dữ liệu sạch."""

    def __init__(self, duong_dan):
        self.duong_dan = duong_dan
        self.df = None
        self.don_huy = None

    def _kiem_tra_da_doc(self):
        """Kiểm tra xem dữ liệu đã được nạp hay chưa trước khi thao tác."""
        if self.df is None:
            raise ValueError("Chưa đọc dữ liệu! Hãy gọi doc() trước.")

    def doc(self):
        """Đọc file CSV và kiểm tra các cột bắt buộc."""
        # Dùng cp850 để đọc đúng ký tự dấu/đặc biệt; tắt nhận diện "NA" mặc định để không mất vùng North America
        # Ép kiểu str cho các cột mã để giữ nguyên số 0 đầu hoặc định dạng mã
        self.df = pd.read_csv(
            self.duong_dan,
            encoding="cp850",
            keep_default_na=False,
            na_values=[""],
            dtype={"ORDERNUMBER": str, "PRODUCTCODE": str, "POSTALCODE": str, "PHONE": str},
        )

        cac_cot_thieu = [cot for cot in COT_BAT_BUOC if cot not in self.df.columns]
        if cac_cot_thieu:
            raise ValueError(f"File dữ liệu thiếu các cột bắt buộc: {cac_cot_thieu}")

        print(f"Đã đọc {len(self.df)} dòng, {len(self.df.columns)} cột.")

    def kiem_tra(self):
        """In nhanh kiểu dữ liệu, số ô thiếu và số dòng trùng lặp."""
        self._kiem_tra_da_doc()

        print("Kiểu dữ liệu từng cột:")
        print(self.df.dtypes)
        print("\nSố ô trống từng cột:")
        print(self.df.isnull().sum())
        print("\nSố dòng trùng hoàn toàn:", int(self.df.duplicated().sum()))

    def lam_sach(self):
        """Làm sạch dữ liệu theo từng bước và in số lượng dòng sau mỗi bước."""
        self._kiem_tra_da_doc()

        df = self.df.copy()
        print(f"Ban đầu: {len(df)} dòng")

        # 1. Chuyển cột ngày sang datetime (để lỗi nếu sai định dạng nhằm phát hiện sớm)
        df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"], format="%m/%d/%Y %H:%M")
        print(f"B1 - Chuẩn hóa ORDERDATE: {len(df)} dòng")

        # 2. Xóa dòng trùng hoàn toàn; báo thêm số dòng trùng khóa (đơn hàng + dòng chi tiết) nếu có
        df = df.drop_duplicates()
        so_trung_khoa = int(df.duplicated(subset=["ORDERNUMBER", "ORDERLINENUMBER"]).sum())
        print(f"B2 - Xóa dòng trùng lặp: {len(df)} dòng (trùng khóa đơn + dòng: {so_trung_khoa})")

        # 3. Chuẩn hóa chuỗi: gọn khoảng trắng, thống nhất tên thành phố và vùng của Singapore
        so_dia_chi_du_space = int(df["ADDRESSLINE1"].str.contains(r"\s{2,}", regex=True, na=False).sum())
        for cot in df.select_dtypes(include=["object", "string"]).columns:
            df[cot] = df[cot].str.strip().str.replace(r"\s{2,}", " ", regex=True)

        so_nyc = int((df["CITY"] == "NYC").sum())
        df["CITY"] = df["CITY"].replace({"NYC": "New York"})

        sai_vung_sg = (df["COUNTRY"] == "Singapore") & (df["TERRITORY"] != "APAC")
        so_sg = int(sai_vung_sg.sum())
        df.loc[sai_vung_sg, "TERRITORY"] = "APAC"
        print(
            f"B3 - Chuẩn hóa chữ: sửa {so_dia_chi_du_space} địa chỉ dư khoảng trắng, "
            f"{so_nyc} dòng 'NYC', {so_sg} dòng vùng 'Singapore' -> {len(df)} dòng"
        )

        # 4. Tách đơn hủy sang bảng riêng để phân tích riêng, giữ phần còn lại trong bảng chính
        la_don_huy = df["STATUS"].isin(TRANG_THAI_HUY)
        self.don_huy = df[la_don_huy].copy()
        df = df[~la_don_huy]
        print(f"B4 - Tách {len(self.don_huy)} đơn hủy: còn {len(df)} dòng")

        # 5. Loại bỏ các dòng có số lượng, đơn giá hoặc doanh thu <= 0 (nếu phát sinh lỗi nhập liệu)
        hop_le = (df["QUANTITYORDERED"] > 0) & (df["PRICEEACH"] > 0) & (df["SALES"] > 0)
        df = df[hop_le]
        print(f"B5 - Lọc giá trị dương (số lượng, đơn giá, doanh thu): còn {len(df)} dòng")

        # 6. Xử lý giá trị thiếu theo ý nghĩa từng cột
        df = df.dropna(subset=["CUSTOMERNAME", "PRODUCTLINE"])
        df["STATE"] = df["STATE"].fillna("Not applicable")
        df["POSTALCODE"] = df["POSTALCODE"].fillna("Unknown")
        if "ADDRESSLINE2" in df.columns:
            df = df.drop(columns=["ADDRESSLINE2"])
        print(
            f"B6 - Xử lý giá trị thiếu: còn {len(df)} dòng "
            f"(ô trống còn lại: {int(df.isnull().sum().sum())})"
        )

        # 7. Giữ lại đơn giá trị lớn (vì đơn lớn ở bộ này là có thật) và chỉ đếm để tham khảo
        nguong_sales = gioi_han_outlier(df["SALES"])
        so_outlier = int((df["SALES"] > nguong_sales).sum())
        print(f"B7 - Có {so_outlier} dòng SALES > {nguong_sales:,.0f}: giữ lại, còn {len(df)} dòng")

        self.df = df

    def them_cot(self):
        """Tạo các cột dẫn xuất phục vụ phân tích."""
        self._kiem_tra_da_doc()

        # Dùng trực tiếp SALES thay vì QUANTITYORDERED * PRICEEACH vì PRICEEACH bị chặn tối đa ở mức 100
        self.df["Revenue"] = self.df["SALES"]
        self.df["UnitPriceReal"] = (self.df["SALES"] / self.df["QUANTITYORDERED"]).round(2)
        self.df["Month"] = self.df["ORDERDATE"].dt.strftime("%Y-%m")
        self.df["Weekday"] = self.df["ORDERDATE"].dt.day_of_week  # 0: Thứ 2 ... 6: Chủ nhật
        self.df["IsCompleted"] = self.df["STATUS"].isin(TRANG_THAI_HOAN_TAT)
        self.df["IsOutlier"] = self.df["SALES"] > gioi_han_outlier(self.df["SALES"])

        print("Đã thêm 6 cột: Revenue, UnitPriceReal, Month, Weekday, IsCompleted, IsOutlier.")

    def loc_theo_quoc_gia(self, quoc_gia):
        """Lọc các dòng theo tên quốc gia (không phân biệt hoa/thường và khoảng trắng thừa)."""
        self._kiem_tra_da_doc()
        ten_chuan = quoc_gia.strip().lower()
        return self.df[self.df["COUNTRY"].str.strip().str.lower() == ten_chuan]

    def tim_san_pham(self, tu_khoa):
        """Tìm sản phẩm theo từ khóa trên dòng sản phẩm (PRODUCTLINE) hoặc mã sản phẩm (PRODUCTCODE)."""
        self._kiem_tra_da_doc()
        tu_khoa = tu_khoa.strip()
        if not tu_khoa:
            raise ValueError("Từ khóa tìm kiếm không được để trống.")

        khop_dong = self.df["PRODUCTLINE"].str.contains(tu_khoa, case=False, regex=False, na=False)
        khop_ma = self.df["PRODUCTCODE"].str.contains(tu_khoa, case=False, regex=False, na=False)
        return self.df[khop_dong | khop_ma]

    def sap_xep(self, cot, tang_dan=False, so_dong=10):
        """Sắp xếp theo cột chỉ định và trả về `so_dong` dòng đầu."""
        self._kiem_tra_da_doc()
        if cot not in self.df.columns:
            raise ValueError(f"Không có cột '{cot}'. Các cột hiện có: {list(self.df.columns)}")
        return self.df.sort_values(cot, ascending=tang_dan).head(so_dong)

    def luu(self, duong_dan):
        """Lưu dữ liệu ra file CSV chuẩn UTF-8 (có BOM để mở đẹp trên Excel)."""
        self._kiem_tra_da_doc()
        self.df.to_csv(duong_dan, index=False, encoding="utf-8-sig")
        print(f"Đã lưu dữ liệu vào: {duong_dan}")


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
    print(f"Quốc gia Germany: {len(duc)} dòng | Doanh thu: {duc['Revenue'].sum():,.0f}")

    xe_co = du_lieu.tim_san_pham("Classic")
    print(f"Từ khóa 'Classic': {len(xe_co)} dòng | Doanh thu: {xe_co['Revenue'].sum():,.0f}")

    print("\nTop 5 đơn có doanh thu cao nhất:")
    cot_hien_thi = ["ORDERNUMBER", "CUSTOMERNAME", "PRODUCTLINE", "QUANTITYORDERED", "UnitPriceReal", "Revenue"]
    print(du_lieu.sap_xep("Revenue", so_dong=5)[cot_hien_thi].to_string(index=False))

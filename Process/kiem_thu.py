"""Kiểm thử cho lam_sach, them_cot, loc, tim, sap_xep của lớp RetailData.  Chạy:  python kiem_thu_lam_sach.py"""
 
import pandas as pd
 
from du_lieu import RetailData
 
# Một dòng "chuẩn", các dòng khác chỉ thay đổi vài giá trị để tạo lỗi cố ý
DONG_MAU = dict(
    ORDERNUMBER="1", ORDERLINENUMBER=1, QUANTITYORDERED=10, PRICEEACH=100.0, SALES=1500.0,
    ORDERDATE="2/24/2003 0:00", STATUS="Shipped", PRODUCTLINE="Classic Cars", PRODUCTCODE="S10_1678",
    CUSTOMERNAME="Land of Toys Inc.", COUNTRY="USA", CITY="NYC", TERRITORY="NA",
    ADDRESSLINE1="897  Long Airport Avenue", ADDRESSLINE2="Suite 1", STATE="NY", POSTALCODE="10022",
)
 
 
def dong(**thay_doi):
    return {**DONG_MAU, **thay_doi}
 
 
du_lieu = RetailData("khong_dung_toi.csv")
du_lieu.df = pd.DataFrame([
    dong(),                                                       # dòng hợp lệ, có NYC và khoảng trắng đôi
    dong(),                                                       # dòng trùng hoàn toàn -> bị xóa ở B2
    dong(ORDERNUMBER="2", STATUS="Cancelled"),                    # đơn hủy -> tách ở B4
    dong(ORDERNUMBER="3", COUNTRY="Singapore", TERRITORY="Japan", # Singapore gán sai vùng, thiếu STATE/POSTALCODE
         STATE=None, POSTALCODE=None, STATUS="On Hold", CITY="Singapore", ADDRESSLINE2=None),
    dong(ORDERNUMBER="4", QUANTITYORDERED=0, SALES=0.0),          # số lượng 0 -> bị bỏ ở B5
    dong(ORDERNUMBER="5", SALES=1000.0, QUANTITYORDERED=10),
    dong(ORDERNUMBER="6", SALES=1200.0, QUANTITYORDERED=10),
    dong(ORDERNUMBER="7", SALES=1400.0, QUANTITYORDERED=10),
    dong(ORDERNUMBER="8", SALES=1600.0, QUANTITYORDERED=10),
    dong(ORDERNUMBER="9", SALES=90000.0, QUANTITYORDERED=90,      # đơn lớn bất thường -> giữ lại, đánh dấu
         PRODUCTLINE="Ships", PRODUCTCODE="S18_1749"),
])
du_lieu.lam_sach()
du_lieu.them_cot()
df = du_lieu.df
 
 
def phai_bao_loi(ham, *tham_so):
    """Trả về True nếu gọi ham(*tham_so) gây ValueError."""
    try:
        ham(*tham_so)
    except ValueError:
        return True
    return False
 
 
# --- lam_sach ---
assert len(df) == 7, "10 dòng - 1 trùng - 1 hủy - 1 số lượng 0 = 7 dòng"
assert len(du_lieu.don_huy) == 1, "Tách đúng 1 dòng hủy đơn"
assert (df["CITY"] != "NYC").all(), "NYC phải đổi thành New York"
assert not df["ADDRESSLINE1"].str.contains("  ").any(), "Phải gộp khoảng trắng đôi"
assert df.loc[df["COUNTRY"] == "Singapore", "TERRITORY"].iloc[0] == "APAC", "Singapore phải về APAC"
assert df.loc[df["COUNTRY"] == "Singapore", "STATE"].iloc[0] == "Not applicable", "STATE thiếu phải được điền"
assert df.loc[df["COUNTRY"] == "Singapore", "POSTALCODE"].iloc[0] == "Unknown", "POSTALCODE thiếu phải được điền"
assert "ADDRESSLINE2" not in df.columns, "Phải bỏ cột ADDRESSLINE2"
assert df.isnull().sum().sum() == 0, "Sau làm sạch không còn ô trống"
 
# --- them_cot ---
assert (df["Revenue"] == df["SALES"]).all(), "Revenue lấy từ SALES"
assert df.loc[df["ORDERNUMBER"] == "1", "UnitPriceReal"].iloc[0] == 150.0, "Đơn giá thực = 1500 / 10"
assert df["IsOutlier"].sum() == 1 and df.loc[df["IsOutlier"], "ORDERNUMBER"].iloc[0] == "9", "Chỉ đơn 90000 là bất thường"
assert not df.loc[df["ORDERNUMBER"] == "3", "IsCompleted"].iloc[0], "Đơn 'On Hold' chưa hoàn tất"
assert df.loc[df["ORDERNUMBER"] == "1", "Month"].iloc[0] == "2003-02", "Cột Month đúng định dạng"
 
# --- lọc, tìm kiếm, sắp xếp ---
assert len(du_lieu.loc_theo_quoc_gia("singapore")) == 1, "Lọc quốc gia không phân biệt hoa thường"
assert len(du_lieu.loc_theo_quoc_gia("Viet Nam")) == 0, "Quốc gia không có thì trả về bảng rỗng"
assert len(du_lieu.tim_san_pham("ships")) == 1, "Tìm theo dòng sản phẩm, không phân biệt hoa thường"
assert len(du_lieu.tim_san_pham("S18_")) == 1, "Tìm theo mã sản phẩm"
assert du_lieu.sap_xep("Revenue", so_dong=1)["ORDERNUMBER"].iloc[0] == "9", "Sắp xếp giảm dần lấy dòng lớn nhất"
 
# --- báo lỗi đúng chỗ ---
assert phai_bao_loi(du_lieu.tim_san_pham, "   "), "Từ khóa rỗng phải báo lỗi"
assert phai_bao_loi(du_lieu.sap_xep, "COT_KHONG_CO"), "Cột không tồn tại phải báo lỗi"
assert phai_bao_loi(RetailData("x.csv").lam_sach), "Chưa gọi doc() phải báo lỗi"
 
print("\nTất cả kiểm thử đều ĐẠT!")
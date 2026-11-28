"""Chương trình chính: đọc, làm sạch, tạo cột mới, lọc/tìm/sắp xếp, trả lời 7 câu hỏi và lưu kết quả.
Biểu đồ của từng câu nằm trong các notebook Outputs/cauN_*.ipynb.  Chạy:  python main.py"""

import os
import sys

import pandas as pd

from Process.xu_li_du_lieu import RetailData
from Process import cau_hoi

# Đường dẫn tính từ vị trí file main.py -> chạy từ thư mục nào cũng đúng
GOC = os.path.dirname(os.path.abspath(__file__))
RAW_DATA = os.path.join(GOC, "Data", "raw_data.csv")
CLEAN_DATA = os.path.join(GOC, "Data", "clean_data.csv")
KQ = os.path.join(GOC, "Outputs")

NGUON = "Kaggle - Sample Sales Data (kyanyoga): https://www.kaggle.com/datasets/kyanyoga/sample-sales-data"
MO_TA = ("Đơn hàng bán sỉ mô hình sưu tầm (xe hơi, mô tô, máy bay, tàu, xe lửa...) "
         "của một công ty cho các cửa hàng ở nhiều nước; mỗi dòng là 1 sản phẩm trong 1 đơn")


QUOC_GIA_LOC = "Germany"
TU_KHOA_SAN_PHAM = "Classic"
COT_SAP_XEP = "Revenue"
SO_DONG_TOP = 5


def tieu_de(line):
    print("\n" + "=" * 70)
    print(line)
    print("=" * 70)


def main():
    tieu_de("1. ĐỌC VÀ KIỂM TRA DỮ LIỆU")
    du_lieu = RetailData(RAW_DATA)
    du_lieu.doc()
    tho = du_lieu.df
    ngay = pd.to_datetime(tho["ORDERDATE"], format="%m/%d/%Y %H:%M")
    print(f"Nguồn: {NGUON}")
    print(f"Nội dung: {MO_TA}")
    print(f"Thời gian: {ngay.min():%d/%m/%Y} - {ngay.max():%d/%m/%Y}")
    print(f"Phạm vi: {tho['COUNTRY'].nunique()} quốc gia: {', '.join(sorted(tho['COUNTRY'].unique()))}")
    print(f"Dung lượng file gốc: {os.path.getsize(RAW_DATA) / 1024:.1f} KB\n")
    du_lieu.kiem_tra()

    tieu_de("2. LÀM SẠCH DỮ LIỆU")
    du_lieu.lam_sach()

    tieu_de("3. TẠO CỘT MỚI VÀ LƯU DỮ LIỆU SẠCH")
    du_lieu.them_cot()
    du_lieu.luu(CLEAN_DATA)
    df = du_lieu.df

    tieu_de("4. LỌC - TÌM KIẾM - SẮP XẾP")
    loc = du_lieu.loc_theo_quoc_gia(QUOC_GIA_LOC)
    print(f"Lọc quốc gia '{QUOC_GIA_LOC}': {len(loc)} dòng | Doanh thu: {loc['Revenue'].sum():,.0f} USD")
    tim = du_lieu.tim_san_pham(TU_KHOA_SAN_PHAM)
    print(f"Tìm từ khóa '{TU_KHOA_SAN_PHAM}': {len(tim)} dòng | Doanh thu: {tim['Revenue'].sum():,.0f} USD")
    print(f"\nTop {SO_DONG_TOP} dòng có {COT_SAP_XEP} cao nhất:")
    cot_hien_thi = ["ORDERNUMBER", "CUSTOMERNAME", "PRODUCTLINE", "QUANTITYORDERED", "UnitPriceReal", "Revenue"]
    print(du_lieu.sap_xep(COT_SAP_XEP, so_dong=SO_DONG_TOP)[cot_hien_thi].to_string(index=False))

    tieu_de("5. THỐNG KÊ MÔ TẢ")
    os.makedirs(KQ, exist_ok=True)
    cau_hoi.thong_ke_mo_ta(df).to_csv(os.path.join(KQ, "thong_ke_mo_ta.csv"), encoding="utf-8-sig")

    tieu_de("6. TRẢ LỜI 7 CÂU HỎI PHÂN TÍCH")
    ket_qua = {
        "cau1_doanh_thu_theo_thang": cau_hoi.cau1_doanh_thu_theo_thang(df),
        "cau2_quoc_gia": cau_hoi.cau2_quoc_gia(df),
        "cau3_san_pham": cau_hoi.cau3_san_pham_ban_chay(df),
        "cau4_mua_vu": cau_hoi.cau4_thoi_diem_mua(df),
        "cau5_gia_tri_don_hang": cau_hoi.cau5_gia_tri_don_hang(df),
        "cau6_khach_hang": cau_hoi.cau6_khach_hang(df),
        "cau7_huy_don": cau_hoi.cau7_huy_don(df, du_lieu.don_huy),
    }

    tieu_de("7. LƯU KẾT QUẢ")
    print("Kết quả đã được lưu vào thư mục Outputs")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, PermissionError) as loi:
        print(f"\nLỖI: {loi}")
        sys.exit(1)

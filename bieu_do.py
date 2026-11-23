"""Mô-đun bieu_do: vẽ đầy đủ 7 biểu đồ bằng Matplotlib và tự động xuất diễn giải chi tiết."""

import os
import matplotlib
matplotlib.use("Agg")  # chỉ vẽ ra file, không mở cửa sổ
import matplotlib.pyplot as plt

TEN_THU = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]


def luu_bieu_do(duong_dan):
    """Căn lề gọn, lưu biểu đồ ra file rồi đóng lại để giải phóng bộ nhớ."""
    plt.tight_layout()
    plt.savefig(duong_dan, dpi=200)
    plt.close()
    print("Đã lưu:", duong_dan)


# ==============================================================================
# PHẦN 1: CÁC HÀM VẼ 7 BIỂU ĐỒ TƯƠNG ỨNG VỚI 7 CÂU HỎI PHÂN TÍCH
# ==============================================================================

def ve_doanh_thu_theo_thang(bang, duong_dan):
    """Biểu đồ 1 (Câu 1): Biểu đồ đường doanh thu theo tháng."""
    plt.figure(figsize=(10, 5))
    plt.plot(bang.index, bang.values / 1000, marker="o", linewidth=2, color="steelblue")
    plt.title("Doanh thu theo tháng (12/2010 - 12/2011)")
    plt.xlabel("Tháng")
    plt.ylabel("Doanh thu (nghìn GBP)")
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)
    luu_bieu_do(duong_dan)


def ve_top_quoc_gia(bang, duong_dan):
    """Biểu đồ 2 (Câu 2): Biểu đồ cột ngang 10 quốc gia doanh thu cao nhất (trừ Anh)."""
    top = bang.drop("United Kingdom").head(10).sort_values("DoanhThu")
    plt.figure(figsize=(9, 5))
    plt.barh(top.index, top["DoanhThu"] / 1000, color="tab:blue")
    plt.title("Top 10 quốc gia theo doanh thu (không tính Anh)")
    plt.xlabel("Doanh thu (nghìn GBP)")
    plt.ylabel("Quốc gia")
    luu_bieu_do(duong_dan)


def ve_top_san_pham(bang, duong_dan):
    """Biểu đồ 3 (Câu 3): Biểu đồ cột ngang 10 sản phẩm doanh thu cao nhất."""
    top = bang.sort_values("DoanhThu")
    plt.figure(figsize=(10, 5))
    plt.barh(top.index, top["DoanhThu"] / 1000, color="darkorange")
    plt.title("Top 10 sản phẩm theo doanh thu")
    plt.xlabel("Doanh thu (nghìn GBP)")
    plt.ylabel("Sản phẩm")
    luu_bieu_do(duong_dan)


def ve_gia_tri_don_hang(don_hang, duong_dan):
    """Biểu đồ 4 (Câu 5): Histogram phân bố giá trị đơn hàng (< 2.000 GBP)."""
    plt.figure(figsize=(9, 5))
    plt.hist(don_hang[don_hang < 2000], bins=50, edgecolor="white", color="tab:blue")
    plt.axvline(don_hang.median(), color="red", linestyle="--",
                label=f"Trung vị: {don_hang.median():.0f} GBP")
    plt.title("Phân bố giá trị đơn hàng (các đơn dưới 2.000 GBP)")
    plt.xlabel("Giá trị đơn hàng (GBP)")
    plt.ylabel("Số đơn hàng")
    plt.legend()
    luu_bieu_do(duong_dan)


def ve_thoi_diem_mua(bang, duong_dan):
    """Biểu đồ 5 (Câu 4): Bản đồ nhiệt (Heatmap) doanh thu theo Thứ và Giờ."""
    plt.figure(figsize=(11, 5))
    plt.imshow(bang.values / 1000, aspect="auto", cmap="YlOrRd")
    plt.colorbar(label="Doanh thu (nghìn GBP)")
    plt.yticks(range(len(bang.index)), [TEN_THU[i] for i in bang.index])
    plt.xticks(range(len(bang.columns)), [f"{h}h" for h in bang.columns])
    plt.title("Bản đồ nhiệt doanh thu theo Thứ và Giờ trong ngày")
    plt.xlabel("Giờ trong ngày")
    plt.ylabel("Thứ trong tuần")
    luu_bieu_do(duong_dan)


def ve_top_khach_hang(bang, duong_dan):
    """Biểu đồ 6 (Câu 6): Biểu đồ cột ngang Top 10 khách hàng doanh thu cao nhất."""
    top = bang.head(10).sort_values("DoanhThu")
    plt.figure(figsize=(9, 5))
    plt.barh([f"KH {cid}" for cid in top.index], top["DoanhThu"] / 1000, color="seagreen")
    plt.title("Top 10 khách hàng đóng góp doanh thu cao nhất")
    plt.xlabel("Doanh thu (nghìn GBP)")
    plt.ylabel("Mã khách hàng")
    luu_bieu_do(duong_dan)


def ve_top_huy_don(bang, duong_dan):
    """Biểu đồ 7 (Câu 7): Biểu đồ cột ngang Top 10 sản phẩm bị hủy nhiều nhất."""
    top = bang.sort_values()
    plt.figure(figsize=(10, 5))
    plt.barh(top.index, top.values, color="crimson")
    plt.title("Top 10 sản phẩm có số lần bị hủy nhiều nhất")
    plt.xlabel("Số hóa đơn hủy")
    plt.ylabel("Sản phẩm")
    luu_bieu_do(duong_dan)


# ==============================================================================
# PHẦN 2: HÀM TỰ ĐỘNG SINH DIỄN GIẢI BIỂU ĐỒ RA MÀN HÌNH & FILE VĂN BẢN (.TXT/.MD)
# ==============================================================================

def xuat_dien_giai(df, don_huy, b1, b2, b3, b4, b5, b6, b7, duong_dan_file):
    """Tự động tính toán các chỉ số từ 7 bảng phân tích và xuất ra file diễn giải."""
    # Câu 1
    du_thang = b1.iloc[:-1]

    # Câu 2
    nuoc_ngoai = b2.drop("United Kingdom")

    # Câu 4
    theo_thu = b4.sum(axis=1)
    theo_gio = b4.sum(axis=0)

    # Câu 6
    ty_le_mua_lai = (b6["SoDon"] >= 2).mean() * 100
    ty_le_top10 = b6["DoanhThu"].head(10).sum() / b6["DoanhThu"].sum() * 100

    # Câu 7
    so_don_huy = don_huy["InvoiceNo"].nunique()
    so_don_ban = df["InvoiceNo"].nunique()
    ty_le_huy = so_don_huy / (so_don_huy + so_don_ban) * 100

    noi_dung = f"""# BÁO CÁO DIỄN GIẢI KẾT QUẢ TRỰC QUAN HÓA DỮ LIỆU

## 1. Xu hướng doanh thu theo tháng (Biểu đồ 1)
- Doanh thu duy trì ổn định trong giai đoạn đầu năm và tăng trưởng bứt phá vào quý IV (mùa mua sắm cuối năm).
- Tháng đạt doanh thu cao nhất là **{b1.idxmax()}** với **{b1.max():,.0f} GBP**, gấp {b1.max()/du_thang.min():.1f} lần tháng thấp nhất (không tính tháng cuối) là **{du_thang.idxmin()}** ({du_thang.min():,.0f} GBP).
- Tháng 2011-12 giảm thấp do dữ liệu chỉ ghi nhận đến ngày 09/12/2011.

## 2. Cơ cấu doanh thu theo quốc gia (Biểu đồ 2)
- Vương quốc Anh (United Kingdom) chiếm áp đảo **{b2.loc['United Kingdom', 'TyLe_%']:.1f}%** tổng doanh thu nên được tách riêng để làm rõ bức tranh các thị trường xuất khẩu.
- Dẫn đầu thị trường quốc tế là **{nuoc_ngoai.index[0]}** ({nuoc_ngoai['DoanhThu'].iloc[0]:,.0f} GBP - {nuoc_ngoai['TyLe_%'].iloc[0]:.1f}%), theo sau là **{nuoc_ngoai.index[1]}** ({nuoc_ngoai['DoanhThu'].iloc[1]:,.0f} GBP) và **{nuoc_ngoai.index[2]}** ({nuoc_ngoai['DoanhThu'].iloc[2]:,.0f} GBP).

## 3. Top 10 sản phẩm doanh thu cao nhất (Biểu đồ 3)
- Sản phẩm mang lại doanh thu cao nhất là **{b3.index[0]}** đạt **{b3['DoanhThu'].iloc[0]:,.0f} GBP** (với {b3['SoLuong'].iloc[0]:,.0f} sản phẩm bán ra).
- Đứng thứ hai là **{b3.index[1]}** ({b3['DoanhThu'].iloc[1]:,.0f} GBP) và thứ ba là **{b3.index[2]}** ({b3['DoanhThu'].iloc[2]:,.0f} GBP).

## 4. Thời điểm mua sắm của khách hàng (Biểu đồ 5)
- Lượng giao dịch tập trung chủ yếu vào khung giờ hành chính từ **10h đến 15h**, đạt đỉnh vào lúc **{theo_gio.idxmax()}h** ({theo_gio.max():,.0f} GBP).
- **{TEN_THU[theo_thu.idxmax()]}** là ngày có doanh thu cao nhất trong tuần ({theo_thu.max():,.0f} GBP). Cửa hàng không phát sinh giao dịch vào Thứ 7.

## 5. Phân bố giá trị đơn hàng (Biểu đồ 4)
- Phân bố có dạng lệch phải mạnh: giá trị trung bình đạt **{b5.mean():,.0f} GBP/đơn**, cao hơn nhiều so với mức trung vị **{b5.median():,.0f} GBP/đơn**.
- Phần lớn các đơn hàng có quy mô nhỏ và vừa (dưới 500 GBP), bên cạnh một số ít đơn hàng bán buôn giá trị rất lớn kéo mức trung bình lên cao.

## 6. Hành vi khách hàng và Top 10 khách hàng lớn (Biểu đồ 6)
- Trong tổng số **{len(b6):,}** khách hàng định danh, có **{ty_le_mua_lai:.1f}%** khách hàng quay lại mua từ 2 đơn trở lên.
- Nhóm Top 10 khách hàng lớn nhất đóng góp **{ty_le_top10:.1f}%** tổng doanh thu của nhóm khách có mã, dẫn đầu là mã **{b6.index[0]}** ({b6['DoanhThu'].iloc[0]:,.0f} GBP với {b6['SoDon'].iloc[0]} đơn hàng).

## 7. Tình hình hủy đơn hàng (Biểu đồ 7)
- Tổng cộng có **{so_don_huy:,}** hóa đơn bị hủy trên tổng số **{so_don_huy + so_don_ban:,}** giao dịch (tỷ lệ hủy chiếm **{ty_le_huy:.1f}%**).
- Mặt hàng bị hủy nhiều nhất là **{b7.index[0]}** với **{b7.iloc[0]}** hóa đơn hủy, cao gấp đôi sản phẩm đứng thứ hai là **{b7.index[1]}** ({b7.iloc[1]} hóa đơn).
"""
    with open(duong_dan_file, "w", encoding="utf-8") as f:
        f.write(noi_dung)
    print("Đã lưu diễn giải tự động tại:", duong_dan_file)
    return noi_dung


# ==============================================================================
# PHẦN 3: HÀM TỔNG HỢP CHẠY TOÀN BỘ QUY TRÌNH CỦA BIEU_DO.PY
# ==============================================================================

def chay_tat_ca(df, don_huy, bang1, bang2, bang3, bang4, bang5, bang6, bang7, thu_muc_kq="outputs"):
    """Hàm điều phối vẽ đủ 7 biểu đồ và xuất file diễn giải."""
    os.makedirs(thu_muc_kq, exist_ok=True)

    ve_doanh_thu_theo_thang(bang1, f"{thu_muc_kq}/bieu_do_1_doanh_thu_theo_thang.png")
    ve_top_quoc_gia(bang2, f"{thu_muc_kq}/bieu_do_2_top_quoc_gia.png")
    ve_top_san_pham(bang3, f"{thu_muc_kq}/bieu_do_3_top_san_pham.png")
    ve_gia_tri_don_hang(bang5, f"{thu_muc_kq}/bieu_do_4_gia_tri_don_hang.png")
    ve_thoi_diem_mua(bang4, f"{thu_muc_kq}/bieu_do_5_thoi_diem_mua.png")
    ve_top_khach_hang(bang6, f"{thu_muc_kq}/bieu_do_6_top_khach_hang.png")
    ve_top_huy_don(bang7, f"{thu_muc_kq}/bieu_do_7_top_huy_don.png")

    xuat_dien_giai(
        df, don_huy, bang1, bang2, bang3, bang4, bang5, bang6, bang7,
        f"{thu_muc_kq}/dien_giai_bieu_do.md"
    )
"""Mô-đun bieu_do: vẽ 7 biểu đồ tương tác bằng Plotly (xem trực tiếp trên IDE + xuất PNG/HTML) và tự động xuất diễn giải."""

import os
import plotly.express as px

TEN_THU = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]


def luu_va_hien_thi(fig, duong_dan, hien_thi=True):
    """Lưu biểu đồ ra file PNG (để làm PDF), file HTML (tương tác) và bật xem trên IDE."""
    fig.update_layout(template="plotly_white", font=dict(size=12))

    # 1. Lưu file tương tác .html (mở bằng trình duyệt để rê chuột xem số liệu)
    duong_dan_html = os.path.splitext(duong_dan)[0] + ".html"
    fig.write_html(duong_dan_html)

    # 2. Lưu file ảnh tĩnh .png (cần thư viện kaleido) để chèn vào báo cáo PDF
    try:
        fig.write_image(duong_dan, scale=2)
        print("Đã lưu:", duong_dan, "và", duong_dan_html)
    except Exception:
        print("Đã lưu bản tương tác:", duong_dan_html, "(cài thêm 'pip install kaleido' nếu muốn xuất kèm PNG)")

    # 3. Hiển thị trực tiếp trên IDE / trình duyệt để xem số liệu
    if hien_thi:
        fig.show()


# ==============================================================================
# PHẦN 1: CÁC HÀM VẼ 7 BIỂU ĐỒ TƯƠNG TÁC BẰNG PLOTLY
# ==============================================================================

def ve_doanh_thu_theo_thang(bang, duong_dan, hien_thi=True):
    """Biểu đồ 1 (Câu 1): Biểu đồ đường doanh thu theo tháng."""
    df_plot = bang.reset_index()
    df_plot.columns = ["Thang", "DoanhThu"]
    df_plot["DoanhThu_Nghin"] = df_plot["DoanhThu"] / 1000

    fig = px.line(
        df_plot, x="Thang", y="DoanhThu_Nghin", markers=True,
        title="Doanh thu theo tháng (12/2010 - 12/2011)",
        labels={"Thang": "Tháng", "DoanhThu_Nghin": "Doanh thu (nghìn GBP)"},
        hover_data={"DoanhThu": ":,.0f", "DoanhThu_Nghin": ":.2f"}
    )
    fig.update_traces(line=dict(width=3, color="steelblue"), marker=dict(size=8))
    luu_va_hien_thi(fig, duong_dan, hien_thi)


def ve_top_quoc_gia(bang, duong_dan, hien_thi=True):
    """Biểu đồ 2 (Câu 2): Biểu đồ cột ngang 10 quốc gia doanh thu cao nhất (trừ Anh)."""
    top = bang.drop("United Kingdom").head(10).sort_values("DoanhThu").reset_index()
    top["DoanhThu_Nghin"] = top["DoanhThu"] / 1000

    fig = px.bar(
        top, x="DoanhThu_Nghin", y=top.columns[0], orientation="h",
        title="Top 10 quốc gia theo doanh thu (không tính Anh)",
        labels={"DoanhThu_Nghin": "Doanh thu (nghìn GBP)", top.columns[0]: "Quốc gia"},
        hover_data={"DoanhThu": ":,.0f", "TyLe_%": ":.2f"} if "TyLe_%" in top.columns else {"DoanhThu": ":,.0f"}
    )
    fig.update_traces(marker_color="#1f77b4")
    luu_va_hien_thi(fig, duong_dan, hien_thi)


def ve_top_san_pham(bang, duong_dan, hien_thi=True):
    """Biểu đồ 3 (Câu 3): Biểu đồ cột ngang 10 sản phẩm doanh thu cao nhất."""
    top = bang.sort_values("DoanhThu").reset_index()
    top["DoanhThu_Nghin"] = top["DoanhThu"] / 1000

    fig = px.bar(
        top, x="DoanhThu_Nghin", y=top.columns[0], orientation="h",
        title="Top 10 sản phẩm theo doanh thu",
        labels={"DoanhThu_Nghin": "Doanh thu (nghìn GBP)", top.columns[0]: "Sản phẩm"},
        hover_data={"DoanhThu": ":,.0f", "SoLuong": ":,.0f"} if "SoLuong" in top.columns else {"DoanhThu": ":,.0f"}
    )
    fig.update_traces(marker_color="darkorange")
    luu_va_hien_thi(fig, duong_dan, hien_thi)


def ve_gia_tri_don_hang(don_hang, duong_dan, hien_thi=True):
    """Biểu đồ 4 (Câu 5): Histogram phân bố giá trị đơn hàng (< 2.000 GBP)."""
    df_plot = don_hang[don_hang < 2000].reset_index()
    df_plot.columns = ["MaDon", "GiaTri"]
    trung_vi = don_hang.median()

    fig = px.histogram(
        df_plot, x="GiaTri", nbins=50,
        title="Phân bố giá trị đơn hàng (các đơn dưới 2.000 GBP)",
        labels={"GiaTri": "Giá trị đơn hàng (GBP)", "count": "Số đơn hàng"}
    )
    fig.update_traces(marker_color="#1f77b4", marker_line_color="white", marker_line_width=1)
    fig.add_vline(
        x=trung_vi, line_dash="dash", line_color="red",
        annotation_text=f"Trung vị: {trung_vi:.0f} GBP",
        annotation_position="top right"
    )
    luu_va_hien_thi(fig, duong_dan, hien_thi)


def ve_thoi_diem_mua(bang, duong_dan, hien_thi=True):
    """Biểu đồ 5 (Câu 4): Bản đồ nhiệt (Heatmap) doanh thu theo Thứ và Giờ."""
    du_lieu_nghin = bang.values / 1000
    nhan_thu = [TEN_THU[i] for i in bang.index]
    nhan_gio = [f"{h}h" for h in bang.columns]

    fig = px.imshow(
        du_lieu_nghin,
        x=nhan_gio, y=nhan_thu,
        color_continuous_scale="YlOrRd",
        aspect="auto",
        title="Bản đồ nhiệt doanh thu theo Thứ và Giờ trong ngày",
        labels=dict(x="Giờ trong ngày", y="Thứ trong tuần", color="Doanh thu (nghìn GBP)")
    )
    luu_va_hien_thi(fig, duong_dan, hien_thi)


def ve_top_khach_hang(bang, duong_dan, hien_thi=True):
    """Biểu đồ 6 (Câu 6): Biểu đồ cột ngang Top 10 khách hàng doanh thu cao nhất."""
    top = bang.head(10).sort_values("DoanhThu").reset_index()
    top["KhachHang"] = [f"KH {cid}" for cid in top[top.columns[0]]]
    top["DoanhThu_Nghin"] = top["DoanhThu"] / 1000

    fig = px.bar(
        top, x="DoanhThu_Nghin", y="KhachHang", orientation="h",
        title="Top 10 khách hàng đóng góp doanh thu cao nhất",
        labels={"DoanhThu_Nghin": "Doanh thu (nghìn GBP)", "KhachHang": "Mã khách hàng"},
        hover_data={"DoanhThu": ":,.0f", "SoDon": True} if "SoDon" in top.columns else {"DoanhThu": ":,.0f"}
    )
    fig.update_traces(marker_color="seagreen")
    luu_va_hien_thi(fig, duong_dan, hien_thi)


def ve_top_huy_don(bang, duong_dan, hien_thi=True):
    """Biểu đồ 7 (Câu 7): Biểu đồ cột ngang Top 10 sản phẩm bị hủy nhiều nhất."""
    top = bang.sort_values().reset_index()
    top.columns = ["SanPham", "SoLanHuy"]

    fig = px.bar(
        top, x="SoLanHuy", y="SanPham", orientation="h",
        title="Top 10 sản phẩm có số lần bị hủy nhiều nhất",
        labels={"SoLanHuy": "Số hóa đơn hủy", "SanPham": "Sản phẩm"}
    )
    fig.update_traces(marker_color="crimson")
    luu_va_hien_thi(fig, duong_dan, hien_thi)


# ==============================================================================
# PHẦN 2: HÀM TỰ ĐỘNG SINH DIỄN GIẢI BIỂU ĐỒ RA FILE VĂN BẢN (.MD)
# ==============================================================================

def xuat_dien_giai(df, don_huy, b1, b2, b3, b4, b5, b6, b7, duong_dan_file):
    """Tự động tính toán các chỉ số từ 7 bảng phân tích và xuất ra file diễn giải."""
    du_thang = b1.iloc[:-1]
    nuoc_ngoai = b2.drop("United Kingdom")
    theo_thu = b4.sum(axis=1)
    theo_gio = b4.sum(axis=0)
    ty_le_mua_lai = (b6["SoDon"] >= 2).mean() * 100
    ty_le_top10 = b6["DoanhThu"].head(10).sum() / b6["DoanhThu"].sum() * 100
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

def chay_tat_ca(df, don_huy, bang1, bang2, bang3, bang4, bang5, bang6, bang7, thu_muc_kq="outputs", hien_thi=True):
    """Hàm điều phối vẽ đủ 7 biểu đồ tương tác và xuất file diễn giải."""
    os.makedirs(thu_muc_kq, exist_ok=True)

    ve_doanh_thu_theo_thang(bang1, f"{thu_muc_kq}/bieu_do_1_doanh_thu_theo_thang.png", hien_thi)
    ve_top_quoc_gia(bang2, f"{thu_muc_kq}/bieu_do_2_top_quoc_gia.png", hien_thi)
    ve_top_san_pham(bang3, f"{thu_muc_kq}/bieu_do_3_top_san_pham.png", hien_thi)
    ve_gia_tri_don_hang(bang5, f"{thu_muc_kq}/bieu_do_4_gia_tri_don_hang.png", hien_thi)
    ve_thoi_diem_mua(bang4, f"{thu_muc_kq}/bieu_do_5_thoi_diem_mua.png", hien_thi)
    ve_top_khach_hang(bang6, f"{thu_muc_kq}/bieu_do_6_top_khach_hang.png", hien_thi)
    ve_top_huy_don(bang7, f"{thu_muc_kq}/bieu_do_7_top_huy_don.png", hien_thi)

    xuat_dien_giai(
        df, don_huy, bang1, bang2, bang3, bang4, bang5, bang6, bang7,
        f"{thu_muc_kq}/dien_giai_bieu_do.md"
    )
"""Mô-đun phan_tich: thống kê mô tả và 7 hàm trả lời 7 câu hỏi về doanh thu và xu hướng bán hàng."""

import pandas as pd


def thong_ke_mo_ta(df):
    """Thống kê mô tả các cột số và vài con số tổng quan."""
    bang = df[["QUANTITYORDERED", "PRICEEACH", "Revenue"]].describe().round(2)
    print(bang)
    print(f"\nTổng doanh thu: {df['Revenue'].sum():,.0f} USD")
    print("Số đơn hàng:", df["ORDERNUMBER"].nunique())
    print("Số khách hàng:", df["CUSTOMERNAME"].nunique())
    print("Số sản phẩm:", df["PRODUCTCODE"].nunique())
    print("Số quốc gia:", df["COUNTRY"].nunique())
    return bang


def cau1_doanh_thu_theo_thang(df):
    """Câu 1: Doanh thu từng tháng ra sao? Năm sau tăng bao nhiêu % so với năm trước?"""
    print("\nCÂU 1: Doanh thu theo tháng và tăng trưởng")
    bang = df.groupby("Month")["Revenue"].sum().round(0)
    print(bang)
    print(f"→ Tháng cao nhất: {bang.idxmax()} với {bang.max():,.0f} USD")
    print(f"→ Tháng thấp nhất: {bang.idxmin()} với {bang.min():,.0f} USD")

    theo_nam = df.groupby("YEAR_ID")["Revenue"].sum()
    print("\nDoanh thu theo năm (năm 2005 chỉ có đến tháng 5):")
    print(theo_nam.round(0))
    tang_2004 = (theo_nam.loc[2004] / theo_nam.loc[2003] - 1) * 100
    print(f"→ Năm 2004 so với năm 2003: {tang_2004:+.1f}%")

    # Năm 2005 chưa đủ 12 tháng nên so với CÙNG KỲ (tháng 1-5) của năm 2004 mới công bằng
    cung_ky = df[df["MONTH_ID"] <= 5].groupby("YEAR_ID")["Revenue"].sum()
    tang_2005 = (cung_ky.loc[2005] / cung_ky.loc[2004] - 1) * 100
    print(f"→ 5 tháng đầu 2005 so với 5 tháng đầu 2004: {tang_2005:+.1f}%")
    return bang


def cau2_quoc_gia(df):
    """Câu 2: Quốc gia nào mang lại nhiều doanh thu nhất?"""
    print("\nCÂU 2: Doanh thu theo quốc gia")
    bang = df.groupby("COUNTRY").agg(
        DoanhThu=("Revenue", "sum"),            # tổng doanh thu
        SoDon=("ORDERNUMBER", "nunique"),       # số đơn hàng khác nhau
        SoKhach=("CUSTOMERNAME", "nunique"),    # số khách hàng khác nhau
    )
    bang["TyLe_%"] = bang["DoanhThu"] / bang["DoanhThu"].sum() * 100
    bang["GiaTriDonTB"] = bang["DoanhThu"] / bang["SoDon"]
    bang = bang.sort_values("DoanhThu", ascending=False).round(1)
    print(bang.head(10))
    print(f"→ Nước doanh thu cao nhất: {bang.index[0]} ({bang['TyLe_%'].iloc[0]}%)")
    print(f"→ 3 nước đầu chiếm {bang['TyLe_%'].head(3).sum():.1f}% doanh thu")
    return bang


def cau3_san_pham_ban_chay(df):
    """Câu 3: Sản phẩm nào bán chạy nhất? Dòng sản phẩm nào đang tăng, dòng nào giảm?"""
    print("\nCÂU 3: Top 10 sản phẩm theo doanh thu")
    bang = df.groupby("PRODUCTCODE").agg(
        DoanhThu=("Revenue", "sum"),
        SoLuong=("QUANTITYORDERED", "sum"),
        DongSanPham=("PRODUCTLINE", "first"),   # mỗi mã thuộc đúng 1 dòng sản phẩm
    )
    bang["DoanhThu"] = bang["DoanhThu"].round(0)
    bang = bang.sort_values("DoanhThu", ascending=False).head(10)
    print(bang)
    print(f"→ Doanh thu cao nhất: {bang.index[0]} ({bang['DoanhThu'].iloc[0]:,.0f} USD)")

    # Xu hướng: doanh thu từng dòng sản phẩm qua các năm, kèm % tăng trưởng 2004 so với 2003
    theo_dong = pd.pivot_table(df, values="Revenue", index="PRODUCTLINE",
                               columns="YEAR_ID", aggfunc="sum", fill_value=0).round(0)
    theo_dong["TangTruong_2004_%"] = ((theo_dong[2004] / theo_dong[2003] - 1) * 100).round(1)
    theo_dong = theo_dong.sort_values(2004, ascending=False)
    print("\nDoanh thu theo dòng sản phẩm qua các năm (2005 mới có 5 tháng):")
    print(theo_dong)
    tang_nhat = theo_dong["TangTruong_2004_%"].idxmax()
    giam_nhat = theo_dong["TangTruong_2004_%"].idxmin()
    print(f"→ Tăng mạnh nhất 2004 so với 2003: {tang_nhat} ({theo_dong.loc[tang_nhat, 'TangTruong_2004_%']:+.1f}%)")
    print(f"→ Tăng yếu nhất (hoặc giảm): {giam_nhat} ({theo_dong.loc[giam_nhat, 'TangTruong_2004_%']:+.1f}%)")
    return bang


def cau4_thoi_diem_mua(df):
    """Câu 4: Doanh thu cao nhất vào tháng nào, quý nào trong năm (mùa vụ)?"""
    print("\nCÂU 4: Doanh thu theo năm (hàng) và tháng trong năm (cột)")
    bang = pd.pivot_table(df, values="Revenue", index="YEAR_ID", columns="MONTH_ID",
                          aggfunc="sum", fill_value=0).round(0)
    print(bang.to_string())

    # Chỉ dùng 2 năm đủ 12 tháng (2003, 2004) để so sánh công bằng
    hai_nam = df[df["YEAR_ID"].isin([2003, 2004])]
    theo_thang = hai_nam.groupby("MONTH_ID")["Revenue"].sum()
    ty_le_thang = theo_thang / theo_thang.sum() * 100
    thang_cao = ty_le_thang.idxmax()
    print(f"→ Tháng bán nhiều nhất: tháng {thang_cao} (chiếm {ty_le_thang.max():.1f}% doanh thu cả năm)")

    theo_quy = hai_nam.groupby("QTR_ID")["Revenue"].sum()
    ty_le_quy = theo_quy / theo_quy.sum() * 100
    print("\nTỷ trọng doanh thu theo quý (%):")
    print(ty_le_quy.round(1))
    print(f"→ Quý bán nhiều nhất: quý {ty_le_quy.idxmax()} (chiếm {ty_le_quy.max():.1f}%)")
    return bang


def cau5_gia_tri_don_hang(df):
    """Câu 5: Một đơn hàng thường có giá trị bao nhiêu?"""
    print("\nCÂU 5: Giá trị mỗi đơn hàng")
    don_hang = df.groupby("ORDERNUMBER")["Revenue"].sum()  # tổng tiền của từng đơn
    print(don_hang.describe().round(1))
    print(f"→ Trung bình {don_hang.mean():,.0f} USD/đơn, trung vị {don_hang.median():,.0f} USD/đơn")
    if don_hang.mean() > don_hang.median():
        print("→ Trung bình lớn hơn trung vị: một số ít đơn rất lớn kéo trung bình lên")
    return don_hang


def cau6_khach_hang(df):
    """Câu 6: Doanh thu phụ thuộc vào bao nhiêu khách lớn?"""
    print("\nCÂU 6: Khách hàng đóng góp doanh thu")
    bang = df.groupby("CUSTOMERNAME").agg(
        SoDon=("ORDERNUMBER", "nunique"),
        DoanhThu=("Revenue", "sum"),
    ).sort_values("DoanhThu", ascending=False)
    bang["TyLe_%"] = (bang["DoanhThu"] / bang["DoanhThu"].sum() * 100).round(1)
    bang["DoanhThu"] = bang["DoanhThu"].round(0)
    print(bang.head(10))
    print(f"→ Khách lớn nhất ({bang.index[0]}) chiếm {bang['TyLe_%'].iloc[0]}% doanh thu")
    print(f"→ 10 khách lớn nhất chiếm {bang['TyLe_%'].head(10).sum():.1f}% doanh thu "
          f"(trong tổng {len(bang)} khách)")
    return bang


def cau7_huy_don(df, don_huy):
    """Câu 7: Hủy đơn làm mất bao nhiêu doanh thu? Dòng sản phẩm nào mất nhiều nhất?"""
    print("\nCÂU 7: Hủy đơn")
    so_don_huy = don_huy["ORDERNUMBER"].nunique()
    so_don_ban = df["ORDERNUMBER"].nunique()
    ty_le = so_don_huy / (so_don_huy + so_don_ban) * 100
    bang = don_huy.groupby("PRODUCTLINE").agg(
        SoDon=("ORDERNUMBER", "nunique"),   # số đơn hủy có chứa dòng sản phẩm này
        SoDong=("ORDERNUMBER", "size"),     # số dòng hàng bị hủy
        DoanhThuMat=("SALES", "sum"),       # doanh thu bị mất
    ).sort_values("DoanhThuMat", ascending=False).round(0)
    print(bang)
    mat = don_huy["SALES"].sum()
    ty_le_mat = mat / (mat + df["Revenue"].sum()) * 100
    print(f"→ Tỷ lệ đơn bị hủy: {ty_le:.1f}% ({so_don_huy} / {so_don_huy + so_don_ban} đơn)")
    print(f"→ Doanh thu bị mất do hủy: {mat:,.0f} USD ({ty_le_mat:.1f}% so với tổng doanh thu)")
    print(f"→ Dòng sản phẩm mất nhiều nhất: {bang.index[0]} ({bang['DoanhThuMat'].iloc[0]:,.0f} USD)")
    return bang

    cau6_khach_hang(df)
    cau7_huy_don(df, du_lieu.don_huy)

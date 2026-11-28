"""Mô-đun bieu_do: mỗi câu hỏi 1 hàm vẽ biểu đồ Plotly, trả về fig để notebook hiển thị."""

import plotly.express as px


def ve_cot_ngang(chuoi, tieu_de, nhan_y, mau):
    """Cột ngang cho một Series (nhãn -> doanh thu USD), giá trị lớn nhất nằm trên cùng."""
    chuoi = chuoi.sort_values()  # cột ngang vẽ từ dưới lên nên sắp tăng dần để cột dài nhất ở trên
    fig = px.bar(x=chuoi.values / 1000, y=chuoi.index, orientation="h", title=tieu_de,
                 labels={"x": "Doanh thu (nghìn USD)", "y": nhan_y})
    fig.update_traces(marker_color=mau)
    return fig


def ve_doanh_thu_theo_thang(bang):
    """Biểu đồ Câu 1: đường doanh thu theo tháng."""
    fig = px.line(x=bang.index, y=bang.values / 1000, markers=True,
                  title="Doanh thu theo tháng (01/2003 - 05/2005)",
                  labels={"x": "Tháng", "y": "Doanh thu (nghìn USD)"})
    return fig


def ve_top_quoc_gia(bang):
    """Biểu đồ Câu 2: cột ngang 10 quốc gia doanh thu cao nhất."""
    return ve_cot_ngang(bang["DoanhThu"].head(10), "Top 10 quốc gia theo doanh thu",
                        "Quốc gia", "#1f77b4")


def ve_top_san_pham(bang):
    """Biểu đồ Câu 3: cột ngang 10 sản phẩm doanh thu cao nhất (kèm dòng sản phẩm)."""
    chuoi = bang["DoanhThu"].copy()
    chuoi.index = [f"{ma} ({dong})" for ma, dong in zip(bang.index, bang["DongSanPham"])]
    return ve_cot_ngang(chuoi, "Top 10 sản phẩm theo doanh thu",
                        "Mã sản phẩm (dòng sản phẩm)", "darkorange")


def ve_mua_vu(bang):
    """Biểu đồ Câu 4: heatmap doanh thu năm x tháng; ô trống = chưa có dữ liệu."""
    fig = px.imshow(bang.values / 1000, x=[str(t) for t in bang.columns], y=[str(n) for n in bang.index],
                    color_continuous_scale="YlOrRd", aspect="auto", text_auto=".0f",
                    title="Doanh thu theo năm và tháng (nghìn USD, ô trống: chưa có dữ liệu)",
                    labels={"x": "Tháng", "y": "Năm", "color": "Nghìn USD"})
    return fig


def ve_gia_tri_don_hang(don_hang):
    """Biểu đồ Câu 5: histogram giá trị đơn hàng, kẻ đường trung vị."""
    trung_vi = don_hang.median()
    fig = px.histogram(x=don_hang.values / 1000, nbins=30, title="Phân bố giá trị đơn hàng",
                       labels={"x": "Giá trị đơn hàng (nghìn USD)"})
    fig.update_layout(yaxis_title="Số đơn hàng", bargap=0.05)
    fig.add_vline(x=trung_vi / 1000, line_dash="dash", line_color="red",
                  annotation_text=f"Trung vị: {trung_vi:,.0f} USD")
    return fig


def ve_top_khach_hang(bang):
    """Biểu đồ Câu 6: cột ngang 10 khách hàng doanh thu cao nhất."""
    return ve_cot_ngang(bang["DoanhThu"].head(10), "Top 10 khách hàng theo doanh thu",
                        "Khách hàng", "seagreen")


def ve_huy_don(bang):
    """Biểu đồ Câu 7: cột doanh thu mất do hủy đơn theo dòng sản phẩm."""
    fig = px.bar(x=bang.index, y=bang["DoanhThuMat"] / 1000,
                 title="Doanh thu mất do hủy đơn theo dòng sản phẩm",
                 labels={"x": "Dòng sản phẩm", "y": "Doanh thu mất (nghìn USD)"})
    fig.update_traces(marker_color="crimson")
    return fig


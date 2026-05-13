import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Dashboard Tuntutan Elaun Lebih Masa",
    page_icon="📊",
    layout="wide"
)

# =========================
# CONFIG
# =========================
EXCEL_FILE = "TUNTUTAN ELAUN LEBIH MASA TAHUN 2023-2025v2.xlsx"
SHEET_NAME = "Sheet1"

BASE_DIR = Path(__file__).parent
FILE_PATH = BASE_DIR / EXCEL_FILE


# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path, sheet_name=SHEET_NAME)

    # Buang kolum kosong
    df = df.dropna(axis=1, how="all")

    # Bersihkan nama kolum
    df.columns = [str(col).strip() for col in df.columns]

    # Pastikan Amount nombor
    if "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

    # Convert Month seperti Mar-25, Sep-25 kepada tarikh
    if "Month" in df.columns:
        df["Month_Date"] = pd.to_datetime(df["Month"], format="%b-%y", errors="coerce")
        df["Tahun"] = df["Month_Date"].dt.year
        df["Bulan_No"] = df["Month_Date"].dt.month
        df["Bulan"] = df["Month_Date"].dt.strftime("%b")
        df["Bulan_Tahun"] = df["Month_Date"].dt.strftime("%b-%Y")

    # Convert Start Date jika ada
    if "Start Date" in df.columns:
        if pd.api.types.is_numeric_dtype(df["Start Date"]):
            df["Start Date Clean"] = pd.to_datetime(
                df["Start Date"],
                unit="D",
                origin="1899-12-30",
                errors="coerce"
            )
        else:
            df["Start Date Clean"] = pd.to_datetime(df["Start Date"], errors="coerce")

    return df


# =========================
# CHECK FILE
# =========================
if not FILE_PATH.exists():
    st.error("Fail Excel tidak ditemui.")
    st.write("Sila pastikan fail ini berada dalam folder yang sama dengan app.py:")
    st.code(EXCEL_FILE)
    st.stop()

df = load_data(FILE_PATH)


# =========================
# SIDEBAR
# =========================
st.sidebar.title("Dashboard OT")
st.sidebar.caption("Tuntutan Elaun Lebih Masa 2023-2025")

menu = st.sidebar.radio(
    "Menu Utama",
    [
        "Ringkasan",
        "Analisis Bulanan",
        "Analisis Bahagian",
        "Analisis Pegawai",
        "Data Penuh"
    ]
)

st.sidebar.divider()

# Filter Tahun
if "Tahun" in df.columns:
    senarai_tahun = ["Semua"] + sorted(df["Tahun"].dropna().astype(int).astype(str).unique().tolist())
else:
    senarai_tahun = ["Semua"]

pilih_tahun = st.sidebar.selectbox("Pilih Tahun", senarai_tahun)

# Filter Bulan
senarai_bulan = [
    "Semua",
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

pilih_bulan = st.sidebar.selectbox("Pilih Bulan", senarai_bulan)

# Filter Personnel Area
if "Personnel Area" in df.columns:
    senarai_area = ["Semua"] + sorted(df["Personnel Area"].dropna().astype(str).unique().tolist())
    pilih_area = st.sidebar.selectbox("Pilih Personnel Area", senarai_area)
else:
    pilih_area = "Semua"

# Filter Personnel Subarea
if "Personnel Subarea" in df.columns:
    senarai_subarea = ["Semua"] + sorted(df["Personnel Subarea"].dropna().astype(str).unique().tolist())
    pilih_subarea = st.sidebar.selectbox("Pilih Personnel Subarea", senarai_subarea)
else:
    pilih_subarea = "Semua"

# Filter nama pegawai
if "Personnel Number" in df.columns:
    senarai_pegawai = ["Semua"] + sorted(df["Personnel Number"].dropna().astype(str).unique().tolist())
    pilih_pegawai = st.sidebar.selectbox("Pilih Pegawai", senarai_pegawai)
else:
    pilih_pegawai = "Semua"


# =========================
# APPLY FILTER
# =========================
df_filter = df.copy()

if pilih_tahun != "Semua" and "Tahun" in df_filter.columns:
    df_filter = df_filter[df_filter["Tahun"].astype("Int64").astype(str) == pilih_tahun]

if pilih_bulan != "Semua" and "Bulan" in df_filter.columns:
    df_filter = df_filter[df_filter["Bulan"] == pilih_bulan]

if pilih_area != "Semua" and "Personnel Area" in df_filter.columns:
    df_filter = df_filter[df_filter["Personnel Area"].astype(str) == pilih_area]

if pilih_subarea != "Semua" and "Personnel Subarea" in df_filter.columns:
    df_filter = df_filter[df_filter["Personnel Subarea"].astype(str) == pilih_subarea]

if pilih_pegawai != "Semua" and "Personnel Number" in df_filter.columns:
    df_filter = df_filter[df_filter["Personnel Number"].astype(str) == pilih_pegawai]


# =========================
# MAIN TITLE
# =========================
st.title("Dashboard Tuntutan Elaun Lebih Masa")
st.caption("Data Tahun 2023 - 2025")

st.divider()


# =========================
# KPI
# =========================
jumlah_rekod = len(df_filter)
jumlah_tuntutan = df_filter["Amount"].sum() if "Amount" in df_filter.columns else 0
purata_tuntutan = df_filter["Amount"].mean() if "Amount" in df_filter.columns and len(df_filter) > 0 else 0

if "Pers.No." in df_filter.columns:
    jumlah_pegawai = df_filter["Pers.No."].nunique()
elif "Personnel Number" in df_filter.columns:
    jumlah_pegawai = df_filter["Personnel Number"].nunique()
else:
    jumlah_pegawai = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Jumlah Rekod", f"{jumlah_rekod:,}")

with col2:
    st.metric("Jumlah Tuntutan", f"RM {jumlah_tuntutan:,.2f}")

with col3:
    st.metric("Jumlah Pegawai", f"{jumlah_pegawai:,}")

with col4:
    st.metric("Purata Tuntutan", f"RM {purata_tuntutan:,.2f}")


# =========================
# PAGE: RINGKASAN
# =========================
if menu == "Ringkasan":
    st.subheader("Ringkasan Data")

    left, right = st.columns(2)

    with left:
        if "Tahun" in df_filter.columns and "Amount" in df_filter.columns:
            yearly = (
                df_filter
                .groupby("Tahun", as_index=False)["Amount"]
                .sum()
                .sort_values("Tahun")
            )

            fig_year = px.bar(
                yearly,
                x="Tahun",
                y="Amount",
                text_auto=".2s",
                title="Jumlah Tuntutan Mengikut Tahun"
            )

            st.plotly_chart(fig_year, use_container_width=True)

    with right:
        if "Personnel Area" in df_filter.columns and "Amount" in df_filter.columns:
            area = (
                df_filter
                .groupby("Personnel Area", as_index=False)["Amount"]
                .sum()
                .sort_values("Amount", ascending=False)
                .head(10)
            )

            fig_area = px.bar(
                area,
                x="Amount",
                y="Personnel Area",
                orientation="h",
                text_auto=".2s",
                title="Top 10 Personnel Area Mengikut Jumlah Tuntutan"
            )

            st.plotly_chart(fig_area, use_container_width=True)

    st.subheader("Preview Data")
    st.dataframe(df_filter.head(30), use_container_width=True)


# =========================
# PAGE: ANALISIS BULANAN
# =========================
elif menu == "Analisis Bulanan":
    st.subheader("Analisis Bulanan")

    if "Month_Date" in df_filter.columns and "Amount" in df_filter.columns:
        monthly = (
            df_filter
            .dropna(subset=["Month_Date"])
            .groupby(["Month_Date", "Bulan_Tahun"], as_index=False)["Amount"]
            .sum()
            .sort_values("Month_Date")
        )

        fig_month = px.line(
            monthly,
            x="Bulan_Tahun",
            y="Amount",
            markers=True,
            title="Trend Jumlah Tuntutan Mengikut Bulan"
        )

        st.plotly_chart(fig_month, use_container_width=True)

        st.dataframe(monthly, use_container_width=True)
    else:
        st.warning("Kolum Month atau Amount tidak ditemui.")


# =========================
# PAGE: ANALISIS BAHAGIAN
# =========================
elif menu == "Analisis Bahagian":
    st.subheader("Analisis Mengikut Bahagian / Personnel Subarea")

    if "Personnel Subarea" in df_filter.columns and "Amount" in df_filter.columns and "Pers.No." in df_filter.columns:
        bahagian_summary = (
            df_filter
            .groupby("Personnel Subarea", as_index=False)
            .agg(
                Jumlah_Tuntutan=("Amount", "sum"),
                Jumlah_Rekod=("Amount", "count"),
                Jumlah_Pegawai=("Pers.No.", "nunique"),
                Purata_Tuntutan=("Amount", "mean")
            )
            .sort_values("Jumlah_Tuntutan", ascending=False)
        )

        fig = px.bar(
            bahagian_summary.head(20),
            x="Jumlah_Tuntutan",
            y="Personnel Subarea",
            orientation="h",
            text_auto=".2s",
            title="Top 20 Bahagian Mengikut Jumlah Tuntutan"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Jadual Ringkasan Bahagian")
        st.dataframe(bahagian_summary, use_container_width=True)

        st.subheader("Maklumat Terperinci Mengikut Bahagian")

        detail_bahagian = df_filter[
            [
                "Personnel Subarea",
                "Pers.No.",
                "Personnel Number",
                "Month",
                "Amount"
            ]
        ].copy()

        detail_bahagian = detail_bahagian.sort_values(
            ["Personnel Subarea", "Pers.No.", "Month"]
        )

        st.dataframe(detail_bahagian, use_container_width=True)

    else:
        st.warning("Kolum Personnel Subarea, Pers.No. atau Amount tidak ditemui.")


# =========================
# PAGE: ANALISIS PEGAWAI
# =========================
elif menu == "Analisis Pegawai":
    st.subheader("Analisis Mengikut Pegawai")

    if "Pers.No." in df_filter.columns and "Personnel Number" in df_filter.columns and "Amount" in df_filter.columns:
        pegawai_summary = (
            df_filter
            .groupby(["Pers.No.", "Personnel Number"], as_index=False)
            .agg(
                Jumlah_Tuntutan=("Amount", "sum"),
                Jumlah_Rekod=("Amount", "count"),
                Purata_Tuntutan=("Amount", "mean")
            )
            .sort_values("Jumlah_Tuntutan", ascending=False)
        )

        fig = px.bar(
            pegawai_summary.head(20),
            x="Jumlah_Tuntutan",
            y="Personnel Number",
            orientation="h",
            text_auto=".2s",
            title="Top 20 Pegawai Mengikut Jumlah Tuntutan",
            hover_data=["Pers.No.", "Jumlah_Rekod", "Purata_Tuntutan"]
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Jadual Ringkasan Pegawai")
        st.dataframe(pegawai_summary, use_container_width=True)

        st.subheader("Maklumat Terperinci Pegawai")

        detail_pegawai = df_filter[
            [
                "Pers.No.",
                "Personnel Number",
                "Personnel Subarea",
                "Month",
                "Amount"
            ]
        ].copy()

        detail_pegawai = detail_pegawai.sort_values(
            ["Pers.No.", "Month"]
        )

        st.dataframe(detail_pegawai, use_container_width=True)

    else:
        st.warning("Kolum Pers.No., Personnel Number atau Amount tidak ditemui.")


# =========================
# PAGE: DATA PENUH
# =========================
elif menu == "Data Penuh":
    st.subheader("Data Penuh Selepas Filter")

    st.dataframe(df_filter, use_container_width=True)

    st.download_button(
        label="Download Data Filtered CSV",
        data=df_filter.to_csv(index=False).encode("utf-8-sig"),
        file_name="data_ot_filtered.csv",
        mime="text/csv"
    )
import streamlit as st
import ibpmodel as ibp
import pandas as pd
import numpy as np

# ====================== KONFIGURASI HALAMAN ======================
st.set_page_config(
    page_title="IBP Model Calculator",
    page_icon="🌌",
    layout="wide"
)

st.title("🌌 Ionospheric Bubble Probability (IBP) Calculator")
st.markdown("""
Aplikasi ini menghitung **probabilitas terjadinya Plasma Bubble** di ionosfer ekuatorial  
menggunakan model resmi Swarm (ESA) — mendukung **Model Klimatologis** dan **Model Machine Learning**.
""")

# ====================== SIDEBAR - INPUT ======================
st.sidebar.header("⚙️ Parameter Input")

# Pilihan model
model_type = st.sidebar.radio(
    "Pilih Model",
    options=["Klimatologis (Klasik)", "Machine Learning (ML)"],
    index=1,  # default ke ML
    help="ML lebih sensitif terhadap bubble yang lemah"
)

elec_density = True if "Machine Learning" in model_type else False

# Input parameter
col1, col2 = st.sidebar.columns(2)

with col1:
    input_type = st.radio("Tipe Waktu", ["Day of Year (DOY)", "Bulan"])

with col2:
    if input_type == "Day of Year (DOY)":
        day_month = st.number_input("DOY", min_value=1, max_value=365, value=15)
    else:
        day_month = st.selectbox(
            "Bulan",
            options=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            index=0
        )

longitude = st.sidebar.slider(
    "Longitude (°)",
    min_value=-180,
    max_value=180,
    value=0,
    step=5
)

# --- PERBAIKAN SLIDER WAKTU LOKAL ---
local_time_slider = st.sidebar.slider(
    "Local Time (18:00 - 06:00)",
    min_value=18.0,
    max_value=30.0,   # 24.0 = 00:00, 30.0 = 06:00 pagi
    value=21.0,
    step=0.5,
    help="Geser untuk memilih waktu. Angka 24.0 berarti tengah malam (00:00)."
)

# Tambahkan teks kecil di bawah slider agar pengguna paham
st.sidebar.caption("💡 Angka 18.0 - 23.5 = Malam hari | 24.0 - 30.0 = Pagi hari (Contoh: 25.0 = 01:00 Pagi)")

# Konversi kembali ke format 0-24 jam untuk dibaca oleh model ibpmodel
if local_time_slider >= 24.0:
    local_time_model = local_time_slider - 24.0
else:
    local_time_model = local_time_slider

# ------------------------------------

f107 = st.sidebar.slider(
    "F10.7 Solar Flux",
    min_value=70,
    max_value=200,
    value=150,
    step=1
)

# Tombol hitung
hitung = st.sidebar.button("🚀 Hitung IBP", type="primary", use_container_width=True)

# ====================== HASIL ======================
if hitung:
    with st.spinner("Sedang menghitung..."):
        try:
            # Panggil model menggunakan local_time_model (yang sudah dikonversi ke 0-24)
            result = ibp.calculateIBPindex(
                day_month=day_month,
                longitude=longitude,
                local_time=local_time_model, 
                f107=f107,
                elecDensity=elec_density
            )

            ibp_value = float(result["IBP"].values[0])

            # ========== TAMPILAN HASIL ==========
            st.success("Perhitungan berhasil!")

            # Metric besar
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Nilai IBP", f"{ibp_value:.4f}")
            with col_b:
                st.metric("Probabilitas", f"{ibp_value*100:.1f} %")
            with col_c:
                if ibp_value < 0.2:
                    status = "Rendah 🟢"
                elif ibp_value < 0.5:
                    status = "Sedang 🟡"
                else:
                    status = "Tinggi 🔴"
                st.metric("Status Risiko", status)

            # Interpretasi
            st.subheader("📋 Interpretasi")
            if ibp_value < 0.2:
                st.info("Probabilitas rendah. Kemungkinan terjadinya plasma bubble kecil.")
            elif ibp_value < 0.5:
                st.warning("Probabilitas sedang. Perlu diwaspadai, terutama untuk komunikasi/satelit.")
            else:
                st.error("Probabilitas tinggi. Risiko gangguan ionosfer (scintillation) cukup besar.")

            # Detail parameter
            with st.expander("Lihat detail parameter & hasil mentah"):
                st.dataframe(result, use_container_width=True)
                # Tambahan info waktu yang dikonversi
                st.write(f"Waktu lokal yang diproses oleh model: **{local_time_model:.2f} jam (format 0-24)**")

            # Info model
            st.caption(f"Model yang digunakan: **{model_type}** | Sumber: Swarm L2 Product (IBP_CLI)")

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            st.info("Pastikan parameter berada dalam rentang yang valid.")

else:
    st.info("👈 Silakan atur parameter di sidebar kiri, lalu klik tombol **Hitung IBP**.")

# ====================== FOOTER ======================
st.markdown("---")
st.markdown("""
**Catatan:**  
- Model **Machine Learning** lebih sensitif terhadap plasma bubble yang lemah.  
- Model berlaku untuk lintang ±45° dan ketinggian ~350–500 km.  
- Referensi: Stolle et al. (2024) & perluasan ML Swarm.
""")

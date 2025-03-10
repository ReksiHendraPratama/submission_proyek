import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set tema dan konfigurasi halaman sebagai perintah pertama
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# Load dataset yang sudah dibersihkan
@st.cache_data
def load_data():
    day_df = pd.read_csv("day.csv")
    hour_df = pd.read_csv("hour.csv")
    
    # Konversi kolom tanggal
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    # Mapping kategori musim agar lebih deskriptif (diperbarui sesuai 1:Spring, 2:Summer, 3:Fall, 4:Winter)
    season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    day_df["season"] = day_df["season"].map(season_mapping)
    hour_df["season"] = hour_df["season"].map(season_mapping)
    
    # Pembersihan data untuk menghindari duplikat atau label yang salah
    day_df = day_df.drop_duplicates(subset=['dteday', 'season'])
    hour_df = hour_df.drop_duplicates(subset=['dteday', 'hr', 'season'])
    
    # Mapping kondisi cuaca
    weather_mapping = {1: "Clear", 2: "Cloudy", 3: "Light Rain", 4: "Heavy Rain"}
    day_df["weathersit"] = day_df["weathersit"].map(weather_mapping)
    hour_df["weathersit"] = hour_df["weathersit"].map(weather_mapping)
    
    return day_df, hour_df

day_df, hour_df = load_data()

# Judul dashboard
st.title("🚴‍♂️ Dashboard Analisis Penyewaan Sepeda")
st.subheader("Eksplorasi Data Penyewaan Sepeda Berdasarkan Musim dan Waktu")
st.markdown("**Oleh: Reksi Hendra Pratama** | Email: reksihendrapratama637@gmail.com | ID Dicoding: MC189D5Y0840")

# Membuat tab untuk navigasi
tab1, tab2, tab3 = st.tabs(["Pengaruh Musim", "Pola Penyewaan Weekdays", "Kesimpulan"])

# Tab 1: Pengaruh Musim
with tab1:
    st.header("Pengaruh Musim terhadap Penyewaan Sepeda")
    st.markdown("Analisis ini mengeksplorasi bagaimana musim memengaruhi jumlah penyewaan sepeda.")
    
    # Fitur interaktif untuk filter musim
    st.sidebar.header("Filter Data")
    custom_season_order = ["Fall", "Spring", "Summer", "Winter"]
    selected_season = st.sidebar.selectbox(
        "Pilih Musim",
        options=["All"] + custom_season_order
    )
    
    # Filter data berdasarkan input pengguna
    filtered_df = day_df if selected_season == "All" else day_df[day_df['season'] == selected_season]
    
    # Boxplot pengaruh musim
    st.subheader("Distribusi Penyewaan Sepeda per Musim")
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    sns.boxplot(data=filtered_df, x='season', y='cnt', palette='coolwarm',
                order=custom_season_order if selected_season == "All" else [selected_season], ax=ax1)
    ax1.set_title('Distribusi Jumlah Penyewaan Sepeda Berdasarkan Musim', fontsize=14)
    ax1.set_xlabel('Musim', fontsize=12)
    ax1.set_ylabel('Jumlah Penyewa', fontsize=12)
    st.pyplot(fig1)

    # Barplot total penyewaan per musim
    st.subheader("Total Penyewaan Sepeda per Musim")
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    ax2 = sns.barplot(x='season', y='cnt', data=filtered_df, estimator=sum, palette='viridis',
                    order=custom_season_order if selected_season == "All" else [selected_season], ax=ax2)

    # Menghitung total penyewaan per musim
    totals = filtered_df.groupby('season', sort=False)['cnt'].sum().reindex(custom_season_order if selected_season == "All" else [selected_season])
    max_total = totals.max()  # Ambil nilai total terbesar
    ax2.set_ylim(0, max_total * 1.1)  # Tambahkan margin atas 10%

    # Menambahkan label nilai di atas setiap bar dengan jarak 10% dari max_total
    for i, total in enumerate(totals):
        ax2.text(i, total + (max_total * 0.05), f'{total:,.0f}', color='black', ha="center", fontsize=10, weight='bold',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

    ax2.set_title('Total Jumlah Penyewaan Sepeda Berdasarkan Musim', fontsize=14)
    ax2.set_xlabel('Musim', fontsize=12)
    ax2.set_ylabel('Total Penyewa', fontsize=12)
    st.pyplot(fig2)

    
    # Statistik deskriptif per musim
    st.subheader("Statistik Penyewaan per Musim")
    season_stats = filtered_df.groupby('season')['cnt'].agg(['mean', 'median', 'min', 'max']).reindex(custom_season_order if selected_season == "All" else [selected_season]).reset_index()
    st.dataframe(season_stats.style.format("{:.2f}", subset=['mean', 'median', 'min', 'max']))

    # Insight
    st.markdown("""
    **Insight:**
    - Musim Fall menunjukkan jumlah penyewaan tertinggi, baik dari distribusi (boxplot) maupun total penyewaan (barplot).
    - Musim Spring memiliki jumlah penyewaan paling rendah, konsisten di kedua visualisasi.
    - Cuaca yang hangat meningkatkan minat bersepeda, sedangkan cuaca dingin menguranginya.
    """)

# Tab 2: Pola Penyewaan Weekdays
with tab2:
    st.header("Pola Penyewaan Sepeda pada Hari Kerja")
    st.markdown("Analisis ini mengeksplorasi pola penyewaan sepeda dalam sehari pada hari kerja (weekdays).")
    
    # Filter hanya hari kerja (menggunakan workingday == 1)
    weekdays_df = hour_df[hour_df['workingday'] == 1]
    
    # Fitur interaktif untuk filter rentang jam dan musim
    st.sidebar.header("Filter Data (Pola Weekdays)")
    min_hour, max_hour = st.sidebar.slider(
        "Pilih Rentang Jam",
        min_value=int(weekdays_df['hr'].min()),
        max_value=int(weekdays_df['hr'].max()),
        value=(int(weekdays_df['hr'].min()), int(weekdays_df['hr'].max()))
    )
    selected_weekday_season = st.sidebar.selectbox(
        "Pilih Musim untuk Weekdays",
        options=["All"] + list(weekdays_df['season'].unique())
    )
    
    # Filter data berdasarkan input pengguna
    filtered_weekdays_df = weekdays_df[(weekdays_df['hr'] >= min_hour) & (weekdays_df['hr'] <= max_hour)]
    if selected_weekday_season != "All":
        filtered_weekdays_df = filtered_weekdays_df[filtered_weekdays_df['season'] == selected_weekday_season]
    
    # Lineplot pola penyewaan sepeda per jam dalam sehari
    st.subheader("Tren Penyewaan Sepeda di Weekdays Berdasarkan Jam")
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    sns.lineplot(x='hr', y='cnt', data=filtered_weekdays_df, estimator=sum, marker='o', color='b', ax=ax2)
    ax2.set_title('Tren Penyewaan Sepeda di Weekdays Berdasarkan Jam', fontsize=14)
    ax2.set_xlabel('Jam', fontsize=12)
    ax2.set_ylabel('Jumlah Penyewa', fontsize=12)
    ax2.set_xticks(range(0, 24))
    ax2.set_xlim(min_hour, max_hour)
    st.pyplot(fig2)
    
    # Barplot total penyewaan sepeda per jam
    st.subheader("Total Penyewaan Sepeda pada Weekdays Berdasarkan Jam")
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    sns.barplot(x='hr', y='cnt', data=filtered_weekdays_df, estimator=sum, palette='coolwarm', ax=ax3)
    ax3.set_title('Total Penyewaan Sepeda pada Weekdays Berdasarkan Jam', fontsize=14)
    ax3.set_xlabel('Jam', fontsize=12)
    ax3.set_ylabel('Total Penyewa', fontsize=12)
    ax3.set_xticks(range(0, 24))
    ax3.set_xlim(min_hour, max_hour)
    st.pyplot(fig3)

    # Insight
    st.markdown("""
    **Insight:**
    - Lonjakan penyewaan terjadi pada pukul 07:00-09:00 (pagi) dan 17:00-19:00 (sore) dalam rentang jam yang dipilih.
    - Pola ini mencerminkan penggunaan sepeda untuk commuting (ke dan dari tempat kerja/sekolah).
    - Penyewaan cenderung rendah di luar jam sibuk, menandakan penggunaan rekreasi lebih sedikit pada hari kerja.
    """)

# Tab 3: Kesimpulan
with tab3:
    st.header("Kesimpulan Analisis")
    st.markdown("""
    ### 1. Pengaruh Musim terhadap Penyewaan Sepeda
    - **Musim Fall** menunjukkan jumlah penyewaan tertinggi, kemungkinan karena cuaca yang hangat dan nyaman untuk bersepeda.
    - **Musim Spring** memiliki penyewaan terendah, dipengaruhi oleh suhu dingin dan kondisi cuaca yang kurang mendukung.
    - Implikasi: Strategi pemasaran dapat difokuskan pada musim Fall untuk meningkatkan penyewaan.

    ### 2. Pola Penyewaan Sepeda pada Hari Kerja
    - Terdapat **lonjakan signifikan** pada jam sibuk pagi (07:00-09:00) dan sore (17:00-19:00) dalam rentang jam yang dipilih, menunjukkan penggunaan sepeda untuk keperluan komuter.
    - Penyewaan lebih rendah di luar jam sibuk, menandakan penggunaan rekreasi lebih sedikit pada hari kerja.
    - Implikasi: Penyedia layanan dapat menambah stok sepeda pada jam sibuk untuk memenuhi permintaan.
    """)

# Sidebar untuk navigasi tambahan
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972528.png", width=100)
    st.markdown("### Bike Sharing Analysis")
    st.markdown("Dashboard ini menganalisis data penyewaan sepeda berdasarkan musim dan pola waktu pada hari kerja.")
    st.markdown("**Pertanyaan Bisnis:**")
    st.markdown("- Bagaimana pengaruh musim terhadap penyewaan sepeda?")
    st.markdown("- Bagaimana pola penyewaan sepeda dalam sehari saat weekdays?")
    st.markdown("---")
    st.markdown("**Kontak:**")
    st.markdown("Nama: Reksi Hendra Pratama")
    st.markdown("Email: reksihendrapratama637@gmail.com")
    st.markdown("ID Dicoding: MC189D5Y0840")

# Footer
st.markdown("---")
st.markdown("© 2025 Reksi Hendra Pratama | Dibuat dengan Streamlit untuk Analisis Data Bike Sharing")

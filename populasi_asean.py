# Impor library yang diperlukan
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import requests

# Inisialisasi aplikasi Dash
app = dash.Dash(__name__)

# --------------------------------------
# 1. Mengimpor Daftar Negara dari Google Spreadsheet Publik
# --------------------------------------
# Link spreadsheet publik untuk daftar negara
countries_link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBWnU-Uoe0VGRXAAb4Q_zOZgu8nwmmY4e2LBJ4TyoPe0_Zu_4PcTaqwnGreA09IhzQ8dpr9NcAmlQF/pub?output=csv"
countries = pd.read_csv(countries_link)

# Debugging: Cetak kolom untuk memeriksa struktur data
print("Kolom di countries:", countries.columns.tolist())

# Pastikan kolom yang diperlukan ada
required_columns = ['country', 'lat', 'lon', 'wb_code']
for col in required_columns:
    if col not in countries.columns:
        raise ValueError(f"Kolom '{col}' tidak ditemukan di spreadsheet. Kolom yang tersedia: {countries.columns.tolist()}")

# --------------------------------------
# 2. Mengimpor Data Populasi dari World Bank API
# --------------------------------------
# Mengambil data populasi dari World Bank API
api_data = []
for _, country in countries.iterrows():
    url = f"http://api.worldbank.org/v2/country/{country['wb_code']}/indicator/SP.POP.TOTL?format=json&date=2022"
    response = requests.get(url).json()
    if len(response) > 1 and response[1] and response[1][0]["value"]:
        population = response[1][0]["value"] / 1_000_000  # Konversi ke jutaan
        api_data.append({
            "country": country["country"],
            "lat": country["lat"],
            "lon": country["lon"],
            "wb_code": country["wb_code"],
            "population": population
        })
    else:
        print(f"Gagal mengambil data untuk {country['country']}")

api_data = pd.DataFrame(api_data)

# Debugging: Cetak data API untuk memeriksa
print("Data dari API:\n", api_data)

# --------------------------------------
# Membuat Visualisasi Peta Choropleth
# --------------------------------------
# Fungsi untuk membuat peta choropleth menggunakan Plotly
def create_choropleth_map(data, title):
    if data.empty:
        raise ValueError("DataFrame kosong, tidak bisa membuat peta.")
    fig = px.choropleth(
        data,
        locations="wb_code",  # Menggunakan kode ISO-3 (wb_code) untuk peta
        color="population",   # Warna berdasarkan populasi
        hover_name="country", # Nama negara saat hover
        color_continuous_scale=px.colors.sequential.Blues,  # Skala warna biru
        projection="mercator",
        title=title,
        height=800  # Tinggi peta lebih besar untuk detail
    )
    fig.update_geos(
        visible=True,
        resolution=50,
        showcountries=True, countrycolor="Black",
        showcoastlines=True, coastlinecolor="Black",
        showland=True, landcolor="LightGreen",
        fitbounds="geojson",  # Menyesuaikan batas tampilan
        
        lonaxis_range=[90, 155],  # Batas longitude
        lataxis_range=[-5, 28]    # Batas latitude
    )
    fig.update_layout(
        showlegend=True,
        title_x=0.5,  # Posisi judul di tengah
        margin={"r":0,"t":50,"l":0,"b":0}  # Mengurangi margin untuk tampilan lebih besar
    )
    return fig

# Membuat peta choropleth untuk data API
choropleth_map = create_choropleth_map(api_data, "Jumlah Penduduk Negara ASEAN (World Bank API, 2022)")

# --------------------------------------
# Layout Dashboard Dash
# --------------------------------------
app.layout = html.Div([
    html.H1("Visualisasi Jumlah Penduduk di Negara-Negara ASEAN"),
    
    # Peta choropleth dari API
    html.H3("Data dari World Bank API"),
    dcc.Graph(figure=choropleth_map)
])

# --------------------------------------
# Menjalankan Aplikasi
# --------------------------------------
# Bagian ini dikomentari karena akan di-deploy (misalnya di PythonAnywhere)
#if __name__ == '__main__':
#    app.run_server(debug=True)

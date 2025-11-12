import pandas as pd
import folium
import webbrowser
from folium.plugins import MarkerCluster
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
def showMap(map):
    map.save("map.html")
    webbrowser.open("map.html")
hospital = pd.read_excel('c:/data/1.병원정보서비스 2024.9.xlsx')
hospital = hospital.dropna(subset=['좌표(Y)', '좌표(X)'])
hospital = hospital[hospital['시도코드명'].isin(['서울', '경기'])].reset_index(drop = True)
pharmacy = pd.read_excel('c:/data/2.약국정보서비스 2024.9.xlsx')
pharmacy = pharmacy.dropna(subset=['좌표(Y)', '좌표(X)'])
pharmacy = pharmacy[pharmacy['시도코드명'].isin(['서울', '경기'])].reset_index(drop = True)
def get_color(count_doctor):
    if count_doctor <= 100:
        return 'blue'
    elif count_doctor <= 500:   
        return 'orange'
    else:
        return 'red'
map = folium.Map(location=[hospital['좌표(Y)'].mean(), hospital['좌표(X)'].mean()], zoom_start=11)
hospital_cluster = MarkerCluster().add_to(map)
pharmacy_cluster = MarkerCluster().add_to(map)
for i in range(len(hospital)):
    doctor_count = hospital.loc[i, '총의사수']
    color = get_color(doctor_count)
    if doctor_count <= 200:
        folium.Marker(
            location=[hospital.loc[i, '좌표(Y)'], hospital.loc[i, '좌표(X)']],
            icon=folium.Icon(color=color, icon="plus-square", prefix="fa")
        ).add_to(hospital_cluster)
    else:
        folium.Marker(
            location=[hospital.loc[i, '좌표(Y)'], hospital.loc[i, '좌표(X)']],
            icon=folium.Icon(color=color, icon="plus-square", prefix="fa")
        ).add_to(map)
for i in range(len(pharmacy)):
    folium.Marker(
        location=[pharmacy.loc[i, '좌표(Y)'], pharmacy.loc[i, '좌표(X)']],
        icon=folium.Icon(color='purple', icon="medkit", prefix="fa")
    ).add_to(pharmacy_cluster)
showMap(map)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c
def count_pharmacies(hospital_row, pharmacy_df):
    lat, lon = hospital_row['좌표(Y)'], hospital_row['좌표(X)']
    nearby_pharmacies = pharmacy_df[
    (pharmacy_df['좌표(Y)'] > lat - 0.005) & (pharmacy_df['좌표(Y)'] < lat + 0.005) &
    (pharmacy_df['좌표(X)'] > lon - 0.005) & (pharmacy_df['좌표(X)'] < lon + 0.005)]
    distances = haversine(lat, lon, nearby_pharmacies['좌표(Y)'], nearby_pharmacies['좌표(X)'])
    return (distances <= 0.5).sum()
hospital['약국개수'] = hospital.apply(count_pharmacies, axis=1, pharmacy_df = pharmacy)
hospital['의사 밀집도'] = pd.cut(
    hospital['총의사수'], bins=[1, 100, 500, hospital['총의사수'].max()],
    labels=['1-100명', '100-500명', '500명 이상'])
hospital.groupby('의사 밀집도')['약국개수'].mean()
sns.set_theme(style="whitegrid", rc={"figure.figsize": (5, 5), "font.family": "Malgun Gothic"})
sns.barplot(data = hospital, x='의사 밀집도', y='약국개수', estimator='mean', hue='의사 밀집도', legend = None, errorbar = None )
plt.title('의사 밀집도에 따른 주위 약국의 개수 평균 (500m 이내)')
plt.xlabel('의사 밀집도')
plt.ylabel('약국 개수 평균')
plt.show()
plt.figure(figsize=(5, 5))
sns.lineplot(x = hospital['의사 밀집도'], y = hospital['약국개수'], marker='o', color='b', errorbar = None)
plt.title('의사 밀집도에 따른 주위 약국의 개수 평균 (500m 이내)')
plt.xlabel('의사 밀집도')
plt.ylabel('약국 개수 평균')
plt.grid(False)
plt.show()
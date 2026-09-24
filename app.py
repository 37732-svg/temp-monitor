import pandas as pd
import streamlit as st
import plotly.express as px

SHEET_ID = "ใส่_SHEET_ID"
SHEET_NAME = "Data"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

st.set_page_config(page_title="Temperature Monitor", page_icon="🌡️", layout="wide")
st.title("🌡️ ระบบตรวจวัดอุณหภูมิและความชื้น")

# โหลดข้อมูล (แคช 30 วินาที เพื่อไม่ให้ยิงขอข้อมูลถี่เกินไป)
@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(URL)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"]).sort_values("Timestamp")
    return df

df = load_data()

if df.empty:
    st.warning("ยังไม่มีข้อมูลในชีต")
    st.stop()

# ค่าล่าสุด
latest = df.iloc[-1]
c1, c2, c3 = st.columns(3)
c1.metric("อุณหภูมิล่าสุด", f"{latest['Temperature (C)']:.1f} °C")
c2.metric("ความชื้นล่าสุด", f"{latest['Humidity (%)']:.1f} %")
c3.metric("อัปเดตล่าสุด", latest["Timestamp"].strftime("%d/%m/%Y %H:%M:%S"))

# แจ้งเตือน
if latest["Alert"] == "YES":
    st.error(f"⚠️ แจ้งเตือน: {latest['Alert Type']}")
if latest["Humidity Low"] == "YES":
    st.warning("💧 ความชื้นต่ำกว่าเกณฑ์")

# เลือกช่วงเวลา
hours = st.selectbox("ช่วงเวลา", [1, 6, 24, 72, 168], index=2,
                     format_func=lambda h: f"{h} ชั่วโมงล่าสุด")
since = df["Timestamp"].max() - pd.Timedelta(hours=hours)
view = df[df["Timestamp"] >= since]

# กราฟ
left, right = st.columns(2)
left.plotly_chart(px.line(view, x="Timestamp", y="Temperature (C)",
                          title="อุณหภูมิ (°C)"), use_container_width=True)
right.plotly_chart(px.line(view, x="Timestamp", y="Humidity (%)",
                           title="ความชื้น (%)"), use_container_width=True)

# ตารางข้อมูล
with st.expander("ดูตารางข้อมูลดิบ"):
    st.dataframe(view.sort_values("Timestamp", ascending=False), use_container_width=True)

# ปุ่มรีเฟรช
if st.button("🔄 รีเฟรชข้อมูล"):
    st.cache_data.clear()
    st.rerun()
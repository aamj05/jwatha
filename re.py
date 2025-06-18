import streamlit as st
import pymysql
import pandas as pd

st.set_page_config(page_title="📊 جلب البيانات")

# دالة تحميل البيانات من قاعدة البيانات
@st.cache_data
def load_data():
    try:
        conn = pymysql.connect(
            host=st.secrets["DB_HOST"],
            port=int(st.secrets["DB_PORT"]),
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            charset='utf8mb4'
        )
        df = pd.read_sql("SELECT * FROM users", conn)
        return df
    except Exception as e:
        st.error(f"❌ خطأ: {e}")
        return pd.DataFrame()

# زر لجلب البيانات
if st.button("🔄 جلب البيانات"):
    st.cache_data.clear()
    df = load_data()
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("ℹ️ لا توجد بيانات.")

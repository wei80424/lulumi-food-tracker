import streamlit as st
import pandas as pd
# 🌟 修改 1：多匯入 timedelta 和 timezone 來處理時差
from datetime import datetime, timedelta, timezone
import gspread
import traceback

# --- 1. 網頁基本設定 ---
st.set_page_config(page_title="嚕嚕米副食品日記", page_icon="🍼", layout="centered")

# --- 2. 自訂 UI 美化 ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #FFB347;
        color: white;
        border-radius: 12px;
        font-weight: bold;
        width: 100%;
        border: none;
        padding: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF9B1A;
        transform: translateY(-2px);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. 初始化資料庫連線 ---
@st.cache_resource
def init_connection():
    try:
        credentials = dict(st.secrets["gcp_service_account"])
        gc = gspread.service_account_from_dict(credentials)
        return gc.open("嚕嚕米副食品日記").sheet1
    except Exception as e:
        st.error("連線失敗！請確認試算表名稱與權限。")
        st.code(traceback.format_exc())
        st.stop()

worksheet = init_connection()

# --- 4. 頂部標題區 ---
st.title("👶 嚕嚕米副食品探險日記")
st.caption("溫馨紀錄 嚕嚕米成長的每一口 ✨")

tab1, tab2 = st.tabs(["📝 新增紀錄", "📊 成就看板"])

# ==========================================
# 分頁 1：新增紀錄
# ==========================================
with tab1:
    st.subheader("今日餵食狀況")
    
    # 🌟 修改 2：建立台灣專屬時區 (UTC+8)
    tz_tw = timezone(timedelta(hours=8))
    # 🌟 修改 3：強制抓取台灣時間
    now = datetime.now(tz_tw)
    
    # 日期選擇 (使用校正後的 now)
    date_val = st.date_input("🗓️ 餵食日期", now.date())
    
    st.write("⏰ 餵食時間")
    time_options = []
    for h in range(24):
        for m in range(0, 60, 5):
            time_options.append(f"{h:02d}{m:02d}")
    
    # 計算當前對齊時間 (使用校正後的 now)
    rounded_min = (now.minute // 5) * 5
    current_hhmm = f"{now.hour:02d}{rounded_min:02d}"
    
    default_idx = time_options.index(current_hhmm) if current_hhmm in time_options else 0
    final_time_str = st.selectbox("請選擇 4 位數時間 (HHMM)", time_options, index=default_idx, label_visibility="collapsed")

    # 食材分類
    food_categories = {
        "🌾 全穀雜糧類": ["十倍粥", "七倍粥", "五倍粥", "地瓜", "南瓜", "馬鈴薯", "山藥", "燕麥", "玉米"],
        "🥬 蔬菜類": ["高麗菜", "紅蘿蔔", "青花菜", "菠菜", "洋蔥", "冬瓜", "番茄", "絲瓜", "甜椒"],
        "🍎 水果類": ["蘋果", "香蕉", "水梨", "木瓜", "葡萄", "酪梨", "奇異果", "火龍果"],
        "🥩 蛋白質(肉/蛋/豆)": ["蛋黃", "嫩豆腐", "鯛魚", "鱸魚", "鮭魚", "雞肉", "豬肉", "牛肉"],
        "❓ 其它": ["自訂輸入 (請寫於備註)"]
    }

    col_cat, col_food = st.columns(2)
    with col_cat:
        selected_cat = st.selectbox("🥦 食材大類", list(food_categories.keys()))
    with col_food:
        food_val = st.selectbox("🥗 具體食材", food_categories[selected_cat])

    amount_val = st.selectbox("🥄 份量", ["試味道 (1-2口)", "5 ml", "10 ml", "15 ml", "30 ml", "50 ml", "半碗", "一碗"])
    reaction_val = st.radio("🩺 身體反應", ["✅ 正常", "⚠️ 紅疹", "💩 腹瀉/便秘", "🤮 嘔吐"], horizontal=True)
    note_val = st.text_input("📝 觀察備註", placeholder="紀錄喜好或狀況...")

    if st.button("💾 儲存今日紀錄"):
        try:
            new_row = [date_val.strftime("%Y-%m-%d"), final_time_str, food_val, amount_val, reaction_val, note_val]
            worksheet.append_row(new_row)
            st.toast(f"已同步：{food_val} ({final_time_str})", icon="🎉")
            if "正常" in reaction_val:
                st.balloons()
        except Exception as e:
            st.error(f"寫入失敗：{e}")

# ==========================================
# 分頁 2：歷史紀錄
# ==========================================
with tab2:
    try:
        data = worksheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.subheader("🏆 嚕嚕米成就統計")
            m1, m2 = st.columns(2)
            m1.metric("嘗試次數", f"{len(df)} 次")
            m2.metric("解鎖食材", f"{df['食材名稱'].nunique()} 種")
            st.divider()
            st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
        else:
            st.info("目前還沒有紀錄喔！")
    except:
        st.warning("暫時無法讀取數據。")

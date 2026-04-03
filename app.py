import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 網頁基本設定 ---
# 必須放在第一行！設定網頁標題、Icon 與寬度佈局
st.set_page_config(page_title="嚕嚕米 副食品日記", page_icon="👶", layout="centered")

# --- 2. 自訂 UI 美化 (CSS) ---
st.markdown("""
    <style>
    /* 調整按鈕顏色與圓角，增加高級感 */
    .stButton>button {
        background-color: #FFB347;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF9B1A;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 標題區塊 ---
st.title("🍼 嚕嚕米 的副食品探險日記")
st.markdown("紀錄寶寶每一口的新嘗試與腸胃耐受度。")
st.divider() # 分隔線

# 檔案設定
FILE_NAME = "Lulumi_Allergy_Tracker.csv"

# --- 4. 擴充版食材清單 ---
food_options = [
    # 主食與根莖類
    "十倍粥", "七倍粥", "五倍粥", "燕麥粥", "馬鈴薯泥", "地瓜泥", "南瓜泥", "山藥泥",
    # 蔬菜類
    "紅蘿蔔泥", "高麗菜泥", "青花菜泥", "菠菜泥", "小白菜泥", "洋蔥泥", "冬瓜泥", "玉米泥",
    # 水果類
    "蘋果泥", "香蕉泥", "水梨泥", "木瓜泥", "葡萄泥", "酪梨泥", "黑棗泥 (解便秘)",
    # 蛋白質類 (初階)
    "蛋黃泥", "嫩豆腐", "鯛魚泥", "鱸魚泥", "雞肉泥",
    # 其它/未列出
    "自訂輸入 (請寫於備註)"
]

# --- 5. 輸入表單介面 (使用 Columns 讓版面更緊湊專業) ---
col1, col2 = st.columns(2)
with col1:
    date_val = st.date_input("🗓️ 餵食日期", datetime.today())
with col2:
    time_val = st.time_input("⏰ 餵食時間", datetime.now().time())

# 食材與份量
col3, col4 = st.columns(2)
with col3:
    food_val = st.selectbox("🥦 食材名稱", food_options)
with col4:
    amount_val = st.selectbox("🥄 份量", ["試味道 (1-2口)", "5 ml", "10 ml", "15 ml (1大匙)", "30 ml", "50 ml", "半碗", "一碗"])

reaction_val = st.radio("🩺 身體反應", 
                        ["✅ 正常 (無異狀)", "⚠️ 起紅疹/發癢", "💩 腹瀉/便秘", "🤮 嘔吐/嚴重溢奶"], 
                        horizontal=True)

note_val = st.text_input("📝 觀察備註 (選填)", placeholder="例如：吃了兩口就不吃、隔天大便偏硬...")

# --- 6. 存檔邏輯 ---
if st.button("💾 儲存今日紀錄"):
    # 整理準備存入的資料
    new_data = pd.DataFrame([{
        "日期": date_val.strftime("%Y-%m-%d"),
        "時間": time_val.strftime("%H:%M"),
        "食材名稱": food_val,
        "份量": amount_val,
        "身體反應": reaction_val,
        "備註": note_val
    }])
    
    # 寫入 CSV (若檔案不存在則建立並加上標題，存在則附加在後面)
    if not os.path.exists(FILE_NAME):
        new_data.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
    else:
        new_data.to_csv(FILE_NAME, mode='a', header=False, index=False, encoding='utf-8-sig')
    
    st.success(f"🎉 成功紀錄 嚕嚕米 嘗試了 {food_val}！")

# --- 7. 歷史紀錄預覽區 ---
st.divider()
st.subheader("📊 近期試敏紀錄預覽")
if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
    # 反轉順序，讓最新的紀錄在最上面
    st.dataframe(df.iloc[::-1].head(10), use_container_width=True)
else:
    st.info("目前還沒有紀錄喔，趕快新增第一筆吧！")
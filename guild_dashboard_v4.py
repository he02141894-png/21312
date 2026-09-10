import streamlit as st
import pandas as pd

# 設定網頁標題與排版
st.set_page_config(page_title="地圖收藏資料庫", layout="wide")

# 1. 初始化原始資料 (使用 st.session_state 確保數字加減後能保存狀態)
if 'df' not in st.session_state:
    raw_data = [
        {"地圖(等級)": "蟲1(84-92)", "紫收藏": "重力反應石", "白": 25, "綠": 82, "藍": 84, "紫": 105},
        {"地圖(等級)": "蟲1(100-108)", "紫收藏": "赤紅橋梁碎片", "白": 0, "綠": 43, "藍": 89, "紫": 116},
        {"地圖(等級)": "火2(86-91)", "紫收藏": "戰鬥用無人機遙控器", "白": 0, "綠": 97, "藍": 10, "紫": 30},
        {"地圖(等級)": "火2(86-91)", "紫收藏": "探查用無人機遙控器", "白": 122, "綠": 129, "藍": 51, "紫": 46},
        {"地圖(等級)": "火2(86-91)", "紫收藏": "偵查用無人機遙控器", "白": 139, "綠": 135, "藍": 43, "紫": 47},
        {"地圖(等級)": "火2(96-101)", "紫收藏": "實驗用電漿", "白": 0, "綠": 0, "藍": 0, "紫": 32},
        {"地圖(等級)": "火2(96-101)", "紫收藏": "保管用電漿", "白": 0, "綠": 30, "藍": 55, "紫": 47},
        {"地圖(等級)": "火2(96-101)", "紫收藏": "爆破用電漿", "白": 0, "綠": 0, "藍": 17, "紫": 33},
        {"地圖(等級)": "戰域1(82)", "紫收藏": "精煉的尼得水晶", "白": 0, "綠": 6, "藍": 7, "紫": 7},
        {"地圖(等級)": "戰域1(90-102)", "紫收藏": "超重力對應框", "白": 0, "綠": 3, "藍": 9, "紫": 10},
        {"地圖(等級)": "戰域2(82)", "紫收藏": "尼德金柱的碎片", "白": 38, "綠": 42, "藍": 21, "紫": 15},
        {"地圖(等級)": "戰域2(90-102)", "紫收藏": "赤紅工廠碎片", "白": 0, "綠": 0, "藍": 0, "紫": 13},
        {"地圖(等級)": "戰域3(82)", "紫收藏": "外行星用淨化過濾器", "白": 0, "綠": 18, "藍": 6, "紫": 13},
        {"地圖(等級)": "戰域3(90-102)", "紫收藏": "尼德的記錄裝置", "白": 0, "綠": 0, "藍": 16, "紫": 16},
        {"地圖(等級)": "專2(82-90)", "紫收藏": "流血的水晶", "白": 0, "綠": 0, "藍": 0, "紫": 14},
        {"地圖(等級)": "機器人12(85)", "紫收藏": "機器人廢棄指南", "白": 0, "綠": 52, "藍": 22, "紫": 39},
        {"地圖(等級)": "卡勒碼峽谷(86-88)", "紫收藏": "砲座瞄準裝置", "白": 71, "綠": 48, "藍": 55, "紫": 23},
        {"地圖(等級)": "那依弗採集場(89-91)", "紫收藏": "控制設施遠端裝置", "白": 0, "綠": 0, "藍": 0, "紫": 19},
        {"地圖(等級)": "迪亞曼特礦山(92-94)", "紫收藏": "汙染物質汽缸", "白": 0, "綠": 20, "藍": 25, "紫": 45},
        {"地圖(等級)": "流浪雪原(95-97)", "紫收藏": "破損的數據晶片", "白": 84, "綠": 117, "藍": 70, "紫": 55},
        {"地圖(等級)": "露比亞霜林(98-100)", "紫收藏": "受感染的機械零件", "白": 0, "綠": 0, "藍": 0, "紫": 24},
        {"地圖(等級)": "安忒洛斯遺跡(101-103)", "紫收藏": "遺跡水晶", "白": 24, "綠": 67, "藍": 66, "紫": 54},
        {"地圖(等級)": "洛弗斯海灣(103-106)", "紫收藏": "冰原研究家的身分證", "白": 22, "綠": 83, "藍": 65, "紫": 54}
    ]
    st.session_state.df = pd.DataFrame(raw_data)

st.title("🎮 地圖收藏資料庫 (Python 網頁版)")
st.caption("點擊欄位數值旁的 ＋ 或 － 按鈕，可以直接進行加減，也能點進去直接輸入數字。")

# 2. 搜尋功能
search_query = st.text_input("🔍 輸入關鍵字搜尋（可搜尋地圖或紫收藏名稱）", "").strip().lower()

# 根據搜尋條件篩選要顯示的資料列索引
if search_query:
    filtered_indices = st.session_state.df[
        st.session_state.df["地圖(等級)"].str.lower().str.contains(search_query) | 
        st.session_state.df["紫收藏"].str.lower().str.contains(search_query)
    ].index.tolist()
else:
    filtered_indices = st.session_state.df.index.tolist()

# 3. 表格標頭（排版）
cols = st.columns([2.5, 3, 1.5, 1.5, 1.5, 1.5])
cols[0].markdown("**地圖(等級)**")
cols[1].markdown("**紫收藏**")
cols[2].markdown("⚪ **白**")
cols[3].markdown("🟢 **綠**")
cols[4].markdown("🔵 **藍**")
cols[5].markdown("🟣 **紫**")
st.divider()

# 4. 渲染可增減數量的欄位
if not filtered_indices:
    st.info("查無相符的資料")
else:
    for idx in filtered_indices:
        row = st.session_state.df.iloc[idx]
        row_cols = st.columns([2.5, 3, 1.5, 1.5, 1.5, 1.5])
        
        # 顯示地圖與名稱
        row_cols[0].write(row["地圖(等級)"])
        row_cols[1].write(row["紫收藏"])
        
        # 使用 number_input 製作可加減、輸入的數字格
        # 每一次欄位變動都會即時更新回 st.session_state.df 裡
        st.session_state.df.at[idx, "白"] = row_cols[2].number_input(
            "白", min_value=0, value=int(row["白"]), step=1, label_visibility="collapsed", key=f"w_{idx}"
        )
        st.session_state.df.at[idx, "綠"] = row_cols[3].number_input(
            "綠", min_value=0, value=int(row["綠"]), step=1, label_visibility="collapsed", key=f"g_{idx}"
        )
        st.session_state.df.at[idx, "藍"] = row_cols[4].number_input(
            "藍", min_value=0, value=int(row["藍"]), step=1, label_visibility="collapsed", key=f"b_{idx}"
        )
        st.session_state.df.at[idx, "紫"] = row_cols[5].number_input(
            "紫", min_value=0, value=int(row["紫"]), step=1, label_visibility="collapsed", key=f"p_{idx}"
        )

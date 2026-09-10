import streamlit as st
import pandas as pd

# 設定網頁標題與排版
st.set_page_config(page_title="戰力成員管理資料庫", layout="wide")

# 1. 初始化原始資料 (使用 st.session_state 確保新增人員與調整戰力後能保存狀態)
if 'member_df' not in st.session_state:
    # 建立預設的初始資料（包含標頭結構與一筆範例）
    initial_data = [
        {"排行": 1, "ID": "範例玩家A", "職業": "制裁者", "戰力": 500000}
    ]
    st.session_state.member_df = pd.DataFrame(initial_data)

st.title("🏆 戰力成員管理系統 (Python 網頁版)")
st.caption("你可以在左側側邊欄「新增人員」，並在右側主畫面「調整戰力」或「搜尋隊員」。")

# ==================== 側邊欄：新增人員功能 ====================
with st.sidebar:
    st.header("👤 新增成員")
    with st.form(key="add_member_form", clear_on_submit=True):
        new_id = st.text_input("輸入玩家 ID", placeholder="例如：斬擊之王").strip()
        
        # 🟢 已更新：替換為你指定的 8 種專屬職業
        job_options = ["制裁者", "幻影神兵", "執行者", "操靈師", "無畏艦", "匠師", "仲裁者", "毀滅"]
        new_job = st.selectbox("選擇職業", job_options)
        
        # 戰力輸入，設定步進為 1000
        new_power = st.number_input("設定初始戰力", min_value=0, value=10000, step=1000)
        
        submit_button = st.form_submit_button(label="➕ 點擊新增")
        
        if submit_button:
            if new_id == "":
                st.error("❌ 玩家 ID 不能為空！")
            elif new_id in st.session_state.member_df["ID"].values:
                st.error("❌ 該 ID 已存在於資料庫中！")
            else:
                # 計算新排行（依目前總人數 + 1，後續會依戰力重新排序）
                new_rank = len(st.session_state.member_df) + 1
                new_row = {"排行": new_rank, "ID": new_id, "職業": new_job, "戰力": new_power}
                
                # 將新資料加入 DataFrame
                st.session_state.member_df = pd.concat([st.session_state.member_df, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"🎉 成功新增：{new_id} ({new_job})")

# ==================== 主畫面：搜尋與排序邏輯 ====================
# 每次畫面刷新時，自動依「戰力」由高到低重新計算「排行」
st.session_state.member_df = st.session_state.member_df.sort_values(by="戰力", ascending=False).reset_index(drop=True)
st.session_state.member_df["排行"] = st.session_state.member_df.index + 1

# 搜尋功能（可搜尋 ID 或 職業）
search_query = st.text_input("🔍 輸入關鍵字搜尋（可搜尋 ID 或 職業）", "").strip().lower()

# 根據搜尋條件篩選要顯示的資料列索引
if search_query:
    filtered_indices = st.session_state.member_df[
        st.session_state.member_df["ID"].str.lower().str.contains(search_query) | 
        st.session_state.member_df["職業"].str.lower().str.contains(search_query)
    ].index.tolist()
else:
    filtered_indices = st.session_state.member_df.index.tolist()

# ==================== 主畫面：表格排版與渲染 ====================
# 設定表格欄位寬度比例
col1, col2, col3, col4 = st.columns([1.5, 3, 2, 3.5])
col1.markdown("**排行**")
col2.markdown("**ID**")
col3.markdown("**職業**")
col4.markdown("⚔️ **戰力 (可直接增減調整)**")
st.divider()


# ==================== 主畫面：表格排版與渲染 ====================
if not filtered_indices:
    st.info("💡 目前資料庫空空如也，或者查無相符的資料。請使用左側側邊欄新增人員！")
else:
    # 第 78 行是 else:
    # 第 79 行的 for 前面必須要有 4 個空格的縮排！
    for idx in filtered_indices:
        row = st.session_state.member_df.iloc[idx]
        
        # 迴圈內部的程式碼前面必須要有 8 個空格的縮排！
        r_col1, r_col2, r_col3, r_col4 = st.columns([1.5, 3, 2, 3.5])
        
        rank_display = row["排行"]
        if rank_display == 1: 
            rank_display = "🥇 1"
        elif rank_display == 2: 
            rank_display = "🥈 2"
        elif rank_display == 3: 
            rank_display = "🥉 3"
        
        r_col1.write(f"**{rank_display}**")
        r_col2.write(row["ID"])
        r_col3.write(row["職業"])
        
        # 戰力輸入框也放進最後一欄 r_col4
        st.session_state.member_df.at[idx, "戰力"] = r_col4.number_input(
            "戰力", 
            min_value=0, 
            value=int(row["戰力"]), 
            step=1000, 
            label_visibility="collapsed", 
            key=f"power_{row['ID']}"
        )


                # 戰力輸入框
        st.session_state.member_df.at[idx, "戰力"] = r_col4.number_input(
            "戰力", 
            min_value=0, 
            value=int(row["戰力"]), 
            step=1000, 
            label_visibility="collapsed", 
            # 🟢 修正：使用複合 Key，既能保證唯一，又能鎖定當前名次，防止分裂成兩格
            key=f"power_{row['ID']}_{idx}"  
        )




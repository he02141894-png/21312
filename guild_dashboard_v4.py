import streamlit as st
import pandas as pd

# 設定網頁標題與排版
st.set_page_config(page_title="戰力成員管理資料庫", layout="wide")

# 1. 初始化原始資料 (使用 st.session_state 確保資料能長久保存)
if 'member_df' not in st.session_state:
    initial_data = [

    ]
    st.session_state.member_df = pd.DataFrame(initial_data)

# ==================== 側邊欄：新增人員功能 ====================
with st.sidebar:
    st.header("👤 新增成員")
    with st.form(key="add_member_form", clear_on_submit=True):
        new_id = st.text_input("輸入玩家 ID", placeholder="例如：").strip()
        
        job_options = ["制裁者", "幻影神兵", "執行者", "操靈師", "無畏艦", "匠師", "仲裁者", "毀滅"]
        new_job = st.selectbox("選擇職業", job_options)
        
        new_power = st.number_input("設定初始戰力", min_value=0, value=0, step=1)
        
        submit_button = st.form_submit_button(label="➕ 點擊新增人員")
        
        if submit_button:
            if new_id == "":
                st.error("❌ 玩家 ID 不能為空！")
            elif new_id in st.session_state.member_df["ID"].values:
                st.error("❌ 該 ID 已存在於資料庫中！")
            else:
                new_row = {"ID": new_id, "職業": new_job, "戰力": new_power}
                st.session_state.member_df = pd.concat([st.session_state.member_df, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"🎉 成功新增：{new_id} ({new_job})")
                st.rerun()

# ==================== 主畫面：自動排序名次 ====================
# 每次正式點擊儲存刷新時，依「戰力」由高到低排序，並建立或更新「排行」欄位
st.session_state.member_df = st.session_state.member_df.sort_values(by="戰力", ascending=False).reset_index(drop=True)
st.session_state.member_df["排行"] = st.session_state.member_df.index + 1

# 將「排行」移到最前面的欄位顯示
cols_order = ["排行", "ID", "職業", "戰力"]
display_df = st.session_state.member_df[cols_order]

# ==================== 主畫面：手動編輯表格 ====================
# 使用 data_editor，設定排行、ID、職業為唯讀，只有「戰力」可以點擊手動打字輸入
edited_df = st.data_editor(
    display_df,
    hide_index=True,
    use_container_width=True,
    num_rows="fixed", # 固定目前列數（新增一律走側邊欄表單）
    column_config={
        "排行": st.column_config.Column("排行 ", disabled=True, width="medium"),
        "ID": st.column_config.Column("ID", disabled=True, width="large"),
        "職業": st.column_config.Column("職業", disabled=True, width="medium"),
        "戰力": st.column_config.NumberColumn("戰力", disabled=False, min_value=0, format="%d" # 純數字格式，去除微調按鈕 
                                           )
    }
)

# 放兩個橫向排列的按鈕：一個儲存排行，一個負責刪除
btn_col1, btn_col2, _ = st.columns([2, 2, 6])

with btn_col1:
    if st.button("💾 儲存並更新排行", type="primary", use_container_width=True):
        # 將使用者剛才手動輸入修改完的戰力，存回系統後台
        st.session_state.member_df["戰力"] = edited_df["戰力"]
        st.toast("✅ 戰力修改已儲存，排行已重新計算！")
        st.rerun()

with btn_col2:
    # 點選表格中任何人的名字，都可以在這裡進行一鍵刪除
    delete_target = st.selectbox(
        "選擇要刪除的人員", 
        ["-- 請選擇 --"] + st.session_state.member_df["ID"].tolist(),
        label_visibility="collapsed"
    )
    if delete_target != "-- 請選擇 --":
        if st.button("🗑️ 刪除選中人員", type="secondary", use_container_width=True):
            st.session_state.member_df = st.session_state.member_df[
                st.session_state.member_df["ID"] != delete_target
            ].reset_index(drop=True)
            st.toast(f"🗑️ 已成功刪除成員：{delete_target}")
            st.rerun()

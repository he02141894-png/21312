import streamlit as st
import pandas as pd
import io

# 設定網頁標題與排版
st.set_page_config(page_title="戰力成員管理資料庫", layout="wide")

# 1. 初始化原始資料 (使用 st.session_state 確保資料能長久保存)
if 'member_df' not in st.session_state:
    initial_data = [
        {"ID": "範例玩家A", "職業": "制裁者", "戰力": 500000},
        {"ID": "煉獄", "職業": "制裁者", "戰力": 10000}
    ]
    st.session_state.member_df = pd.DataFrame(initial_data)

st.title("🏆 戰力成員管理系統 (手動輸入 + Excel 匯出版)")
st.caption("💡 操作說明：\n1. 雙擊 **戰力** 欄位即可直接用鍵盤輸入數字。\n2. 修改完成後，點擊 **「💾 儲存並更新排行」**。\n3. 排行更新後，點擊最下方的 **「📥 下載目前排行至 Excel」** 按鈕即可匯出檔案。")

# ==================== 側邊欄：新增人員功能 ====================
with st.sidebar:
    st.header("👤 新增成員")
    with st.form(key="add_member_form", clear_on_submit=True):
        new_id = st.text_input("輸入玩家 ID", placeholder="例如：斬擊之王").strip()
        
        job_options = ["制裁者", "幻影神兵", "執行者", "操靈師", "無畏艦", "匠師", "仲裁者", "毀滅"]
        new_job = st.selectbox("選擇職業", job_options)
        
        new_power = st.number_input("設定初始戰力", min_value=0, value=10000, step=1000)
        
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
# 依「戰力」由高到低排序，並建立或更新「排行」欄位
st.session_state.member_df = st.session_state.member_df.sort_values(by="戰力", ascending=False).reset_index(drop=True)
st.session_state.member_df["排行"] = st.session_state.member_df.index + 1

# 將「排行」移到最前面的欄位顯示
cols_order = ["排行", "ID", "職業", "戰力"]
display_df = st.session_state.member_df[cols_order]

# ==================== 主畫面：手動編輯表格 ====================
edited_df = st.data_editor(
    display_df,
    hide_index=True,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "排行": st.column_config.Column("排行 🏆", disabled=True, width="medium"),
        "ID": st.column_config.Column("玩家 ID 👤", disabled=True, width="large"),
        "職業": st.column_config.Column("職業 ⚔️", disabled=True, width="medium"),
        "戰力": st.column_config.NumberColumn(
            "戰力 (點擊兩下手動輸入) 📊", 
            disabled=False, 
            min_value=0,
            format="%d"
        )
    }
)

# 功能按鈕區：儲存與刪除
btn_col1, btn_col2, _ = st.columns([2, 3, 5])

with btn_col1:
    if st.button("💾 儲存並更新排行", type="primary", use_container_width=True):
        st.session_state.member_df["戰力"] = edited_df["戰力"]
        st.toast("✅ 戰力修改已儲存，排行已重新計算！")
        st.rerun()

with btn_col2:
    delete_target = st.selectbox(
        "選擇要刪除的人員", 
        ["-- 選擇刪除人員 --"] + st.session_state.member_df["ID"].tolist(),
        label_visibility="collapsed"
    )
    if delete_target != "-- 選擇刪除人員 --":
        if st.button("🗑️ 刪除選中人員", type="secondary", use_container_width=True):
            st.session_state.member_df = st.session_state.member_df[
                st.session_state.member_df["ID"] != delete_target
            ].reset_index(drop=True)
            st.toast(f"🗑️ 已成功刪除成員：{delete_target}")
            st.rerun()

st.divider()

# ==================== 🟢 新增：一鍵導出 Excel 功能 ====================
st.subheader("📥 數據導出中心")

# 將現有的 DataFrame 轉化成記憶體中的 Excel 二進位串流
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    # 導出排好序的完整資料，且不保留 Pandas 內建的 index 索引軸
    display_df.to_excel(writer, index=False, sheet_name='公會戰力排行')

# 建立 Streamlit 內建下載按鈕
st.download_button(
    label="📥 下載目前排行至 Excel 檔案 (.xlsx)",
    data=buffer.getvalue(),
    file_name="公會戰力排行表.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=False
)

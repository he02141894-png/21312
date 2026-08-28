import streamlit as st
import pandas as pd
import json
import os
from streamlit_gsheets import GSheetsConnection

# 設定網頁標題與排版
st.set_page_config(page_title="公會資訊管理系統 v17", page_icon="⚔️", layout="wide")

# LOCAL_DB 檔名，用來保障新增/刪除永久儲存不消失
LOCAL_DB = "guild_cloud_db.json"

# ==========================================
# 🔑 密碼與雲端安全機制
# ==========================================
JOB_PASSWORD = st.secrets.get("job_password", "job123")      # 💡 職業維護專用密碼
ADMIN_PASSWORD = st.secrets.get("admin_password", "admin123")  # 💡 最高幹部管理密碼

# --- 定義遊戲職業選項 ---
JOB_OPTIONS = ["制裁者", "幻影神兵", "執行者", "操靈師", "無畏艦", "匠師", "仲裁者", "毀滅"]

# --- 精準定義 17 格客製化核心裝備規格欄位清單 ---
GEAR_FIELDS = [
"主武", "二武", "三武",  "頸部", "上身", "手臂", "下身", "腿部", 
"頭冠", "耳環", "項鍊", "手環", "戒指", "驅動器", "觀測儀", "偏轉器"
]

# 串接 Google Sheets 連線 (作為初始讀取)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 函式：讀取與儲存雲端資料 ---
def load_data_from_storage():
    if os.path.exists(LOCAL_DB):
        try:
            with open(LOCAL_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    try:
        df_sheet = conn.read(ttl="0")
        df_sheet["戰力"] = pd.to_numeric(df_sheet["戰力"], errors="coerce").fillna(0).astype(int)
        data = df_sheet.to_dict(orient="records")
        with open(LOCAL_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
    except Exception as e:
        default_gears = {field: "無" for field in GEAR_FIELDS}
        default_gears["主武"] = "究極終焉劍 +15"
        default_gears["二武"] = "弒神之刃 +14"
        default_gears["三武"] = "破空短刃 +10"
        default_gears["驅動器"] = "量子核心 Mk-III"
        default_gears["偏轉器"] = "絕對防禦障壁"
        init_data = [
            {"角色名稱": "傲視群雄_X", "職業": "制裁者、毀滅", "戰力": 1250000, **default_gears},
            {"角色名稱": "影之刃_凱", "職業": "幻影神兵", "戰力": 1180000, **{f: "無" for f in GEAR_FIELDS}}
        ]
        return init_data

def save_data_to_storage(data_list):
    with open(LOCAL_DB, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)
    st.session_state.guild_list = data_list

# 初始化網頁記憶體快取
if "guild_list" not in st.session_state:
    st.session_state.guild_list = load_data_from_storage()

st.title("⚔️ 公會資訊雲端管理系統 v17 (功能全面安全版)")

# ==========================================
# 🔐 權限控制中心
# ==========================================
st.sidebar.title("🔐 身分與權限驗證")
role_choice = st.sidebar.radio(
    "請選擇您的存取權限：", 
    ["一般成員 (僅限瀏覽)", "職業負責人 (僅限變更職業)", "最高幹部 (擁有全部權限)"]
)

is_admin = False
is_job_updater = False

if role_choice == "最高幹部 (擁有全部權限)":
    pwd = st.sidebar.text_input("請輸入最高管理密碼：", type="password", key="admin_pwd")
    if pwd == ADMIN_PASSWORD:
        st.sidebar.success("👑 最高權限已解鎖！")
        is_admin = True
    elif pwd != "":
        st.sidebar.error("❌ 密碼錯誤！")

elif role_choice == "職業負責人 (僅限變更職業)":
    pwd = st.sidebar.text_input("請輸入職業專用密碼：", type="password", key="job_pwd")
    if pwd == JOB_PASSWORD:
        st.sidebar.success("🛡️ 職業修改權限已解鎖！")
        is_job_updater = True
    elif pwd != "":
        st.sidebar.error("❌ 密碼錯誤！")
else:
    st.sidebar.info("ℹ️ 當前為「公開瀏覽模式」，前五名大佬的戰力已被單獨遮蔽。")

# ==========================================
# 📝 權限 A：最高幹部專屬區
# ==========================================
if is_admin:
    st.subheader("📝 成員全面資料維護 (最高幹部專區)")
    
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = -1

    if st.session_state.edit_index != -1 and st.session_state.edit_index < len(st.session_state.guild_list):
        current_item = st.session_state.guild_list[st.session_state.edit_index]
        default_name = current_item.get("角色名稱", "")
        raw_jobs = current_item.get("職業", "")
        default_jobs = [j.strip() for j in str(raw_jobs).split("、") if j.strip() in JOB_OPTIONS]
        default_power = int(current_item.get("戰力", 0))
        default_gears = {field: current_item.get(field, "無") for field in GEAR_FIELDS}
        button_label = "💾 儲存修改資訊"
    else:
        default_name = ""
        default_jobs = []
        default_power = 0
        default_gears = {field: "無" for field in GEAR_FIELDS}
        button_label = "➕ 新增公會成員"

    with st.form(key="admin_member_form_v17", clear_on_submit=True):
        st.markdown("##### 📌 基礎基本資訊")
        col1, col2, col3 = st.columns(3)
        with col1:
            name_input = st.text_input("角色名稱", value=default_name)
        with col2:
            jobs_input = st.multiselect("職業選項 (可多選)", options=JOB_OPTIONS, default=default_jobs)
        with col3:
            power_input = st.number_input("目前戰力", min_value=0, step=1000, value=default_power)
        
        st.write("---")
        st.markdown("##### 🛡️ 17 格客製化核心裝備細項面板")
        
        gear_inputs = {}
        st.markdown("**第一組：武器**")
        g_col1, g_col2, g_col3,  = st.columns(3)
        with g_col1:
            gear_inputs["主武"] = st.text_input("主武", value=default_gears["主武"])
        with g_col2:
            gear_inputs["二武"] = st.text_input("二武", value=default_gears["二武"])
        with g_col3:
            gear_inputs["三武"] = st.text_input("三武", value=default_gears["三武"])

        st.markdown("**第二組：防具**")
        g_col5, g_col6, g_col7, g_col8, g_col9 = st.columns(5)
        with g_col5:
            gear_inputs["頸部"] = st.text_input("頸部", value=default_gears["頸部"])
        with g_col6:
            gear_inputs["上身"] = st.text_input("上身", value=default_gears["上身"])
        with g_col7:
            gear_inputs["手臂"] = st.text_input("手臂", value=default_gears["手臂"])
        with g_col8:
            gear_inputs["下身"] = st.text_input("下身", value=default_gears["下身"])
        with g_col9:
            gear_inputs["腿部"] = st.text_input("腿部", value=default_gears["腿部"])

        st.markdown("**第三組：飾品**")
        g_co20, g_co21, g_co22, g_co23, g_co24 = st.columns(5)
        with g_co20:
            gear_inputs["頭冠"] = st.text_input("頭冠", value=default_gears["頭冠"])
        with g_co21:
            gear_inputs["耳環"] = st.text_input("耳環", value=default_gears["耳環"])
        with g_co22:
            gear_inputs["項鍊"] = st.text_input("項鍊", value=default_gears["項鍊"])
        with g_co23:
            gear_inputs["手環"] = st.text_input("手環", value=default_gears["手環"])
        with g_co24:
            gear_inputs["戒指"] = st.text_input("戒指", value=default_gears["戒指"])

        st.markdown("**第四組：擴充**")
        g_co25, g_co26, g_co27= st.columns(3)
        with g_co25:
            gear_inputs["驅動器"] = st.text_input("驅動器", value=default_gears["驅動器"])
        with g_co26:
            gear_inputs["觀測儀"] = st.text_input("觀測儀", value=default_gears["觀測儀"])
        with g_co27:
            gear_inputs["偏轉器"] = st.text_input("偏轉器", value=default_gears["偏轉器"])

        submit_button = st.form_submit_button(label=button_label, type="primary")

    if submit_button:
        if not name_input.strip():
            st.error("❌ 角色名稱不能為空！")
        elif not jobs_input:
            st.error("❌ 請至少選擇一個職業！")
        else:
            job_str = "、".join(jobs_input)
            new_member = {"角色名稱": name_input.strip(), "職業": job_str, "戰力": power_input, **gear_inputs}
            
            current_list = load_data_from_storage()
            if st.session_state.edit_index == -1:
                current_list.append(new_member)
                st.toast(f"✅ 已成功新增成員：{name_input}")
            else:
                if st.session_state.edit_index < len(current_list):
                    current_list[st.session_state.edit_index] = new_member
                st.toast(f"🔄 已成功更新成員資料：{name_input}")
                st.session_state.edit_index = -1
                
            save_data_to_storage(current_list)
            st.rerun()

    if st.session_state.edit_index != -1:
        if st.button("❌ 取消修改"):
            st.session_state.edit_index = -1
            st.rerun()

# ==========================================
# 📝 權限 B：職業負責人專屬區
# ==========================================
elif is_job_updater:
    st.subheader("🛡️ 職業標籤即時更新 (職業負責人專區)")
    st.caption("💡 提示：此模式下您可以更新所有人的職業，但無法更動或看見前五名的戰力。")
    
    current_list = load_data_from_storage()
    member_names = [m["角色名稱"] for m in current_list]
    
    if member_names:
        with st.form(key="job_only_form_v16"):
            c_select, c_job = st.columns(2) 
            with c_select:
                selected_name = st.selectbox("請選擇要更新職業的角色：", options=member_names)
            
            target_idx = next(i for i, x in enumerate(current_list) if x["角色名稱"] == selected_name)
            raw_current_jobs = current_list[target_idx].get("職業", "")
            valid_current_jobs = [j.strip() for j in str(raw_current_jobs).split("、") if j.strip() in JOB_OPTIONS]
            
            with c_job:
                updated_jobs = st.multiselect("重新設定該角色的職業 (可複選)：", options=JOB_OPTIONS, default=valid_current_jobs)
                
            job_submit = st.form_submit_button("💾 僅儲存職業變更", type="primary")
            
        if job_submit:
            if not updated_jobs:
                st.error("❌ 角色至少需要保留一個職業！")
            else:
                current_list[target_idx]["職業"] = "、".join(updated_jobs)
                save_data_to_storage(current_list)
                st.success(f"✅ 成功將職業變更即時存入系統！")
                st.rerun()

# ==========================================
# 📊 核心排行榜
# ==========================================
st.write("---")
st.subheader("📊 自動化整理：最新公會全裝備名單")

current_list = load_data_from_storage()

if current_list:
    full_df = pd.DataFrame(current_list)
    full_df = full_df.sort_values(by="戰力", ascending=False).reset_index(drop=True)
    full_df["真實排名"] = full_df.index + 1
    full_df["職業顯示"] = full_df["職業"]

    # 複製一份專門用來在網頁表格顯示的 DataFrame
    display_df = full_df.copy()

    # 🔒 戰力精準遮蔽前五名
    if not is_admin:
        st.warning("🔒 戰力安全防護：目前權限下，系統已自動遮蔽公會前 5 名大佬的【戰力數字】與【真實排名】。")
        display_df["戰力(排名)"] = display_df.apply(
            lambda r: f"🔒 資訊保密" if r["真實排名"] <= 5 else f"{int(r['戰力']):,} (#{r['真實排名']})", axis=1
        )
        display_df["排名顯示"] = display_df["真實排名"].apply(lambda x: "🎖️ 大佬" if x <= 5 else str(x))
    else:
        display_df["戰力(排名)"] = display_df.apply(lambda r: f"{int(r['戰力']):,} (#{r['真實排名']})", axis=1)

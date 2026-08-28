import streamlit as st
import pandas as pd
import json
import os

# 設定網頁標題與排版
st.set_page_config(page_title="公會資訊自動化管理系統", page_icon="⚔️", layout="wide")

# 獨立本地持久化資料庫，保障新增/修改/刪除永久儲存不消失
LOCAL_DB = "guild_cloud_db.json"

# ==========================================
# 🔑 密碼權限隱藏安全機制 (從系統保險箱中讀取)
# ==========================================
JOB_PASSWORD = st.secrets.get("job_password", "job123")      # 🛡️ 職業負責人專用密碼
GEAR_PASSWORD = st.secrets.get("gear_password", "gear123")    # ⚙️ 裝備負責人專用密碼 (全新加入)
ADMIN_PASSWORD = st.secrets.get("admin_password", "admin123")  # 👑 最高幹部管理密碼

# --- 定義遊戲職業選項 (客製化 8 大職業) ---
JOB_OPTIONS = ["制裁者", "幻影神兵", "執行者", "操靈師", "無畏艦", "匠師", "仲裁者", "毀滅"]

# --- 定義 17 格客製化裝備欄位清單 ---
GEAR_FIELDS = [
    "主武", "二武", "三武", "四武", 
    "頸部", "上身", "手臂", "下身",
    "腿部", "頭冠", "耳環", "項鍊", 
    "手環", "戒指", "驅動器", "觀測儀", "偏轉器"
]

# --- 函式：讀取與儲存本地持久化資料 ---
def load_data_from_storage():
    if os.path.exists(LOCAL_DB):
        try:
            with open(LOCAL_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # 若為初次運行，自動生成保底的初始名單
    default_gears = {field: "無" for field in GEAR_FIELDS}
    default_gears["主武"] = "究極終焉劍 +15"
    default_gears["二武"] = "弒神之刃 +14"
    default_gears["三武"] = "破空短刃 +10"
    default_gears["四武"] = "元素副刃 +9"
    default_gears["驅動器"] = "量子核心 Mk-III"
    default_gears["偏轉器"] = "絕對防禦障壁"
    
    init_data = [
        {"角色名稱": "傲視群雄_X", "職業": ["制裁者", "毀滅"], "戰力": 1250000, **default_gears},
        {"角色名稱": "影之刃_凱", "職業": ["幻影神兵"], "戰力": 1180000, **{f: "無" for f in GEAR_FIELDS}},
        {"角色名稱": "元素主宰_麗", "職業": ["操靈師"], "戰力": 1120000, **{f: "無" for f in GEAR_FIELDS}},
        {"角色名稱": "聖光守護_明", "職業": ["仲裁者"], "戰力": 1050000, **{f: "無" for f in GEAR_FIELDS}},
        {"角色名稱": "暗夜箭神_風", "職業": ["幻影神兵"], "戰力": 980000, **{f: "無" for f in GEAR_FIELDS}},
        {"角色名稱": "無情流星", "職業": ["執行者"], "戰力": 850000, **{f: "無" for f in GEAR_FIELDS}},
        {"角色名稱": "補血機器人", "職業": ["匠師"], "戰力": 720000, **{f: "無" for f in GEAR_FIELDS}}
    ]
    with open(LOCAL_DB, "w", encoding="utf-8") as f:
        json.dump(init_data, f, ensure_ascii=False, indent=4)
    return init_data

def save_data_to_storage(data_list):
    with open(LOCAL_DB, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)
    st.session_state.guild_list = data_list

# 初始化網頁記憶體快取
if "guild_list" not in st.session_state:
    st.session_state.guild_list = load_data_from_storage()

st.title("⚔️ 公會資訊自動化整理與管理系統 (職權階層版)")

# ==========================================
# 🔐 權限控制中心 (升級為 4 種身分切換)
# ==========================================
st.sidebar.title("🔐 身分與權限驗證")
role_choice = st.sidebar.radio(
    "請選擇您的存取權限：", 
    ["一般成員 (僅限瀏覽)", "職業負責人 (僅限變更職業)", "裝備負責人 (僅限變更裝備)", "最高幹部 (擁有全部權限)"]
)

is_admin = False
is_job_updater = False
is_gear_updater = False

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

elif role_choice == "裝備負責人 (僅限變更裝備)":
    pwd = st.sidebar.text_input("請輸入裝備專用密碼：", type="password", key="gear_pwd")
    if pwd == GEAR_PASSWORD:
        st.sidebar.success("⚙️ 裝備維護權限已解鎖！")
        is_gear_updater = True
    elif pwd != "":
        st.sidebar.error("❌ 密碼錯誤！")
else:
    st.sidebar.info("ℹ️ 當前為「公開瀏覽模式」，前五名大佬的戰力已被單獨遮蔽。")

# ==========================================
# 📝 權限 A：最高幹部專屬區 (全面新增與修改)
# ==========================================
if is_admin:
    st.subheader("📝 成員全面資料維護 (最高幹部專區)")
    
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = -1

    if st.session_state.edit_index != -1 and st.session_state.edit_index < len(st.session_state.guild_list):
        current_item = st.session_state.guild_list[st.session_state.edit_index]
        default_name = current_item.get("角色名稱", "")
        raw_jobs = current_item.get("職業", [])
        if isinstance(raw_jobs, str):
            raw_jobs = [raw_jobs]
        default_jobs = [j for j in raw_jobs if j in JOB_OPTIONS]
        default_power = int(current_item.get("戰力", 0))
        default_gears = {field: current_item.get(field, "無") for field in GEAR_FIELDS}
        button_label = "💾 儲存修改資訊"
    else:
        default_name = ""
        default_jobs = []
        default_power = 0
        default_gears = {field: "無" for field in GEAR_FIELDS}
        button_label = "➕ 新增公會成員"

    with st.form(key="admin_member_form_v18", clear_on_submit=True):
        st.markdown("##### 📌 基礎基本資訊")
        col1, col2, col3 = st.columns(3)
        with col1: name_input = st.text_input("角色名稱", value=default_name)
        with col2: jobs_input = st.multiselect("職業選項 (可多選)", options=JOB_OPTIONS, default=default_jobs)
        with col3: power_input = st.number_input("目前戰力", min_value=0, step=1000, value=default_power)
        
        st.write("---")
        st.markdown("##### 🛡️ 17 格客製化核心裝備細項面板")
        gear_inputs = {}
        st.markdown("**第一組：四武器體系面板**")
        g_col1, g_col2, g_col3, g_col4 = st.columns(4)
        with g_col1: gear_inputs["主武"] = st.text_input("主武", value=default_gears["主武"])
        with g_col2: gear_inputs["二武"] = st.text_input("二武", value=default_gears["二武"])
        with g_col3: gear_inputs["三武"] = st.text_input("三武", value=default_gears["三武"])
        with g_col4: gear_inputs["四武"] = st.text_input("四武", value=default_gears["四武"])
            
        st.markdown("**第二組：身體與飾品裝備**")
        g_col5, g_col6, g_col7 = st.columns(3)
        with g_col5:
            gear_inputs["頸部"] = st.text_input("頸部", value=default_gears["頸部"])
            gear_inputs["下身"] = st.text_input("下身", value=default_gears["下身"])
            gear_inputs["耳環"] = st.text_input("耳環", value=default_gears["耳環"])
            gear_inputs["戒指"] = st.text_input("戒指", value=default_gears["戒指"])
        with g_col6:
            gear_inputs["上身"] = st.text_input("上身", value=default_gears["上身"])
            gear_inputs["腿部"] = st.text_input("腿部", value=default_gears["腿部"])
            gear_inputs["項鍊"] = st.text_input("項鍊", value=default_gears["項鍊"])
            gear_inputs["驅動器"] = st.text_input("驅動器", value=default_gears["驅動器"])
        with g_col7:
            gear_inputs["手臂"] = st.text_input("手臂", value=default_gears["手臂"])
            gear_inputs["頭冠"] = st.text_input("頭冠", value=default_gears["頭冠"])
            gear_inputs["手環"] = st.text_input("手環", value=default_gears["手環"])
            gear_inputs["觀測儀"] = st.text_input("觀測儀", value=default_gears["觀測儀"])
            gear_inputs["偏轉器"] = st.text_input("偏轉器", value=default_gears["偏轉器"])

        submit_button = st.form_submit_button(label=button_label, type="primary")

    if submit_button:
        if not name_input.strip(): st.error("❌ 角色名稱不能為空！")
        elif not jobs_input: st.error("❌ 請至少選擇一個職業！")
        else:
            new_member = {"角色名稱": name_input.strip(), "職業": jobs_input, "戰力": power_input, **gear_inputs}
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

# ==========================================
# 📝 權限 B：職業負責人專屬區 (僅能變更職業)
# ==========================================
elif is_job_updater:
    st.subheader("🛡️ 職業標籤即時更新 (職業負責人專區)")
    current_list = load_data_from_storage()
    member_names = [m["角色名稱"] for m in current_list]
    
    if member_names:
        with st.form(key="job_only_form_v18"):
            c_select, c_job = st.columns(2) 
            with c_select: selected_name = st.selectbox("請選擇要更新職業的角色：", options=member_names)
            target_idx = next(i for i, x in enumerate(current_list) if x["角色名稱"] == selected_name)
            raw_current_jobs = current_list[target_idx].get("職業", [])
            if isinstance(raw_current_jobs, str): raw_current_jobs = [raw_current_jobs]
            valid_current_jobs = [j for j in raw_current_jobs if j in JOB_OPTIONS]
            
            with c_job: updated_jobs = st.multiselect("重新設定職業 (可複選)：", options=JOB_OPTIONS, default=valid_current_jobs)
            job_submit = st.form_submit_button("💾 僅儲存職業變更", type="primary")
            
        if job_submit:
            if not updated_jobs: st.error("❌ 角色至少需要保留一個職業！")
            else:
                current_list[target_idx]["職業"] = updated_jobs
                save_data_to_storage(current_list)
                st.success(f"✅ 成功將職業變更即時存入系統！")
                st.rerun()

# ==========================================
# 📝 權限 C：⚙️ 裝備負責人專屬區 (💡 全新功能：單獨變更裝備)
# ==========================================
elif is_gear_updater:
    st.subheader("⚙️ 17 格裝備分項獨立更新 (裝備負責人專區)")
    st.caption("💡 提示：此模式下您可以自由調整任何隊員的 17 格配裝，但無法修改角色名字、戰力與職業，也無法刪除隊員。")
    current_list = load_data_from_storage()
    member_names = [m["角色名稱"] for m in current_list]
    
    if member_names:
        with st.form(key="gear_only_form_v18"):
            selected_name_gear = st.selectbox("請選擇要維護裝備的角色：", options=member_names)
            target_idx_gear = next(i for i, x in enumerate(current_list) if x["角色名稱"] == selected_name_gear)
            current_member_gear = current_list[target_idx_gear]
            
            # 精準拉出該角色當前的 17 格裝備作為預設值

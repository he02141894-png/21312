import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 設定網頁標題與排版
st.set_page_config(page_title="公會資訊管理系統 v16", page_icon="⚔️", layout="wide")

# ==========================================
# 🔑 密碼與雲端資料庫安全機制
# ==========================================
JOB_PASSWORD = st.secrets.get("job_password", "job123")      # 💡 職業維護專用密碼
ADMIN_PASSWORD = st.secrets.get("admin_password", "admin123")  # 💡 最高幹部管理密碼

# --- 定義遊戲職業選項 ---
JOB_OPTIONS = ["制裁者", "幻影神兵", "執行者", "操靈師", "無畏艦", "匠師", "仲裁者", "毀滅"]

# --- 精準定義 16 格裝備規格清單 ---
GEAR_FIELDS = [
    "主武", "二武", "三武",  "頸部", "上身", "手臂", "下身", "腿部", 
    "頭冠", "耳環", "項鍊", "手環", "戒指", "驅動器", "觀測儀"
]

# 串接 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 函式：讀取與儲存雲端資料 ---
def load_data_from_sheet():
    try:
        # 從設定好的 Google 試算表讀取資料
        df_sheet = conn.read(ttl="0")
        # 清洗與確保必要的欄位格式
        df_sheet["戰力"] = pd.to_numeric(df_sheet["戰力"], errors="coerce").fillna(0).astype(int)
        return df_sheet.to_dict(orient="records")
    except Exception as e:
        # 若雲端目前沒資料，提供初始格式防錯
        default_gears = {field: "無" for field in GEAR_FIELDS}
        default_gears["主武"] = "究極終焉劍 +15"
        init_data = [
            {"角色名稱": "傲視群雄_X", "職業": "制裁者、毀滅", "戰力": 1250000, **default_gears},
            {"角色名稱": "影之刃_凱", "職業": "幻影神兵", "戰力": 1180000, **{f: "無" for f in GEAR_FIELDS}}
        ]
        return init_data

def save_data_to_sheet(data_list):
    df_save = pd.DataFrame(data_list)
    # 將最新整理的資料覆寫回雲端 Google Sheets 檔案中
    conn.update(data=df_save)
    st.session_state.guild_list = data_list

# 初始化網頁記憶體快取
if "guild_list" not in st.session_state:
    st.session_state.guild_list = load_data_from_sheet()

st.title("⚔️ 公會資訊雲端管理系統 v16 (永久儲存防消失版)")

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
# 📝 權限 A：最高幹部專屬區 (全面新增與修改)
# ==========================================
if is_admin:
    st.subheader("📝 成員全面資料維護 (最高幹部專區)")
    
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = -1

    if st.session_state.edit_index != -1 and st.session_state.edit_index < len(st.session_state.guild_list):
        current_item = st.session_state.guild_list[st.session_state.edit_index]
        default_name = current_item.get("角色名稱", "")
        raw_jobs = current_item.get("職業", "")
        # 解析儲存的字串為多選列表
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

    with st.form(key="admin_member_form_v16", clear_on_submit=True):
        st.markdown("##### 📌 基礎基本資訊")
        col1, col2, col3 = st.columns(3)
        with col1:
            name_input = st.text_input("角色名稱", value=default_name)
        with col2:
            jobs_input = st.multiselect("職業選項 (可多選)", options=JOB_OPTIONS, default=default_jobs)
        with col3:
            power_input = st.number_input("目前戰力", min_value=0, step=1000, value=default_power)
        
        st.write("---")
        st.markdown("##### 🛡️ 16 格新制核心裝備細項面板")
        
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
            
            current_list = load_data_from_sheet()
            if st.session_state.edit_index == -1:
                current_list.append(new_member)
                st.toast(f"✅ 已成功新增並同步雲端：{name_input}")
            else:
                if st.session_state.edit_index < len(current_list):
                    current_list[st.session_state.edit_index] = new_member
                st.toast(f"🔄 已成功更新雲端成員：{name_input}")
                st.session_state.edit_index = -1
                
            save_data_to_sheet(current_list)
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
    st.caption("💡 提示：在此模式下您可以更新所有人的職業，但無法更動或看見前五名的戰力。")
    
    current_list = load_data_from_sheet()
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
                save_data_to_sheet(current_list)
                st.success(f"✅ 成功將職業變更即時存入雲端！")
                st.rerun()

# ==========================================
# 📊 核心排行榜
# ==========================================
st.subheader("📊 自動化整理：最新公會全裝備雲端名單")

# 強制重新拉取雲端最真實的名單
current_list = load_data_from_sheet()

if current_list:
    df = pd.DataFrame(current_list)
    df = df.sort_values(by="戰力", ascending=False).reset_index(drop=True)
    df["真實排名"] = df.index + 1
    
    df["職業顯示"] = df["職業"]

    # 🔒 戰力精準遮蔽前五名
    if not is_admin:
        st.warning("🔒 戰力安全防護：目前權限下，系統已自動遮蔽公會前 5 名大佬的【戰力數字】與【真實排名】。")
        df["戰力(排名)"] = df.apply(
            lambda r: f"🔒 資訊保密" if r["真實排名"] <= 5 else f"{int(r['戰力']):,} (#{r['真實排名']})", axis=1
        )
        df["排名顯示"] = df["真實排名"].apply(lambda x: "🎖️ 大佬" if x <= 5 else str(x))
    else:
        df["戰力(排名)"] = df.apply(lambda r: f"{int(r['戰力']):,} (#{r['真實排名']})", axis=1)
        df["排名顯示"] = df["真實排名"].astype(str)

    display_cols = ["排名顯示", "角色名稱", "職業顯示", "戰力(排名)"] + GEAR_FIELDS
    display_df = df[display_cols]
    display_df = display_df.rename(columns={"排名顯示": "排名", "職業顯示": "職業"})
    
    # 🔍 全體職業篩選器
    filter_job = st.selectbox("🔍 依職業篩選現有排行榜 (可選填)：", ["顯示全部職業"] + JOB_OPTIONS)
    if filter_job != "顯示全部職業":
        display_df = display_df[display_df["職業"].apply(lambda x: filter_job in str(x))].reset_index(drop=True)

    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # ==========================================
    # 🔧 快捷管理鍵 (僅幹部看見)
    # ==========================================
   if is_admin:
    st.write("🔧 **最高幹部管理快捷鍵：**")
    for idx, row in df.iterrows():
        # 💡 在 for 迴圈之下的「每一行」，最前面都必須再多加上 4 個英文空格（或 1 個 Tab）！
        orig_idx = next(i for i, x in enumerate(st.session_state.guild_list) if x["角色名稱"] == row["角色名稱"])
        c1, col_space, c2, c3 = st.columns(4) 

import io
import os
import numpy as np
import pandas as pd
import streamlit as st
from google import genai

# =============================================================================
# 1. PAGE CONFIGURATION (Glitch-Free Native Sidebar)
# =============================================================================
st.set_page_config(
    page_title="C.Arch | Consulting Architecture & People Analytics",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# 2. ORIGINAL C.ARCH MIDNIGHT NAVY / TEAL DESIGN SYSTEM + DARK/LIGHT TOGGLE
# =============================================================================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def apply_carch_theme(is_dark: bool):
    if is_dark:
        app_bg = "#070D19"
        sidebar_bg = "#0E1628"
        card_bg = "#0C1526"
        card_border = "#0E7490"
        card_shadow = "0 4px 20px rgba(6, 182, 212, 0.08)"
        text_main = "#F8FAFC"
        text_muted = "#94A3B8"
        input_bg = "#131F38"
        input_border = "#1E293B"
        tab_active = "#06B6D4"
        emerald_btn = "#10B981"
        emerald_hover = "#059669"
    else:
        app_bg = "#F8FAFC"
        sidebar_bg = "#F1F5F9"
        card_bg = "#FFFFFF"
        card_border = "#0891B2"
        card_shadow = "0 4px 14px rgba(15, 23, 42, 0.05)"
        text_main = "#0F172A"
        text_muted = "#475569"
        input_bg = "#FFFFFF"
        input_border = "#CBD5E1"
        tab_active = "#0891B2"
        emerald_btn = "#10B981"
        emerald_hover = "#059669"

    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {app_bg} !important;
            color: {text_main} !important;
        }}
        .block-container {{
            padding-top: 2.8rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1360px;
        }}

        /* Sidebar Styling (Preserves native collapse/expand button) */
        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {input_border} !important;
        }}
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {{
            color: {text_main} !important;
        }}

        /* Main Headings & Copy */
        h1, h2, h3, h4 {{
            color: {text_main} !important;
            font-weight: 700 !important;
            letter-spacing: -0.015em !important;
        }}
        p, label, .stMarkdown {{
            color: {text_main};
        }}
        .stCaption {{
            color: {text_muted} !important;
        }}

        /* Teal-Bordered KPI Metric Cards */
        div[data-testid="stMetric"] {{
            background-color: {card_bg} !important;
            border: 1px solid {card_border} !important;
            border-radius: 12px !important;
            padding: 18px 22px !important;
            box-shadow: {card_shadow} !important;
        }}
        div[data-testid="stMetricLabel"] p {{
            color: {text_muted} !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
        }}
        div[data-testid="stMetricValue"] div {{
            color: {text_main} !important;
            font-size: 2.0rem !important;
            font-weight: 700 !important;
        }}

        /* Inputs, Text Areas & Selectboxes */
        .stTextArea textarea,
        .stTextInput input,
        div[data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            color: {text_main} !important;
            border: 1px solid {input_border} !important;
            border-radius: 8px !important;
        }}

        /* File Uploader & Expanders */
        section[data-testid="stFileUploaderDropzone"],
        div[data-testid="stExpander"] {{
            background-color: {card_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 10px !important;
        }}

        /* Popover Buttons (Info & Prompt Tips) */
        div[data-testid="stPopover"] > button {{
            background-color: {input_bg} !important;
            color: {text_main} !important;
            border: 1px solid {input_border} !important;
            border-radius: 8px !important;
        }}

        /* Primary Action Button */
        button[kind="primary"] {{
            background-color: #0284C7 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }}
        button[kind="primary"]:hover {{
            background-color: #0369A1 !important;
        }}

        /* Emerald Green Export Download Buttons */
        div[data-testid="stDownloadButton"] button {{
            background-color: {emerald_btn} !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.55rem 1.2rem !important;
        }}
        div[data-testid="stDownloadButton"] button:hover {{
            background-color: {emerald_hover} !important;
            color: #FFFFFF !important;
        }}

        /* Tabs Accent Bar */
        button[data-baseweb="tab"] {{
            color: {text_muted} !important;
            font-weight: 500 !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {tab_active} !important;
            border-bottom-color: {tab_active} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

apply_carch_theme(st.session_state.dark_mode)

# =============================================================================
# 3. SAMPLE DATASET (Matches Original Nairobi/Mombasa/Kisumu Consulting Schema)
# =============================================================================
@st.cache_data
def load_sample_consulting_data() -> pd.DataFrame:
    return pd.DataFrame({
        "Employee_ID": ["E01", "E02", "E03", "E04", "E05", "E05", "E06", "E07", "E08", "E09"],
        "Department": ["Consulting", "Audit", "Consulting", "Tax", "Audit", "Audit", "Advisory", "Consulting", "Advisory", "Tax"],
        "Region": ["Nairobi", "nairobi", "Mombasa", "Nairobi", "Kisumu", "Kisumu", "Nairobi", "Mombasa", "Nairobi", "Kisumu"],
        "Target_Revenue": [120000, 95000, 130000, 88000, 102000, 102000, 115000, 125000, 110000, 90000],
        "Actual_Revenue": [134000, 91000, 142000, 82000, 105000, 105000, 118000, 139000, 104000, 94000],
        "Engagement_Score": [4.5, 3.2, 4.8, 2.9, 3.7, 3.7, 4.1, 4.6, 3.4, np.nan],
        "Attrition_Risk": [1.8, 3.9, 1.5, 4.2, 3.1, 3.1, 2.4, 1.6, 3.6, 2.8],
    })

# =============================================================================
# 4. BRAND HEADER, SESSION STATE & DATA INGESTION
# =============================================================================
st.markdown("# 🏛️ C.Arch")
st.markdown("#### Consulting Architecture & People Analytics Workbench")
st.write("")

if "active_ai_prompt" not in st.session_state:
    st.session_state.active_ai_prompt = ""
if "ai_transformed_df" not in st.session_state:
    st.session_state.ai_transformed_df = None
if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

with st.expander("📂 Upload Client Dataset (CSV / Excel) or Toggle Sample Sandbox", expanded=False):
    up_c1, up_c2 = st.columns([3, 1])
    with up_c1:
        uploaded_file = st.file_uploader("Upload CSV or Excel (.xlsx):", type=["csv", "xlsx", "xls"])
    with up_c2:
        st.write("")
        st.write("")
        use_sample = st.checkbox("Use Built-In Consulting Dataset", value=(uploaded_file is None))

df = None
source_label = None

if uploaded_file is not None:
    source_label = uploaded_file.name
    if st.session_state.last_uploaded_name != source_label:
        st.session_state.ai_transformed_df = None
        st.session_state.last_uploaded_name = source_label
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
elif use_sample:
    source_label = "sample_consulting_data"
    if st.session_state.last_uploaded_name != source_label:
        st.session_state.ai_transformed_df = None
        st.session_state.last_uploaded_name = source_label
    df = load_sample_consulting_data()

# =============================================================================
# 5. SIDEBAR (Original C.Arch Branding + 12 Excel Controls + API + 14 Playbook)
# =============================================================================
with st.sidebar:
    st.markdown("## 🏛️ C.Arch")
    st.caption("Consulting Architecture & People Analytics")

    mode_toggle = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if mode_toggle != st.session_state.dark_mode:
        st.session_state.dark_mode = mode_toggle
        st.rerun()

    if st.session_state.ai_transformed_df is not None:
        if st.button("🔄 Reset AI Transformations", use_container_width=True):
            st.session_state.ai_transformed_df = None
            st.rerun()

    st.divider()

    # --- A. DATA HYGIENE & 12 EXCEL CONTROLS ---
    st.markdown("### 🧹 Data Hygiene")
    st.caption("Standardize raw exports before analysis.")

    ctrl_dedup = st.checkbox("1. Remove duplicate rows", value=False)
    ctrl_trim = st.checkbox("2. Trim spaces & standardize casing", value=False)
    ctrl_drop_na = st.checkbox("3. Drop rows with missing values", value=False)

    with st.expander("⚙️ More Excel Controls (4–12)", expanded=False):
        ctrl_title = st.checkbox("4. Title Case text (Excel PROPER)", value=False)
        ctrl_drop_empty_cols = st.checkbox("5. Drop >80% empty columns", value=False)
        ctrl_fill_num = st.selectbox(
            "6. Fill blank numbers with:",
            ["Leave blank (NaN)", "0 (Zero)", "Column Median", "Column Mean"]
        )
        ctrl_fill_txt = st.checkbox("7. Fill blank text with 'N/A'", value=False)
        ctrl_dates = st.checkbox("8. Format date columns (YYYY-MM-DD)", value=False)
        ctrl_abs_num = st.checkbox("9. Force negative numbers positive (ABS)", value=False)
        ctrl_round = st.checkbox("10. Round decimals to 2 places", value=False)
        ctrl_row_id = st.checkbox("11. Insert 'Row_ID' index (1, 2, 3...)", value=False)
        sort_col = st.selectbox("12. Sort dataset by:", ["(Original Order)"] + (list(df.columns) if df is not None else []))
        sort_asc = st.radio("Sort direction:", ["Ascending (A→Z)", "Descending (Z→A)"], horizontal=True)

    st.divider()

    # --- B. AI CO-PILOT (Hosted Secrets + Optional Override) ---
    st.markdown("### 🤖 AI Co-Pilot")
    default_api_key = ""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            default_api_key = st.secrets["GEMINI_API_KEY"]
    except FileNotFoundError:
        default_api_key = os.getenv("GEMINI_API_KEY", "")

    if default_api_key:
        api_key = default_api_key
        st.success("🔑 Hosted Gemini Engine: Active")
        with st.expander("Override API Key (Optional)", expanded=False):
            custom_key = st.text_input("Custom Gemini API Key", type="password")
            if custom_key:
                api_key = custom_key
    else:
        st.caption("Connect your Google AI Studio key.")
        api_key = st.text_input("Gemini API Key", type="password")

    st.divider()

    # --- C. 14-SCENARIO EXCEL & CONSULTING PROMPT PLAYBOOK ---
    st.markdown("### 📘 Consulting Prompt Playbook")
    st.caption("Load everyday Excel & consulting workflows:")

    EXCEL_PLAYBOOK = {
        "— Select a Scenario —": "",
        "1. Conditional Tiering (Nested IF)": (
            "Create a new column 'Performance_Tier' based on the primary numeric column: "
            "label the top 25% as 'High', middle 50% as 'Moderate', and bottom 25% as 'Low'."
        ),
        "2. Group Totals & % Share (SUMIFS)": (
            "Calculate group totals by the first category column and add a 'Pct_of_Group_Total' "
            "column showing each row's percentage contribution to its group."
        ),
        "3. Category Frequency Count (COUNTIFS)": (
            "Add a column 'Category_Frequency' showing how many times each value in the primary "
            "text/category column appears across the dataset."
        ),
        "4. Variance & % Delta (Target vs. Actual)": (
            "Identify the two main numeric comparison columns (such as target vs actual), compute "
            "'Variance_Abs' (Actual - Target) and 'Variance_Pct', and flag rows >10% off target."
        ),
        "5. Flag Duplicate IDs Without Deleting": (
            "Do not delete rows. Create a boolean column 'Is_Duplicate_Entry' marking True "
            "for any repeated records based on the first ID or name column."
        ),
        "6. Split Full Name / Email Domain": (
            "If there is a full name or email column, split it into clean separate columns "
            "(e.g., 'First_Name' and 'Last_Name', or 'Email_User' and 'Email_Domain')."
        ),
        "7. Date Aging & Buckets (TODAY)": (
            "Find the primary date column, calculate 'Days_Elapsed' from that date to today, "
            "and bucket rows into '0-30 Days', '31-90 Days', and '90+ Days'."
        ),
        "8. Top 15 Rank & Filter (RANK)": (
            "Create a 'Rank_Order' column ranking rows from highest to lowest on the primary "
            "numeric metric, and keep only the Top 15 rows."
        ),
        "9. Outlier & Anomaly Audit (Z-Score)": (
            "Compute Z-scores for numeric columns and add an 'Outlier_Alert' column flagging "
            "'Review Required' wherever any metric exceeds 2.5 standard deviations from the mean."
        ),
        "10. Executive 0-100 Composite Index": (
            "Normalize the primary numeric columns onto a 0-to-100 scale and create an average "
            "'Composite_Index_Score' column rounded to 1 decimal place."
        ),
        "11. Multi-Criteria Above-Average Filter": (
            "Filter the dataset to keep only complete rows where the primary numeric metric is "
            "above the column average, then sort from highest to lowest."
        ),
        "12. Text Keyword Priority Tagging": (
            "Scan text columns for urgent, risk, high, or priority keywords and create a 'Priority_Tag' "
            "column labeling matching rows as 'Action Needed' and others as 'Standard'."
        ),
        "13. Survey / Likert Scoring & Straightlining": (
            "Compute row-wise mean and standard deviation across numeric survey items into 'Scale_Mean' "
            "and 'Scale_SD', and flag 'Straightline_Response' as True where Scale_SD == 0."
        ),
        "14. Executive Column Reorder for Export": (
            "Move ID and categorical columns to the front, numeric metrics to the middle, "
            "and calculated flags/scores to the end, removing any all-blank rows."
        ),
    }

    chosen_template = st.selectbox("Choose Workflow:", list(EXCEL_PLAYBOOK.keys()))
    if st.button("📥 Load Prompt into Box", use_container_width=True):
        if EXCEL_PLAYBOOK[chosen_template]:
            st.session_state.active_ai_prompt = EXCEL_PLAYBOOK[chosen_template]
            st.toast(f"Loaded: {chosen_template}")

# =============================================================================
# 6. MAIN WORKSPACE (Exact Original C.Arch Layout + Upgraded Tabs & Info Guides)
# =============================================================================
if df is not None:
    if st.session_state.ai_transformed_df is not None:
        df = st.session_state.ai_transformed_df.copy()

    # Apply the 12 Sidebar Hygiene & Excel Controls
    if ctrl_dedup:
        df = df.drop_duplicates()
    if ctrl_trim:
        for col in df.select_dtypes(include=["object", "string"]).columns:
            df[col] = df[col].astype(str).str.strip().str.title().replace({"Nan": np.nan, "None": np.nan})
    if ctrl_title:
        for col in df.select_dtypes(include=["object", "string"]).columns:
            df[col] = df[col].apply(lambda x: x.title() if isinstance(x, str) else x)
    if ctrl_drop_empty_cols:
        thresh = int(len(df) * 0.20)
        df = df.dropna(axis=1, thresh=max(1, thresh))
    if ctrl_drop_na:
        df = df.dropna()
    if ctrl_fill_num != "Leave blank (NaN)":
        for col in df.select_dtypes(include=[np.number]).columns:
            if ctrl_fill_num == "0 (Zero)":
                df[col] = df[col].fillna(0)
            elif ctrl_fill_num == "Column Median":
                df[col] = df[col].fillna(df[col].median())
            elif ctrl_fill_num == "Column Mean":
                df[col] = df[col].fillna(df[col].mean())
    if ctrl_fill_txt:
        txt_cols_clean = df.select_dtypes(include=["object", "string"]).columns
        df[txt_cols_clean] = df[txt_cols_clean].fillna("N/A")
    if ctrl_dates:
        for col in df.columns:
            if "date" in col.lower() or "time" in col.lower():
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().sum() > 0:
                    df[col] = parsed.dt.strftime("%Y-%m-%d")
    if ctrl_abs_num:
        num_cols_clean = df.select_dtypes(include=[np.number]).columns
        df[num_cols_clean] = df[num_cols_clean].abs()
    if ctrl_round:
        num_cols_clean = df.select_dtypes(include=[np.number]).columns
        df[num_cols_clean] = df[num_cols_clean].round(2)
    if sort_col != "(Original Order)" and sort_col in df.columns:
        df = df.sort_values(by=sort_col, ascending=("Ascending" in sort_asc))
    if ctrl_row_id:
        df = df.reset_index(drop=True)
        if "Row_ID" in df.columns:
            df = df.drop(columns=["Row_ID"])
        df.insert(0, "Row_ID", range(1, len(df) + 1))

    # -------------------------------------------------------------------------
    # SECTION 1: DATA HEALTH OVERVIEW + INFO POPOVER
    # -------------------------------------------------------------------------
    h1_col, h1_info = st.columns([6, 1])
    with h1_col:
        st.subheader("1. Data Health Overview")
    with h1_info:
        with st.popover("ℹ️ Info"):
            st.markdown("""
            **Executive Data Audit:**
            - **Total Records & Variables:** Dimensions of your active table (`rows × columns`).
            - **Duplicate Rows:** Exact repeated rows that distort means and counts.
            - **Missing Cells:** Total `NaN` / empty cells across the entire dataset.
            """)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", f"{df.shape[0]:,}")
    c2.metric("Variables", df.shape[1])
    c3.metric("Duplicate Rows", int(df.duplicated().sum()))
    c4.metric("Missing Cells", int(df.isna().sum().sum()))

    st.write("")

    # -------------------------------------------------------------------------
    # SECTION 2: AI DATA INSTRUCTION BOX + PROMPT TIPS POPOVER
    # -------------------------------------------------------------------------
    h2_col, h2_info = st.columns([6, 1])
    with h2_col:
        st.subheader("2. AI Data Instruction Box")
    with h2_info:
        with st.popover("ℹ️ Prompt Tips"):
            st.markdown("""
            **Example Multi-Task Instructions:**
            - *"Sort rows by Engagement_Score descending"*
            - *"Filter rows where Attrition_Risk > 3.0"*
            - *"Create a Risk_Tier column labeled 'High' if Attrition_Risk >= 3.5 else 'Normal'"*
            - *"Compute Variance_Abs and Variance_Pct between Target_Revenue and Actual_Revenue"*
            """)

    instruction = st.text_area(
        "Enter a plain-English transformation or filtering rule (or load a template from the sidebar):",
        value=st.session_state.active_ai_prompt,
        height=85,
        placeholder="e.g., Filter rows where Attrition_Risk > 3.0 and sort by Engagement_Score descending"
    )

    run_ai = st.button("⚡ Execute AI Transformation", type="primary")

    if run_ai and instruction:
        if not api_key:
            st.warning("Open the left sidebar and connect your Gemini API key to activate AI transformations.")
        else:
            with st.spinner("Generating audit-ready pandas transformation..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
You are a senior data analyst writing Python pandas code.
Given a DataFrame named `df` with columns and dtypes:
{df.dtypes.to_dict()}

And sample rows:
{df.head(3).to_dict(orient="records")}

User instruction:
"{instruction}"

Return ONLY valid, executable Python code that modifies `df` in-place or reassigns `df`.
Do not include markdown backticks, explanations, or print statements. `pd` and `np` are already imported.
"""
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    generated_code = (
                        response.text.strip()
                        .removeprefix("```python")
                        .removeprefix("```")
                        .removesuffix("```")
                        .strip()
                    )
                    local_vars = {"df": df.copy(), "pd": pd, "np": np}
                    exec(generated_code, {}, local_vars)
                    df = local_vars["df"]
                    st.session_state.ai_transformed_df = df.copy()
                    st.success("✅ AI Transformation applied successfully!")
                    with st.expander("🔍 View Executed Audit Code", expanded=False):
                        st.code(generated_code, language="python")
                except Exception as e:
                    st.error(f"Transformation error: {e}")

    st.write("")

    # -------------------------------------------------------------------------
    # SECTION 3: CLEAN TABBED WORKSPACE (With Dedicated Info Popovers per Tab)
    # -------------------------------------------------------------------------
    tab_work, tab_piv, tab_seg, tab_corr, tab_calc, tab_docs = st.tabs([
        "📋 Working Dataset",
        "📊 Recommended Pivot Tables",
        "📈 Group Segmentation",
        "🧠 Behavioral Correlation Matrix",
        "🧮 Formula Builder",
        "📘 User Guide & Documentation",
    ])

    pivot_df = None
    cat_cols = [c for c in df.select_dtypes(include=["object", "string", "category"]).columns if 1 < df[c].nunique() <= 50]
    num_cols = list(df.select_dtypes(include=[np.number]).columns)

    # TAB 1: WORKING DATASET
    with tab_work:
        w_top, w_info = st.columns([6, 1])
        with w_top:
            st.caption("Live table reflecting all active sidebar hygiene rules, AI commands, and Formula Builder columns.")
        with w_info:
            with st.popover("ℹ️ Info"):
                st.markdown("""
                **Working Dataset — How It Works:**
                - **Live Pipeline:** Updates automatically whenever you toggle sidebar cleaning rules, execute an AI instruction, or apply a Formula Builder column.
                - **Zero-Typo Schema Check:** Expand *Column Dictionary* below to inspect exact column names and data types before writing prompts.
                - **Quick Search:** Filter rows visually without altering your exported dataset.
                """)

        q_col1, q_col2 = st.columns([2.5, 1.5])
        with q_col1:
            search_query = st.text_input("🔍 Quick Search / Filter Rows (Visual Preview):", placeholder="Type any keyword, category, or ID to filter view...")
        with q_col2:
            st.write("")
            show_schema = st.checkbox("📑 Show Column Dictionary", value=False)

        if show_schema:
            schema_df = pd.DataFrame({
                "Column Name": df.columns,
                "Type": ["Numeric" if pd.api.types.is_numeric_dtype(df[c]) else "Text / Category" for c in df.columns],
                "Unique Values": [df[c].nunique() for c in df.columns],
                "Missing Cells": [int(df[c].isna().sum()) for c in df.columns],
            })
            st.dataframe(schema_df, use_container_width=True, hide_index=True)

        display_df = df
        if search_query:
            mask = df.astype(str).apply(lambda col: col.str.contains(search_query, case=False, na=False)).any(axis=1)
            display_df = df[mask]
            st.caption(f"Showing {len(display_df)} matching rows out of {len(df)} total records.")

        st.dataframe(display_df, use_container_width=True, height=340)

    # TAB 2: RECOMMENDED PIVOT TABLES
    with tab_piv:
        p_top, p_info = st.columns([6, 1])
        with p_top:
            st.caption("Instant executive summaries and cross-tabulations modeled after Excel PivotTables.")
        with p_info:
            with st.popover("ℹ️ Info"):
                st.markdown("""
                **Recommended Pivot Tables — How It Works:**
                - **Smart Auto-Detection:** C.Arch automatically pairs your primary category and metric columns into ready-made executive pivots.
                - **`% of Total` Share:** Automatically calculated on single-dimension `sum` and `count` pivots for rapid Pareto / contribution analysis.
                - **Workbook Sync:** Whatever Pivot Table is active here is automatically saved into the **`Pivot_Summary`** tab when you click **Export Multi-Sheet Excel (.xlsx)**.
                """)

        if cat_cols and num_cols:
            recommendations = [
                f"Recommended 1: Total {num_cols[0]} by {cat_cols[0]} (with % of Total)",
                f"Recommended 2: Average {num_cols[0]} by {cat_cols[0]}",
            ]
            if len(cat_cols) >= 2:
                recommendations.append(f"Recommended 3: Cross-Tab Matrix — {cat_cols[0]} × {cat_cols[1]} ({num_cols[0]})")
            recommendations.append("Custom Pivot Builder (Choose your own rows, columns & aggregation)")

            selected_pivot = st.selectbox("Select a Recommended Pivot View:", recommendations)

            if selected_pivot.startswith("Recommended 1"):
                p_row, p_col, p_val, p_agg = cat_cols[0], None, num_cols[0], "sum"
            elif selected_pivot.startswith("Recommended 2"):
                p_row, p_col, p_val, p_agg = cat_cols[0], None, num_cols[0], "mean"
            elif selected_pivot.startswith("Recommended 3"):
                p_row, p_col, p_val, p_agg = cat_cols[0], cat_cols[1], num_cols[0], "sum"
            else:
                pc1, pc2, pc3, pc4 = st.columns(4)
                p_row = pc1.selectbox("Rows (Group By):", cat_cols, key="piv_row")
                p_col_choice = pc2.selectbox("Columns (Optional Split):", ["(None)"] + [c for c in cat_cols if c != p_row], key="piv_col")
                p_col = None if p_col_choice == "(None)" else p_col_choice
                p_val = pc3.selectbox("Values (Metric):", num_cols, key="piv_val")
                p_agg = pc4.selectbox("Aggregation:", ["sum", "mean", "count", "median", "max", "min"], key="piv_agg")

            try:
                pivot_df = pd.pivot_table(
                    df, index=p_row, columns=p_col, values=p_val, aggfunc=p_agg, fill_value=0
                ).round(2)
                if p_col is None and p_agg in ["sum", "count"] and p_val in pivot_df.columns:
                    total_sum = pivot_df[p_val].sum()
                    if total_sum != 0:
                        pivot_df["% of Total"] = ((pivot_df[p_val] / total_sum) * 100).round(2)
                pivot_df = pivot_df.reset_index()
                st.dataframe(pivot_df, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not generate pivot table: {e}")
        else:
            st.info("Upload a dataset with at least one categorical column and one numeric column to generate Pivot Tables.")

    # TAB 3: GROUP SEGMENTATION
    with tab_seg:
        s_top, s_info = st.columns([6, 1])
        with s_top:
            st.caption("Multi-metric breakdown (`Count`, `Mean`, and `Sum`) across every numeric variable simultaneously.")
        with s_info:
            with st.popover("ℹ️ Info"):
                st.markdown("""
                **Group Segmentation — How It Works:**
                - **All-Metric View:** Unlike a single Pivot Table, Group Segmentation evaluates *every* numeric column simultaneously across your chosen category.
                - **Consulting Tip:** Always check **`count`** alongside **`mean`** and **`sum`** so small sample groups are not mistaken for systemic trends.
                """)

        if cat_cols and num_cols:
            seg_col = st.selectbox("Segment Dataset By:", cat_cols, key="seg_col")
            seg_summary = df.groupby(seg_col)[num_cols].agg(["count", "mean", "sum"]).round(2)
            seg_summary.columns = [f"{col}_{stat}" for col, stat in seg_summary.columns]
            st.dataframe(seg_summary.reset_index(), use_container_width=True)
        else:
            st.info("Requires at least one categorical and one numeric variable.")

    # TAB 4: BEHAVIORAL CORRELATION MATRIX
    with tab_corr:
        c_top, c_info = st.columns([6, 1])
        with c_top:
            st.caption("Pearson correlation matrix measuring linear relationships across numeric variables.")
        with c_info:
            with st.popover("ℹ️ Info"):
                st.markdown("""
                **Behavioral Correlation Matrix — How It Works:**
                - **`+0.70 to +1.00`:** Strong positive relationship (both metrics move up together).
                - **`-0.70 to -1.00`:** Strong inverse relationship (as one rises, the other falls).
                - **`-0.20 to +0.20`:** Little to no linear relationship.
                - **Auto-Insights:** C.Arch automatically extracts the strongest variable pairs below the matrix to save scanning time.
                """)

        if len(num_cols) >= 2:
            corr_matrix = df[num_cols].corr().round(3)
            st.dataframe(corr_matrix, use_container_width=True)

            # Auto-surface Top Strongest Correlations to reduce cognitive load
            corr_pairs = (
                corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
                .stack()
                .reset_index()
            )
            corr_pairs.columns = ["Variable A", "Variable B", "Pearson r"]
            corr_pairs["Abs_r"] = corr_pairs["Pearson r"].abs()
            top_pairs = corr_pairs.sort_values("Abs_r", ascending=False).head(3)
            if not top_pairs.empty:
                st.markdown("**⚡ Key Correlation Takeaways (Auto-Detected):**")
                for _, row in top_pairs.iterrows():
                    direction = "positively" if row["Pearson r"] >= 0 else "inversely"
                    st.write(f"- **{row['Variable A']}** and **{row['Variable B']}** are {direction} correlated (`r = {row['Pearson r']}`).")
        else:
            st.info("Requires at least two numeric variables to compute correlations.")

    # TAB 5: NO-CODE EXCEL FORMULA & CONDITIONAL IF BUILDER
    with tab_calc:
        f_top, f_info = st.columns([6, 1])
        with f_top:
            st.caption("Create deterministic Excel-style calculated columns and conditional flags with zero code.")
        with f_info:
            with st.popover("ℹ️ How to Use Formula Builder"):
                st.markdown("""
                **How to Use Formula Builder (3 Steps):**
                1. **Choose Formula Type:** Pick **Two-Column Math** (`+`, `-`, `*`, `/`, `% Delta`) for ratios/variances, or **Conditional IF Flag** (`=IF`) for risk/performance thresholds.
                2. **Configure Inputs & Name:** Select your source column(s), set your operator or numeric threshold, and name your new output column.
                3. **Activate:** Check **Apply Column to Working Dataset**—your new column immediately appears in the **Working Dataset** tab and is included in your final CSV/Excel export.
                """)

        sub_math, sub_if = st.tabs(["Two-Column Math (+, -, *, /, % Delta)", "Conditional IF Flag (=IF)"])
        with sub_math:
            if len(num_cols) >= 2:
                fc1, fc2, fc3, fc4 = st.columns([2, 1.6, 2, 2])
                col_a = fc1.selectbox("Column A", num_cols, key="calc_a")
                op = fc2.selectbox("Operation", ["+ (Add)", "- (Subtract)", "* (Multiply)", "/ (Divide)", "% Change ((B-A)/A)"])
                col_b = fc3.selectbox("Column B", num_cols, index=min(1, len(num_cols) - 1), key="calc_b")
                new_col_name = fc4.text_input("New Column Name", value=f"{col_a}_vs_{col_b}")

                op_symbol = op.split(" ")[0]
                formula_preview = f"=ROUND(({col_b} - {col_a}) / {col_a} * 100, 2)" if op_symbol == "%" else f"={col_a} {op_symbol} {col_b}"
                st.caption(f"Excel Formula Equivalent: `{formula_preview}`")

                if st.checkbox("Apply Math Column to Working Dataset"):
                    if op.startswith("+"):
                        df[new_col_name] = df[col_a] + df[col_b]
                    elif op.startswith("-"):
                        df[new_col_name] = df[col_a] - df[col_b]
                    elif op.startswith("*"):
                        df[new_col_name] = df[col_a] * df[col_b]
                    elif op.startswith("/"):
                        df[new_col_name] = np.where(df[col_b] != 0, df[col_a] / df[col_b], np.nan)
                    elif op.startswith("%"):
                        df[new_col_name] = np.where(df[col_a] != 0, ((df[col_b] - df[col_a]) / df[col_a]) * 100, np.nan).round(2)
                    st.success(f"✅ Column `{new_col_name}` added to Working Dataset!")
            else:
                st.info("Requires at least 2 numeric columns.")

        with sub_if:
            if len(num_cols) >= 1:
                ic1, ic2, ic3, ic4, ic5 = st.columns([2, 1.2, 1.5, 1.8, 1.8])
                if_col = ic1.selectbox("Target Metric", num_cols, key="if_col")
                if_op = ic2.selectbox("Condition", [">", ">=", "<", "<=", "=="], key="if_op")
                if_val = ic3.number_input("Threshold", value=float(df[if_col].median()) if df[if_col].notna().any() else 0.0)
                true_lbl = ic4.text_input("If True Label", value="High / Flagged")
                false_lbl = ic5.text_input("If False Label", value="Normal")
                if_out_name = st.text_input("Output Flag Column Name", value=f"{if_col}_Status")

                st.caption(f'Excel Formula Equivalent: `=IF({if_col} {if_op} {if_val}, "{true_lbl}", "{false_lbl}")`')

                if st.checkbox("Apply Conditional IF Column to Working Dataset"):
                    if if_op == ">":
                        cond = df[if_col] > if_val
                    elif if_op == ">=":
                        cond = df[if_col] >= if_val
                    elif if_op == "<":
                        cond = df[if_col] < if_val
                    elif if_op == "<=":
                        cond = df[if_col] <= if_val
                    else:
                        cond = df[if_col] == if_val
                    df[if_out_name] = np.where(cond, true_lbl, false_lbl)
                    st.success(f"✅ Flag column `{if_out_name}` added to Working Dataset!")
            else:
                st.info("Requires at least 1 numeric column.")

    # TAB 6: USER GUIDE & DOCUMENTATION
    with tab_docs:
        st.markdown("""
        ### 🏛️ C.Arch Platform Manual — Fast-Track Workflow
        1. **Step 1 — Ingest & Audit:** Upload any CSV or Excel workbook at the top (or test with the built-in consulting dataset) and verify record counts, duplicates, and missing cells in **1. Data Health Overview**.
        2. **Step 2 — Deterministic Hygiene (Left Sidebar):** Apply any of the **12 Quick Excel Controls** (`TRIM`, `PROPER`, deduplication, median/zero imputation, ISO dates, `Row_ID`, sorting) to standardize your data cleanly.
        3. **Step 3 — AI Co-Pilot or No-Code Formulas:** Either pick one of the **14 Consulting Prompt Playbook** templates in the sidebar to run multi-step AI transformations, or use the **Formula Builder** tab for instant deterministic Excel math and `=IF` flags.
        4. **Step 4 — Pivot & Behavioral Diagnostics:** Inspect auto-generated summaries in **Recommended Pivot Tables**, multi-metric breakdowns in **Group Segmentation**, and key drivers in **Behavioral Correlation Matrix**.
        5. **Step 5 — Executive Deliverable Export:** Click **Export Deliverable (CSV)** for flat tables or **Export Multi-Sheet Excel (.xlsx)** to download a complete workbook containing `Cleaned_Data`, `Pivot_Summary`, and `Summary_Stats`.
        """)

    st.write("")

    # -------------------------------------------------------------------------
    # SECTION 4: EMERALD GREEN EXPORT BUTTONS (CSV + MULTI-SHEET EXCEL)
    # -------------------------------------------------------------------------
    exp_col1, exp_col2, _ = st.columns([1.4, 1.6, 3])

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    exp_col1.download_button(
        label="⬇️ Export Deliverable (CSV)",
        data=csv_bytes,
        file_name="CArch_Deliverable.csv",
        mime="text/csv",
        use_container_width=True,
    )

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Cleaned_Data", index=False)
        if pivot_df is not None:
            pivot_df.to_excel(writer, sheet_name="Pivot_Summary", index=False)
        df.describe().round(2).to_excel(writer, sheet_name="Summary_Stats")
    excel_buffer.seek(0)

    exp_col2.download_button(
        label="📊 Export Multi-Sheet Excel (.xlsx)",
        data=excel_buffer,
        file_name="CArch_Executive_Workbook.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
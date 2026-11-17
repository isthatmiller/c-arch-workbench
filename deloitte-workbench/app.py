import io
import os
import numpy as np
import pandas as pd
import streamlit as st
from google import genai

# =============================================================================
# 1. PAGE CONFIGURATION (Glitch-Free Native Expanded Sidebar)
# =============================================================================
st.set_page_config(
    page_title="C.Arch | Consulting Architecture Workbench",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean, lightweight styling that never interferes with Streamlit's sidebar toggle
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 12px 16px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. SAMPLE DATASET GENERATOR (For Instant 1-Click Recruiter / User Testing)
# =============================================================================
@st.cache_data
def load_sample_consulting_data() -> pd.DataFrame:
    np.random.seed(42)
    n = 60
    departments = ["Strategy & Ops", "People Analytics", "Commercial", "Technology", "Finance"]
    regions = ["Nairobi", "London", "New York", "Singapore"]
    df_sample = pd.DataFrame({
        "Employee_ID": [f"EMP-{1000 + i}" for i in range(n)],
        "Department": np.random.choice(departments, n),
        "Region": np.random.choice(regions, n),
        "Tenure_Months": np.random.randint(3, 72, n),
        "Target_Revenue_USD": np.random.randint(40000, 120000, n),
        "Actual_Revenue_USD": np.random.randint(32000, 135000, n),
        "Engagement_Score": np.round(np.random.uniform(2.1, 5.0, n), 2),
        "Attrition_Risk": np.round(np.random.uniform(1.0, 4.9, n), 2),
        "Review_Date": pd.date_range("2026-01-10", periods=n, freq="3D").strftime("%Y-%m-%d"),
    })
    # Inject a couple of realistic anomalies/blanks to showcase hygiene controls
    df_sample.loc[2, "Department"] = "  strategy & ops  "
    df_sample.loc[5, "Engagement_Score"] = np.nan
    df_sample = pd.concat([df_sample, df_sample.iloc[[0]]], ignore_index=True)
    return df_sample

# =============================================================================
# 3. HEADER & DATA INGESTION
# =============================================================================
st.title("📊 C.Arch | Consulting Architecture Workbench")
st.caption("Executive Data Hygiene, Excel-Grade Pivot Modeling & AI-Powered Transformation Engine")

if "active_ai_prompt" not in st.session_state:
    st.session_state.active_ai_prompt = ""
if "ai_transformed_df" not in st.session_state:
    st.session_state.ai_transformed_df = None
if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

up_col1, up_col2 = st.columns([3, 1])
with up_col1:
    uploaded_file = st.file_uploader(
        "Upload your raw dataset (CSV or Excel .xlsx):",
        type=["csv", "xlsx", "xls"]
    )
with up_col2:
    st.write("")
    st.write("")
    use_sample = st.checkbox("🧪 Use Sample Consulting Dataset", value=(uploaded_file is None))

df = None
source_label = None

if uploaded_file is not None:
    source_label = uploaded_file.name
    if st.session_state.last_uploaded_name != source_label:
        st.session_state.ai_transformed_df = None
        st.session_state.last_uploaded_name = source_label
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
elif use_sample:
    source_label = "sample_consulting_data"
    if st.session_state.last_uploaded_name != source_label:
        st.session_state.ai_transformed_df = None
        st.session_state.last_uploaded_name = source_label
    df = load_sample_consulting_data()

# =============================================================================
# 4. MAIN WORKBENCH (When Dataset Is Loaded)
# =============================================================================
if df is not None:
    # Start from AI-transformed snapshot if user already executed an AI command
    if st.session_state.ai_transformed_df is not None:
        df = st.session_state.ai_transformed_df.copy()

    # -------------------------------------------------------------------------
    # SIDEBAR CONTROL CENTER (12 Excel Controls + API + 14-Template Playbook)
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("## 🛠️ C.Arch Control Center")
        st.caption("Use the native **×** or **>** button above to collapse or reopen anytime.")

        if st.session_state.ai_transformed_df is not None:
            if st.button("🔄 Reset Dataset to Original Upload", use_container_width=True):
                st.session_state.ai_transformed_df = None
                st.rerun()

        # --- A. HOSTED GEMINI API CONNECTION ---
        with st.expander("🔑 AI Engine Connection", expanded=False):
            default_api_key = ""
            try:
                if "GEMINI_API_KEY" in st.secrets:
                    default_api_key = st.secrets["GEMINI_API_KEY"]
            except FileNotFoundError:
                default_api_key = os.getenv("GEMINI_API_KEY", "")

            if default_api_key:
                api_key = default_api_key
                st.success("Hosted Gemini Engine: Active")
                custom_key = st.text_input("Override API Key (Optional)", type="password")
                if custom_key:
                    api_key = custom_key
            else:
                st.info("Set GEMINI_API_KEY in Secrets or paste below:")
                api_key = st.text_input("Gemini API Key", type="password")

        st.divider()

        # --- B. 12 ONE-CLICK EXCEL & DATA HYGIENE CONTROLS ---
        st.markdown("### 🧹 12 Quick Excel Controls")
        st.caption("Deterministic cleaning applied live before export:")

        ctrl_dedup = st.checkbox("1. Remove exact duplicate rows", value=False)
        ctrl_trim = st.checkbox("2. Trim extra spaces (Excel TRIM)", value=True)
        ctrl_title = st.checkbox("3. Standardize text to Title Case (PROPER)", value=False)
        ctrl_drop_empty_cols = st.checkbox("4. Drop mostly empty columns (>80% blank)", value=False)
        ctrl_drop_na = st.checkbox("5. Drop rows with any blank cells", value=False)
        ctrl_fill_num = st.selectbox(
            "6. Fill blank numbers with:",
            ["Leave blank (NaN)", "0 (Zero)", "Column Median", "Column Mean"]
        )
        ctrl_fill_txt = st.checkbox("7. Fill blank text cells with 'N/A'", value=False)
        ctrl_dates = st.checkbox("8. Format date columns (YYYY-MM-DD)", value=False)
        ctrl_abs_num = st.checkbox("9. Force negative numbers positive (ABS)", value=False)
        ctrl_round = st.checkbox("10. Round decimals to 2 places", value=False)
        ctrl_row_id = st.checkbox("11. Insert 'Row_ID' index column (1, 2, 3...)", value=False)

        sort_col = st.selectbox("12. Sort dataset by column:", ["(Original Order)"] + list(df.columns))
        sort_asc = st.radio("Sort order:", ["Ascending (A→Z / 0→9)", "Descending (Z→A / 9→0)"], horizontal=True)

        # Execute the 12 deterministic Excel controls
        if ctrl_dedup:
            df = df.drop_duplicates()
        if ctrl_trim:
            for col in df.select_dtypes(include=["object", "string"]).columns:
                df[col] = df[col].astype(str).str.strip().replace({"nan": np.nan, "None": np.nan})
        if ctrl_title:
            for col in df.select_dtypes(include=["object", "string"]).columns:
                df[col] = df[col].apply(lambda x: x.title() if isinstance(x, str) else x)
        if ctrl_drop_empty_cols:
            thresh = int(len(df) * 0.20)
            df = df.dropna(axis=1, thresh=max(1, thresh))
        if ctrl_drop_na:
            df = df.dropna()
        if ctrl_fill_num != "Leave blank (NaN)":
            num_cols_clean = df.select_dtypes(include=[np.number]).columns
            for col in num_cols_clean:
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

        st.divider()

        # --- C. 14-TEMPLATE EXCEL & CONSULTING PROMPT PLAYBOOK ---
        st.markdown("### 📘 Excel & Consulting Playbook")
        st.caption("Select any everyday Excel workflow to load into the AI Command Box:")

        EXCEL_PLAYBOOK = {
            "— Select a Template —": "",
            "1. Conditional Tiering (Excel Nested IF)": (
                "Create a new column 'Performance_Tier' based on the primary numeric column: "
                "label the top 25% as 'High', middle 50% as 'Moderate', and bottom 25% as 'Low'."
            ),
            "2. Group Totals & % Share (Excel SUMIFS)": (
                "Calculate group totals by the first category column and add a 'Pct_of_Group_Total' "
                "column showing each row's percentage share of its group total."
            ),
            "3. Category Frequency Count (Excel COUNTIFS)": (
                "Add a column 'Category_Frequency' showing how many times each value in the primary "
                "text/category column appears across the dataset."
            ),
            "4. Variance & % Delta (Budget vs. Actual)": (
                "Identify the two main numeric comparison columns (such as target vs actual), compute "
                "'Variance_Abs' (Actual - Target) and 'Variance_Pct', and flag rows >10% off target."
            ),
            "5. Flag Duplicate IDs Without Deleting": (
                "Do not delete rows. Create a boolean column 'Is_Duplicate_Entry' that marks True "
                "for any repeated records based on the first ID or name column."
            ),
            "6. Split Full Name / Email Domain (Text-to-Columns)": (
                "If there is a full name or email column, split it into clean separate columns "
                "(e.g., 'First_Name' and 'Last_Name', or 'Email_User' and 'Email_Domain')."
            ),
            "7. Date Aging & Buckets (Excel TODAY)": (
                "Find the primary date column, calculate 'Days_Elapsed' from that date to today, "
                "and bucket rows into '0-30 Days', '31-90 Days', and '90+ Days'."
            ),
            "8. Top 15 Rank & Filter (Excel RANK)": (
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
            "12. Text Keyword Priority Tagging (Excel SEARCH/IF)": (
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

        chosen_template = st.selectbox("Choose an Excel / Consulting Workflow:", list(EXCEL_PLAYBOOK.keys()))
        if st.button("📥 Load Prompt into Workbench", use_container_width=True):
            if EXCEL_PLAYBOOK[chosen_template]:
                st.session_state.active_ai_prompt = EXCEL_PLAYBOOK[chosen_template]
                st.toast(f"Loaded: {chosen_template}")

    # -------------------------------------------------------------------------
    # SECTION 1: EXECUTIVE DATA HEALTH OVERVIEW
    # -------------------------------------------------------------------------
    st.subheader("1. Data Health Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", f"{df.shape[0]:,}")
    c2.metric("Variables", df.shape[1])
    c3.metric("Duplicate Rows", int(df.duplicated().sum()))
    c4.metric("Missing Cells", int(df.isna().sum().sum()))

    st.divider()

    # -------------------------------------------------------------------------
    # SECTION 2: AI DATA INSTRUCTION BOX
    # -------------------------------------------------------------------------
    st.subheader("2. AI Data Instruction Box")
    instruction = st.text_area(
        "Enter a plain-English or multi-step command (or load any of the 14 Excel templates from the left sidebar):",
        value=st.session_state.active_ai_prompt,
        height=105,
        placeholder="e.g., Calculate variance between Target_Revenue_USD and Actual_Revenue_USD, create a Performance_Tier column, and sort descending..."
    )

    run_ai = st.button("⚡ Execute AI Transformation", type="primary")

    if run_ai and instruction:
        if not api_key:
            st.warning("Open the left sidebar (**>**) and configure your Gemini API key to activate AI transformations.")
        else:
            with st.spinner("Generating audit-ready pandas transformation..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
You are a senior management consultant and Python pandas engineer.
Given a DataFrame named `df` with columns and dtypes:
{df.dtypes.to_dict()}

Sample rows:
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

    st.divider()

    # -------------------------------------------------------------------------
    # SECTION 3: NO-CODE EXCEL FORMULA & CONDITIONAL IF BUILDER
    # -------------------------------------------------------------------------
    with st.expander("🧮 3. Quick Excel Formula Builder (No-Code Calculated Columns)", expanded=False):
        st.caption("Create instant deterministic columns without writing code or prompts:")
        num_cols = list(df.select_dtypes(include=[np.number]).columns)

        tab_math, tab_if = st.tabs(["Two-Column Math (+, -, *, /, % Delta)", "Conditional IF Flag (=IF)"])

        with tab_math:
            if len(num_cols) >= 2:
                fc1, fc2, fc3, fc4 = st.columns([2, 1.6, 2, 2])
                col_a = fc1.selectbox("Column A", num_cols, key="calc_a")
                op = fc2.selectbox("Operation", ["+ (Add)", "- (Subtract)", "* (Multiply)", "/ (Divide)", "% Change ((B-A)/A)"])
                col_b = fc3.selectbox("Column B", num_cols, index=min(1, len(num_cols) - 1), key="calc_b")
                new_col_name = fc4.text_input("New Column Name", value=f"{col_a}_vs_{col_b}")

                if st.checkbox("Apply Math Column to Table"):
                    if op.startswith("+"):
                        df[new_col_name] = df[col_a] + df[col_b]
                    elif op.startswith("-"):
                        df[new_col_name] = df[col_a] - df[col_b]
                    elif op.startswith("*"):
                        df[new_col_name] = df[col_a] * df[col_b]
                    elif op.startswith("/"):
                        df[new_col_name] = np.where(df[col_b] != 0, df[col_a] / df[col_b], np.nan)
                    elif op.startswith("%"):
                        df[new_col_name] = np.where(
                            df[col_a] != 0, ((df[col_b] - df[col_a]) / df[col_a]) * 100, np.nan
                        ).round(2)
            else:
                st.info("Requires at least 2 numeric columns.")

        with tab_if:
            if len(num_cols) >= 1:
                ic1, ic2, ic3, ic4, ic5 = st.columns([2, 1.2, 1.5, 1.8, 1.8])
                if_col = ic1.selectbox("Target Metric", num_cols, key="if_col")
                if_op = ic2.selectbox("Condition", [">", ">=", "<", "<=", "=="], key="if_op")
                if_val = ic3.number_input("Threshold", value=float(df[if_col].median()) if df[if_col].notna().any() else 0.0)
                true_lbl = ic4.text_input("If True Label", value="Flagged / High")
                false_lbl = ic5.text_input("If False Label", value="Normal")
                if_out_name = st.text_input("Output Flag Column Name", value=f"{if_col}_Status")

                if st.checkbox("Apply Conditional IF Column to Table"):
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
            else:
                st.info("Requires at least 1 numeric column.")

    st.divider()

    # -------------------------------------------------------------------------
    # SECTION 4: RECOMMENDED PIVOT TABLES ENGINE
    # -------------------------------------------------------------------------
    st.subheader("4. Recommended Pivot Tables")
    cat_cols = [c for c in df.select_dtypes(include=["object", "string", "category"]).columns if 1 < df[c].nunique() <= 50]
    num_cols = list(df.select_dtypes(include=[np.number]).columns)

    pivot_df = None
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
                df,
                index=p_row,
                columns=p_col,
                values=p_val,
                aggfunc=p_agg,
                fill_value=0,
            ).round(2)

            if p_col is None and p_agg in ["sum", "count"] and p_val in pivot_df.columns:
                total_sum = pivot_df[p_val].sum()
                if total_sum != 0:
                    pivot_df["% of Total"] = ((pivot_df[p_val] / total_sum) * 100).round(2)

            pivot_df = pivot_df.reset_index()
            st.dataframe(pivot_df, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate pivot table with current selection: {e}")
    else:
        st.info("Recommended Pivot Tables appear automatically when your dataset has at least one category column and one numeric column.")

    st.divider()

    # -------------------------------------------------------------------------
    # SECTION 5: LIVE DATA PREVIEW, SUMMARY STATS & MULTI-SHEET EXPORT
    # -------------------------------------------------------------------------
    st.subheader("5. Cleaned Dataset Preview & Executive Export")

    tab_data, tab_stats = st.tabs(["📋 Live Cleaned Table", "📈 Descriptive Statistics Summary"])
    with tab_data:
        st.dataframe(df, use_container_width=True, height=340)
    with tab_stats:
        stats_df = df.describe(include="all").T
        st.dataframe(stats_df, use_container_width=True)

    exp_col1, exp_col2 = st.columns(2)

    # CSV Export
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    exp_col1.download_button(
        label="📄 Download Cleaned CSV",
        data=csv_bytes,
        file_name="CArch_Cleaned_Deliverable.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # Multi-Sheet Excel (.xlsx) Export (Cleaned Data + Pivot Summary + Summary Stats)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Cleaned_Data", index=False)
        if pivot_df is not None:
            pivot_df.to_excel(writer, sheet_name="Pivot_Summary", index=False)
        df.describe().round(2).to_excel(writer, sheet_name="Summary_Stats")
    excel_buffer.seek(0)

    exp_col2.download_button(
        label="📊 Download Multi-Sheet Excel (.xlsx)",
        data=excel_buffer,
        file_name="CArch_Executive_Workbook.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
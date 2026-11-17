import streamlit as st
import pandas as pd
from google import genai

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "collapsed"

st.set_page_config(
    page_title="C.Arch | Consulting Architecture & People Analytics",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state=st.session_state.sidebar_state
)

# High-Contrast Dynamic Color Palette
if st.session_state.dark_mode:
    bg_main = "#0B0F19"
    bg_card = "#111827"
    bg_header = "#1E293B"
    bg_input = "#1E293B"
    text_main = "#F8FAFC"
    text_muted = "#94A3B8"
    border_col = "#273549"
    accent = "#10B981"
    accent_soft = "rgba(16, 185, 129, 0.14)"
else:
    bg_main = "#F8FAFC"
    bg_card = "#FFFFFF"
    bg_header = "#F1F5F9"
    bg_input = "#FFFFFF"
    text_main = "#0F172A"
    text_muted = "#475569"
    border_col = "#CBD5E1"
    accent = "#047857"
    accent_soft = "#ECFDF5"

def render_themed_table(dataframe):
    html_table = dataframe.to_html(classes="carch-table", border=0)
    st.markdown(f'<div class="carch-table-wrap">{html_table}</div>', unsafe_allow_html=True)

# Website-Grade CSS & Typography
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

.stApp {{
    background-color: {bg_main};
    color: {text_main};
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

/* Hide default Streamlit header bar */
header[data-testid="stHeader"] {{
    display: none;
}}

.block-container {{
    padding-top: 1.4rem !important;
    max-width: 100% !important;
}}

/* Integrated Top Navigation Bar Shell */
div[data-testid="stHorizontalBlock"]:first-of-type {{
    background-color: {bg_card};
    border: 1px solid {border_col};
    border-radius: 14px;
    padding: 12px 22px;
    margin-bottom: 22px;
    align-items: center;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}}

.carch-brand {{
    display: flex;
    align-items: center;
    gap: 14px;
}}
.carch-logo {{
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: {text_main};
    letter-spacing: -0.03em;
    line-height: 1;
}}
.carch-logo span {{
    color: {accent};
}}
.carch-sub {{
    font-size: 0.82rem;
    color: {text_muted};
    border-left: 1px solid {border_col};
    padding-left: 14px;
}}
.carch-pill {{
    background-color: {accent_soft};
    color: {accent};
    border: 1px solid {accent};
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 6px 14px;
    border-radius: 999px;
    text-transform: uppercase;
    white-space: nowrap;
    text-align: center;
    display: inline-block;
}}

/* Sidebar Drawer */
section[data-testid="stSidebar"] {{
    background-color: {bg_card};
    border-right: 1px solid {border_col};
}}
section[data-testid="stSidebar"] * {{
    color: {text_main};
}}
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small {{
    color: {text_muted} !important;
}}

/* Headings & Text */
h1, h2, h3, h4, p, label, span, li, strong {{
    color: {text_main};
}}
h1, h2, h3 {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.015em;
}}

/* Elevated KPI Cards */
div[data-testid="stMetric"] {{
    background-color: {bg_card};
    border: 1px solid {border_col};
    border-top: 3px solid {accent};
    padding: 18px 22px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}}
div[data-testid="stMetricLabel"] p {{
    color: {text_muted} !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
div[data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: {text_main} !important;
}}

/* File Uploader, Inputs & Selectboxes */
div[data-testid="stFileUploader"] section {{
    background-color: {bg_card} !important;
    border: 1px dashed {border_col} !important;
    color: {text_main} !important;
}}
div[data-testid="stFileUploader"] button {{
    background-color: {accent_soft} !important;
    color: {accent} !important;
    border: 1px solid {accent} !important;
}}
input[type="text"], input[type="password"], div[data-baseweb="select"] > div {{
    background-color: {bg_input} !important;
    color: {text_main} !important;
    border: 1px solid {border_col} !important;
}}
input::placeholder {{
    color: {text_muted} !important;
    opacity: 0.85 !important;
}}

/* Buttons & Popovers */
div[data-testid="stPopover"] > button,
button[kind="secondary"] {{
    background-color: {bg_card} !important;
    color: {text_main} !important;
    border: 1px solid {border_col} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
div[data-testid="stPopover"] > button:hover,
button[kind="secondary"]:hover {{
    border-color: {accent} !important;
    color: {accent} !important;
}}
div[data-testid="stPopoverBody"],
div[data-testid="stPopoverBody"] > div {{
    background-color: {bg_card} !important;
    color: {text_main} !important;
    border: 1px solid {border_col} !important;
    border-radius: 12px !important;
}}
div[data-testid="stPopoverBody"] p,
div[data-testid="stPopoverBody"] li,
div[data-testid="stPopoverBody"] strong,
div[data-testid="stPopoverBody"] em {{
    color: {text_main} !important;
}}

/* Custom Theme-Aware Table */
.carch-table-wrap {{
    width: 100%;
    overflow-x: auto;
    border: 1px solid {border_col};
    border-radius: 10px;
    background-color: {bg_card};
    margin-bottom: 14px;
}}
table.carch-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    text-align: left;
}}
table.carch-table thead th {{
    background-color: {bg_header};
    color: {text_muted};
    font-weight: 700;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 12px 16px;
    border-bottom: 1px solid {border_col};
}}
table.carch-table tbody th {{
    background-color: {bg_header};
    color: {text_muted};
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    padding: 10px 14px;
    border-bottom: 1px solid {border_col};
    border-right: 1px solid {border_col};
    width: 48px;
}}
table.carch-table tbody td {{
    background-color: {bg_card};
    color: {text_main};
    padding: 10px 16px;
    border-bottom: 1px solid {border_col};
}}
table.carch-table tbody tr:hover td {{
    background-color: {accent_soft};
}}

/* Download Button */
.stDownloadButton button {{
    background-color: {accent} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.1rem;
}}

/* Tabs */
button[data-baseweb="tab"] p {{
    color: {text_muted} !important;
    font-weight: 600 !important;
}}
button[data-baseweb="tab"][aria-selected="true"] p {{
    color: {accent} !important;
}}
</style>
""", unsafe_allow_html=True)

# Top Navigation Bar: [Sidebar Trigger] | [C.Arch Brand] | [Dark Mode Toggle] | [Live Status Pill]
nav_btn, nav_brand, nav_theme, nav_pill = st.columns([0.9, 4.3, 1.1, 1.7], vertical_alignment="center")

with nav_btn:
    btn_label = "✕ Close" if st.session_state.sidebar_state == "expanded" else "☰ Controls"
    if st.button(btn_label, key="sidebar_toggle", use_container_width=True):
        st.session_state.sidebar_state = (
            "collapsed" if st.session_state.sidebar_state == "expanded" else "expanded"
        )
        st.rerun()

with nav_brand:
    st.markdown("""
    <div class="carch-brand">
        <div class="carch-logo">C<span>.</span>Arch</div>
        <div class="carch-sub">Consulting Architecture &bull; People Analytics &amp; AI Workbench</div>
    </div>
    """, unsafe_allow_html=True)

with nav_theme:
    new_dark = st.toggle("🌙 Dark", value=st.session_state.dark_mode, key="top_theme_toggle")
    if new_dark != st.session_state.dark_mode:
        st.session_state.dark_mode = new_dark
        st.rerun()

with nav_pill:
    st.markdown('<div style="text-align:right;"><span class="carch-pill">Live Advisory Environment</span></div>', unsafe_allow_html=True)

# File Uploader + Contextual Help Popover
col_up, col_sample, col_help = st.columns([2.8, 1.1, 0.7])
with col_up:
    uploaded_file = st.file_uploader("Upload client dataset (CSV or Excel)", type=["csv", "xlsx"])
with col_sample:
    st.write("")
    st.write("")
    use_sample = st.checkbox("Use sample HR dataset", value=True)
with col_help:
    st.write("")
    st.write("")
    with st.popover("ℹ️ Quick Guide"):
        st.markdown("""
        **Getting Started with C.Arch:**
        1. **Controls Drawer:** Click **☰ Controls** in the top-left bar to open Data Hygiene & API Key settings.
        2. **Ingest:** Upload any `.csv` or `.xlsx` export, or keep the built-in HR survey sample active.
        3. **Transform:** Type plain-English rules into the AI Command Bar to filter, sort, or engineer new columns.
        """)

df = None
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
elif use_sample:
    df = pd.DataFrame({
        "Employee_ID": ["E01", "E02", "E03", "E04", "E05", "E05", "E06"],
        "Department": ["Consulting", "Audit", "Consulting", "Tax", "Audit", "Audit", "Advisory"],
        "Region": ["Nairobi ", "nairobi", "Mombasa", "Nairobi", "Kisumu", "Kisumu", None],
        "Engagement_Score": [4.5, 3.2, 4.8, 2.9, 3.7, 3.7, 4.1],
        "Attrition_Risk": [1.8, 3.9, 1.5, 4.2, 3.1, 3.1, 2.4]
    })

if df is not None:
    # Dedicated Left Sidebar Drawer (Triggered via ☰ Controls)
    with st.sidebar:
        st.markdown("### 🧹 Data Hygiene")
        st.caption("Standardize raw exports before analysis.")
        if st.checkbox("Remove duplicate rows"):
            df = df.drop_duplicates()
        if st.checkbox("Trim spaces & standardize casing"):
            for col in df.select_dtypes(include=["object", "string"]).columns:
                df[col] = df[col].astype(str).str.strip().str.title().replace("None", pd.NA).replace("Nan", pd.NA)
        if st.checkbox("Drop rows with missing values"):
            df = df.dropna()

        st.markdown("### 🤖 AI Co-Pilot")
        default_api_key = ""
        try:
            if "GEMINI_API_KEY" in st.secrets:
                default_api_key = st.secrets["GEMINI_API_KEY"]
        except FileNotFoundError:
            default_api_key = ""

        if default_api_key:
            api_key = default_api_key
            st.success("🔑 Hosted Gemini Engine: Active")
            custom_key = st.text_input("Custom API Key (Optional Override)", type="password")
            if custom_key:
                api_key = custom_key
        else:
            st.caption("Connect your Google AI Studio key or set GEMINI_API_KEY in Secrets.")
            api_key = st.text_input("Gemini API Key", type="password")
        
        
        

    # Section 1: Data Health Overview + Info Popover
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
    c1.metric("Total Records", df.shape[0])
    c2.metric("Variables", df.shape[1])
    c3.metric("Duplicate Rows", int(df.duplicated().sum()))
    c4.metric("Missing Cells", int(df.isna().sum().sum()))

    st.write("")

    # Section 2: AI Data Instruction Box + Consulting Prompt Playbook
    h2_col, h2_info = st.columns([6, 1])
    with h2_col:
        st.subheader("2. AI Data Instruction Box")
    with h2_info:
        with st.popover("📘 Prompt Booklet"):
            st.markdown("""
            **C.Arch Multi-Task Prompting Guide:**
            Chain multiple cleaning, segmentation, and analytical operations in a single command:

            - **1. Executive Data Hygiene:**
              *"Standardize text columns to Title Case, strip extra whitespace, convert date columns to YYYY-MM-DD, and create a boolean 'is_complete' column where no fields are null."*
            - **2. People Analytics & Risk Banding:**
              *"Segment numeric scores into 'Low', 'Moderate', and 'High' tiers using quantiles, flag Z-score outliers (>2.5 or <-2.5) in 'outlier_flag', and compute a 0-100 composite index."*
            - **3. Survey & Psychometric Scoring:**
              *"Compute row-wise mean and standard deviation across numeric Likert items, classify top-quartile respondents as 'Elevated', and add 'straightline_flag' if all item scores match."*
            - **4. Commercial Variance & Margin Audit:**
              *"Calculate absolute and percentage variance between target and actual numeric columns, label rows 'Favorable', 'On-Target', or 'Unfavorable', and sort by impact."*
            - **5. Filtering & Feature Ratios:**
              *"Filter rows where Attrition_Risk > 3.0, compute a ratio between the top two numeric metrics, and keep only key reporting columns."*
            """)

    PROMPT_PLAYBOOK = {
        "Custom Multi-Task Command (Write your own below)": "",
        "Scenario 1: Executive Data Hygiene & Standardization": (
            "Standardize all text columns to Title Case, strip leading/trailing whitespace, "
            "convert any date columns to ISO format (YYYY-MM-DD), and add a boolean 'is_complete_record' "
            "column that is True only when all columns have non-null values."
        ),
        "Scenario 2: People Analytics — Risk Tiering & Outlier Audit": (
            "Segment the primary numeric score column into 'Low', 'Moderate', and 'High' tiers using quantiles, "
            "flag statistical outliers (Z-score > 2.5 or < -2.5) in a new 'outlier_flag' column, "
            "and sort rows by highest risk first."
        ),
        "Scenario 3: Psychometric / Survey Scale Composite & Straightlining": (
            "Compute row-wise mean and standard deviation across numeric survey columns into 'scale_mean' and 'scale_sd', "
            "classify respondents in the top quartile as 'High_Bracket' in a 'severity_tier' column, "
            "and create a boolean 'straightline_flag' where row standard deviation equals 0."
        ),
        "Scenario 4: Commercial Variance & Performance Ranking": (
            "Identify budget/target and actual numeric columns, calculate 'variance_abs' and 'variance_pct', "
            "classify rows as 'Favorable', 'On-Target', or 'Unfavorable', and rank rows by absolute variance."
        ),
    }

    selected_scenario = st.selectbox(
        "Consulting Scenario Playbook (Select a preset or write a custom multi-task prompt):",
        options=list(PROMPT_PLAYBOOK.keys())
    )

    instruction = st.text_area(
        "Enter a plain-English or multi-step transformation command (Editable):",
        value=PROMPT_PLAYBOOK[selected_scenario],
        height=105,
        placeholder="e.g., Filter rows where Attrition_Risk > 3.0, create a Risk_Tier column, and sort by Engagement_Score descending..."
    )

    run_ai = st.button("⚡ Execute AI Transformation", type="primary")

    if run_ai and instruction:
    
        if not api_key:
            st.warning("Open **☰ Controls** in the top-left bar and paste your Gemini API key to activate AI transformations.")
        else:
            with st.spinner("Generating audit-ready pandas transformation..."):
                client = genai.Client(api_key=api_key)
                prompt = f"""
You are a senior data analyst writing Python pandas code.
Given a DataFrame named `df` with columns and types:
{df.dtypes.to_dict()}

And sample rows:
{df.head(3).to_dict(orient="records")}

Write ONLY valid Python code that transforms `df` according to this instruction: "{instruction}"
Rules:
- Modify or reassign `df` directly (e.g., df = df[...]).
- Do NOT include markdown backticks, explanations, imports, or print statements.
"""
                try:
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt,
                    )
                except Exception:
                    response = client.models.generate_content(
                        model="gemini-3.8-flash-lite",
                        contents=prompt,
                    )

                generated_code = response.text.strip().removeprefix("```python").removeprefix("```").removesuffix("```").strip()

                with st.expander("View generated Python code (Audit Trail)"):
                    st.code(generated_code, language="python")

                try:
                    local_vars = {"df": df.copy(), "pd": pd}
                    exec(generated_code, {}, local_vars)
                    df = local_vars["df"]
                    st.success("Transformation applied successfully.")
                except Exception as e:
                    st.error(f"Could not apply instruction: {e}")

    st.write("")

    # Section 3: Workspace Tabs + Dedicated Tutorial & Documentation Tab
    tab_data, tab_seg, tab_corr, tab_guide = st.tabs([
        "📋 Working Dataset",
        "📊 Group Segmentation",
        "🧠 Behavioral Correlation Matrix",
        "📘 User Guide & Documentation"
    ])

    with tab_data:
        st.caption("Live table reflecting all active sidebar hygiene rules and AI transformations.")
        render_themed_table(df)
        st.download_button(
            "⬇️ Export Deliverable (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            "carch_deliverable.csv",
            "text/csv"
        )

    with tab_seg:
        seg_head, seg_info = st.columns([6, 1])
        with seg_head:
            st.markdown("#### Cross-Tab & Descriptive Statistics")
        with seg_info:
            with st.popover("ℹ️ Guide"):
                st.markdown("""
                **How to Read Segmentation:**
                - **Count:** Sample size ($n$) per subgroup.
                - **Mean vs. Median:** Compare both—if Mean diverges sharply from Median, check for outliers.
                - **Std_Dev:** Spread/variability within that group.
                """)

        cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()

        if cat_cols and num_cols:
            p1, p2 = st.columns(2)
            group_col = p1.selectbox("Segment By (Category)", cat_cols)
            metric_col = p2.selectbox("Evaluate Metric (Numeric)", num_cols)

            summary = (
                df.groupby(group_col, dropna=False)[metric_col]
                .agg(Count="count", Mean="mean", Median="median", Std_Dev="std")
                .round(2)
                .reset_index()
            )
            t_col, chart_col = st.columns([1.2, 1])
            with t_col:
                render_themed_table(summary)
            with chart_col:
                st.bar_chart(summary.set_index(group_col)["Mean"], color=accent)

    with tab_corr:
        corr_head, corr_info = st.columns([6, 1])
        with corr_head:
            st.markdown("#### Pearson Correlation Matrix ($r$)")
        with corr_info:
            with st.popover("ℹ️ Guide"):
                st.markdown("""
                **Interpreting Pearson's $r$ (-1.0 to +1.0):**
                - **+0.70 to +1.00:** Strong positive relationship.
                - **-0.70 to -1.00:** Strong inverse relationship (e.g., higher engagement predicting lower attrition risk).
                - **Near 0.00:** No linear relationship.
                """)

        num_df = df.select_dtypes(include=["number"])
        if num_df.shape[1] >= 2:
            corr = num_df.corr().round(3)
            render_themed_table(corr)
        else:
            st.info("Upload a dataset with at least two numeric columns to compute correlations.")

    with tab_guide:
        st.markdown("### 🏛️ C.Arch Platform Manual & Consulting Workflow")
        st.write("Follow this four-step MECE workflow when auditing raw client datasets, survey exports, or operational logs:")

        g1, g2 = st.columns(2)
        with g1:
            st.markdown("""
            #### Step 1: Ingestion & Health Audit
            - Drop in a `.csv` or `.xlsx` file at the top of the page.
            - Check the **4 KPI cards** immediately to spot duplicate rows or missing cells before running any statistics.

            #### Step 2: Automated Data Hygiene
            - Click **☰ Controls** in the top-left navigation bar to open the **Data Hygiene** drawer.
            - Toggle **Remove duplicate rows** and **Trim spaces & standardize casing** to merge inconsistent entries (like `"Nairobi "` and `"nairobi"`).
            """)
        with g2:
            st.markdown("""
            #### Step 3: Natural-Language AI Transformation
            - Paste your free **Google AI Studio** key into the **AI Co-Pilot** section inside **☰ Controls**.
            - Type plain-English filtering, sorting, or calculated-column rules into the **AI Data Instruction Box**.
            - Always expand **View generated Python code (Audit Trail)** to verify the exact `pandas` logic before exporting.

            #### Step 4: Segmentation, Correlation & Export
            - Use **Group Segmentation** for subgroup comparisons and **Behavioral Correlation Matrix** to test linear drivers ($r$).
            - Click **Export Deliverable (CSV)** under *Working Dataset* to download your clean, client-ready table.
            """)
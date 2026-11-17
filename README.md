# 🏛️ C.Arch | Consulting Architecture & People Analytics Workbench

**Live Application:** [https://exec-c-arch.streamlit.app](https://exec-c-arch.streamlit.app)

C.Arch is an interactive, browser-based data hygiene, pivot modeling, and AI transformation workbench built to compress messy raw CSV/Excel exports into executive-ready consulting deliverables in minutes.

---

## Key Capabilities

* **12 Deterministic Excel Hygiene Controls:** One-click deduplication, `TRIM` whitespace removal, `PROPER` Title Case standardization, empty-column pruning, median/mean/zero imputation, ISO date formatting (`YYYY-MM-DD`), `ABS` sign enforcement, rounding, `Row_ID` indexing, and multi-direction sorting.
* **AI Co-Pilot & 14-Scenario Consulting Playbook:** Powered by Google Gemini (`google-genai`) to translate plain-English instructions—such as nested `IF` performance tiering, `SUMIFS`/`COUNTIFS` group shares, budget-vs-actual variance deltas, Z-score anomaly audits, and psychometric Likert straightlining flags—into inspectable, audit-ready Python code.
* **No-Code Formula Builder:** Deterministic two-column math (`+`, `-`, `*`, `/`, `% Change`) and conditional `=IF` flag generation with live Excel formula previews.
* **Automated Pivot & Behavioral Diagnostics:** Smart-recommended Pivot Tables (including `% of Total` shares and cross-tab matrices), multi-metric Group Segmentation (`count`, `mean`, `sum`), and automated Pearson correlation extraction.
* **Multi-Sheet Executive Export:** Compiles `Cleaned_Data`, `Pivot_Summary`, and `Summary_Stats` into a single downloadable `.xlsx` workbook alongside flat `.csv` export.

---

## Tech Stack

* **Frontend & App Framework:** Python, Streamlit (Custom Midnight Navy/Teal & Light Mode UI)
* **Data & Quantitative Engine:** Pandas, NumPy, OpenPyXL
* **Generative AI Integration:** Google GenAI SDK (`gemini-2.5-flash`)

---

## Repository Structure

```text
c-arch-workbench/
├── deloitte-workbench/
│   ├── app.py              # Main Streamlit application & UI design system
│   └── requirements.txt    # Cloud deployment dependencies
└── README.md               # Project documentation

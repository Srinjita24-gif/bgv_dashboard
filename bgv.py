import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

st.set_page_config(page_title="BGV Analysis Dashboard", layout="wide", initial_sidebar_state="expanded")

C_BLUE   = "#1D4ED8"; C_GREEN  = "#059669"; C_RED    = "#DC2626"; C_ORANGE = "#D97706"
C_PURPLE = "#7C3AED"; C_TEAL   = "#0891B2"; C_INDIGO = "#3730A3"; C_AMBER  = "#B45309"
C_SLATE  = "#475569"

LABEL_COLOR = "#0F172A"
AXIS_FONT   = dict(size=12, color=LABEL_COLOR, family="Inter")
TICK_FONT   = dict(size=10, color=LABEL_COLOR, family="Inter")
TITLE_FONT  = dict(size=14, color=LABEL_COLOR, family="Inter")
AVATAR_COLORS = [C_BLUE, C_GREEN, C_PURPLE, C_RED, C_ORANGE, C_TEAL, C_INDIGO, C_AMBER]

NAV = [
    "Overview",
    "Pending Cases",
    "Orange Report",
    "Tenure Analysis",
    "Employee View",
]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #F0F4F8; color: #1E293B; }
section[data-testid="stSidebar"] { background: #0F172A !important; min-width: 270px !important; width: 270px !important; }
section[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
section[data-testid="stSidebar"] hr { border-color: #1E293B !important; }
section[data-testid="stSidebar"] .stMarkdown p { color: #94A3B8 !important; font-size:.78rem; }
section[data-testid="stSidebar"] .stButton > button {
    width:100%; background:linear-gradient(135deg,#DC2626,#991B1B) !important;
    color:white !important; border:none !important; border-radius:8px !important;
    padding:.5rem .8rem !important; font-weight:700 !important; font-size:.8rem !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
section[data-testid="stSidebar"] .stTextInput input {
    background:#1E293B !important; color:#E2E8F0 !important; border-color:#334155 !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span { color:#E2E8F0 !important; }
section[data-testid="stSidebar"] .stSelectbox svg { fill:#94A3B8 !important; }
section[data-testid="stSidebar"] .stRadio > div > label {
    padding:6px 10px !important; border-radius:6px !important;
    margin:1px 0 !important; font-size:.85rem !important; font-weight:600 !important;
}
section[data-testid="stSidebar"] .stRadio > div > label:hover { background:#1E293B !important; }
.kc { background:#FFF; border-radius:10px; padding:14px 12px 12px; border:1px solid #E2E8F0;
      border-left:4px solid; box-shadow:0 1px 4px rgba(0,0,0,.07); margin-bottom:4px; text-align:center; }
.kv { font-size:1.7rem; font-weight:900; line-height:1.1; margin-bottom:2px; }
.kl { font-size:.65rem; text-transform:uppercase; letter-spacing:1.2px; color:#0F172A; font-weight:800; }
.ks { font-size:.58rem; color:#1E293B; margin-top:2px; font-weight:600; font-style:italic; }
.sh { font-size:.88rem; font-weight:800; color:#0F172A; border-left:3px solid #2563EB;
      padding:5px 12px; background:#EFF6FF; border-radius:0 6px 6px 0;
      margin-bottom:10px; margin-top:12px; }
.ph { background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 100%); border-radius:10px;
      padding:16px 24px; margin-bottom:14px; border:1px solid #1E3A5F; }
.ph h1 { color:white !important; font-size:1.3rem; margin:0; font-weight:800; }
.ph p  { color:#94A3B8 !important; margin:3px 0 0; font-size:.8rem; }
[data-testid="stFileUploader"] { background:#1E293B !important; border-radius:10px !important; padding:8px !important; }
[data-testid="stFileUploader"] section { background:#1E293B !important; border:2px dashed #334155 !important; border-radius:8px !important; }
[data-testid="stFileUploader"] section:hover { border-color:#60A5FA !important; }
[data-testid="stFileUploaderDropzoneInstructions"] div span { color:#94A3B8 !important; }
[data-testid="stFileUploaderDropzoneInstructions"] div small { color:#64748B !important; }
[data-testid="stTextInput"] input {
    border:1.5px solid #0F172A !important; border-radius:6px !important;
    background:#FFF !important; color:#0F172A !important; font-weight:500 !important;
}
[data-testid="stTextInput"] input:focus { border:2px solid #1D4ED8 !important; box-shadow:0 0 0 2px rgba(29,78,216,.15) !important; }
[data-testid="stTextInput"] input::placeholder { color:#94A3B8 !important; font-weight:400 !important; }
#MainMenu, footer, header { display:none !important; }
[data-testid="stElementToolbar"] { display:none !important; }
button[data-testid="collapsedControl"], div[data-testid="stSidebarCollapsedControl"] { display:none !important; }
div[data-baseweb="select"] div[class*="singleValue"],
div[data-baseweb="select"] div[class*="placeholder"] { color:#0F172A !important; }
div[data-baseweb="option"] { color:#0F172A !important; background:#FFF !important; }
div[data-baseweb="option"]:hover { background:#EFF6FF !important; color:#1D4ED8 !important; }
.stDataFrame th { background:#1E293B !important; color:white !important; font-weight:700 !important; font-size:.8rem !important; }
.stDataFrame td { font-size:.8rem !important; color:#0F172A !important; font-weight:500 !important; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def _avatar_color(name):
    return AVATAR_COLORS[sum(ord(c) for c in str(name)) % len(AVATAR_COLORS)]

def _initials(name):
    parts = str(name or '').strip().split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else str(name or '??')[:2].upper()

def section(title, color=C_BLUE):
    st.markdown(f'<div class="sh" style="border-left-color:{color}">{title}</div>', unsafe_allow_html=True)

def kpi_card(col, value, label, color, sub=""):
    s = f'<div class="ks">{sub}</div>' if sub else ""
    col.markdown(
        f'<div class="kc" style="border-left-color:{color}">'
        f'<div class="kv" style="color:{color}">{value}</div>'
        f'<div class="kl">{label}</div>{s}</div>',
        unsafe_allow_html=True)

def navigate_to(page_label):
    st.session_state["_nav_index"] = NAV.index(page_label)
    st.rerun()

def style_fig(fig, xtitle=None, ytitle=None, title=None):
    fig.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        title=dict(text=f"<b>{title}</b>", font=TITLE_FONT) if title else {},
        xaxis=dict(title=dict(text=xtitle or "", font=AXIS_FONT), tickfont=TICK_FONT,
                   gridcolor="#E2E8F0", linecolor="#CBD5E1"),
        yaxis=dict(title=dict(text=ytitle or "", font=AXIS_FONT), tickfont=TICK_FONT,
                   gridcolor="#E2E8F0", linecolor="#CBD5E1"),
        margin=dict(t=50, b=40, l=40, r=20), font=dict(family="Inter")
    )
    return fig

def fmt_date(val):
    if pd.isna(val) or val is None or str(val).strip() in ("", "nan", "None", "NaT"):
        return "Not Applicable"
    try:
        return pd.to_datetime(val).strftime("%d %b %Y")
    except:
        return "Not Applicable"

def fmt_tenure(days_val):
    if pd.isna(days_val) or days_val is None:
        return "Not Applicable"
    try:
        d = int(days_val)
        if d < 30:
            return f"{d}D"
        months = d // 30
        rem    = d % 30
        if rem == 0:
            return f"{months}M"
        return f"{months}M {rem}D"
    except:
        return "Not Applicable"


def toggle_show(key, df_sub, list_key, title_str, color):
    show_key = f"_show_{key}"
    is_open  = st.session_state.get(show_key, False)
    label    = "Hide Employees" if is_open else "View Employees"
    if st.button(label, key=f"_btn_{key}", use_container_width=True):
        st.session_state[show_key] = not is_open
        st.rerun()


def render_toggle_list(key, df_sub, title_str, color):
    if st.session_state.get(f"_show_{key}", False):
        section(title_str, color)
        render_employee_list_cards(df_sub, f"_list_{key}")


# ─── MONTHLY BGV STATUS BREAKDOWN ────────────────────────────────────────────
def render_monthly_bgv_breakdown(df, date_col="DOJ", section_title="Monthly BGV Status Breakdown", toggle_key="monthly_breakdown"):
    if date_col not in df.columns or df[date_col].notna().sum() == 0:
        return

    show_key = f"_show_{toggle_key}"
    is_open  = st.session_state.get(show_key, False)
    btn_label = "Hide Monthly Analysis" if is_open else "Monthly BGV Analysis"

    if st.button(btn_label, key=f"_btn_{toggle_key}", use_container_width=False):
        st.session_state[show_key] = not is_open
        st.rerun()

    if not is_open:
        return

    section(section_title, C_INDIGO)

    df_m = df[df[date_col].notna()].copy()
    df_m["_Month"]     = df_m[date_col].dt.strftime("%b %Y")
    df_m["_Sort"]      = df_m[date_col].dt.to_period("M")
    df_m["_BGV_Group"] = df_m.apply(_bgv_group, axis=1)

    months_sorted = (df_m[["_Month", "_Sort"]]
                     .drop_duplicates()
                     .sort_values("_Sort")["_Month"]
                     .tolist())

    grouped = (df_m.groupby(["_Month", "_Sort", "_BGV_Group"])
               .size()
               .reset_index(name="Count"))
    grouped = grouped.sort_values("_Sort")

    STATUS_COLORS = {
        "Completed":     C_GREEN,
        "Pending":       C_ORANGE,
        "Orange Report": C_AMBER,
        "Not Initiated": C_PURPLE,
        "Other":         C_SLATE,
    }

    fig = go.Figure()
    for grp, color in STATUS_COLORS.items():
        sub = grouped[grouped["_BGV_Group"] == grp]
        month_counts = dict(zip(sub["_Month"], sub["Count"]))
        y_vals = [month_counts.get(m, 0) for m in months_sorted]
        if sum(y_vals) == 0:
            continue  # skip empty groups from legend
        fig.add_trace(go.Bar(
            name=grp,
            x=months_sorted,
            y=y_vals,
            marker=dict(color=color, line=dict(color="#000", width=1)),
            text=[str(v) if v > 0 else "" for v in y_vals],
            textposition="inside",
            textfont=dict(size=10, color="white", family="Inter"),
        ))

    style_fig(fig, xtitle="Month", ytitle="Employees", title=section_title)
    fig.update_layout(
        barmode="stack",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11, family="Inter")),
        height=320,
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<p style="font-size:.75rem;color:#64748B;font-weight:500;margin:4px 0 4px 0;">'
        'select a month to view employees</p>',
        unsafe_allow_html=True
    )
    month_sel_key = f"_month_sel_{toggle_key}"
    selected_month = st.selectbox(
        "Select Month",
        ["— Select —"] + months_sorted,
        key=month_sel_key,
        label_visibility="collapsed"
    )

    if selected_month and selected_month != "— Select —":
        df_month = df_m[df_m["_Month"] == selected_month].copy()
        completed_m     = df_month[df_month["_BGV_Group"] == "Completed"]
        pending_m       = df_month[df_month["_BGV_Group"] == "Pending"]
        orange_m        = df_month[df_month["_BGV_Group"] == "Orange Report"]
        not_initiated_m = df_month[df_month["_BGV_Group"] == "Not Initiated"]
        other_m         = df_month[df_month["_BGV_Group"] == "Other"]

        c1, c2, c3, c4, c5 = st.columns(5)
        kpi_card(c1, len(df_month),      f"Total in {selected_month}", C_BLUE)
        kpi_card(c2, len(completed_m),   "BGV Completed",               C_GREEN)
        kpi_card(c3, len(pending_m),     "Pending / In-Progress",       C_ORANGE)
        kpi_card(c4, len(orange_m),      "Orange Report",               C_AMBER)
        kpi_card(c5, len(not_initiated_m), "Not Initiated",             C_PURPLE)

        mk = f"{toggle_key}_{selected_month.replace(' ','_')}"

        with c1:
            toggle_show(f"{mk}_all",      df_month,         f"all_list_{mk}",      f"All — {selected_month} ({len(df_month)})", C_BLUE)
        with c2:
            toggle_show(f"{mk}_comp",     completed_m,      f"comp_list_{mk}",     f"Completed — {selected_month} ({len(completed_m)})", C_GREEN)
        with c3:
            toggle_show(f"{mk}_pend",     pending_m,        f"pend_list_{mk}",     f"Pending — {selected_month} ({len(pending_m)})", C_ORANGE)
        with c4:
            toggle_show(f"{mk}_orange",   orange_m,         f"orange_list_{mk}",   f"Orange Report — {selected_month} ({len(orange_m)})", C_AMBER)
        with c5:
            toggle_show(f"{mk}_noinit",   not_initiated_m,  f"noinit_list_{mk}",   f"Not Initiated — {selected_month} ({len(not_initiated_m)})", C_PURPLE)

        render_toggle_list(f"{mk}_all",    df_month,         f"All — {selected_month} ({len(df_month)})", C_BLUE)
        render_toggle_list(f"{mk}_comp",   completed_m,      f"Completed — {selected_month} ({len(completed_m)})", C_GREEN)
        render_toggle_list(f"{mk}_pend",   pending_m,        f"Pending — {selected_month} ({len(pending_m)})", C_ORANGE)
        render_toggle_list(f"{mk}_orange", orange_m,         f"Orange Report — {selected_month} ({len(orange_m)})", C_AMBER)
        render_toggle_list(f"{mk}_noinit", not_initiated_m,  f"Not Initiated — {selected_month} ({len(not_initiated_m)})", C_PURPLE)

        if len(other_m) > 0:
            ok = f"{mk}_other"
            toggle_show(ok, other_m, f"other_list_{mk}", f"Other/Exceptional — {selected_month} ({len(other_m)})", C_SLATE)
            render_toggle_list(ok, other_m, f"Other/Exceptional — {selected_month} ({len(other_m)})", C_SLATE)


# ─── FIX: _bgv_group now correctly handles no-init employees ─────────────────
def _bgv_group(row):
    exc = row.get("Exceptional Case")
    if pd.notna(exc) and exc not in (None, "", "None", "nan"):
        return "Other"
    has_orange = bool(row.get("Has Orange Report", False))
    if has_orange:
        return "Orange Report"
    has_comp = pd.notna(row.get("BGV Completion Date")) if "BGV Completion Date" in row.index else False
    has_init = pd.notna(row.get("BGV Initiated Date"))  if "BGV Initiated Date"  in row.index else False
    if has_init and has_comp:
        return "Completed"
    if has_init and not has_comp:
        return "Pending"
    # No initiation date at all — was wrongly falling into "Pending" before
    return "Not Initiated"


# ─── BACK TO OVERVIEW BUTTON ─────────────────────────────────────────────────
def back_to_overview_btn(key_suffix=""):
    if st.button("Back to Overview", key=f"_back_overview_{key_suffix}"):
        navigate_to("Overview")


# ─── DATA PROCESSING ─────────────────────────────────────────────────────────
def parse_date_col(series):
    for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%d-%b-%Y", "%d/%b/%Y",
                "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y", "%d %b %Y", "%d %B %Y"]:
        try:
            parsed = pd.to_datetime(series, format=fmt, errors="coerce")
            if parsed.notna().sum() > len(series) * 0.4:
                return parsed
        except:
            continue
    return pd.to_datetime(series, dayfirst=True, errors="coerce")

COLUMN_MAP = {
    "employee name": "Employee Name", "name": "Employee Name", "emp name": "Employee Name",
    "employee id": "Employee ID", "emp id": "Employee ID", "id": "Employee ID",
    "doj": "DOJ", "date of joining": "DOJ", "joining date": "DOJ", "doj (date of joining)": "DOJ",
    "department": "Department", "dept": "Department",
    "designation": "Designation", "role": "Designation",
    "location": "Location", "branch": "Location",
    "mobile number": "Mobile Number", "mobile": "Mobile Number",
    "email id": "Email ID", "email": "Email ID",
    "bgv status": "BGV Status",
    "bgv agency": "BGV Agency", "agency": "BGV Agency",
    "bgv initiated date": "BGV Initiated Date", "bgv initiate date": "BGV Initiated Date",
    "bgv orange report date": "BGV Orange Report Date", "orange report date": "BGV Orange Report Date",
    "final bgv completion date": "BGV Completion Date", "bgv completion date": "BGV Completion Date",
    "bgv completed date": "BGV Completion Date",
    "remarks": "Remarks",
    "bgv initiate tenure": "_SKIP", "bgv completed tenure": "_SKIP",
    "inititate tenure": "_SKIP",    "initiate tenure": "_SKIP",
    "completed tenure": "_SKIP",    "initiate tenure,": "_SKIP",
}

def normalise_columns(df):
    df = df.copy()
    df.columns = df.columns.str.strip()
    rename = {}
    for col in df.columns:
        mapped = COLUMN_MAP.get(col.strip().lower())
        if mapped == "_SKIP":
            rename[col] = f"__drop_{col}"
        elif mapped:
            rename[col] = mapped
    df = df.rename(columns=rename)
    df = df.drop(columns=[c for c in df.columns if c.startswith("__drop_")])
    return df

def process_bgv(raw: pd.DataFrame) -> pd.DataFrame:
    df = normalise_columns(raw.copy())

    for col in ["DOJ", "BGV Initiated Date", "BGV Orange Report Date", "BGV Completion Date"]:
        if col in df.columns:
            df[col] = parse_date_col(df[col])

    if "BGV Initiated Date" in df.columns and "DOJ" in df.columns:
        df["BGV Initiate Tenure"] = (df["BGV Initiated Date"] - df["DOJ"]).dt.days
        df["BGV Initiate Tenure"] = df["BGV Initiate Tenure"].where(
            df["BGV Initiate Tenure"].ge(0) & df["BGV Initiated Date"].notna() & df["DOJ"].notna(), None)
    else:
        df["BGV Initiate Tenure"] = None

    if "BGV Completion Date" in df.columns and "BGV Initiated Date" in df.columns:
        df["BGV Completed Tenure"] = (df["BGV Completion Date"] - df["BGV Initiated Date"]).dt.days
        df["BGV Completed Tenure"] = df["BGV Completed Tenure"].where(
            df["BGV Completed Tenure"].ge(0) & df["BGV Completion Date"].notna() & df["BGV Initiated Date"].notna(), None)
    else:
        df["BGV Completed Tenure"] = None

    if "BGV Status" not in df.columns:
        df["BGV Status"] = "Unknown"
    df["BGV Status"] = df["BGV Status"].astype(str).str.strip()

    has_init = df["BGV Initiated Date"].notna() if "BGV Initiated Date" in df.columns else pd.Series(False, index=df.index)
    has_comp = df["BGV Completion Date"].notna() if "BGV Completion Date" in df.columns else pd.Series(False, index=df.index)

    df["Has Orange Report"] = (
        df["BGV Orange Report Date"].notna() if "BGV Orange Report Date" in df.columns
        else pd.Series(False, index=df.index))

    # FIX: Pending = has initiation date BUT no completion date AND no orange report.
    # Orange Report cases are their own category — they must not double-count as
    # "Pending" or "Not Yet Completed" on the Overview/Pending pages.
    df["Is Pending"] = has_init & ~has_comp & ~df["Has Orange Report"]

    # FIX: Track not-yet-initiated separately so they don't bleed into pending views
    df["Not Initiated"] = ~has_init & ~has_comp & ~df["Has Orange Report"]

    def _classify_exceptional(val):
        vl = str(val).strip().lower()
        if "caller" in vl: return "Caller"
        if "sab" in vl: return "SAB Employee"
        if "offroll" in vl or "onroll" in vl or "off roll" in vl or "on roll" in vl:
            return "Transferred to Offroll to Onroll"
        if "t salary" in vl or "tsalary" in vl: return "T Salary"
        if ("joined" in vl and "left" in vl) or "left same month" in vl:
            return "Joined and Left Same Month"
        return None

    df["Exceptional Case"] = df["BGV Status"].str.strip().apply(_classify_exceptional)
    return df

def load_excel(file_bytes, file_name):
    buf = io.BytesIO(file_bytes)
    ext = file_name.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                buf.seek(0)
                return pd.read_csv(buf, dtype=object, encoding=enc)
            except UnicodeDecodeError:
                continue
    else:
        for engine in ["openpyxl", "xlrd", "calamine"]:
            try:
                buf.seek(0)
                return pd.read_excel(buf, dtype=object, engine=engine)
            except:
                continue
    return pd.DataFrame()


# ─── EMPLOYEE CARD ──────────────────────────────────────────────────────────
def _badge(txt, bg, fg):
    return (f'<span style="background:{bg};color:{fg};font-size:.65rem;font-weight:700;'
            f'padding:2px 8px;border-radius:20px;display:inline-block;margin:1px 2px">{txt}</span>')


def render_employee_list_cards(df, key_prefix="emp"):
    if df.empty:
        st.info("No employees found.")
        return

    search = st.text_input("Search by Name or ID", placeholder="Type name or ID...",
                           key=f"{key_prefix}_search", label_visibility="collapsed")
    if search:
        mask = pd.Series(False, index=df.index)
        if "Employee Name" in df.columns:
            mask |= df["Employee Name"].astype(str).str.contains(search, case=False, na=False)
        if "Employee ID" in df.columns:
            mask |= df["Employee ID"].astype(str).str.contains(search, case=False, na=False)
        df = df[mask]

    st.caption(f"{len(df)} employee(s)")

    for _, row in df.iterrows():
        name      = str(row.get("Employee Name", "Unknown"))
        emp_id    = str(row.get("Employee ID", "—"))
        desig     = str(row.get("Designation", "—"))
        dept      = str(row.get("Department", "—"))
        loc       = str(row.get("Location", "—"))
        status    = str(row.get("BGV Status", "—"))
        doj       = fmt_date(row.get("DOJ"))
        bgv_init  = fmt_date(row.get("BGV Initiated Date"))
        bgv_comp  = fmt_date(row.get("BGV Completion Date"))
        bgv_or    = fmt_date(row.get("BGV Orange Report Date"))
        it_days   = row.get("BGV Initiate Tenure")
        ct_days   = row.get("BGV Completed Tenure")
        it_str    = fmt_tenure(it_days)
        ct_str    = fmt_tenure(ct_days)
        orange    = row.get("Has Orange Report", False)
        is_pend   = row.get("Is Pending", False)
        not_init  = row.get("Not Initiated", False)

        color_av = _avatar_color(name)
        ini      = _initials(name)
        exp_key  = f"{key_prefix}_exp_{name}_{emp_id}"
        is_open  = st.session_state.get(exp_key, False)

        sl = status.lower()
        if "complete" in sl or "clear" in sl:       s_bg, s_fg = "#DCFCE7", "#166534"
        elif "pending" in sl or "initiated" in sl:  s_bg, s_fg = "#FEF3C7", "#92400E"
        elif "orange" in sl:                        s_bg, s_fg = "#FFEDD5", "#9A3412"
        else:                                       s_bg, s_fg = "#F1F5F9", "#475569"

        it_color = "#DC2626" if pd.notna(it_days) and (it_days or 0) > 30 else "#059669"
        ct_color = "#DC2626" if pd.notna(ct_days) and (ct_days or 0) > 14 else "#059669"

        badges = _badge(status, s_bg, s_fg)
        if dept  not in ("—","None","nan",""): badges += _badge(dept,  "#DBEAFE", "#1D4ED8")
        if desig not in ("—","None","nan",""): badges += _badge(desig, "#EDE9FE", "#6D28D9")
        if loc   not in ("—","None","nan",""): badges += _badge(loc,   "#CCFBF1", "#0F766E")
        if is_pend:   badges += _badge("Pending",          "#FEF3C7", "#92400E")
        if not_init:  badges += _badge("BGV Not Initiated","#EDE9FE", "#6D28D9")
        if orange:    badges += _badge("Orange Report",    "#FFEDD5", "#C2410C")

        def _fld(lbl, val, col="#1E293B"):
            return (f'<div style="display:flex;flex-direction:column;min-width:90px">'
                    f'<span style="font-size:.58rem;font-weight:700;color:#94A3B8;text-transform:uppercase;'
                    f'letter-spacing:.7px">{lbl}</span>'
                    f'<span style="font-size:.78rem;font-weight:700;color:{col}">{val}</span></div>')

        it_disp = it_str if it_str != "Not Applicable" else "—"
        ct_disp = ct_str if ct_str != "Not Applicable" else "—"

        fields_html = (
            _fld("Date of Joining", doj) +
            _fld("BGV Initiated",   bgv_init) +
            _fld("BGV Completed",   bgv_comp) +
            _fld("Orange Report",   bgv_or) +
            _fld("Init Tenure",     it_disp, it_color) +
            _fld("Done Tenure",     ct_disp, ct_color)
        )

        card_html = f"""
        <div style="background:#FFF;border:1.5px solid #E2E8F0;border-radius:10px;
                    padding:12px 16px;margin-bottom:6px;box-shadow:0 1px 4px rgba(0,0,0,.06);
                    display:flex;align-items:center;gap:14px;flex-wrap:nowrap;overflow:hidden">
          <div style="display:flex;align-items:center;gap:10px;flex:0 0 240px;min-width:0">
            <span style="width:38px;height:38px;border-radius:50%;background:{color_av};
                  display:inline-flex;align-items:center;justify-content:center;
                  font-size:13px;font-weight:800;color:#fff;flex-shrink:0">{ini}</span>
            <div style="min-width:0">
              <div style="font-size:.92rem;font-weight:800;color:#0F172A;
                          white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{name}</div>
              <div style="font-size:.72rem;color:#64748B;white-space:nowrap;margin-bottom:4px">
                {(desig + " &nbsp;·&nbsp; ") if desig not in ("—","None","nan","") else ""}ID: {emp_id}
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:2px">{badges}</div>
            </div>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:10px 20px;flex:1;align-items:flex-start">
            {fields_html}
          </div>
        </div>"""

        col_card, col_btn = st.columns([12, 1])
        with col_card:
            st.markdown(card_html, unsafe_allow_html=True)
        with col_btn:
            if st.button("Hide" if is_open else "View",
                         key=f"{key_prefix}_btn_{name}_{emp_id}",
                         use_container_width=True):
                st.session_state[exp_key] = not is_open
                st.rerun()

        if is_open:
            st.markdown(
                f'<div style="background:#F8FAFC;border:1.5px solid #CBD5E1;border-radius:8px;'
                f'padding:12px 16px;margin:-2px 0 8px 0;font-size:.78rem;color:#0F172A">'
                f'<div style="display:flex;flex-wrap:wrap;gap:12px 28px">'
                + _fld("Department",       dept)
                + _fld("Designation",      desig)
                + _fld("Location",         loc)
                + _fld("Employee ID",      emp_id)
                + _fld("Date of Joining",  doj)
                + _fld("BGV Initiated",    bgv_init)
                + _fld("BGV Completed",    bgv_comp)
                + _fld("Orange Report",    bgv_or)
                + _fld("Init Tenure",      it_disp, it_color)
                + _fld("Done Tenure",      ct_disp, ct_color)
                + f'</div></div>',
                unsafe_allow_html=True
            )


# ─── EXPORT REPORT ────────────────────────────────────────────────────────────
def render_export(df):
    st.markdown("<br>", unsafe_allow_html=True)
    section("Export Report", C_SLATE)

    export_cols = [c for c in [
        "Employee Name", "Employee ID", "Department", "Designation", "Location",
        "DOJ", "BGV Status", "BGV Agency",
        "BGV Initiated Date", "BGV Orange Report Date", "BGV Completion Date",
        "BGV Initiate Tenure", "BGV Completed Tenure",
        "Is Pending", "Has Orange Report", "Remarks"
    ] if c in df.columns]

    df_exp = df[export_cols].copy()
    for dc in ["DOJ", "BGV Initiated Date", "BGV Orange Report Date", "BGV Completion Date"]:
        if dc in df_exp.columns:
            df_exp[dc] = df_exp[dc].apply(fmt_date)

    csv_data = df_exp.to_csv(index=False).encode("utf-8-sig")
    import hashlib
    key_hash = hashlib.md5(csv_data).hexdigest()[:8]
    st.download_button(
        label="Download as CSV (.csv)",
        data=csv_data,
        file_name=f"BGV_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=False,
        key=f"dl_csv_{key_hash}",
    )


# ─── EXCEPTIONAL CASES BREAKDOWN ─────────────────────────────────────────────
EXCEPTIONAL_CATEGORIES = [
    ("Caller",                           C_BLUE),
    ("SAB Employee",                     C_PURPLE),
    ("Transferred to Offroll to Onroll", C_TEAL),
    ("T Salary",                         C_AMBER),
    ("Joined and Left Same Month",       C_RED),
]

def render_exceptional_breakdown(df, key_prefix="exc"):
    exc_df = df[df["Exceptional Case"].notna()].copy() if "Exceptional Case" in df.columns else pd.DataFrame()

    if exc_df.empty:
        st.info("No exceptional cases found.")
        return

    section(f"Exceptional Cases Breakdown — {len(exc_df)} employee(s)", C_RED)

    cat_dfs = {}
    for cat, color in EXCEPTIONAL_CATEGORIES:
        cat_dfs[cat] = exc_df[exc_df["Exceptional Case"] == cat]

    cols = st.columns(len(EXCEPTIONAL_CATEGORIES))
    for i, (cat, color) in enumerate(EXCEPTIONAL_CATEGORIES):
        kpi_card(cols[i], len(cat_dfs[cat]), cat, color)

    btn_cols = st.columns(len(EXCEPTIONAL_CATEGORIES))
    for i, (cat, color) in enumerate(EXCEPTIONAL_CATEGORIES):
        if len(cat_dfs[cat]) > 0:
            with btn_cols[i]:
                toggle_show(f"{key_prefix}_{cat.replace(' ','_')}", cat_dfs[cat],
                            f"{key_prefix}_{cat}_list", f"{cat} ({len(cat_dfs[cat])})", color)

    for cat, color in EXCEPTIONAL_CATEGORIES:
        render_toggle_list(f"{key_prefix}_{cat.replace(' ','_')}", cat_dfs[cat],
                           f"{cat} ({len(cat_dfs[cat])})", color)


# ─── PAGE: OVERVIEW ──────────────────────────────────────────────────────────
def render_overview(df):
    total      = len(df)
    has_init   = df["BGV Initiated Date"].notna() if "BGV Initiated Date" in df.columns else pd.Series(False, index=df.index)
    has_comp   = df["BGV Completion Date"].notna() if "BGV Completion Date" in df.columns else pd.Series(False, index=df.index)
    completed  = int((has_init & has_comp).sum())
    pending    = int(df["Is Pending"].sum())
    orange     = int(df["Has Orange Report"].sum())
    exceptional = int(df["Exceptional Case"].notna().sum()) if "Exceptional Case" in df.columns else 0
    avg_init   = df["BGV Initiate Tenure"].mean()
    completion_pct = round(completed / max(total, 1) * 100, 1)

    df_completed = df[has_init & has_comp]

    # FIX: "Not Yet Completed" = has initiation but no completion AND no orange report
    # (orange report cases belong only on the Orange Report page)
    df_notcomp = df[has_init & ~has_comp & ~df["Has Orange Report"]]

    section("Executive Summary")

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, total,       "Total Employees",      C_BLUE)
    kpi_card(c2, completed,   "BGV Completed",         C_GREEN, f"{completion_pct}% completion rate")
    kpi_card(c3, pending,     "Pending / In-Progress", C_ORANGE)
    kpi_card(c4, orange,      "Orange Reports",         C_AMBER)
    kpi_card(c5, exceptional, "Exceptional Cases",      C_RED)

    with c1:
        if st.button("View All Employees", key="ov_nav_emp", use_container_width=True):
            navigate_to("Employee View")
    with c2:
        toggle_show("ov_completed", df_completed, "ov_comp_list", f"BGV Completed ({completed})", C_GREEN)
    with c3:
        if st.button("View Pending", key="ov_nav_pending", use_container_width=True):
            navigate_to("Pending Cases")
    with c4:
        if st.button("View Orange", key="ov_nav_orange", use_container_width=True):
            navigate_to("Orange Report")
    with c5:
        toggle_show("ov_exceptional", df[df["Exceptional Case"].notna()] if "Exceptional Case" in df.columns else pd.DataFrame(),
                    "ov_exc_list", f"Exceptional Cases ({exceptional})", C_RED)

    render_toggle_list("ov_completed", df_completed, f"BGV Completed ({completed})", C_GREEN)

    if st.session_state.get("_show_ov_exceptional", False):
        render_exceptional_breakdown(df, key_prefix="ov_exc")

    c6, c7 = st.columns(2)
    # FIX: label updated to match corrected scope (initiated but not completed)
    kpi_card(c6, len(df_notcomp), "Initiated — Not Yet Completed", C_SLATE)
    kpi_card(c7, fmt_tenure(avg_init) if pd.notna(avg_init) else "N/A",
             "Avg Initiate Tenure", C_TEAL, "View full breakdown in Tenure Analysis")

    with c6:
        toggle_show("ov_notcomp", df_notcomp, "ov_notcomp_list",
                    f"Initiated — Not Yet Completed ({len(df_notcomp)})", C_SLATE)
    with c7:
        if st.button("View Tenure Analysis", key="ov_nav_tenure", use_container_width=True):
            navigate_to("Tenure Analysis")

    render_toggle_list("ov_notcomp", df_notcomp,
                       f"Initiated — Not Yet Completed ({len(df_notcomp)})", C_SLATE)

    if "BGV Status" in df.columns:
        st.markdown("<br>", unsafe_allow_html=True)
        section("BGV Status Distribution")
        status_counts = df["BGV Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        colors = []
        for s in status_counts["Status"]:
            sl = s.lower()
            if "complete" in sl or "clear" in sl:      colors.append(C_GREEN)
            elif "pending" in sl or "initiated" in sl: colors.append(C_ORANGE)
            elif "orange" in sl:                       colors.append(C_AMBER)
            else:                                      colors.append(C_BLUE)
        pct_vals  = (status_counts["Count"] / status_counts["Count"].sum() * 100).round(1)
        text_vals = [f"{c} ({p}%)" for c, p in zip(status_counts["Count"], pct_vals)]
        fig = go.Figure(go.Bar(
            x=status_counts["Status"], y=status_counts["Count"],
            marker=dict(color=colors, line=dict(color="#000", width=1.5)),
            text=text_vals, textposition="outside",
            textfont=dict(size=12, color="#0F172A")
        ))
        style_fig(fig, xtitle="BGV Status", ytitle="Count", title="BGV Status Distribution")
        fig.update_layout(showlegend=False, height=320, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    if "DOJ" in df.columns and df["DOJ"].notna().sum() > 0:
        section("Monthly Joining Trend")
        df_doj = df[df["DOJ"].notna()].copy()
        df_doj["Join Month"] = df_doj["DOJ"].dt.strftime("%b %Y")
        df_doj["Sort"]       = df_doj["DOJ"].dt.to_period("M")
        monthly = df_doj.groupby(["Join Month", "Sort"]).size().reset_index(name="Joined").sort_values("Sort")
        pct_m  = (monthly["Joined"] / monthly["Joined"].sum() * 100).round(1)
        text_m = [f"{c} ({p}%)" for c, p in zip(monthly["Joined"], pct_m)]
        fig3 = go.Figure(go.Bar(
            x=monthly["Join Month"], y=monthly["Joined"],
            marker=dict(color=C_BLUE, line=dict(color="#1E3A5F", width=1.5)),
            text=text_m, textposition="outside",
            textfont=dict(size=11, color="#0F172A")
        ))
        style_fig(fig3, xtitle="Month", ytitle="Employees Joined", title="Monthly Joining Trend")
        fig3.update_layout(showlegend=False, height=310)
        st.plotly_chart(fig3, use_container_width=True)

        render_monthly_bgv_breakdown(
            df, date_col="DOJ",
            section_title="Monthly Joining — BGV Status Breakdown",
            toggle_key="ov_monthly_doj"
        )

    render_export(df)


# ─── PAGE: PENDING CASES ─────────────────────────────────────────────────────
def render_pending(df):
    back_to_overview_btn("pending_top")
    st.markdown("<br>", unsafe_allow_html=True)

    # FIX: pending_df strictly = has initiation date & no completion date
    # Employees with no initiation date do NOT appear here
    pending_df = df[df["Is Pending"]].copy()
    total_pend = len(pending_df)

    # FIX: "BGV Not Yet Initiated" — employees from full df with no BGV initiation date
    # (and not exceptional cases, and not orange report), shown as a separate awareness KPI
    has_init_all = df["BGV Initiated Date"].notna() if "BGV Initiated Date" in df.columns else pd.Series(False, index=df.index)
    has_comp_all = df["BGV Completion Date"].notna() if "BGV Completion Date" in df.columns else pd.Series(False, index=df.index)
    exc_mask     = df["Exceptional Case"].notna() if "Exceptional Case" in df.columns else pd.Series(False, index=df.index)
    orange_mask  = df["Has Orange Report"] if "Has Orange Report" in df.columns else pd.Series(False, index=df.index)
    not_init_df  = df[~has_init_all & ~has_comp_all & ~exc_mask & ~orange_mask].copy()

    section(f"Pending BGV Cases — {total_pend} employee(s)", C_ORANGE)
    if pending_df.empty and not_init_df.empty:
        st.success("No pending BGV cases!")
        render_export(df)
        return

    gt30_days = 0
    gt30_df   = pd.DataFrame()
    if "BGV Initiate Tenure" in pending_df.columns:
        mask_gt30 = pending_df["BGV Initiate Tenure"].fillna(0) > 30
        gt30_days = int(mask_gt30.sum())
        gt30_df   = pending_df[mask_gt30]

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, total_pend,        "Initiated — Awaiting Completion", C_ORANGE)
    kpi_card(c2, len(not_init_df),  "BGV Not Yet Initiated",           C_PURPLE)
    kpi_card(c3, gt30_days,         "Initiated > 1 Month Ago",         C_RED, "needs attention")
    kpi_card(c4, total_pend + len(not_init_df), "Total Action Required", C_AMBER)

    with c1: toggle_show("pend_all",    pending_df,  "pend_all_list",    f"Awaiting Completion ({total_pend})", C_ORANGE)
    with c2: toggle_show("pend_noinit", not_init_df, "pend_noinit_list", f"Not Yet Initiated ({len(not_init_df)})", C_PURPLE)
    with c3: toggle_show("pend_gt30",   gt30_df,     "pend_gt30_list",   f"Initiated > 1 Month ({gt30_days})", C_RED)

    render_toggle_list("pend_all",    pending_df,  f"Awaiting Completion ({total_pend})", C_ORANGE)
    render_toggle_list("pend_noinit", not_init_df, f"Not Yet Initiated ({len(not_init_df)})", C_PURPLE)
    render_toggle_list("pend_gt30",   gt30_df,     f"Initiated > 1 Month ({gt30_days})", C_RED)

    st.markdown("<br>", unsafe_allow_html=True)

    if not pending_df.empty:
        if "BGV Initiate Tenure" in pending_df.columns and pending_df["BGV Initiate Tenure"].notna().sum() > 0:
            section("Pending — Initiate Tenure Distribution", C_ORANGE)
            df_it = pending_df[pending_df["BGV Initiate Tenure"].notna()].copy()
            bins_it   = [0, 30, 60, 90, 180, float("inf")]
            labels_it = ["< 1M", "1-2M", "2-3M", "3-6M", "6M+"]
            df_it["Bucket"] = pd.cut(df_it["BGV Initiate Tenure"], bins=bins_it, labels=labels_it, right=True)
            bc_it = df_it["Bucket"].value_counts().reindex(labels_it, fill_value=0).reset_index()
            bc_it.columns = ["Bucket", "Count"]
            pct_it = (bc_it["Count"] / bc_it["Count"].sum() * 100).round(1)
            text_it = [f"{c} ({p}%)" for c, p in zip(bc_it["Count"], pct_it)]
            fig_it = go.Figure(go.Bar(
                x=bc_it["Bucket"], y=bc_it["Count"],
                marker=dict(color=[C_GREEN, C_TEAL, C_ORANGE, C_RED, C_PURPLE],
                            line=dict(color="#000", width=1.5)),
                text=text_it, textposition="outside",
                textfont=dict(size=11, color="#0F172A")
            ))
            style_fig(fig_it, xtitle="Time since Joining", ytitle="Employees",
                      title="How Long Pending BGV Was Awaiting Initiation")
            fig_it.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig_it, use_container_width=True)

        if "BGV Initiated Date" in pending_df.columns and pending_df["BGV Initiated Date"].notna().sum() > 0:
            render_monthly_bgv_breakdown(
                pending_df, date_col="BGV Initiated Date",
                section_title="Monthly BGV Initiated — Status Breakdown",
                toggle_key="pend_monthly_init"
            )

            section("Pending — BGV Initiated by Month", C_AMBER)
            df_im = pending_df[pending_df["BGV Initiated Date"].notna()].copy()
            df_im["Month"] = df_im["BGV Initiated Date"].dt.strftime("%b %Y")
            df_im["Sort"]  = df_im["BGV Initiated Date"].dt.to_period("M")
            m_cnt = df_im.groupby(["Month", "Sort"]).size().reset_index(name="Count").sort_values("Sort")
            fig_im = go.Figure(go.Scatter(
                x=m_cnt["Month"], y=m_cnt["Count"],
                mode="lines+markers+text",
                line=dict(color=C_AMBER, width=2.5),
                marker=dict(size=8, color=C_AMBER, line=dict(color="#78350F", width=1.5)),
                text=m_cnt["Count"], textposition="top center",
                textfont=dict(size=11, color="#0F172A")
            ))
            style_fig(fig_im, xtitle="Month", ytitle="Initiated", title="Pending Cases — BGV Initiated by Month")
            fig_im.update_layout(height=280)
            st.plotly_chart(fig_im, use_container_width=True)

        if "DOJ" in pending_df.columns and pending_df["DOJ"].notna().sum() > 0:
            render_monthly_bgv_breakdown(
                pending_df, date_col="DOJ",
                section_title="Pending Cohort — Monthly Joining BGV Breakdown",
                toggle_key="pend_monthly_doj"
            )

            section("Joining Cohort — Still Pending", C_PURPLE)
            df_doj = pending_df[pending_df["DOJ"].notna()].copy()
            df_doj["Join Month"] = df_doj["DOJ"].dt.strftime("%b %Y")
            df_doj["Sort"]       = df_doj["DOJ"].dt.to_period("M")
            jcoh = df_doj.groupby(["Join Month", "Sort"]).size().reset_index(name="Pending").sort_values("Sort")
            pct_jc = (jcoh["Pending"] / jcoh["Pending"].sum() * 100).round(1)
            text_jc = [f"{c} ({p}%)" for c, p in zip(jcoh["Pending"], pct_jc)]
            fig_jc = go.Figure(go.Bar(
                x=jcoh["Join Month"], y=jcoh["Pending"],
                marker=dict(color=C_PURPLE, line=dict(color="#4C1D95", width=1.5)),
                text=text_jc, textposition="outside",
                textfont=dict(size=11, color="#0F172A")
            ))
            style_fig(fig_jc, xtitle="Joining Month", ytitle="Still Pending",
                      title="Pending BGV by Employee Joining Month")
            fig_jc.update_layout(showlegend=False, height=290, xaxis_tickangle=-30)
            st.plotly_chart(fig_jc, use_container_width=True)

    render_export(pending_df)

    st.markdown("<br>", unsafe_allow_html=True)
    back_to_overview_btn("pending_bottom")


# ─── PAGE: ORANGE REPORT ─────────────────────────────────────────────────────
def render_orange(df):
    back_to_overview_btn("orange_top")
    st.markdown("<br>", unsafe_allow_html=True)

    orange_df    = df[df["Has Orange Report"]].copy()
    total_orange = len(orange_df)

    section(f"Orange Report Cases — {total_orange} employee(s)", C_AMBER)
    if orange_df.empty:
        st.success("No orange report cases found!")
        render_export(df)
        return

    has_comp_or    = orange_df["BGV Completion Date"].notna() if "BGV Completion Date" in orange_df.columns else pd.Series(False, index=orange_df.index)
    still_pending  = int((~has_comp_or).sum())
    resolved       = int(has_comp_or.sum())
    pending_or_df  = orange_df[~has_comp_or]
    resolved_or_df = orange_df[has_comp_or]

    c1, c2, c3 = st.columns(3)
    kpi_card(c1, total_orange,  "Total Orange Reports", C_AMBER)
    kpi_card(c2, still_pending, "Still Pending",         C_RED)
    kpi_card(c3, resolved,      "Resolved",              C_GREEN)

    with c1: toggle_show("or_all",      orange_df,      "or_all_list",      f"All Orange Reports ({total_orange})", C_AMBER)
    with c2: toggle_show("or_pending",  pending_or_df,  "or_pending_list",  f"Still Pending ({still_pending})",    C_RED)
    with c3: toggle_show("or_resolved", resolved_or_df, "or_resolved_list", f"Resolved ({resolved})",              C_GREEN)

    render_toggle_list("or_all",      orange_df,      f"All Orange Reports ({total_orange})", C_AMBER)
    render_toggle_list("or_pending",  pending_or_df,  f"Still Pending ({still_pending})", C_RED)
    render_toggle_list("or_resolved", resolved_or_df, f"Resolved ({resolved})", C_GREEN)

    if "BGV Orange Report Date" in orange_df.columns and orange_df["BGV Orange Report Date"].notna().sum() > 0:

        render_monthly_bgv_breakdown(
            orange_df, date_col="BGV Orange Report Date",
            section_title="Monthly Orange Reports — BGV Status Breakdown",
            toggle_key="or_monthly"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        section("Orange Report Timeline", C_AMBER)
        df_or = orange_df[orange_df["BGV Orange Report Date"].notna()].copy()
        df_or["Orange Month"] = df_or["BGV Orange Report Date"].dt.strftime("%b %Y")
        df_or["Sort"]         = df_or["BGV Orange Report Date"].dt.to_period("M")
        monthly_or = df_or.groupby(["Orange Month", "Sort"]).size().reset_index(name="Count").sort_values("Sort")
        fig2 = go.Figure(go.Scatter(
            x=monthly_or["Orange Month"], y=monthly_or["Count"],
            mode="lines+markers+text",
            line=dict(color=C_AMBER, width=2.5),
            marker=dict(size=8, color=C_AMBER, line=dict(color="#78350F", width=1.5)),
            text=monthly_or["Count"], textposition="top center",
            textfont=dict(size=11, color="#0F172A")
        ))
        style_fig(fig2, xtitle="Month", ytitle="Orange Reports", title="Orange Reports Over Time")
        fig2.update_layout(height=290)
        st.plotly_chart(fig2, use_container_width=True)

    render_export(orange_df)

    st.markdown("<br>", unsafe_allow_html=True)
    back_to_overview_btn("orange_bottom")


# ─── PAGE: TENURE ANALYSIS ───────────────────────────────────────────────────
def render_tenure(df):
    back_to_overview_btn("tenure_top")
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs([
        "Company to BGV (Initiate Tenure)",
        "BGV Verification (Complete Tenure)"
    ])
    with tab1:
        _render_initiate_tenure(df)
    with tab2:
        _render_complete_tenure(df)

    st.markdown("<br>", unsafe_allow_html=True)
    back_to_overview_btn("tenure_bottom")

def _render_initiate_tenure(df):
    col_name = "BGV Initiate Tenure"
    # FIX: only employees who actually have an initiation date have a tenure value
    # notna() filter already excludes no-init employees since tenure = None for them
    df_t = df[df[col_name].notna()].copy() if col_name in df.columns else pd.DataFrame()

    section("Time Taken by Organisation to Share BGV Details", C_TEAL)
    st.caption("Calculated as: BGV Initiated Date minus Date of Joining")

    if df_t.empty:
        st.info("No initiate tenure data available.")
        render_export(df)
        return

    avg  = df_t[col_name].mean()
    med  = df_t[col_name].median()
    gt30_df = df_t[df_t[col_name] > 30]
    le30_df = df_t[df_t[col_name] <= 30]

    c1, c2, c3 = st.columns(3)
    kpi_card(c1, f"{int(avg)}" if pd.notna(avg) else "N/A",   "Avg Duration",   C_TEAL, "no of days")
    kpi_card(c2, f"{int(med)}" if pd.notna(med) else "N/A",   "Median Duration", C_BLUE, "no of days")
    kpi_card(c3, len(gt30_df),                                  "> 1M (Late)",    C_ORANGE, "no of days")

    with c2: toggle_show("it_le30", le30_df, "it_le30_list", f"Within 1M ({len(le30_df)})", C_GREEN)
    with c3: toggle_show("it_gt30", gt30_df, "it_gt30_list", f"Over 1M ({len(gt30_df)})", C_ORANGE)

    render_toggle_list("it_le30", le30_df, f"Within 1M ({len(le30_df)})", C_GREEN)
    render_toggle_list("it_gt30", gt30_df, f"Over 1M ({len(gt30_df)})", C_ORANGE)

    st.markdown("<br>", unsafe_allow_html=True)
    bins_m   = [0, 30, 60, 90, 180, float("inf")]
    labels_m = ["< 1M", "1-2M", "2-3M", "3-6M", "6M+"]
    df_t["Bucket"] = pd.cut(df_t[col_name], bins=bins_m, labels=labels_m, right=True)
    bc = df_t["Bucket"].value_counts().reindex(labels_m, fill_value=0).reset_index()
    bc.columns = ["Bucket", "Count"]
    pct_bc = (bc["Count"] / bc["Count"].sum() * 100).round(1)
    text_bc = [f"{c} ({p}%)" for c, p in zip(bc["Count"], pct_bc)]
    fig = go.Figure(go.Bar(
        x=bc["Bucket"], y=bc["Count"],
        marker=dict(color=[C_GREEN, C_TEAL, C_BLUE, C_ORANGE, C_RED][:len(bc)],
                    line=dict(color="#000", width=1.5)),
        text=text_bc, textposition="outside",
        textfont=dict(size=11, color="#0F172A")
    ))
    style_fig(fig, xtitle="Duration", ytitle="Employees",
              title="Distribution — Time to Initiate BGV")
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

    if "DOJ" in df_t.columns and df_t["DOJ"].notna().sum() > 0:
        render_monthly_bgv_breakdown(
            df_t, date_col="DOJ",
            section_title="Monthly — Initiate Tenure BGV Status",
            toggle_key="it_monthly_doj"
        )

    render_export(df_t)

def _render_complete_tenure(df):
    col_name = "BGV Completed Tenure"
    # FIX: notna() filter already ensures only employees with both init+completion dates
    # appear here — employees without initiation dates naturally excluded
    df_t = df[df[col_name].notna()].copy() if col_name in df.columns else pd.DataFrame()

    section("Time Taken by BGV Agency to Complete Verification", C_INDIGO)
    st.caption("Calculated as: BGV Completion Date minus BGV Initiated Date")

    if df_t.empty:
        st.info("No completion tenure data available.")
        render_export(df)
        return

    avg  = df_t[col_name].mean()
    med  = df_t[col_name].median()
    gt14_df = df_t[df_t[col_name] > 14]
    le14_df = df_t[df_t[col_name] <= 14]

    c1, c2, c3 = st.columns(3)
    kpi_card(c1, f"{int(avg)}" if pd.notna(avg) else "N/A",   "Avg Duration",    C_INDIGO, "no of days")
    kpi_card(c2, f"{int(med)}" if pd.notna(med) else "N/A",   "Median Duration", C_BLUE, "no of days")
    kpi_card(c3, len(gt14_df),                                  "> 2 Weeks (Slow)", C_ORANGE, "no of days")

    with c2: toggle_show("ct_le14", le14_df, "ct_le14_list", f"Within 2W ({len(le14_df)})", C_GREEN)
    with c3: toggle_show("ct_gt14", gt14_df, "ct_gt14_list", f"Over 2W ({len(gt14_df)})", C_RED)

    render_toggle_list("ct_le14", le14_df, f"Within 2W ({len(le14_df)})", C_GREEN)
    render_toggle_list("ct_gt14", gt14_df, f"Over 2W ({len(gt14_df)})", C_RED)

    st.markdown("<br>", unsafe_allow_html=True)
    bins_c   = [0, 7, 14, 30, 60, float("inf")]
    labels_c = ["< 1W", "1-2W", "2-4W", "1-2M", "2M+"]
    df_t["Bucket"] = pd.cut(df_t[col_name], bins=bins_c, labels=labels_c, right=True)
    bc = df_t["Bucket"].value_counts().reindex(labels_c, fill_value=0).reset_index()
    bc.columns = ["Bucket", "Count"]
    pct_bc = (bc["Count"] / bc["Count"].sum() * 100).round(1)
    text_bc = [f"{c} ({p}%)" for c, p in zip(bc["Count"], pct_bc)]
    fig = go.Figure(go.Bar(
        x=bc["Bucket"], y=bc["Count"],
        marker=dict(color=[C_GREEN, C_TEAL, C_BLUE, C_ORANGE, C_RED][:len(bc)],
                    line=dict(color="#000", width=1.5)),
        text=text_bc, textposition="outside",
        textfont=dict(size=11, color="#0F172A")
    ))
    style_fig(fig, xtitle="Duration", ytitle="Employees",
              title="Distribution — Time to Complete BGV")
    fig.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

    if "BGV Agency" in df_t.columns and df_t["BGV Agency"].notna().sum() > 0:
        agency_avg = df_t.groupby("BGV Agency")[col_name].agg(["mean", "count"]).reset_index()
        agency_avg.columns = ["Agency", "Avg Days", "Count"]
        agency_avg["Avg Label"] = agency_avg["Avg Days"].apply(fmt_tenure)
        agency_avg = agency_avg.sort_values("Avg Days")
        fig3 = go.Figure(go.Bar(
            x=agency_avg["Agency"], y=agency_avg["Avg Days"],
            marker=dict(color=C_INDIGO, line=dict(color="#312E81", width=1.5)),
            text=agency_avg["Avg Label"], textposition="outside",
            textfont=dict(size=11, color="#0F172A")
        ))
        style_fig(fig3, xtitle="BGV Agency", ytitle="Avg Days",
                  title="Agency-wise Avg Completion Time")
        fig3.update_layout(showlegend=False, height=300, xaxis_tickangle=-30)
        st.plotly_chart(fig3, use_container_width=True)

    if "BGV Initiated Date" in df_t.columns and df_t["BGV Initiated Date"].notna().sum() > 0:
        render_monthly_bgv_breakdown(
            df_t, date_col="BGV Initiated Date",
            section_title="Monthly — Complete Tenure BGV Status",
            toggle_key="ct_monthly_init"
        )

    render_export(df_t)


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="color:white;font-weight:800;font-size:.95rem;padding:4px 0 8px">BGV Dashboard</div>',
                unsafe_allow_html=True)
    uploaded = st.file_uploader("Drop BGV Excel / CSV File", type=["xlsx", "xls", "csv"],
                                key="bgv_file")
    st.markdown("---")

    nav_index = st.session_state.get("_nav_index", 0)
    view_mode = st.radio("Navigation", NAV, index=nav_index,
                         label_visibility="collapsed")
    st.session_state["_nav_index"] = NAV.index(view_mode)
    st.markdown("---")

    if "bgv_data" in st.session_state and not st.session_state["bgv_data"].empty:
        df_f = st.session_state["bgv_data"]
        dept_opts  = ["All"] + sorted([x for x in df_f["Department"].dropna().unique() if x]) \
            if "Department"  in df_f.columns else ["All"]
        desig_opts = ["All"] + sorted([x for x in df_f["Designation"].dropna().unique() if x]) \
            if "Designation" in df_f.columns else ["All"]
        status_opts = ["All"] + sorted([x for x in df_f["BGV Status"].dropna().unique() if x]) \
            if "BGV Status" in df_f.columns else ["All"]

        sel_dept   = st.selectbox("Department",  dept_opts,
                                   index=dept_opts.index(st.session_state.get("f_dept", "All"))
                                         if st.session_state.get("f_dept", "All") in dept_opts else 0,
                                   key="f_dept")
        sel_desig  = st.selectbox("Designation", desig_opts,
                                   index=desig_opts.index(st.session_state.get("f_desig", "All"))
                                         if st.session_state.get("f_desig", "All") in desig_opts else 0,
                                   key="f_desig")
        sel_status = st.selectbox("BGV Status",  status_opts,
                                   index=status_opts.index(st.session_state.get("f_status", "All"))
                                         if st.session_state.get("f_status", "All") in status_opts else 0,
                                   key="f_status")
        st.markdown("---")
        if st.button("Reset Filters", use_container_width=True):
            st.session_state["f_dept"]   = "All"
            st.session_state["f_desig"]  = "All"
            st.session_state["f_status"] = "All"
            st.rerun()


# ─── LOAD FILE ────────────────────────────────────────────────────────────────
if uploaded:
    fhash = str(len(uploaded.getvalue())) + uploaded.name
    if st.session_state.get("_file_hash") != fhash:
        with st.spinner("Processing BGV data..."):
            raw = load_excel(uploaded.getvalue(), uploaded.name)
            if not raw.empty:
                st.session_state["bgv_data"]   = process_bgv(raw)
                st.session_state["_file_hash"] = fhash
            else:
                st.error("Could not read the file. Please check the format.")

if "bgv_data" not in st.session_state or st.session_state["bgv_data"].empty:
    st.markdown("""
    <div style="background:#1E293B;border-radius:14px;padding:60px 28px;text-align:center;
                margin-top:60px;max-width:620px;margin-left:auto;margin-right:auto">
      <div style="color:white;font-size:1.4rem;font-weight:800;margin-bottom:8px">Upload your file here</div>
      <div style="color:#94A3B8;font-size:.9rem;margin-bottom:20px;line-height:1.7">
        Upload file using the sidebar.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── APPLY FILTERS ───────────────────────────────────────────────────────────
df_all    = st.session_state["bgv_data"].copy()
sel_dept  = st.session_state.get("f_dept",   "All")
sel_desig = st.session_state.get("f_desig",  "All")
sel_status = st.session_state.get("f_status", "All")

df_view = df_all.copy()
if sel_dept   != "All" and "Department"  in df_view.columns:
    df_view = df_view[df_view["Department"]  == sel_dept]
if sel_desig  != "All" and "Designation" in df_view.columns:
    df_view = df_view[df_view["Designation"] == sel_desig]
if sel_status != "All" and "BGV Status"  in df_view.columns:
    df_view = df_view[df_view["BGV Status"]  == sel_status]

if df_view.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ─── PAGE HEADER ─────────────────────────────────────────────────────────────
total   = len(df_all)
f_total = len(df_view)
active  = [x for x in [
    f"Dept: {sel_dept}"     if sel_dept   != "All" else "",
    f"Desig: {sel_desig}"   if sel_desig  != "All" else "",
    f"Status: {sel_status}" if sel_status != "All" else "",
] if x]
filter_label = " · ".join(active) if active else "No active filters"

st.markdown(
    f'<div class="ph"><h1>BGV Analysis Dashboard</h1>'
    f'<p>Showing {f_total} of {total} employees &nbsp;·&nbsp; {filter_label}</p></div>',
    unsafe_allow_html=True)

# ─── ROUTE ───────────────────────────────────────────────────────────────────
_nav_idx = st.session_state.get("_nav_index", 0)
page = NAV[_nav_idx] if 0 <= _nav_idx < len(NAV) else NAV[0]
if   page == "Overview":          render_overview(df_view)
elif page == "Pending Cases":     render_pending(df_view)
elif page == "Orange Report":     render_orange(df_view)
elif page == "Tenure Analysis":   render_tenure(df_view)
elif page == "Employee View":
    section("Employee View — Full Search", C_BLUE)
    render_employee_list_cards(df_view, "emp_view_all")
    render_export(df_view)
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from streamlit_local_storage import LocalStorage

st.set_page_config(
    page_title="Stanford ChemE 4-Year Planner",
    page_icon="⚗️",
    layout="wide",
)

STANFORD_RED = "#8C1515"
YEARS = ["2026-2027", "2027-2028", "2028-2029", "2029-2030"]
QUARTERS = ["Fall", "Winter", "Spring", "Summer"]
SLOTS = 7
GRADES = ["", "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F", "CR", "NC", "W"]

st.markdown(f"""
<style>
    .main .block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 100%; }}
    .title-bar {{
        background: {STANFORD_RED};
        color: white;
        font-size: 26px;
        font-weight: 700;
        text-align: center;
        padding: 14px 20px;
        border-radius: 6px;
        margin-bottom: 18px;
    }}
    .year-band {{
        background: {STANFORD_RED};
        color: white;
        font-weight: 700;
        font-size: 14px;
        padding: 7px 14px;
        border-radius: 4px 4px 0 0;
        margin-top: 22px;
    }}
    .quarter-header {{
        background: {STANFORD_RED};
        color: white;
        font-weight: 600;
        font-size: 12px;
        text-align: center;
        padding: 4px 2px;
        border-radius: 3px;
        margin-bottom: 3px;
    }}
    .year-pill {{
        background: {STANFORD_RED};
        color: white;
        font-weight: 700;
        font-size: 13px;
        text-align: center;
        padding: 6px 3px;
        border-radius: 4px;
        height: 100%;
        min-height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .cat-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 600;
        color: white;
        margin-bottom: 2px;
    }}
    [data-testid="stSidebar"] {{ background: #fcfcfc; }}

    /* ── Course info cards ── */
    .course-info-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 4px 0 10px 0;
    }}
    .course-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3px solid var(--cat-color, #8C1515);
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 11.5px;
        line-height: 1.5;
        flex: 1 1 200px;
        min-width: 180px;
        max-width: 320px;
    }}
    .course-card-code {{ font-weight: 700; color: #1e293b; }}
    .course-card-name {{ color: #374151; margin-bottom: 3px; }}
    .course-card-meta {{ color: #64748b; font-size: 10.5px; }}
    .course-card-desc {{ color: #475569; font-size: 11px; margin-top: 4px; }}
</style>
""", unsafe_allow_html=True)

# ── Load Course Catalog from JSON ─────────────────────────────────────────────

CHEME_REQUIRED = {
    "CHEMENG 20", "CHEMENG 100", "CHEMENG 110A", "CHEMENG 110B",
    "CHEMENG 120A", "CHEMENG 120B", "CHEMENG 130A", "CHEMENG 130B",
    "CHEMENG 140", "CHEMENG 140X", "CHEMENG 150", "CHEMENG 160",
    "CHEMENG 185", "CHEMENG 190",
}

SUBJECT_TO_CAT = {
    "CHEMENG":  "ChemE",          # split below into Core vs Elective
    "MATH":     "Mathematics",
    "CME":      "Mathematics",
    "CHEM":     "Science",
    "PHYSICS":  "Science",
    "BIOE":     "Science",
    "BIO":      "Science",
    "HUMBIO":   "Science",
    "CS":       "Engineering",
    "ENGR":     "Engineering",
    "ME":       "Engineering",
    "EE":       "Engineering",
    "MATSCI":   "Engineering",
    "CEE":      "Engineering",
    "STS":      "Technology in Society",
    "ETHICSOC": "Technology in Society",
    "ESS":      "Other Elective",
    "ENERGY":   "Other Elective",
    "STATS":    "Other Elective",
    "ECON":     "Other Elective",
    "PWR":      "General Education",
    "THINK":    "General Education",
}

CAT_COLORS = {
    "ChemE Core":              "#B91C1C",
    "ChemE Elective":          "#DB2777",
    "Mathematics":             "#2563EB",
    "Science":                 "#16A34A",
    "Engineering":             "#EA580C",
    "Technology in Society":   "#7C3AED",
    "General Education":       "#6B7280",
    "Other Elective":          "#0891B2",
}

@st.cache_data
def load_catalog():
    path = Path(__file__).parent / "courses.json"
    with open(path) as f:
        raw = json.load(f)
    catalog = []
    for c in raw:
        subj = c.get("subject", "")
        code = c["code"]
        if subj == "CHEMENG":
            cat = "ChemE Core" if code in CHEME_REQUIRED else "ChemE Elective"
        else:
            cat = SUBJECT_TO_CAT.get(subj, "Other Elective")
        catalog.append({
            "code":     code,
            "name":     c["name"],
            "units":    c["units"],
            "units_max":c.get("units_max", c["units"]),
            "desc":     c.get("desc",""),
            "gers":     c.get("gers",""),
            "qtrs":     c.get("qtrs",[]),
            "subject":  subj,
            "cat":      cat,
        })
    return catalog

CATALOG = load_catalog()
CATALOG_BY_CODE = {c["code"]: c for c in CATALOG}
COURSE_CODES = [""] + [c["code"] for c in CATALOG]

# ── ChemE BS Requirements ─────────────────────────────────────────────────────

REQUIREMENTS = {
    "Mathematics": {
        "min_units": 15,
        "required": ["MATH 19","MATH 20","MATH 21","CME 100","CME 102"],
        "alts": {"MATH 19":"MATH 41","MATH 20":"MATH 42","CME 100":"MATH 51","CME 102":"MATH 53"},
        "note": "15-17 units. Calc sequence + CME 100 + CME 102. Alts allowed.",
        "cats": ["Mathematics"],
    },
    "Science": {
        "min_units": 23,
        "required": ["CHEM 31A","CHEM 31B","CHEM 35","PHYSICS 41","PHYSICS 43","BIOE 80"],
        "alts": {"CHEM 31A":"CHEM 33","CHEM 31B":"CHEM 33","BIOE 80":"BIO 82"},
        "note": "23-29 units. Chemistry, physics, biology courses.",
        "cats": ["Science"],
    },
    "Technology in Society": {
        "min_units": 3,
        "required": [],
        "alts": {},
        "note": "3-5 units. One SoE-approved TiS course. See ughb.stanford.edu for list.",
        "cats": ["Technology in Society"],
    },
    "Engineering Fundamentals": {
        "min_units": 8,
        "required": [],
        "alts": {},
        "note": "8 units. Two engineering foundation courses (e.g. CS 106A + ENGR 40M).",
        "cats": ["Engineering"],
    },
    "ChemE Core": {
        "min_units": 46,
        "required": [
            "CHEMENG 20","CHEMENG 110A","CHEMENG 110B",
            "CHEMENG 120A","CHEMENG 120B","CHEMENG 130A",
            "CHEMENG 130B","CHEMENG 140","CHEMENG 150",
            "CHEMENG 160","CHEMENG 185","CHEMENG 190",
        ],
        "alts": {"CHEMENG 140":"CHEMENG 140X"},
        "note": "46 units min. Required core courses + ChemE electives. 95 total major units.",
        "cats": ["ChemE Core","ChemE Elective"],
    },
}

# ── Session State ─────────────────────────────────────────────────────────────

def _empty_df():
    return pd.DataFrame({
        "Course": [""] * SLOTS,
        "Units":  [0]   * SLOTS,
        "Grade":  [""]  * SLOTS,
    })

def _serialize_plan(plan):
    return {yr: {q: plan[yr][q].fillna("").to_dict("records") for q in QUARTERS} for yr in YEARS}

def _deserialize_plan(data):
    plan = {}
    for yr in YEARS:
        plan[yr] = {}
        for q in QUARTERS:
            records = data.get(yr, {}).get(q, [])
            df = pd.DataFrame(records) if records else _empty_df()
            for col in ["Course", "Units", "Grade"]:
                if col not in df.columns:
                    df[col] = "" if col != "Units" else 0
            df["Units"] = pd.to_numeric(df["Units"], errors="coerce").fillna(0).astype(int)
            plan[yr][q] = df[["Course", "Units", "Grade"]].head(SLOTS)
    return plan

_ls = LocalStorage()
_LS_KEY = "stanford_cheme_plan_v1"

if "plan" not in st.session_state:
    st.session_state.plan = {yr: {q: _empty_df() for q in QUARTERS} for yr in YEARS}
    st.session_state._ls_attempts = 0
    st.session_state._ls_ready = False

# Try to load from localStorage until confirmed (component needs 1-2 reruns to mount)
if not st.session_state._ls_ready:
    _saved = _ls.getItem(_LS_KEY)
    if _saved is not None:
        try:
            st.session_state.plan = _deserialize_plan(_saved)
        except Exception:
            pass
        st.session_state._ls_ready = True
    else:
        st.session_state._ls_attempts += 1
        if st.session_state._ls_attempts >= 2:
            st.session_state._ls_ready = True  # confirmed: nothing saved

# ── Helpers ───────────────────────────────────────────────────────────────────

def all_scheduled_codes():
    codes = set()
    for yr_data in st.session_state.plan.values():
        for df in yr_data.values():
            for code in df["Course"]:
                s = str(code).strip()
                if s: codes.add(s)
    return codes

def units_by_cats(cat_list):
    total = 0
    for yr_data in st.session_state.plan.values():
        for df in yr_data.values():
            for _, row in df.iterrows():
                code = str(row["Course"]).strip()
                if code and code in CATALOG_BY_CODE and CATALOG_BY_CODE[code]["cat"] in cat_list:
                    try: total += int(row["Units"]) if pd.notna(row["Units"]) else 0
                    except: pass
    return total

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"<h2 style='color:{STANFORD_RED};margin-bottom:2px'>⚗️ ChemE Planner</h2>", unsafe_allow_html=True)
    st.caption(f"**{len(CATALOG):,} Stanford courses** loaded from ExploreCourses")

    tab_cat, tab_req, tab_help = st.tabs(["📚 Catalog", "✅ Progress", "ℹ️ Help"])

    with tab_cat:
        search = st.text_input("🔍 Search courses", placeholder="e.g. thermo, CHEMENG 110, BIO")
        cat_filter = st.selectbox("Category", ["All"] + list(CAT_COLORS.keys()), label_visibility="collapsed")

        _q = search.lower().replace(" ", "")
        _sl = search.lower()
        def _rank(c):
            code_match = _q in c["code"].lower().replace(" ", "")
            name_match = _sl in c["name"].lower()
            return 0 if code_match else (1 if name_match else 2)
        filtered = sorted(
            [c for c in CATALOG
             if (_q in c["code"].lower().replace(" ", "") or _sl in c["name"].lower()
                 or _sl in c["desc"].lower())
             and (cat_filter == "All" or c["cat"] == cat_filter)],
            key=_rank
        )[:120]

        if not filtered:
            st.info("No courses match. Try a different search.")
        else:
            by_cat: dict = {}
            for c in filtered:
                by_cat.setdefault(c["cat"], []).append(c)
            for cat, courses in by_cat.items():
                color = CAT_COLORS.get(cat, "#555")
                st.markdown(f"<span class='cat-badge' style='background:{color}'>{cat}</span>", unsafe_allow_html=True)
                for c in courses:
                    u_str = f"{c['units']}" if c["units"] == c["units_max"] else f"{c['units']}-{c['units_max']}"
                    qtrs_str = " · ".join(c["qtrs"]) if c["qtrs"] else "varies"
                    gers_str = f" · {c['gers']}" if c.get("gers") else ""
                    st.markdown(
                        f"**`{c['code']}`** &nbsp;{u_str}u &nbsp;·&nbsp; "
                        f"<small style='color:#444'>{c['name']}</small>  \n"
                        f"<small style='color:#888'>🗓 {qtrs_str}{gers_str}</small>",
                        unsafe_allow_html=True,
                    )
                    if c.get("desc"):
                        with st.expander("Course description"):
                            st.write(c["desc"])

    with tab_req:
        codes_in_plan = all_scheduled_codes()
        total_major = units_by_cats(list(CAT_COLORS.keys()))
        remaining = max(0, 95 - total_major)
        ca, cb = st.columns(2)
        ca.metric("Major Units", total_major)
        cb.metric("Still Needed", remaining)
        st.progress(min(1.0, total_major / 95), text=f"{total_major} / 95 units")
        st.divider()

        for req_name, req in REQUIREMENTS.items():
            required = req["required"]
            alts = req.get("alts", {})
            # A required course is satisfied if code OR its alt is in plan
            satisfied = []
            missing = []
            for c in required:
                if c in codes_in_plan or alts.get(c,"") in codes_in_plan:
                    satisfied.append(c)
                else:
                    missing.append(c)
            u_done = units_by_cats(req["cats"])
            u_need = req["min_units"]
            all_ok = (not missing) and (u_done >= u_need)
            icon = "✅" if all_ok else "🔴"

            with st.expander(f"{icon} **{req_name}** · {u_done}/{u_need}u"):
                st.progress(min(1.0, u_done / u_need) if u_need else 1.0)
                if missing:
                    st.markdown("**Still needed:**")
                    for c in missing:
                        alt = alts.get(c,"")
                        alt_str = f" *(or `{alt}`)*" if alt else ""
                        st.markdown(f"◻ `{c}`{alt_str}")
                if satisfied:
                    st.markdown("**Satisfied:**")
                    for c in satisfied:
                        st.markdown(f"✓ `{c}`")
                st.caption(req["note"])

    with tab_help:
        st.markdown(f"""
**{len(CATALOG):,} courses** loaded live from ExploreCourses (2025-26).

**How to use:**
1. Click a **Course** cell → type to search → pick from dropdown
2. **Units** auto-fill when you pick a known code
3. Fill **Grade** once you complete the course
4. Check the **Progress** tab for requirement status

**Tip:** Search the **Catalog** tab first to find course codes, then pick from the grid dropdown.

**Verify requirements at:**  
[ughb.stanford.edu](https://ughb.stanford.edu/majors-minors/chemical-engineering-program)
""")

# ── Main Grid ─────────────────────────────────────────────────────────────────

st.markdown('<div class="title-bar">Stanford 4 Year Plan · Chemical Engineering</div>', unsafe_allow_html=True)

QUARTER_COL_CFG = {
    "Course": st.column_config.SelectboxColumn(
        "Course", options=COURSE_CODES, width="medium", required=False,
        help="Type to search, then select",
    ),
    "Units": st.column_config.NumberColumn(
        "Unts", min_value=0, max_value=20, step=1, width="small",
    ),
    "Grade": st.column_config.SelectboxColumn(
        "Grade", options=GRADES, width="small", required=False,
    ),
}

def _course_cards_html(yr: str) -> str:
    """Build compact info cards for all courses in a year, grouped by quarter."""
    cards = []
    for q in QUARTERS:
        df = st.session_state.plan[yr][q]
        for _, row in df.iterrows():
            code = str(row["Course"]).strip()
            if not code:
                continue
            c = CATALOG_BY_CODE.get(code)
            if not c:
                continue
            cat_color = CAT_COLORS.get(c["cat"], "#8C1515")
            u_str = f"{c['units']}u" if c["units"] == c["units_max"] else f"{c['units']}–{c['units_max']}u"
            qtrs_str = " · ".join(c["qtrs"]) if c["qtrs"] else "varies"
            gers_str = f" &nbsp;·&nbsp; {c['gers']}" if c.get("gers") else ""
            desc_str = f'<div class="course-card-desc">{c["desc"][:200]}</div>' if c.get("desc") else ""
            cards.append(
                f'<div class="course-card" style="--cat-color:{cat_color}">'
                f'<span class="course-card-code">{code}</span>'
                f'<div class="course-card-name">{c["name"]}</div>'
                f'<div class="course-card-meta">{q} &nbsp;·&nbsp; {u_str} &nbsp;·&nbsp; {qtrs_str}{gers_str}</div>'
                f'{desc_str}'
                f'</div>'
            )
    if not cards:
        return ""
    return '<div class="course-info-row">' + "".join(cards) + "</div>"

for yr in YEARS:
    st.markdown(f'<div class="year-band">📅 &nbsp; {yr}</div>', unsafe_allow_html=True)

    yr_col, *q_cols, tot_col = st.columns([0.5, 3, 3, 3, 3, 0.7])

    with yr_col:
        st.markdown(
            f'<div class="year-pill"><span style="writing-mode:vertical-rl;transform:rotate(180deg)">{yr}</span></div>',
            unsafe_allow_html=True,
        )

    year_units = 0
    for col, q in zip(q_cols, QUARTERS):
        with col:
            st.markdown(f'<div class="quarter-header">{q}</div>', unsafe_allow_html=True)
            current = st.session_state.plan[yr][q]
            edited = st.data_editor(
                current,
                key=f"de_{yr}_{q}",
                column_config=QUARTER_COL_CFG,
                hide_index=True,
                num_rows="fixed",
                use_container_width=True,
                height=SLOTS * 36 + 38,
            )
            for i, row in edited.iterrows():
                code = str(row["Course"]).strip()
                prev_code = str(current.at[i, "Course"]).strip()
                if code and code in CATALOG_BY_CODE:
                    if code != prev_code or (pd.isna(row["Units"]) or int(row["Units"]) == 0):
                        edited.at[i, "Units"] = CATALOG_BY_CODE[code]["units"]
            st.session_state.plan[yr][q] = edited

            try:
                q_units = int(edited["Units"].fillna(0).astype(int).sum())
            except Exception:
                q_units = 0
            year_units += q_units
            u_color = "#16A34A" if 0 < q_units <= 20 else ("#888" if q_units == 0 else STANFORD_RED)
            st.markdown(
                f"<div style='text-align:center;font-size:12px;color:{u_color};font-weight:600'>{q_units} units</div>",
                unsafe_allow_html=True,
            )

    with tot_col:
        st.markdown(
            f"""<div style="text-align:center;padding-top:40px">
                <div style="font-size:11px;color:#888;font-weight:600">TOTAL</div>
                <div style="font-size:26px;font-weight:700;color:{STANFORD_RED}">{year_units}</div>
                <div style="font-size:11px;color:#888">units</div>
            </div>""",
            unsafe_allow_html=True,
        )


# ── Requirements Summary ──────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### Requirements Summary")
codes_now = all_scheduled_codes()
req_cols = st.columns(len(REQUIREMENTS))

for col, (req_name, req) in zip(req_cols, REQUIREMENTS.items()):
    with col:
        color = CAT_COLORS.get(req["cats"][0], STANFORD_RED)
        alts = req.get("alts", {})
        done = sum(1 for c in req["required"] if c in codes_now or alts.get(c,"") in codes_now)
        total_req = len(req["required"])
        u_done = units_by_cats(req["cats"])
        u_need = req["min_units"]
        pct = min(100, int(u_done / u_need * 100)) if u_need else 100
        ok = (done == total_req) and (u_done >= u_need)
        st.markdown(f"<span class='cat-badge' style='background:{color}'>{req_name}</span>", unsafe_allow_html=True)
        st.progress(pct / 100)
        status = "✅ Done" if ok else f"🔴 {u_need - u_done}u needed"
        st.markdown(f"**{u_done}/{u_need}u** &nbsp; {status}", unsafe_allow_html=True)
        missing_req = [c for c in req["required"] if c not in codes_now and alts.get(c,"") not in codes_now]
        if missing_req:
            st.caption("Need: " + ", ".join(missing_req[:3]) + ("…" if len(missing_req) > 3 else ""))

# ── Auto-save to browser localStorage ────────────────────────────────────────
if st.session_state._ls_ready:
    _ls.setItem(_LS_KEY, _serialize_plan(st.session_state.plan))

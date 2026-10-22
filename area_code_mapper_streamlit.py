import io
import os
import zipfile
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Area Code Mapper & Duplicate Remover", page_icon="📞", layout="wide")

# Internal area code to state mapping
INTERNAL_AREA_CODE_MAP = {
    "201": "NJ", "907": "AK", "205": "AL", "251": "AL", "256": "AL", "334": "AL", "659": "AL", "938": "AL",
    "479": "AR", "501": "AR", "870": "AR", "480": "AZ", "520": "AZ", "602": "AZ", "623": "AZ", "928": "AZ",
    "209": "CA", "213": "CA", "279": "CA", "310": "CA", "323": "CA", "341": "CA", "369": "CA", "408": "CA",
    "415": "CA", "424": "CA", "442": "CA", "510": "CA", "530": "CA", "559": "CA", "562": "CA", "619": "CA",
    "626": "CA", "627": "CA", "628": "CA", "650": "CA", "657": "CA", "661": "CA", "669": "CA", "707": "CA",
    "714": "CA", "747": "CA", "760": "CA", "764": "CA", "805": "CA", "818": "CA", "831": "CA", "858": "CA",
    "909": "CA", "916": "CA", "925": "CA", "935": "CA", "949": "CA", "951": "CA", "840": "CA", "738": "CA",
    "820": "CA", "958": "CA", "303": "CO", "719": "CO", "720": "CO", "970": "CO", "983": "CO",
    "203": "CT", "475": "CT", "860": "CT", "959": "CT",
    "202": "DC", "302": "DE",
    "239": "FL", "305": "FL", "321": "FL", "352": "FL", "386": "FL", "407": "FL", "561": "FL", "689": "FL",
    "727": "FL", "754": "FL", "772": "FL", "786": "FL", "813": "FL", "850": "FL", "863": "FL", "904": "FL",
    "927": "FL", "941": "FL", "954": "FL", "448": "FL", "656": "FL",
    "229": "GA", "404": "GA", "470": "GA", "478": "GA", "678": "GA", "706": "GA", "762": "GA", "770": "GA", "912": "GA",
    "808": "HI",
    "319": "IA", "515": "IA", "563": "IA", "712": "IA", "641": "IA",
    "208": "ID", "986": "ID",
    "217": "IL", "224": "IL", "309": "IL", "312": "IL", "331": "IL", "464": "IL", "618": "IL", "630": "IL",
    "708": "IL", "773": "IL", "779": "IL", "815": "IL", "847": "IL", "872": "IL", "447": "IL",
    "219": "IN", "260": "IN", "317": "IN", "463": "IN", "574": "IN", "765": "IN", "812": "IN", "930": "IN",
    "316": "KS", "620": "KS", "785": "KS", "913": "KS",
    "270": "KY", "502": "KY", "606": "KY", "859": "KY", "364": "KY",
    "225": "LA", "318": "LA", "337": "LA", "504": "LA", "985": "LA",
    "339": "MA", "351": "MA", "413": "MA", "508": "MA", "617": "MA", "774": "MA", "781": "MA", "857": "MA", "978": "MA",
    "240": "MD", "301": "MD", "410": "MD", "443": "MD", "667": "MD",
    "207": "ME",
    "231": "MI", "248": "MI", "269": "MI", "278": "MI", "313": "MI", "517": "MI", "586": "MI", "616": "MI", "679": "MI",
    "734": "MI", "810": "MI", "906": "MI", "947": "MI", "989": "MI",
    "218": "MN", "320": "MN", "507": "MN", "612": "MN", "651": "MN", "763": "MN", "952": "MN",
    "314": "MO", "417": "MO", "557": "MO", "573": "MO", "636": "MO", "660": "MO", "816": "MO", "975": "MO",
    "228": "MS", "601": "MS", "662": "MS", "769": "MS",
    "406": "MT",
    "252": "NC", "336": "NC", "704": "NC", "743": "NC", "828": "NC", "910": "NC", "919": "NC", "980": "NC", "984": "NC",
    "701": "ND",
    "308": "NE", "402": "NE", "531": "NE",
    "603": "NH",
    "551": "NJ", "609": "NJ", "732": "NJ", "848": "NJ", "856": "NJ", "862": "NJ", "908": "NJ", "973": "NJ", "640": "NJ",
    "505": "NM", "575": "NM", "957": "NM",
    "702": "NV", "725": "NV", "775": "NV",
    "212": "NY", "315": "NY", "332": "NY", "347": "NY", "516": "NY", "518": "NY", "585": "NY", "631": "NY", "646": "NY",
    "716": "NY", "718": "NY", "845": "NY", "914": "NY", "917": "NY", "929": "NY", "680": "NY", "838": "NY", "934": "NY",
    "216": "OH", "220": "OH", "234": "OH", "283": "OH", "330": "OH", "380": "OH", "419": "OH", "440": "OH", "513": "OH",
    "567": "OH", "614": "OH", "740": "OH", "937": "OH", "326": "OH",
    "405": "OK", "539": "OK", "580": "OK", "918": "OK", "572": "OK",
    "458": "OR", "503": "OR", "541": "OR", "971": "OR",
    "215": "PA", "223": "PA", "267": "PA", "272": "PA", "412": "PA", "484": "PA", "570": "PA", "610": "PA",
    "717": "PA", "724": "PA", "814": "PA", "835": "PA", "878": "PA", "445": "PA", "582": "PA",
    "450": "QC",
    "401": "RI",
    "803": "SC", "843": "SC", "864": "SC", "839": "SC", "854": "SC",
    "605": "SD",
    "423": "TN", "615": "TN", "629": "TN", "731": "TN", "865": "TN", "901": "TN", "931": "TN",
    "210": "TX", "214": "TX", "254": "TX", "281": "TX", "325": "TX", "346": "TX", "361": "TX", "409": "TX",
    "430": "TX", "432": "TX", "469": "TX", "512": "TX", "682": "TX", "713": "TX", "737": "TX", "806": "TX",
    "817": "TX", "830": "TX", "832": "TX", "903": "TX", "915": "TX", "936": "TX", "940": "TX", "956": "TX",
    "972": "TX", "979": "TX", "726": "TX", "945": "TX",
    "385": "UT", "435": "UT", "801": "UT",
    "276": "VA", "434": "VA", "540": "VA", "571": "VA", "703": "VA", "757": "VA", "804": "VA", "826": "VA", "948": "VA",
    "802": "VT",
    "206": "WA", "253": "WA", "360": "WA", "425": "WA", "509": "WA", "564": "WA",
    "262": "WI", "414": "WI", "608": "WI", "715": "WI", "920": "WI", "534": "WI",
    "304": "WV", "681": "WV",
    "307": "WY",
    "340": "VI"
}

# Area code to timezone mapping from user input
AREA_CODE_TIMEZONE_MAP = {
    "201": "EST", "907": "PST", "205": "CST", "251": "CST", "256": "CST", "334": "CST", "659": "CST", "938": "CST",
    "479": "CST", "501": "CST", "870": "CST", "480": "PST", "520": "PST", "602": "PST", "623": "PST", "928": "PST",
    "209": "PST", "213": "PST", "279": "PST", "310": "PST", "323": "PST", "341": "PST", "369": "PST", "408": "PST",
    "415": "PST", "424": "PST", "442": "PST", "510": "PST", "530": "PST", "559": "PST", "562": "PST", "619": "PST",
    "626": "PST", "627": "PST", "628": "PST", "650": "PST", "657": "PST", "661": "PST", "669": "PST", "707": "PST",
    "714": "PST", "747": "PST", "760": "PST", "764": "PST", "805": "PST", "818": "PST", "831": "PST", "858": "PST",
    "909": "PST", "916": "PST", "925": "PST", "935": "PST", "949": "PST", "951": "PST", "840": "PST", "738": "PST",
    "820": "PST", "958": "PST", "303": "MST", "719": "MST", "720": "MST", "970": "MST", "983": "MST",
    "203": "EST", "475": "EST", "860": "EST", "959": "EST",
    "202": "EST", "302": "PST",
    "239": "EST", "305": "EST", "321": "EST", "352": "EST", "386": "EST", "407": "EST", "561": "EST", "689": "EST",
    "727": "EST", "754": "EST", "772": "EST", "786": "EST", "813": "EST", "850": "EST", "863": "EST", "904": "EST",
    "927": "EST", "941": "EST", "954": "EST", "448": "EST", "656": "EST",
    "229": "EST", "404": "EST", "470": "EST", "478": "EST", "678": "EST", "706": "EST", "762": "EST", "770": "EST", "912": "EST",
    "808": "HST",
    "319": "CST", "515": "CST", "563": "CST", "712": "CST", "641": "CST",
    "208": "MST", "986": "MST",
    "217": "CST", "224": "CST", "309": "CST", "312": "CST", "331": "CST", "464": "CST", "618": "CST", "630": "CST",
    "708": "CST", "773": "CST", "779": "CST", "815": "CST", "847": "CST", "872": "CST",
    "219": "CST", "260": "CST", "317": "CST", "463": "CST", "574": "CST", "765": "CST", "812": "CST", "930": "CST",
    "316": "CST", "620": "CST", "785": "CST", "913": "CST",
    "270": "EST", "502": "EST", "606": "EST", "859": "EST", "364": "EST",
    "225": "PST", "318": "PST", "337": "PST", "504": "PST", "985": "PST",
    "339": "EST", "351": "EST", "413": "EST", "508": "EST", "617": "EST", "774": "EST", "781": "EST", "857": "EST", "978": "EST",
    "240": "EST", "301": "EST", "410": "EST", "443": "EST", "667": "EST",
    "207": "EST",
    "231": "EST", "248": "EST", "269": "EST", "278": "EST", "313": "EST", "517": "EST", "586": "EST", "616": "EST", "679": "EST",
    "734": "EST", "810": "EST", "906": "EST", "947": "EST", "989": "EST",
    "218": "CST", "320": "CST", "507": "CST", "612": "CST", "651": "CST", "763": "CST", "952": "CST",
    "314": "CST", "417": "CST", "557": "CST", "573": "CST", "636": "CST", "660": "CST", "816": "CST", "975": "CST",
    "228": "CST", "601": "CST", "662": "CST", "769": "CST",
    "406": "MST",
    "252": "EST", "336": "EST", "704": "EST", "743": "EST", "828": "EST", "910": "EST", "919": "EST", "980": "EST", "984": "EST",
    "701": "CST",
    "308": "CST", "402": "CST", "531": "CST",
    "603": "EST",
    "551": "EST", "609": "EST", "732": "EST", "848": "EST", "856": "EST", "862": "EST", "908": "EST", "973": "EST", "640": "EST",
    "505": "MST", "575": "MST", "957": "MST",
    "702": "PST", "725": "PST", "775": "PST",
    "212": "EST", "315": "EST", "332": "EST", "347": "EST", "516": "EST", "518": "EST", "585": "EST", "631": "EST", "646": "EST",
    "716": "EST", "718": "EST", "845": "EST", "914": "EST", "917": "EST", "929": "EST", "680": "EST", "838": "EST", "934": "EST",
    "216": "EST", "220": "EST", "234": "EST", "283": "EST", "330": "EST", "380": "EST", "419": "EST", "440": "EST", "513": "EST",
    "567": "EST", "614": "EST", "740": "EST", "937": "EST", "326": "EST",
    "405": "CST", "539": "CST", "580": "CST", "918": "CST",
    "458": "PST", "503": "PST", "541": "PST", "971": "PST",
    "215": "EST", "223": "EST", "267": "EST", "272": "EST", "412": "EST", "484": "EST", "570": "EST", "610": "EST",
    "717": "EST", "724": "EST", "814": "EST", "835": "EST", "878": "EST", "445": "MST", "582": "MST",
    "450": "EST",
    "401": "EST",
    "803": "EST", "843": "EST", "864": "EST", "839": "EST", "854": "EST",
    "605": "CST",
    "423": "CST", "615": "CST", "629": "CST", "731": "CST", "865": "CST", "901": "CST", "931": "CST",
    "210": "CST", "214": "CST", "254": "CST", "281": "CST", "325": "CST", "346": "CST", "361": "CST", "409": "CST",
    "430": "CST", "432": "CST", "469": "CST", "512": "CST", "682": "CST", "713": "CST", "737": "CST", "806": "CST",
    "817": "CST", "830": "CST", "832": "CST", "903": "CST", "915": "CST", "936": "CST", "940": "CST", "956": "CST",
    "972": "CST", "979": "CST", "726": "CST", "945": "CST",
    "385": "MST", "435": "MST", "801": "MST",
    "276": "EST", "434": "EST", "540": "EST", "571": "EST", "703": "EST", "757": "EST", "804": "EST", "826": "EST", "948": "EST",
    "802": "EST",
    "206": "PST", "253": "PST", "360": "PST", "425": "PST", "509": "PST", "564": "PST",
    "262": "CST", "414": "CST", "608": "CST", "715": "CST", "920": "CST", "534": "CST",
    "304": "CST", "681": "EST", "307": "EST",
    "340": "EST"
}


def normalize_area_code(value):
    text = str(value).strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits[:3] if len(digits) >= 10 else None


def load_custom_mapping(uploaded_file):
    mapping_df = pd.read_csv(uploaded_file, dtype=str)
    mapping_df.columns = mapping_df.columns.str.strip().str.lower()
    if not {"area_code", "state"}.issubset(mapping_df.columns):
        raise ValueError("Custom mapping CSV must contain 'area_code' and 'state' columns.")
    mapping_df["area_code"] = mapping_df["area_code"].astype(str).str.extract(r"(\d{3})", expand=False)
    mapping_df["state"] = mapping_df["state"].astype(str).str.strip().str.upper()
    mapping_df = mapping_df.dropna(subset=["area_code", "state"])
    return dict(zip(mapping_df["area_code"], mapping_df["state"]))


def process_uploaded_file(uploaded_file, area_code_map, remove_duplicates):
    extension = os.path.splitext(uploaded_file.name)[1].lower()
    if extension == ".csv":
        df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
    elif extension == ".xlsx":
        df = pd.read_excel(uploaded_file, dtype=str, keep_default_na=False)
    else:
        raise ValueError("Unsupported file type. Please upload a CSV or XLSX file.")
    if df.empty or len(df.columns) == 0:
        raise ValueError("The file is empty or has no columns.")

    first_col = df.columns[0]
    # Clean common formatting characters while retaining the source columns.
    cleaned = df[first_col].astype(str).str.replace(r"\D", "", regex=True)
    cleaned = cleaned.apply(lambda x: x[1:] if len(x) == 11 and x.startswith("1") else x)
    valid_mask = cleaned.str.len() == 10
    df = df.loc[valid_mask].copy()
    df[first_col] = cleaned.loc[valid_mask]

    df["AreaCode"] = df[first_col].str[:3]
    df["State"] = df["AreaCode"].map(area_code_map).fillna("Unknown")
    df["Timezone"] = df["AreaCode"].map(AREA_CODE_TIMEZONE_MAP).fillna("Unknown")
    before_dedup = len(df)
    if remove_duplicates:
        df = df.drop_duplicates(subset=[first_col], keep="first")
    return df, before_dedup - len(df)


def make_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


st.title("📞 Area Code Mapper & Duplicate Remover")
st.caption("Upload one or more CSV or XLSX files, map phone numbers to states and time zones, remove duplicates, and download the processed files.")
st.info(
    "Privacy: this app does not write uploaded files or results to disk, a database, or the GitHub repository. "
    "Files/results are handled in the active app session's memory. If this app is hosted on Streamlit Community Cloud, "
    "uploads are still transmitted to and processed by Streamlit's servers; use the local version for files that must never leave your computer."
)

with st.sidebar:
    st.header("Processing Options")
    use_internal_mapping = st.checkbox("Use built-in area-code mapping", value=True)
    custom_mapping_file = st.file_uploader(
        "Custom mapping CSV (area_code, state)", type=["csv"],
        disabled=use_internal_mapping,
        help="Used when the built-in mapping checkbox is turned off. Required columns: area_code and state."
    )
    remove_duplicates = st.checkbox("Remove duplicate phone numbers", value=True)
    filter_mode = st.radio("Filter output by", ["State", "Timezone"], horizontal=False)

if "upload_widget_version" not in st.session_state:
    st.session_state["upload_widget_version"] = 0

input_files = st.file_uploader(
    "Select input CSV or XLSX file(s)", type=["csv", "xlsx"], accept_multiple_files=True,
    key=f"input_files_{st.session_state['upload_widget_version']}",
    help="Phone numbers must be in the first column. Other source columns are retained. Files are not written to disk by this app."
)

if filter_mode == "State":
    filter_options = sorted(set(INTERNAL_AREA_CODE_MAP.values()))
    filter_label = "States to export separately (optional)"
else:
    filter_options = sorted(set(AREA_CODE_TIMEZONE_MAP.values()))
    filter_label = "Time zones to export separately (optional)"
selected_filters = st.multiselect(filter_label, filter_options, help="Leave empty to create only the full processed CSV for each uploaded file.")

if not use_internal_mapping and custom_mapping_file is None:
    st.warning("Upload a custom mapping CSV or enable the built-in mapping before processing.")

if st.button("🚀 Process Files", type="primary", disabled=not input_files or (not use_internal_mapping and custom_mapping_file is None)):
    try:
        area_code_map = INTERNAL_AREA_CODE_MAP.copy() if use_internal_mapping else load_custom_mapping(custom_mapping_file)
        generated_files = {}
        summary_rows = []
        errors = []
        overall_state_counts = {}

        for uploaded in input_files:
            try:
                uploaded.seek(0)
                df, duplicates_removed = process_uploaded_file(uploaded, area_code_map, remove_duplicates)
                # Prevent same-named uploads from silently overwriting each other.
                base_name = f"{os.path.splitext(os.path.basename(uploaded.name))[0]}.csv"
                if base_name in generated_files:
                    stem, ext = os.path.splitext(base_name)
                    base_name = f"{stem}_{len(generated_files) + 1}{ext}"
                generated_files[base_name] = make_csv_bytes(df)

                if selected_filters:
                    filter_column = "State" if filter_mode == "State" else "Timezone"
                    for value in selected_filters:
                        filtered = df[df[filter_column] == value]
                        if not filtered.empty:
                            filtered_name = f"{value}_{base_name}"
                            # Ensure unique output names.
                            candidate = filtered_name
                            suffix = 2
                            while candidate in generated_files:
                                stem, ext = os.path.splitext(filtered_name)
                                candidate = f"{stem}_{suffix}{ext}"
                                suffix += 1
                            generated_files[candidate] = make_csv_bytes(filtered)

                counts = df["State"].value_counts().to_dict()
                for state, count in counts.items():
                    overall_state_counts[state] = overall_state_counts.get(state, 0) + int(count)
                summary_rows.append({
                    "Input file": uploaded.name,
                    "Valid rows after cleaning": len(df),
                    "Duplicates removed": duplicates_removed,
                    "Known states": int((df["State"] != "Unknown").sum()),
                    "Unknown state": int((df["State"] == "Unknown").sum()),
                    "Output files created": 1 + (sum(1 for value in selected_filters if not df[df["State" if filter_mode == "State" else "Timezone"] == value].empty) if selected_filters else 0),
                })
            except Exception as exc:
                errors.append(f"{uploaded.name}: {exc}")

        if generated_files:
            st.session_state["area_code_generated_files"] = generated_files
            st.session_state["area_code_summary_rows"] = summary_rows
            st.session_state["area_code_state_counts"] = overall_state_counts
            st.session_state["area_code_errors"] = errors
            st.success(f"Processed {len(summary_rows)} file(s). Created {len(generated_files)} downloadable output file(s).")
        else:
            st.error("No files were processed successfully.")
        for error in errors:
            st.error(error)
    except Exception as exc:
        st.error(f"Processing failed: {exc}")

if st.session_state.get("area_code_summary_rows"):
    st.subheader("Processing Summary")
    st.dataframe(pd.DataFrame(st.session_state["area_code_summary_rows"]), use_container_width=True, hide_index=True)
    state_counts = st.session_state.get("area_code_state_counts", {})
    if state_counts:
        st.subheader("Numbers by State")
        state_df = pd.DataFrame([{"State": k, "Count": v} for k, v in sorted(state_counts.items(), key=lambda item: item[0])])
        st.dataframe(state_df, use_container_width=True, hide_index=True)
    outputs = st.session_state.get("area_code_generated_files", {})
    if outputs:
        if len(outputs) == 1:
            filename, data = next(iter(outputs.items()))
            st.download_button(f"⬇ Download {filename}", data=data, file_name=filename, mime="text/csv")
        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                for filename, data in outputs.items():
                    archive.writestr(filename, data)
            st.download_button("⬇ Download All Output Files (ZIP)", data=zip_buffer.getvalue(), file_name="Area_Code_Mapper_Output.zip", mime="application/zip")
        with st.expander("Output files included"):
            st.write("\n".join(f"- {name}" for name in outputs))


st.divider()
if st.button("🧹 Clear session data and uploaded files"):
    for key in (
        "area_code_generated_files", "area_code_summary_rows", "area_code_state_counts",
        "area_code_errors"
    ):
        st.session_state.pop(key, None)
    st.session_state["upload_widget_version"] += 1
    st.rerun()

import json
import re
import streamlit as st

st.set_page_config(
    page_title="SRT Word Mapper", page_icon="😉", layout="wide"
)

st.title("Punjabi Roman SRT Dictionary Builder")
st.write(
    "Upload matching Punjabi (Gurmukhi) and Roman Punjabi `.srt` subtitle files to automatically generate a mapped JSON dictionary."
)


def parse_srt_content(content):
    """Parses raw SRT text content and extracts text by block index."""
    # Normalize Windows/Unix line endings
    content = content.replace('\r\n', '\n')
    entries = {}
    blocks = content.strip().split('\n\n')

    for block in blocks:
        lines = [
            line.strip() for line in block.strip().split('\n') if line.strip()
        ]
        if len(lines) >= 3:
            try:
                idx = int(lines[0])
                # Combine subtitle text lines (skipping timestamp line at index 1)
                entries[idx] = ' '.join(lines[2:])
            except ValueError:
                continue
    return entries


def clean_word(word):
    """Removes special characters and keeps words in lowercase."""
    word = re.sub(r'[^\w\s\u0A00-\u0A7F\'-]', '', word, flags=re.UNICODE)
    return word.strip().lower()


def map_words_from_content(roman_content, punjabi_content):
    """Maps Punjabi words to Roman Punjabi words from in-memory SRT content."""
    roman_entries = parse_srt_content(roman_content)
    punjabi_entries = parse_srt_content(punjabi_content)

    mapping = {}
    common_indexes = sorted(
        set(roman_entries.keys()).intersection(punjabi_entries.keys())
    )

    for idx in common_indexes:
        # Strip out subtitle background music markers (like ♪, [], etc.)
        r_text = re.sub(r'[♪\[\]॥।॥\d:,-->]', '', roman_entries[idx])
        p_text = re.sub(r'[♪\[\]॥।॥\d:,-->]', '', punjabi_entries[idx])

        r_words = [clean_word(w) for w in r_text.split() if clean_word(w)]
        p_words = [clean_word(w) for w in p_text.split() if clean_word(w)]

        # Map when word counts in matching subtitle timestamps align
        if len(r_words) == len(p_words):
            for pw, rw in zip(p_words, r_words):
                if pw and rw and pw not in mapping:
                    mapping[pw] = rw

    return mapping


# File Uploaders
col1, col2 = st.columns(2)

with col1:
    punjabi_file = st.file_uploader(
        "Upload Punjabi SRT (Gurmukhi)", type=["srt"], key="punjabi"
    )

with col2:
    roman_file = st.file_uploader(
        "Upload Roman Punjabi SRT", type=["srt"], key="roman"
    )

if punjabi_file and roman_file:
    # Read files in memory
    punjabi_text = punjabi_file.getvalue().decode('utf-8', errors='ignore')
    roman_text = roman_file.getvalue().decode('utf-8', errors='ignore')

    if st.button("Generate Mapping", type="primary"):
        with st.spinner("Processing subtitles and mapping words..."):
            word_map = map_words_from_content(roman_text, punjabi_text)
            json_output = json.dumps(word_map, ensure_ascii=False, indent=2)

        st.success(
            f"Successfully mapped **{len(word_map)}** unique words!"
        )

        # Download Button
        st.download_button(
            label="Download Mapping JSON",
            data=json_output,
            file_name="punjabi_word_mapping.json",
            mime="application/json",
        )

        st.subheader("Preview Mapping Result")

        tab1, tab2 = st.tabs(["Searchable Table", "Raw JSON View"])

        with tab1:
            st.dataframe(
                [
                    {"Punjabi (Gurmukhi)": k, "Roman Punjabi": v}
                    for k, v in word_map.items()
                ],
                use_container_width=True,
            )

        with tab2:
            st.json(word_map)
else:
    st.info("Please upload both `.srt` files above to generate the mapping.")


st.write(
    "Developed by Punjab Team. Made with Love❤️"
)
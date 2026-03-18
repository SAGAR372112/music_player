"""
app.py
------
Streamlit frontend for the Music Player application.

Layout:
    Left  — Upload section + Now Playing audio player
    Right — Song library: click a song row to play it
"""

import math

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="VINYL // Music Player",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_BASE = "http://localhost:8000"

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0d0d !important;
    color: #e8dcc8 !important;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(180,120,30,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 90%, rgba(180,120,30,0.05) 0%, transparent 50%),
        #0d0d0d;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 2rem 3rem 4rem !important; max-width: 1100px; margin: auto; }

* { font-family: 'DM Mono', monospace !important; }

/* ── Header ── */
.app-header {
    border-bottom: 1px solid rgba(240,192,64,0.25);
    padding-bottom: 1.1rem;
    margin-bottom: 2rem;
}
.app-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 3.2rem;
    color: #f0c040;
    letter-spacing: 0.12em;
    line-height: 1;
    margin: 0;
}
.app-subtitle {
    font-size: 0.65rem;
    color: rgba(240,192,64,0.42);
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

/* ── Section label ── */
.section-label {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 0.95rem;
    color: rgba(240,192,64,0.6);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    display: block;
}

/* ── Upload box ── */
.upload-box {
    background: rgba(255,255,255,0.022);
    border: 1px solid rgba(240,192,64,0.13);
    border-radius: 3px;
    padding: 1.3rem 1.5rem 1.4rem;
    margin-bottom: 1.4rem;
}

/* ── Now Playing ── */
.now-playing-box {
    background: linear-gradient(135deg, rgba(240,192,64,0.09) 0%, rgba(240,192,64,0.03) 100%);
    border: 1px solid rgba(240,192,64,0.28);
    border-radius: 3px;
    padding: 1.1rem 1.5rem 0.9rem;
}
.np-label {
    font-size: 0.56rem;
    letter-spacing: 0.4em;
    color: rgba(240,192,64,0.48);
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}
.np-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.55rem;
    color: #f0c040;
    letter-spacing: 0.07em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Song list ── */
.song-list-header {
    display: flex;
    align-items: baseline;
    gap: 0.7rem;
    margin-bottom: 0.6rem;
}
.song-count {
    font-size: 0.62rem;
    color: rgba(240,192,64,0.3);
    letter-spacing: 0.12em;
}

/* Each song row — rendered via st.button, styled below */
[data-testid="stButton"] > button.song-btn {
    all: unset;
}

/* Style ALL stButton buttons inside the song list as song rows */
div.song-list-area [data-testid="stButton"] > button {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    background: rgba(255,255,255,0.018) !important;
    border: 1px solid rgba(255,255,255,0.04) !important;
    border-radius: 0 !important;
    border-left: none !important;
    border-right: none !important;
    border-top: none !important;
    padding: 0.65rem 1.1rem !important;
    color: #e8dcc8 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.03em !important;
    text-align: left !important;
    cursor: pointer !important;
    transition: background 0.12s ease !important;
    margin: 0 !important;
    height: auto !important;
    opacity: 1 !important;
}
div.song-list-area [data-testid="stButton"] > button:hover {
    background: rgba(240,192,64,0.08) !important;
    color: #f0c040 !important;
    border-color: rgba(240,192,64,0.15) !important;
}
div.song-list-area [data-testid="stButton"] > button:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* Upload button */
div.upload-area [data-testid="stButton"] > button {
    background: #f0c040 !important;
    color: #0d0d0d !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.12em !important;
    padding: 0.45rem 1.4rem !important;
    width: auto !important;
    height: auto !important;
    opacity: 1 !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}
div.upload-area [data-testid="stButton"] > button:hover {
    background: #ffd060 !important;
    box-shadow: 0 3px 14px rgba(240,192,64,0.22) !important;
}

/* Refresh button */
div.refresh-area [data-testid="stButton"] > button {
    background: transparent !important;
    color: rgba(240,192,64,0.5) !important;
    border: 1px solid rgba(240,192,64,0.18) !important;
    border-radius: 2px !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    padding: 0.25rem 0.7rem !important;
    width: auto !important;
    height: auto !important;
    opacity: 1 !important;
    margin: 0 !important;
    cursor: pointer !important;
}
div.refresh-area [data-testid="stButton"] > button:hover {
    background: rgba(240,192,64,0.07) !important;
    color: #f0c040 !important;
}

/* Audio player */
audio {
    width: 100%;
    margin-top: 0.5rem;
    border-radius: 2px;
    filter: sepia(0.15) hue-rotate(8deg);
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(240,192,64,0.2) !important;
    border-radius: 2px !important;
}
[data-testid="stFileUploader"] label {
    font-size: 0.65rem !important;
    letter-spacing: 0.16em !important;
    color: rgba(240,192,64,0.5) !important;
    text-transform: uppercase !important;
}

/* Alerts */
[data-testid="stAlert"] {
    background: rgba(240,192,64,0.04) !important;
    border: 1px solid rgba(240,192,64,0.16) !important;
    border-radius: 2px !important;
    font-size: 0.76rem !important;
}
[data-testid="stAlert"][data-type="success"] {
    border-color: rgba(80,200,120,0.28) !important;
    background: rgba(80,200,120,0.05) !important;
}
[data-testid="stAlert"][data-type="error"] {
    border-color: rgba(220,60,60,0.28) !important;
    background: rgba(220,60,60,0.05) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(240,192,64,0.22); border-radius: 2px; }
</style>
"""

st.markdown(STYLES, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def init_session():
    defaults = {
        "songs": [],
        "playing_song": None,
        "audio_url": None,       # stream URL passed directly to st.audio()
        "upload_message": None,
        "upload_ok": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def api_get(path: str) -> requests.Response:
    return requests.get(f"{API_BASE}{path}", timeout=10)

def api_post(path: str, **kwargs) -> requests.Response:
    return requests.post(f"{API_BASE}{path}", timeout=30, **kwargs)

def fetch_songs() -> list[dict]:
    try:
        resp = api_get("/songs")
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return []

def upload_file(file) -> tuple[bool, str]:
    try:
        resp = api_post(
            "/upload",
            files={"file": (file.name, file.getvalue(), file.type)},
        )
        if resp.status_code == 201:
            data = resp.json()
            return True, f"'{data['song']['title']}' uploaded successfully."
        return False, resp.json().get("detail", "Upload failed.")
    except requests.RequestException as exc:
        return False, f"Network error: {exc}"

def format_date(iso: str) -> str:
    try:
        return iso[:10]
    except Exception:
        return ""

# ---------------------------------------------------------------------------
# Load songs on first render
# ---------------------------------------------------------------------------

if not st.session_state.songs:
    st.session_state.songs = fetch_songs()

songs = st.session_state.songs

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="app-header">
    <div class="app-title">VINYL</div>
    <div class="app-subtitle">Music Player — Upload &amp; Stream</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Two-column layout
# ---------------------------------------------------------------------------

left_col, right_col = st.columns([2, 3], gap="large")

# ===========================================================================
# LEFT — Upload + Now Playing
# ===========================================================================

with left_col:

    # Upload box
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.markdown('<span class="section-label">Upload Track</span>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop MP3 or WAV",
        type=["mp3", "wav"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        size_kb = math.ceil(len(uploaded_file.getvalue()) / 1024)
        st.markdown(
            f'<div style="font-size:0.68rem;color:rgba(240,192,64,0.5);padding:0.45rem 0 0.65rem;">'
            f'<span style="color:#e8dcc8">{uploaded_file.name}</span>'
            f' &nbsp;·&nbsp; {size_kb:,} KB</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        if st.button("Upload", key="do_upload"):
            with st.spinner("Uploading…"):
                ok, msg = upload_file(uploaded_file)
            st.session_state.upload_ok = ok
            st.session_state.upload_message = msg
            if ok:
                st.session_state.songs = fetch_songs()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.upload_message:
        if st.session_state.upload_ok:
            st.success(st.session_state.upload_message)
        else:
            st.error(st.session_state.upload_message)

    st.markdown('</div>', unsafe_allow_html=True)

    # Now Playing
    if st.session_state.playing_song:
        song = st.session_state.playing_song
        st.markdown(f"""
        <div class="now-playing-box">
            <div class="np-label">▶ Now Playing</div>
            <div class="np-title" title="{song['title']}">{song['title']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.audio_url:
            st.audio(st.session_state.audio_url, autoplay=True)
        else:
            st.error("Could not load audio.")
    else:
        st.markdown("""
        <div style="padding:2rem 1.5rem;border:1px dashed rgba(240,192,64,0.1);
             border-radius:3px;text-align:center;color:rgba(232,220,200,0.18);
             font-size:0.73rem;letter-spacing:0.08em;">
            No track selected<br>
            <span style="font-size:1.8rem;opacity:0.25;">♪</span>
        </div>
        """, unsafe_allow_html=True)

    # API status
    st.markdown("<div style='margin-top:1.6rem'></div>", unsafe_allow_html=True)
    try:
        health = requests.get(f"{API_BASE}/health", timeout=3)
        if health.status_code == 200:
            version = health.json().get("version", "?")
            st.markdown(
                f'<div style="font-size:0.58rem;color:rgba(80,200,120,0.48);letter-spacing:0.2em;">'
                f'● API ONLINE &nbsp;·&nbsp; v{version}</div>',
                unsafe_allow_html=True,
            )
    except requests.RequestException:
        st.markdown(
            '<div style="font-size:0.58rem;color:rgba(220,60,60,0.5);letter-spacing:0.2em;">'
            '● API OFFLINE — start the backend</div>',
            unsafe_allow_html=True,
        )

# ===========================================================================
# RIGHT — Song Library
# ===========================================================================

with right_col:

    # Header row
    hdr_l, hdr_r = st.columns([5, 1])
    with hdr_l:
        track_count = f"{len(songs)} track{'s' if len(songs) != 1 else ''}" if songs else "empty"
        st.markdown(
            f'<span class="section-label">Library &nbsp;'
            f'<span style="font-family:\'DM Mono\',monospace;font-size:0.62rem;'
            f'color:rgba(240,192,64,0.28);letter-spacing:0.1em;">{track_count}</span></span>',
            unsafe_allow_html=True,
        )
    with hdr_r:
        st.markdown('<div class="refresh-area">', unsafe_allow_html=True)
        if st.button("↺", key="refresh", help="Refresh library"):
            st.session_state.songs = fetch_songs()
            st.session_state.upload_message = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if not songs:
        st.markdown("""
        <div style="padding:3rem 2rem;text-align:center;
             border:1px dashed rgba(240,192,64,0.1);border-radius:3px;
             color:rgba(232,220,200,0.18);font-size:0.78rem;letter-spacing:0.07em;">
            Library is empty. Upload your first track.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Wrap the song list in a div we can target with CSS
        st.markdown('<div class="song-list-area">', unsafe_allow_html=True)

        for i, song in enumerate(songs, start=1):
            is_active = (
                st.session_state.playing_song is not None
                and st.session_state.playing_song["id"] == song["id"]
            )
            icon = "▶" if is_active else f"{i:02d}"
            date_str = format_date(song.get("uploaded_at", ""))
            title = song["title"]

            # Each button IS the song row — label contains index + title + date
            label = f"{icon}   {title}   {date_str}"

            if st.button(label, key=f"play_{song['id']}", use_container_width=True):
                st.session_state.playing_song = song
                st.session_state.audio_url = f"{API_BASE}/songs/{song['id']}/play"
                st.session_state.upload_message = None
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
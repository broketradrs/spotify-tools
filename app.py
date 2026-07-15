import streamlit as st
from new_releases import get_new_releases
from shuffle_playlist import shuffle_playlist
from split_playlists import update_english_playlist
from datetime import datetime, timedelta
from sheet_utils import get_artists, add_artist, remove_artist, update_artist_image
from spotify_utils import get_artist_from_link, get_artist_info
from public_shuffle import public_shuffle
from playlist_splitter import split_playlist

# ======================
# INITIALIZATION
# ======================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "releases" not in st.session_state:
    st.session_state.releases = []

def check_password():
    if st.session_state.password == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.is_admin = True
        # Auto-run when admin logs in
        end_datetime = datetime.combine(datetime.today(), datetime.min.time())
        start_datetime = end_datetime - timedelta(days=7)
        st.session_state.releases = get_new_releases(days=7, start_date=start_datetime)
    else:
        st.session_state.is_admin = False

st.title("🎵 Ryan's Spotify Tools")

password = st.text_input(
    "Admin Password",
    type="password",
    key="password",
    on_change=check_password
)

if st.session_state.is_admin:
    st.success("🔒 Admin Mode Enabled")

# ===================================================
# ARTIST RELEASE TRACKER
# ===================================================
if st.session_state.is_admin:
    st.header("🎵 Artist Release Tracker")
    col1, col2 = st.columns([10.5, 1])
    with col1:
        artist_link = st.text_input("Spotify Artist Link", label_visibility="collapsed", placeholder="Paste Spotify artist link...")
    with col2:
        add_pressed = st.button("Add")
    
    if add_pressed:
        try:
            artist = get_artist_from_link(artist_link)
            if add_artist(artist["name"], artist["id"], artist["image"]):
                st.success(f"Added {artist['name']}")
                st.rerun()
            else:
                st.warning("Artist already exists")
        except Exception as e:
            st.error(e)

# ===================================================
# WATCHLIST
# ===================================================
artists = get_artists()
with st.expander(f"🎧 Release Watchlist ({len(artists)} artists)"):
    for i in range(0, len(artists), 2):
        row_cols = st.columns(2)
        for j in range(2):
            if i + j >= len(artists): break
            artist = artists[i + j]
            with row_cols[j]:
                col1, col2, col3 = st.columns([1.7, 3, 0.8])
                with col1:
                    if not artist["image"]:
                        info = get_artist_info(artist["id"])
                        update_artist_image(artist["id"], info["image"])
                        artist["image"] = info["image"]
                    if artist["image"]:
                        st.image(artist["image"], width=130)
                with col2:
                    st.markdown(f"### {artist['name']}")
                with col3:
                    if st.session_state.is_admin and st.button("❌", key=f"delete_{artist['id']}"):
                        remove_artist(artist["id"])
                        st.rerun()
        st.divider()

# ===================================================
# NEW RELEASES
# ===================================================
if "release_days" not in st.session_state: st.session_state.release_days = 7
if "release_end_date" not in st.session_state: st.session_state.release_end_date = datetime.today()

col1, col2, col3 = st.columns([1, 5, 0.8])
with col1:
    days_input = st.number_input("Days", min_value=1, value=st.session_state.release_days, label_visibility="collapsed")
with col2:
    end_date_input = st.date_input("End Date", value=st.session_state.release_end_date, label_visibility="collapsed")
with col3:
    refresh_pressed = st.button("Refresh")

if refresh_pressed:
    end_datetime = datetime.combine(end_date_input, datetime.min.time())
    st.session_state.releases = get_new_releases(days=days_input, start_date=end_datetime - timedelta(days=days_input))

with st.expander(f"🎵 New Releases 🔴 {len(st.session_state.releases)}"):
    if not st.session_state.releases:
        st.info("Press Refresh to check for releases.")
    else:
        for release in st.session_state.releases:
            col1, col2 = st.columns([2, 3])
            with col1:
                if release["image"]: st.image(release["image"], width=200)
            with col2:
                st.markdown(f"## {release['album']}")
                st.write(f"🎤 {release['artist']}")
                st.write(f"📅 {release['date']}")
                st.link_button("Open in Spotify", release["url"])
            st.divider()

# ===================================================
# PUBLIC SHUFFLER
# ===================================================
if not st.session_state.is_admin:
    st.divider()
    st.header("🌎 Public Playlist Shuffler")
    public_shuffle()

# ===================================================
# ADMIN SECTIONS
# ===================================================
if st.session_state.is_admin:
    st.divider()
    st.header("🔀 Shuffle Playlist")
    playlist_link = st.text_input("Spotify Playlist Link")
    if st.button("Shuffle Playlist") and playlist_link:
        shuffle_playlist(playlist_link)
        st.success("Playlist shuffled!")

    st.divider()
    st.header("📂 Playlist Tools")
    if st.button("Update English Playlist"):
        update_english_playlist()
        st.success("English playlist updated!")
    
    st.subheader("➖ Playlist Splitter")
    pla = st.text_input("Playlist A Link", key="playlist_a")
    plb = st.text_input("Playlist B Link", key="playlist_b")
    if st.button("Create Split Playlist") and pla and plb:
        split_playlist(pla, plb)
        st.success("Split playlist created!")

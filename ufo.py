import streamlit as st
import pandas as pd
import plotly.express as px
import textwrap
import html
import re
st.set_page_config(page_title="UFO Sightings Map", layout="wide")

st.title("World map - UFO Sightings")
st.markdown("""
Explore UFO sightings across the world!  
- Use the slider to view sightings from a specific year.  
- Hover over any point to see how many sightings occurred at that location.  
- You’ll also see **one example report** from that location for that year.
""")

def clean_and_wrap_text(text, width=80):
    if pd.isna(text):
        return "No description available."
    text = html.unescape(html.unescape(str(text)))

    def fix_numeric_entities(match):
        try:
            return chr(int(match.group(1)))
        except:
            return match.group(0)

    text = re.sub(r"&#(\d+)", fix_numeric_entities, text)

    return "<br>".join(textwrap.wrap(text, width=width))

@st.cache_data
def load_data():
    df = pd.read_csv("C:/Users/Anton/Downloads/scrubbed.csv")
    df.columns = df.columns.str.strip().str.lower()
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["year"] = df["datetime"].dt.year
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    df = df.dropna(subset=["year", "latitude", "longitude"])
    
    text_fields = ["comments", "city", "state", "country", "shape"]
    for field in text_fields:
        df[field] = df[field].fillna("Unknown")
        df[field] = df[field].apply(lambda x: clean_and_wrap_text(x, width=80))

    return df

df = load_data()

years = sorted(df["year"].dropna().unique())
selected_year = st.slider("Select a Year", min_value=int(min(years)), max_value=int(max(years)), value=int(df["year"].median()))

year_df = df[df["year"] == selected_year].copy()
grouped = (
    year_df.groupby(["latitude", "longitude"])
    .agg(
        sightings=("comments", "count"),
        comment=("comments", "first"),
        city=("city", "first"),
        state=("state", "first"),
        country=("country", "first"),
        shape=("shape", "first")
    )
    .reset_index()
)

fig = px.scatter_mapbox(
    grouped,
    lat="latitude",
    lon="longitude",
    size="sightings",
    color="sightings",
    color_continuous_scale="Turbo",
    size_max=15,
    zoom=2.2,

    hover_data={
        "comment": True,
        "city": True,
        "state": False,
        "country": False,
        "shape": True,
        "latitude": False,
        "longitude": False
    },
    height=700
)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
st.markdown(f"### Total sightings in {selected_year}: **{len(year_df):,}**")
st.plotly_chart(fig, use_container_width=True)
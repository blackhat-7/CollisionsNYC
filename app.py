import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import matplotlib.pyplot as plt

DATA_URL = (
    "~/DataScience/Projects/CollisionsNYC/app.py"
)

st.title("New York City Collisions Analysis")
st.markdown("### A visualization of vehicles collisions in NYC")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv('./Motor_Vehicle_Collisions_-_Crashes.csv', nrows=nrows, parse_dates=["CRASH DATE", "CRASH TIME"])
    lowercase = lambda x: x.lower()
    data.rename(lowercase, axis=1, inplace=True)
    data.dropna(subset=["latitude", "longitude"], inplace=True)
    data.rename(columns={'crash time': 'crash_time'}, inplace=True)
    return data

original_data = load_data(100_000)
data = original_data.copy()

st.header("Where are most people injured in NYC?")
injured_people = st.slider("Number of injured people", min_value=0, max_value=19, value=5)
st.map(data=data.loc[data["number of persons injured"] >= injured_people][["latitude", "longitude"]].dropna())

st.header("How many collisions have happened at a given time of the day?")
hour = st.slider("Time of the day", min_value=0, max_value=23, value=0)
data = data[data["crash_time"].dt.hour == hour]
st.markdown("Number of people injured between %i:00 and %i:00" % (hour, (hour+1)%24))


st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": data.latitude.mean(),
        "longitude": data.longitude.mean(),
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[["crash_time", "latitude", "longitude"]],
            get_position=["longitude", "latitude"],
            radius=100,
            extruded=True,
            pickable=True,
            extruded_scale=4,
            extruded_range=[0,1000],
        ),
    ],
))

st.subheader(f"Breakdown by minute between {hour}:00 and {hour+1}:00")
min_count = data[(data["crash_time"].dt.hour >= hour) & (data["crash_time"].dt.hour <= hour+1)][["crash_time"]]
hist = np.histogram(min_count.crash_time.dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(data_frame=chart_data, x="minute", y="crashes", hover_data=["minute", "crashes"], height=400)

st.write(fig)
#crashes_at_hour = data[(data["crash_time"].dt.hour >= hour) & (data["crash_time"].dt.hour <= hour+1)]
#crashes_at_hour["minute"] = crashes_at_hour.crash_time.apply(lambda x: x.minute)
#fig = plt.figure()
#plt.hist(crashes_at_hour.minute, bins=60)
#st.pyplot()

st.header("Top 5 dangerous streets by affected type")
person = st.selectbox("Affected type", ["Pedestrian", "Cyclist", "Motorist", "None"])

data = original_data.copy()

if person == "Pedestrian":
    injured_data = data[(data["number of pedestrians injured"] > 0) | (data["number of pedestrians killed"] > 0)][["on street name", "number of pedestrians injured", "number of pedestrians killed"]]
    injured_data.dropna(inplace=True)
    injured_data = injured_data.groupby("on street name").count().sort_values(["number of pedestrians injured", "number of pedestrians killed"], ascending=False)[:5]
    st.write(injured_data)

elif person == "Cyclist":
    injured_data = data[(data["number of cyclist injured"] > 0) | (data["number of cyclist killed"] > 0)][["on street name", "number of cyclist injured", "number of cyclist killed"]]
    injured_data.dropna(inplace=True)
    injured_data = injured_data.groupby("on street name").count().sort_values(["number of cyclist injured", "number of cyclist killed"], ascending=False)[:5]
    st.write(injured_data)

elif person == "Motorist":
    injured_data = data[(data["number of motorist injured"] > 0) | (data["number of motorist killed"] > 0)][["on street name", "number of motorist injured", "number of motorist killed"]]
    injured_data.dropna(inplace=True)
    injured_data = injured_data.groupby("on street name").count().sort_values(["number of motorist injured", "number of motorist killed"], ascending=False)[:5]
    st.write(injured_data)


if st.checkbox("Raw Data", value=False):
    st.subheader("Raw Data")
    st.write(original_data)

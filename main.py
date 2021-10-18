import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import pydeck as pdk
import plotly.express as px
import json


def compute_medals(row):
    total_medals = 0
    if ('Bronze' in row):
        total_medals += row['Bronze']
    else:
        row['Bronze'] = 0

    if ('Silver' in row):
        total_medals += row['Silver']
    else:
        row['Silver'] = 0

    if ('Gold' in row):
        total_medals += row['Gold']
    else:
        row['Gold'] = 0

    if ('NOC' not in row):
        row['NOC'] = 0

    row['Total Medals'] = total_medals

    return row

df = pd.read_csv('data/final_data.csv')
df_with_sports = pd.read_csv('data/final_data_with_sports.csv')

max_width = 1200

st.markdown(
    f"""
<style>
    .reportview-container .main .block-container{{
        max-width: {max_width}px;
    }}
    .reportview-container .main {{
    }}
</style>
""",
    unsafe_allow_html=True,
)

sport_selectbox = st.sidebar.selectbox(
    "Analyse Data",
    ("Aggregated Olympic Data", "Data By Sports")
)

with open('data/custom.geo.json') as f:
    countries = json.load(f)

page1 = True if (sport_selectbox == "Aggregated Olympic Data") else False

if (page1 == False):
    year_slider_for_df_with_sports = st.slider(
        'Year (WorldMap With Sports)', min(df_with_sports['Year'].astype(int)), max(df_with_sports['Year'].astype(int)), step=4)
    sport_option = st.multiselect('Select Sport',
                                  ['All'] +
                                  df_with_sports['Event'].unique().tolist(), default=['All'])

    if (sport_option == None or 'All' in sport_option):
        df_with_sports = df_with_sports.loc[df_with_sports[
            'Year'] == year_slider_for_df_with_sports, :]
    else:
        df_with_sports = df_with_sports.loc[np.logical_and(df_with_sports[
                                                           'Year'] == year_slider_for_df_with_sports,
                                                           df_with_sports['Event'].isin(sport_option)), :]

    tmp = df_with_sports.groupby(['NOC', 'Medal']).size(
    ).unstack(fill_value=0).reset_index().dropna()

    tmp = tmp.apply(lambda row: compute_medals(row), axis=1)

    if len(tmp) > 0:
        fig = px.choropleth(tmp, geojson=countries, locations="NOC",
                            featureidkey="properties.iso_a3",
                            color='Total Medals',
                            labels={"NOC": "Country"},
                            hover_data=["Gold", "Silver", "Bronze"])
        if (page1 == False):
            st.plotly_chart(fig, use_container_width=True)
    else:
        if (page1 == False):
            st.write("<h2>No Data Available!</h2><br/><br/><br/><br/>",
                     unsafe_allow_html=True)

else:
    # Add a slider to the sidebar:
    year_slider_for_worldmap = st.slider('Year (WorldMap)', min(df['Year']), max(
        df['Year']), step=4)

    df_year_world = df.loc[df['Year'] == year_slider_for_worldmap, :]

    with open('data/custom.geo.json') as f:
        countries = json.load(f)

    fig = px.choropleth(df_year_world, geojson=countries, locations="NOC",
                        featureidkey="properties.iso_a3",
                        color='Total Medals',
                        labels={'Total Medals': 'Total Medals', 'NOC': 'Country'})

    st.plotly_chart(fig, use_container_width=True)

    year_slider_for_bubble = st.slider('Year (Graph)', min(df['Year']), max(
        df['Year']), step=4)
    df_year_bubble = df.loc[df['Year'] == year_slider_for_bubble, :]

    single = alt.selection_single()
    c = alt.Chart(df_year_bubble, height=500).mark_circle().encode(
        x=alt.X('Per Capita GDP', scale=alt.Scale(type='linear')),
        y=alt.Y('Population', scale=alt.Scale(type='linear')),
        color=alt.condition(single, alt.Color('Region:N', scale=alt.Scale(
            scheme='tableau20')), alt.value('lightgray')),
        tooltip=['Total Medals', 'Country', 'Per Capita GDP', 'Population'],
        size=alt.Size('Total Medals', scale=alt.Scale(type='linear', domain=[0, 20]), legend=None)).interactive().add_selection(single)

    st.altair_chart(c, use_container_width=True)

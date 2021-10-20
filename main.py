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

st.write("<h1>Olympic Games Over The Years</h1>",
         unsafe_allow_html=True)

if (page1 == False):
    st.write("""<p>This is a visualization of the number of medals won by 
        participant countries in every Olympic game. 
        Please use the slider to change the Olympic game year.
        You can apply filters to see the data for the selected sports. 
        Use the dropdown to select the sports for which you want to filter the data.
        Use "All" to see the data for all the sports.</p>""",
             unsafe_allow_html=True)
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
            st.write("<h3>No Data Available!</h3>",
                     unsafe_allow_html=True)

else:
    # Add a slider to the sidebar:
    st.write("""<p>This is a visualization of the total number of medals won by participant countries in every Olympic game. 
        This chart can be used in conjunction with the bubble chart below in order to better highlight 
        which countries have been dominating the Olympics. 
        The medal count is scaled where Gold = 3 medals, Silver = 2 medals and Bronze = 1 medal. 
        For an exact count of medals please check the chart on page 2. 
        This is an interactive map, please feel free to zoom, pan or box select any specific areas.</p>""",
             unsafe_allow_html=True)
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

    st.write("""<hr/><p>This is a visualization of the medal count of each participant country on a graph of Population vs Per-Capita GDP. 
        This is an interactive plot. Please feel free to zoom, pan or select different years through the slider.</p>""",
             unsafe_allow_html=True)
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

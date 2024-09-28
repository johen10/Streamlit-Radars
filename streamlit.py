import streamlit as st
import pandas as pd
from mplsoccer import PyPizza
import numpy as np
import matplotlib as mpl
from mplsoccer.radar_chart import Radar
from mplsoccer import PyPizza, add_image, FontManager
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore
from scipy import stats
import math
from urllib.request import urlopen
from PIL import Image
import matplotlib.pyplot as mpl
mpl.rcParams['figure.dpi'] = 600
import os  # <-- Add this line to import the os module
import matplotlib.patches as patches


# Define the path where CSV files are stored
xlsx_directory = 'Data“'  # Make sure this directory contains your CSV files

# Get a list of CSV files in the directory
xlsx_files = [f for f in os.listdir('Data“') if f.endswith('.xlsx')]

# Streamlit: Create the sidebar for file selection
st.sidebar.title("Select Data File and Player")
selected_file = st.sidebar.selectbox("Select League File", xlsx_files)

# Load the selected CSV file
data_path = os.path.join('Data“', selected_file)
data = pd.read_excel(data_path)

data = data.fillna(0)

file_name = os.path.splitext(selected_file)[0]

# Streamlit app layout
st.title('Percentile Charts - Wyscout p/90 Data')
st.subheader("By choosing League, Position, Player and Metrics you'll get a Chart")




attacking_metrics = ['Successful attacking actions per 90', 'Goals per 90', 'xG per 90', 'Shots per 90', 'Assists per 90', 'xA per 90','Offensive duels per 90', 'Dribbles per 90']  # Add your attacking metrics here
possession_metrics = ['Passes per 90', 'Forward passes per 90', 'Long passes per 90', 'Smart passes per 90','Key passes per 90', 'Passes to final third per 90', 'Passes to penalty area per 90','Through passes per 90', 'Deep completions per 90', 'Deep completed crosses per 90', 'Progressive passes per 90', 'Back passes received as GK per 90']  # Add your possession metrics here
defending_metrics = ['Successful defensive actions per 90', 'Defensive duels per 90', 'Aerial duels per 90', 'PAdj Sliding tackles', 'PAdj Interceptions', 'Shots blocked per 90']  # Add your defending metrics here
goalkeeper_metrics = ['Conceded goals per 90', 'Shots against per 90', 'Clean sheets', 'Save rate, %', 'xG against per 90', 'Prevented goals', 'Prevented goals per 90', 'Exits per 90', 'Aerial duels per 90']  # Add your goalkeeper metrics here


min_minutes, max_minutes = st.sidebar.slider(
    "Select Minutes Played Range",
    min_value=int(data['Minutes played'].min()),  # Minimum value from the dataset
    max_value=int(data['Minutes played'].max()),  # Maximum value from the dataset
    value=(int(data['Minutes played'].min()), int(data['Minutes played'].max()))  # Default to the full range
)

# Filter data based on selected minutes
filtered_data = data[(data['Minutes played'] >= min_minutes) & (data['Minutes played'] <= max_minutes)]

# Streamlit: Create the sidebar for player and position selection
if filtered_data.shape[0] > 0:  # Check if there's data after filtering
    selected_position = st.sidebar.selectbox('Select Position', filtered_data['Position'].unique(), index = None)
    selected_player = st.sidebar.selectbox('Select Player', filtered_data['Player'].unique(), index = None)
    



st.sidebar.header("Select Metrics by Category")
selected_attacking_metrics = st.sidebar.multiselect('Select Attacking Metrics', attacking_metrics)
selected_possession_metrics = st.sidebar.multiselect('Select Possession Metrics', possession_metrics)
selected_defending_metrics = st.sidebar.multiselect('Select Defending Metrics', defending_metrics)
selected_goalkeeper_metrics = st.sidebar.multiselect('Select Goalkeeper Metrics', goalkeeper_metrics)
  
  # Combine all selected metrics
selected_metrics = selected_attacking_metrics + selected_possession_metrics + selected_defending_metrics + selected_goalkeeper_metrics


# Get player details (minutes played and team)
player_info = data[data['Player'] == selected_player][['Minutes played', 'Team']].iloc[0]
player_minutes = player_info['Minutes played']
player_team = player_info['Team']

    # Proceed if metrics are selected
# Proceed if metrics are selected
if len(selected_metrics) > 0:
    # Filter the data for the selected position
    position_data = data[data['Position'] == selected_position]

    # Get the selected player's data for the selected metrics
    player_data = data[data['Player'] == selected_player][selected_metrics]

    # Check if player_data is not empty
    if not player_data.empty:
        # Compute the percentile rank for the player's metrics compared to others in the same position
        percentile_player_data = []
        for metric in selected_metrics:
            metric_values = position_data[metric].dropna().values  # Drop NaN values to avoid issues
            player_value = player_data[metric].values[0]  # Get the player's metric value

            # Calculate percentile if there are values to compare
            if len(metric_values) > 0:
                percentile = percentileofscore(metric_values, player_value, kind='rank')
                percentile_player_data.append(round(percentile))  
            else:
                # Handle case where no comparison data is available, defaulting to 50th percentile
                percentile_player_data.append(50)

        # Check if percentile_player_data is valid
        if len(percentile_player_data) == len(selected_metrics):

            slice_colors = []
            for metric in selected_metrics:
                if metric in attacking_metrics:
                    slice_colors.append("#6DD3CE")  # Tomato red for attacking metrics
                elif metric in possession_metrics:
                    slice_colors.append("#C8E9A0")  # Dodger blue for possession metrics
                elif metric in defending_metrics:
                    slice_colors.append("#F7A278")  # Lime green for defending metrics
                elif metric in goalkeeper_metrics:
                    slice_colors.append("#ffee93")  # Gold for goalkeeper metrics


            text_colors = ["#000000"] * len(selected_metrics)

baker = PyPizza(
    params=selected_metrics,                  # list of parameters
    background_color="#fff1cf",     # background color
    straight_line_color="#000000",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_color="#000000",    # color for last line
    last_circle_lw=1,               # linewidth of last circle
    other_circle_lw=1,              # linewidth for other circles
    inner_circle_size=20,           # size of inner circle
    other_circle_ls="-.",           # linestyle for other circles
)


# plot pizza
fig, ax = baker.make_pizza(
    percentile_player_data,                          # list of values
    figsize=(8, 8.5),                # adjust the figsize according to your need
           # use the same color to fill blank space
    slice_colors=slice_colors,       # color for individual slices
    value_colors=text_colors,        # color for the value-text
    value_bck_colors=slice_colors,   # color for the blank spaces
    blank_alpha=0.4,                 # alpha for blank-space colors
    kwargs_slices=dict(
        edgecolor="#000000", zorder=2, linewidth=1
    ),                               # values to be used when plotting slices
    kwargs_params=dict(
        color="#000000", fontsize=7,
         va="center"
    ),                               # values to be used when adding parameter labels
    kwargs_values=dict(
        color="#000000", fontsize=8,
         zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue",
            boxstyle="round,pad=0.2", lw=1
        )
    )                                # values to be used when adding parameter-values labels
)

# add title
fig.text(
   0.50, 0.96, selected_player, size=13,
    ha="center", weight = 'ultralight', color="#000000"
)

# add subtitle
fig.text(
    0.50, 0.93, f"{file_name} | {player_team} | {selected_position} | Minutes Played: {player_minutes}", size=9,
    ha="center", weight = 'ultralight',  color="#000000"


)


# add text
fig.text(
    0.515, 0.053,"Attacking         Possession         Defending        Goalkeeping", size=7,  ha="center", weight = 'ultralight',
     color="#000000"
)

# add rectangles
fig.patches.extend([
      patches.Circle(
        (0.32, 0.057), 0.0075, fill=True, color="#6DD3CE",  # Position and size of the circle
        transform=fig.transFigure, figure=fig
    ),

    patches.Circle(
        (0.41, 0.057), 0.0075, fill=True, color="#C8E9A0",  # Position and size of the circle
        edgecolor="#000000", linewidth=1.5,
        transform=fig.transFigure, figure=fig
    ),

    patches.Circle(
        (0.515, 0.057), 0.0075, fill=True, color="#F7A278", # Position and size of the circle
        edgecolor="black", linewidth=1.5,    
        transform=fig.transFigure, figure=fig
    ),
    
    patches.Circle(
        (0.605, 0.057), 0.0075, fill=True, color="#ffee93", # Position and size of the circle
        edgecolor="black", linewidth=1.5,    
        transform=fig.transFigure, figure=fig
    ),
])

# add credits
CREDIT_1 = 'João Miguel (@JoaoMiguel063)'
CREDIT_2 = "Data: Wyscout - all stats p/90"
CREDIT_3 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"
fig.text(
    0.50, 0.02, f"{CREDIT_1} | {CREDIT_2} | {CREDIT_3}", size=7, weight = 'ultralight',
     color="#000000",
    ha="center"
)
# Show the pizza chart in Streamlit
st.pyplot(fig)

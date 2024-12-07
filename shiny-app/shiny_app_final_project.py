from shiny import App, render, ui
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from vega_datasets import data  
from sklearn.cluster import DBSCAN 
import numpy as np

# Load US states GeoJSON using Geopandas
states = gpd.read_file(data.us_10m.url, layer='states')
states['id'] = states['id'].astype(int)

df_1 = pd.read_csv(r"C:/Users/prash/Downloads/pv_data_regions_divisions.csv")

# Convert xlong and ylat columns to integers
df_1['xlong_1'] = df_1['xlong'].astype(int)
df_1['ylat_1'] = df_1['ylat'].astype(int)

data_dict = {
    "region": ["Northeast", "Midwest", "South", "West"],
    "any_household_energy_insecurity": [3.69, 3.25, 4.66, 2.98],
    "total_cap_dc_region": [639.3, 687.3, 9848.64, 4006.8]
}

df = pd.DataFrame(data_dict)

# State-to-region mapping (FIPS codes based on U.S. GeoJSON)
state_region_mapping = {
    23: 'Northeast', 25: 'Northeast', 33: 'Northeast', 44: 'Northeast', 50: 'Northeast', 9: 'Northeast',
    34: 'Northeast', 36: 'Northeast', 42: 'Northeast',
    17: 'Midwest', 18: 'Midwest', 26: 'Midwest', 39: 'Midwest', 55: 'Midwest',
    19: 'Midwest', 20: 'Midwest', 27: 'Midwest', 29: 'Midwest', 31: 'Midwest', 38: 'Midwest', 46: 'Midwest',
    1: 'South', 5: 'South', 10: 'South', 12: 'South', 13: 'South', 21: 'South', 22: 'South', 24: 'South',
    28: 'South', 37: 'South', 40: 'South', 45: 'South', 47: 'South', 48: 'South', 51: 'South', 54: 'South',
    4: 'West', 8: 'West', 16: 'West', 30: 'West', 32: 'West', 35: 'West', 49: 'West', 56: 'West',
    2: 'West', 6: 'West', 15: 'West', 41: 'West', 53: 'West'
}

# Prepare state-to-region DataFrame
region_data = pd.DataFrame([
    {"id": fips, "region": region} for fips, region in state_region_mapping.items()
])
region_data['id'] = region_data['id'].astype(int)

# Merge states GeoDataFrame with region data
states = states.merge(region_data, how='left', left_on='id', right_on='id')

# Merge with the main data frame to include energy insecurity and DC capacity
states = states.merge(df, how='left', left_on='region', right_on='region')

# Ensure the geometry column is set
states = states.set_geometry('geometry')

# Coding region = NaN as Unclassified
#states['region'] = states['region'].fillna('Unclassified')

# Energy Insecurity levels list
region_list = df_1['region'].unique().tolist()

# Define the UI
app_ui = ui.page_fluid(
    ui.panel_title("Power Capacity in AC (Megawatts) Across the US"),
    ui.input_select("region", "Select Region:", region_list),
    ui.output_plot("my_plot"),
)

# Define Server
def server(input, output, session):
    @output
    @render.plot
    def my_plot():
        selected_region = input.region()

        # Filter the main dataframe to get the states with the selected region
        filtered_states = states[states['region'] == selected_region]

        # Filter the main dataframe to get the points with the selected region
        filtered_points = df_1[df_1['region'] == selected_region]

        fig, ax = plt.subplots(1, 1, figsize=(50, 30))

        # Plot the filtered states
        filtered_states.boundary.plot(ax=ax, linewidth=1)

        # Scatterplot for filtered points
        scatter = ax.scatter(
            filtered_points['xlong_1'],
            filtered_points['ylat_1'],
            c=filtered_points['p_cap_ac'],
            cmap='viridis',
            s=100,
            alpha=0.6,
            edgecolors='w', 
            vmin= 0, 
            vmax = 600
        )

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Power Capacity in AC (Megawatts)')

        if selected_region == 'West': 
            ax.set_xlim(-125, -100)
            ax.set_ylim(31.25, 50)
        
        # Customize the plot
        ax.set_title(f'Power Capacity in AC (Megawatts) in {selected_region}')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.grid(True)
        ax.set_axis_off()

        # Show the plot
        return fig

# Run the Shiny app
app = App(app_ui, server)


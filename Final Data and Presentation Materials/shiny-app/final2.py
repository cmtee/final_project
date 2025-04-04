from shiny import App, render, ui
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from vega_datasets import data  

# Load US states GeoJSON using Geopandas
states = gpd.read_file(data.us_10m.url, layer="states")
states["id"] = states["id"].astype(int)

# Load the data file
df_1 = pd.read_csv(r"C:/Users/prash/Downloads/pv_data_regions_divisions.csv")

# Ensure longitude and latitude are correct and numeric
df_1["xlong"] = pd.to_numeric(df_1["xlong"], errors="coerce")
df_1["ylat"] = pd.to_numeric(df_1["ylat"], errors="coerce")

# Round longitude and latitude to avoid mismatches
df_1["xlong_1"] = df_1["xlong"].round(4)
df_1["ylat_1"] = df_1["ylat"].round(4)

# State-to-region mapping (FIPS codes)
state_region_mapping = {
    23: "Northeast", 25: "Northeast", 33: "Northeast", 44: "Northeast", 50: "Northeast", 9: "Northeast",
    34: "Northeast", 36: "Northeast", 42: "Northeast", 17: "Midwest", 18: "Midwest", 26: "Midwest", 39: "Midwest", 
    55: "Midwest", 19: "Midwest", 20: "Midwest", 27: "Midwest", 29: "Midwest", 31: "Midwest", 38: "Midwest", 46: "Midwest",
    1: "South", 5: "South", 10: "South", 12: "South", 13: "South", 21: "South", 22: "South", 24: "South", 28: "South", 
    37: "South", 40: "South", 45: "South", 47: "South", 48: "South", 51: "South", 54: "South", 4: "West", 8: "West", 
    16: "West", 30: "West", 32: "West", 35: "West", 49: "West", 56: "West", 2: "West", 6: "West", 15: "West", 41: "West", 
    53: "West",
}

# Create DataFrame from state_region_mapping
region_data = pd.DataFrame(
    {"id": list(state_region_mapping.keys()), "region": list(state_region_mapping.values())}
)

# Ensure 'id' is integer
region_data["id"] = region_data["id"].astype(int)

# Merge states GeoDataFrame with region data
states = states.merge(region_data, how="left", left_on="id", right_on="id")

# Add DC capacity data
data_dict = {
    "region": ["Northeast", "Midwest", "South", "West"],
    "total_cap_dc_region": [639.3, 687.3, 9848.64, 4006.8],
}
df = pd.DataFrame(data_dict)
states = states.merge(df, how="left", left_on="region", right_on="region")

# Set geometry column (necessary for GeoPandas)
states = states.set_geometry("geometry")

# List of regions for the dropdown, including "Full US"
region_list = ["Full US"] + states["region"].dropna().unique().tolist()

# Define the Shiny app UI
app_ui = ui.page_fluid(
    ui.panel_title("Power Capacity in AC (Megawatts) Across the US"),
    ui.input_select("region", "Select Region:", region_list),
    ui.input_slider("capacity_filter", "Filter by Power Capacity (MW)", min=0, max=600, step=10, value=[0, 600]),
    ui.output_plot("my_plot"),
)

# Define the server logic
def server(input, output, session):
    @output
    @render.plot
    def my_plot():
        selected_region = input.region()
        capacity_range = input.capacity_filter()

        # Plotting logic based on selected region
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))

        if selected_region == "Full US":
            # Filter out Alaska (id 2) and Hawaii (id 15), but include Washington and Oregon
            contiguous_states = states[~states["id"].isin([2, 15, 60, 69, 72, 78])]
            contiguous_states.boundary.plot(ax=ax, linewidth=1, edgecolor="black")
            filtered_points = df_1  # Use all points for the entire US
            ax.set_title("Power Capacity in AC (Megawatts) Across the US")
            ax.set_xlim(-125, -66)  # Set appropriate xlim for contiguous US
            ax.set_ylim(24, 49)  # Set appropriate ylim for contiguous US
        else:
            # Handle filtering for the selected region
            if selected_region == "West":
                # Exclude only Alaska (id 2) and Hawaii (id 15), keep Washington and Oregon
                filtered_states = states[(states["region"] == selected_region) & ~states["id"].isin([2, 15])]
            else:
                filtered_states = states[states["region"] == selected_region]

            filtered_points = df_1[df_1["region"] == selected_region]
            filtered_states.boundary.plot(ax=ax, linewidth=1, edgecolor="black")
            ax.set_title(f"Power Capacity in AC (Megawatts) in {selected_region}")

        # Filter points based on the capacity slider range
        filtered_points = filtered_points[
            (filtered_points["p_cap_ac"] >= capacity_range[0]) & (filtered_points["p_cap_ac"] <= capacity_range[1])
        ]

        # Scatterplot of the points
        scatter = ax.scatter(
            filtered_points["xlong_1"],
            filtered_points["ylat_1"],
            c=filtered_points["p_cap_ac"],  # Assuming this column holds the power capacity
            cmap="viridis",
            s=100,
            alpha=0.6,
            edgecolors="w",
            vmin=0,  # consistent color scale
            vmax=600  # consistent color scale
        )

        # Add a colorbar for the scatter plot
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Power Capacity in AC (Megawatts)")

        # Customize the plot
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(True)
        ax.set_axis_off()

        return fig


# Run the Shiny app
app = App(app_ui, server)

@output
@render.plot
def my_plot():
    selected_region = input.region()

    # Filter the GeoDataFrame for the selected region
    filtered_states = states[states["region"] == selected_region]

    # Filter the points DataFrame for the selected region
    filtered_points = df_1[df_1["region"] == selected_region]

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    # Plot state boundaries for the selected region
    filtered_states.boundary.plot(ax=ax, linewidth=1, edgecolor="black")

    # Scatterplot of the points within the selected region
    scatter = ax.scatter(
        filtered_points["xlong_1"],
        filtered_points["ylat_1"],
        c=filtered_points["p_cap_ac"],  # Assuming this column holds the power capacity
        cmap="viridis",
        s=100,
        alpha=0.6,
        edgecolors="w",
    )

    # Add a colorbar for the scatter plot
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Power Capacity in AC (Megawatts)")

    # Customize the plot
    ax.set_title(f"Power Capacity in AC (Megawatts) in {selected_region}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True)
    ax.set_axis_off()

    return fig

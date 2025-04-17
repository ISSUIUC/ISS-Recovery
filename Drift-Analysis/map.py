import drift_approx as drift
import folium
from geopy.distance import distance
import numpy as np

# Launch site GPS (FAR location)
launch_lat, launch_lon = 35.347538, -117.809397

def plot_trajectory_map(vectors_list, labels):
    # === CONFIGURABLE PARAMETERS ===
    interp_count = 300         # Number of interpolated points
    start_radius = 50          # Circle radius at start (meters)
    circle_opacity = 0.025       # Fill opacity for error circles
    circle_border_weight = 0   # Outline weight of error circles
    show_point_markers = False # Toggle visibility of small point markers

    # Initialize base map
    m = folium.Map(location=[launch_lat, launch_lon], zoom_start=14, control_scale=True)
    folium.TileLayer('OpenStreetMap').add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='Satellite (Esri)', overlay=False, control=True
    ).add_to(m)

    colors = ['red', 'blue', 'green', 'orange', 'darkred', 'purple', 'cadetblue']

    for idx, (vectors_ft, label) in enumerate(zip(vectors_list, labels)):
        color = colors[idx % len(colors)]
        fg = folium.FeatureGroup(name=label)

        # Calculate cumulative positions
        positions_ft = [np.array([0.0, 0.0])]
        for vec in vectors_ft:
            positions_ft.append(positions_ft[-1] + vec)
        positions_ft = np.array(positions_ft)

        # Calculate total trajectory length and interpolate evenly by distance
        segment_lengths = np.linalg.norm(np.diff(positions_ft, axis=0), axis=1)
        cumulative_lengths = np.insert(np.cumsum(segment_lengths), 0, 0)
        total_length = cumulative_lengths[-1]
        interp_distances = np.linspace(0, total_length, interp_count)

        x_interp = np.interp(interp_distances, cumulative_lengths, positions_ft[:, 0])
        y_interp = np.interp(interp_distances, cumulative_lengths, positions_ft[:, 1])

        # Convert interpolated points to lat/lon
        latlon_points = []
        for x_ft, y_ft in zip(x_interp, y_interp):
            point = distance(feet=y_ft).destination((launch_lat, launch_lon), 0)
            point = distance(feet=x_ft).destination((point.latitude, point.longitude), 90)
            latlon_points.append((point.latitude, point.longitude))

        # Final radius scales with distance from origin
        final_offset = np.linalg.norm(positions_ft[-1]) / 5
        end_radius = max(500, final_offset * 0.25)  # scale appropriately
        radii = np.linspace(start_radius, end_radius, interp_count)

        # Trajectory line
        folium.PolyLine(latlon_points, color=color, weight=3, opacity=0.8, popup=label).add_to(fg)
        folium.Marker(latlon_points[0], popup=f'{label} Launch', icon=folium.Icon(color='blue')).add_to(fg)
        folium.Marker(latlon_points[-1], popup=f'{label} Final', icon=folium.Icon(color='red')).add_to(fg)

        # Error circles
        for i, ((lat, lon), radius_m) in enumerate(zip(latlon_points, radii)):
            if show_point_markers:
                folium.CircleMarker(location=(lat, lon), radius=2, color='black', fill=True).add_to(fg)
            folium.Circle(
                location=(lat, lon),
                radius=radius_m,
                color=color,
                weight=circle_border_weight,
                fill=True,
                fill_opacity=circle_opacity
            ).add_to(fg)

        fg.add_to(m)

    folium.LayerControl().add_to(m)
    return m

def main():
    vectors = drift.four_scenarios_posvecs
    distances = drift.distances
    labels = [f'Sustainer Nominal: {distances[0]:.2f} miles', f'Sustainer Off-Nominal: {distances[1]:.2f} miles', 
              f'Booster Nominal: {distances[2]:.2f} miles', f'Booster Off-Nominal: {distances[3]:.2f} miles']
    trajectory_map = plot_trajectory_map(vectors, labels)
    trajectory_map.save('Drift-Analysis/trajectory_map.html')

if __name__ == "__main__":
    main()
    print("Map saved as trajectory_map.html")
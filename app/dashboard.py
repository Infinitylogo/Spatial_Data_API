import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import folium
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import io
import base64
import pandas as pd
from pymongo import MongoClient
from flask import Flask
import numpy as np

def create_dashboard(flask_app, dashboard_type):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['spatialdb'] 
    
    if dashboard_type == 'location':
        points_collection = db['points']

        dash_app = dash.Dash(server=flask_app, name="Location Dashboard", url_base_pathname='/location/', external_stylesheets=[dbc.themes.BOOTSTRAP])

        # Layout
        dash_app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Location Dashboard"),
                    dcc.Dropdown(id='location-dropdown', options=[], value=None),
                    html.Div(id='location-map', style={'width': '100%', 'height': '100vh'}),
                ], width=12)
            ])
        ], fluid=True)

        # Callback to update location dropdown and map
        @dash_app.callback(
            [Output('location-dropdown', 'options'),
             Output('location-map', 'children')],
            Input('location-dropdown', 'value')
        )
        def update_location_dashboard(selected_location):
            # Fetch all points from the database
            points = list(points_collection.find())
            df = pd.DataFrame(points)
            
            # Limit dropdown options to 5 if more than 5 options are available
            dropdown_options = [{'label': point['name'], 'value': str(point['_id'])} for point in points[:5]]
            
            # Create the Folium map
            folium_map = folium.Map(location=[0, 0], zoom_start=2)
            
            for point in points:
                folium.Marker([point['latitude'], point['longitude']], popup=point['name']).add_to(folium_map)
            
            if selected_location:
                selected_point = next((point for point in points if str(point['_id']) == selected_location), None)
                if selected_point:
                    folium_map = folium.Map(location=[selected_point['latitude'], selected_point['longitude']], zoom_start=12)
                    folium.Marker([selected_point['latitude'], selected_point['longitude']], popup=selected_point['name']).add_to(folium_map)
            
            folium_map.save('folium_map.html')
            folium_map_html = html.Iframe(srcDoc=open('folium_map.html').read(), style={'width': '100%', 'height': '100vh'})
            
            return dropdown_options, folium_map_html

    elif dashboard_type == 'population':
        population_collection = db['polygons'] 

        dash_app = dash.Dash(server=flask_app, name="Population Density Dashboard", url_base_pathname='/population/', external_stylesheets=[dbc.themes.BOOTSTRAP])

        # Layout
        dash_app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Population Density Dashboard"),
                    dcc.Dropdown(id='population-dropdown', options=[], value=None),
                    html.Div(id='population-density-map', style={'width': '100%', 'height': '100vh'}),
                ], width=12)
            ])
        ], fluid=True)

        # Callback to update population dropdown and density map
        @dash_app.callback(
            [Output('population-dropdown', 'options'),
             Output('population-density-map', 'children')],
            Input('population-dropdown', 'value')
        )
        def update_population_density_dashboard(selected_population):
            # Fetch population density data from the database
            population_data = list(population_collection.find())
            df = pd.DataFrame(population_data)
            
            # Limit dropdown options to 5 if more than 5 options are available
            dropdown_options = [{'label': population['name'], 'value': str(population['_id'])} for population in population_data[:5]]
            
            # Create Cartopy map
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
            ax.coastlines()
            ax.add_feature(cfeature.BORDERS)
            
            if selected_population:
                selected_population_data = next((pop for pop in population_data if str(pop['_id']) == selected_population), None)
                if selected_population_data:
                    lons = np.array(selected_population_data['coordinates']['lon'])
                    lats = np.array(selected_population_data['coordinates']['lat'])
                    density = np.array(selected_population_data['density'])
                    
                    # Ensure coordinates and density arrays are of compatible shape
                    if lons.shape == lats.shape and lons.shape == density.shape:
                        pcm = ax.pcolormesh(lons, lats, density, cmap='Oranges', transform=ccrs.PlateCarree(), shading='auto')
                        plt.colorbar(pcm, ax=ax, orientation='vertical', label='Population Density')
                        plt.title("Population Density Map")
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            cartopy_map_image = base64.b64encode(buf.getvalue()).decode()
            cartopy_map_html = html.Img(src=f'data:image/png;base64,{cartopy_map_image}', style={'width': '100%', 'height': '100vh'})

            return dropdown_options, cartopy_map_html

    return dash_app

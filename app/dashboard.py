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
    if dashboard_type == 'location':
        dash_app = dash.Dash(server=flask_app, name="Location Dashboard", url_base_pathname='/location/', external_stylesheets=[dbc.themes.BOOTSTRAP])
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['your_database']  # Replace with your database name
        points_collection = db['points']  # Replace with your collection name

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
            
            # Create dropdown options
            dropdown_options = [{'label': point['name'], 'value': str(point['_id'])} for point in points]
            
            # Create the Folium map
            folium_map = folium.Map(location=[0, 0], zoom_start=2)
            
            for point in points:
                folium.Marker([point['latitude'], point['longitude']], popup=point['name']).add_to(folium_map)
            
            folium_map.save('folium_map.html')
            folium_map_html = html.Iframe(srcDoc=open('folium_map.html').read(), style={'width': '100%', 'height': '100vh'})
            
            return dropdown_options, folium_map_html

    elif dashboard_type == 'population':
        dash_app = dash.Dash(server=flask_app, name="Population Density Dashboard", url_base_pathname='/population/', external_stylesheets=[dbc.themes.BOOTSTRAP])
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['your_database']  # Replace with your database name
        population_collection = db['population']  # Replace with your collection name

        # Layout
        dash_app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Population Density Dashboard"),
                    html.Div(id='population-density-map', style={'width': '100%', 'height': '100vh'}),
                ], width=12)
            ])
        ], fluid=True)

        # Callback to update population density map
        @dash_app.callback(
            Output('population-density-map', 'children')
        )
        def update_population_density_dashboard():
            # Fetch population density data from the database
            population_data = list(population_collection.find())
            df = pd.DataFrame(population_data)
            
            # Create Cartopy map
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
            ax.coastlines()
            ax.add_feature(cfeature.BORDERS)
            
            # Plot population density (mock data here, replace with actual data)
            lon = np.linspace(-180, 180, 360)
            lat = np.linspace(-90, 90, 180)
            lon, lat = np.meshgrid(lon, lat)
            density = np.random.rand(*lon.shape) * 100  # Replace with actual density data

            density_plot = ax.pcolormesh(lon, lat, density, cmap='Oranges', transform=ccrs.PlateCarree(), shading='auto')
            plt.colorbar(density_plot, ax=ax, orientation='vertical', label='Population Density')
            plt.title("Population Density Map")

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            cartopy_map_image = base64.b64encode(buf.getvalue()).decode()
            cartopy_map_html = html.Img(src=f'data:image/png;base64,{cartopy_map_image}', style={'width': '100%', 'height': '100vh'})

            return cartopy_map_html

    return dash_app

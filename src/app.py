# Core imports
import os
import pandas as pd
from dash import Dash, dcc, html, callback, Input, Output, State, ctx, ALL, MATCH
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
import seaborn as sns
from audio_preview import audio_previews
from flask import send_from_directory
import dash

# Init app
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Expose the server variable for Gunicorn

# Configure server
server.config.update(
    dict(
        SECRET_KEY="your_secret_key_here",
        PORT=os.environ.get('PORT', 10000)
    )
)

# Get the absolute path to the directory containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the data file
dataset_path = os.path.join(BASE_DIR, 'data', 'Spotify-2000.csv')
df = pd.read_csv(dataset_path)

# Setting up clusters from sohini's code
features = ['Artist', 'Acousticness', 'Liveness', 'Popularity']
cluster_df = df[features].copy()

le = LabelEncoder()
cluster_df['Artist_encoded'] = le.fit_transform(cluster_df['Artist'])

scaler = StandardScaler()
X = scaler.fit_transform(cluster_df[['Artist_encoded', 'Acousticness', 'Liveness', 'Popularity']])

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X)

cluster_names = {
    0: "Acoustic Mainstream",
    1: "Popular Hits",
    2: "Rising Artists",
    3: "Live Performers"
}
df['Cluster_Name'] = df['Cluster'].map(cluster_names)

# Theme colors
BACKGROUND_COLOR = '#1E1E1E'
TEXT_COLOR = '#FFFFFF'
SPOTIFY_GREEN = '#1DB954'
GRID_COLOR = '#333333'
PLOT_BGCOLOR = '#2B2B2B'
PAPER_BGCOLOR = '#1E1E1E'

# Style configurations
HEADER_STYLE = {
    'color': TEXT_COLOR,
    'marginBottom': 10,
    'marginTop': 20,
    'fontFamily': 'Helvetica'
}

EXPLANATION_STYLE = {
    'color': TEXT_COLOR,
    'marginBottom': 20,
    'fontSize': '1.1em',
    'fontFamily': 'Helvetica',
    'opacity': 0.9,
    'lineHeight': '1.5'
}

HIGHLIGHT_STYLE = {
    'color': SPOTIFY_GREEN,
    'fontWeight': 'bold',
    'display': 'inline-block',
    'padding': '2px 8px',
    'borderRadius': '4px',
    'backgroundColor': 'rgba(29, 185, 84, 0.1)',
    'margin': '0 2px'
}

# Returns formatted feature label with description
def create_feature_label(feature_name):
    descriptions = {
        'Danceability': 'How suitable the song is for dancing',
        'Energy': 'How energetic the song feels',
        'Loudness (dB)': 'Overall loudness in decibels',
        'Speechiness': 'Amount of spoken words',
        'Acousticness': 'Amount of acoustic sound',
        'Liveness': 'Presence of live performance elements',
        'Valence': 'How positive the song sounds',
        'Beats Per Minute (BPM)': 'Speed of the song'
    }
    return f"{feature_name} ({descriptions[feature_name]})"

# Add navigation buttons component
def create_nav_buttons(page_number, total_pages):
    return html.Div([
        html.Button(
            "← Previous Songs",
            id='prev-button',
            style={
                'backgroundColor': 'transparent',
                'border': 'none',
                'color': 'gray',
                'cursor': 'default',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'padding': '8px 15px',
                'position': 'absolute',
                'bottom': '20px',
                'left': '55%'
            },
            disabled=True
        ),
        html.Div(
            f"Page {page_number + 1} of {total_pages}",
            style={
                'color': TEXT_COLOR,
                'fontSize': '14px',
                'position': 'absolute',
                'bottom': '20px',
                'left': '70%',
                'transform': 'translateX(-50%)'
            }
        ),
        html.Button(
            "Next Songs →",
            id='next-button',
            style={
                'backgroundColor': 'transparent',
                'border': 'none',
                'color': SPOTIFY_GREEN,
                'cursor': 'pointer',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'padding': '8px 15px',
                'position': 'absolute',
                'bottom': '20px',
                'right': '50px'
            }
        )
    ], id='nav-buttons', style={'position': 'relative', 'height': '50px', 'marginTop': '10px'})

# Layout
app.layout = html.Div([
    dcc.Store(id='cluster-page', data=0),
    dcc.Store(id='audio-state', data={'playing_index': None}),
    dcc.Store(id='preview-paths', data={}),
    
    # Section 1: Header and Music Style Selection
    html.Div([
        html.H1('Spotify 2000 Songs Analysis Dashboard', 
                style={
                    'textAlign': 'center', 
                    'color': SPOTIFY_GREEN, 
                    'marginBottom': 30,
                    'paddingTop': 20,
                    'fontFamily': 'Helvetica',
                    'fontSize': '2.5em',
                    'textShadow': '2px 2px 4px rgba(0,0,0,0.3)'
                }),
        
        html.P([
            "Welcome to the ",
            html.Span("Spotify Songs Analysis Dashboard!", style={'color': SPOTIFY_GREEN, 'fontWeight': 'bold'}),
            " Dive into our collection of the top 2000 songs on Spotify. ",
            "Each visualization reveals unique patterns and insights about your favorite music. ",
            html.Span("Let's explore!", style={'color': SPOTIFY_GREEN, 'fontWeight': 'bold'})
        ], style=EXPLANATION_STYLE),
        
        html.Div([
            html.H3('Discover Your Music Style', style={
                **HEADER_STYLE,
                'fontSize': '1.8em',
                'textAlign': 'center',
                'marginBottom': '25px'
            }),
            html.P([
                "We've analyzed the songs and grouped them into ",
                html.Span("four distinct styles", style={'color': SPOTIFY_GREEN, 'fontWeight': 'bold'}),
                ". Choose a style below to explore songs that match your taste:",
                html.Br(), html.Br(),
                html.Span("• Acoustic Mainstream: ", style=HIGHLIGHT_STYLE),
                "Songs with rich acoustic elements and proven popularity", html.Br(),
                html.Span("• Popular Hits: ", style=HIGHLIGHT_STYLE),
                "Well-known artists with polished production", html.Br(),
                html.Span("• Rising Artists: ", style=HIGHLIGHT_STYLE),
                "Fresh talent with modern sound", html.Br(),
                html.Span("• Live Performers: ", style=HIGHLIGHT_STYLE),
                "Songs that capture the energy of live performance"
            ], style=EXPLANATION_STYLE),
            html.Label('Select a Music Style:', style={'color': TEXT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.1em'}),
            dcc.Dropdown(
                id='cluster-selector',
                options=[
                    {'label': name, 'value': num} 
                    for num, name in cluster_names.items()
                ],
                value=0,
                style={
                    'backgroundColor': PLOT_BGCOLOR,
                    'color': 'white',
                    'border': f'1px solid {GRID_COLOR}',
                    'width': '100%',
                    'maxWidth': '1400px',
                    'margin': '0 auto'
                },
                className='dropdown-dark'
            ),
            html.Div([
                # Radar Chart and Songs sections...
                html.Div([
                    html.H3('Cluster Characteristics (Average Values)', 
                           style={'textAlign': 'center', 'color': TEXT_COLOR, 'marginBottom': '20px'}),
                    dcc.Graph(
                        id='radar-chart',
                        style={'width': '600px', 'margin': '0 auto'}
                    )
                ], style={'marginBottom': '40px'}),

                html.Div([
                    html.H3('Top Songs in this Category', 
                           style={'textAlign': 'center', 'color': TEXT_COLOR, 'marginBottom': '20px'}),
                    html.Div([
                        dcc.Graph(
                            id='songs-chart',
                            style={'height': '400px'}
                        ),
                        html.Div(id='audio-controls', 
                                style={'marginTop': '20px', 'padding': '0 20px'}),
                    ], style={'width': '100%', 'maxWidth': '1200px', 'margin': '0 auto'}),
                    html.Div(id='nav-buttons', 
                            style={'marginTop': '20px', 'textAlign': 'center'})
                ])
            ], style={'width': '100%', 'maxWidth': '1800px', 'margin': '0 auto', 'padding': '20px'})
        ], style={
            'width': '100%',
            'maxWidth': '1800px',
            'margin': '0 auto',
            'padding': '20px',
            'backgroundColor': 'rgba(43, 43, 43, 0.5)',
            'borderRadius': '15px',
            'border': f'1px solid {GRID_COLOR}',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        }),
    ], style={
        'padding': '20px',
        'borderBottom': f'2px solid {SPOTIFY_GREEN}',
        'marginBottom': '40px'
    }),
    
    # Section 2: Genre Analysis
    html.Div([
        html.H3('Genre and Timeline Analysis', 
                style={
                    'textAlign': 'center',
                    'color': SPOTIFY_GREEN,
                    'fontSize': '2em',
                    'marginBottom': '30px',
                    'textShadow': '2px 2px 4px rgba(0,0,0,0.3)'
                }),
        html.Div([
            # Left side - Genre Analysis
            html.Div([
                html.Div([
                    html.H3('Most Popular Music Genres', style={
                        **HEADER_STYLE,
                        'fontSize': '1.8em',
                        'marginBottom': '20px'
                    }),
                    html.P([
                        "Explore the diverse world of ",
                        html.Span("music genres", style=HIGHLIGHT_STYLE),
                        " in our collection! Use the slider to reveal more or fewer genres in the visualization."
                    ], style=EXPLANATION_STYLE),
                    html.Div([
                        html.Label('Number of genres to display:', 
                                 style={'color': TEXT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.1em'}),
                        dcc.Slider(
                            id='genre-count-slider',
                            min=10,
                            max=149,
                            step=10,
                            value=10,
                            marks={
                                10: {'label': '10', 'style': {'color': TEXT_COLOR}},
                                50: {'label': '50', 'style': {'color': TEXT_COLOR}},
                                100: {'label': '100', 'style': {'color': TEXT_COLOR}},
                                149: {'label': 'All (149)', 'style': {'color': TEXT_COLOR}}
                            },
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                    ], style={'margin': '20px 0'}),
                    dcc.Graph(id='genre-pie')
                ], style={
                    'height': '100%',
                    'padding': '20px',
                    'backgroundColor': 'rgba(43, 43, 43, 0.7)',
                    'borderRadius': '15px',
                    'border': f'1px solid {GRID_COLOR}',
                    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
                })
            ], style={
                'width': '49%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'marginRight': '1%'
            }),
            
            # Right side - Timeline Analysis
            html.Div([
                html.Div([
                    html.H3('Music Through the Years', style={
                        **HEADER_STYLE,
                        'fontSize': '1.8em',
                        'marginBottom': '20px'
                    }),
                    html.P([
                        "Journey through time with our ",
                        html.Span("year-by-year breakdown", style=HIGHLIGHT_STYLE),
                        " of song releases. Discover which years were the most musically prolific!"
                    ], style=EXPLANATION_STYLE),
                    dcc.Graph(id='year-histogram')
                ], style={
                    'height': '100%',
                    'padding': '20px',
                    'backgroundColor': 'rgba(43, 43, 43, 0.7)',
                    'borderRadius': '15px',
                    'border': f'1px solid {GRID_COLOR}',
                    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
                })
            ], style={
                'width': '49%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'marginLeft': '1%'
            })
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'stretch',
            'marginBottom': '40px'
        })
    ], style={
        'width': '100%',
        'maxWidth': '1800px',
        'margin': '40px auto',
        'padding': '20px'
    }),
    
    # Section 3: Song Characteristics and Charts
    html.Div([
        html.H3('Detailed Song Analysis', 
                style={
                    'textAlign': 'center',
                    'color': SPOTIFY_GREEN,
                    'fontSize': '2em',
                    'marginBottom': '30px',
                    'textShadow': '2px 2px 4px rgba(0,0,0,0.3)'
                }),
        
        # Song Characteristics Section
        html.Div([
            html.H3('Explore Song Characteristics', style={
                **HEADER_STYLE,
                'fontSize': '1.8em',
                'textAlign': 'center',
                'marginBottom': '25px'
            }),
            html.P([
                "Uncover the hidden patterns in your favorite music! Compare different ",
                html.Span("song features", style=HIGHLIGHT_STYLE),
                " to see how they relate. Try comparing ",
                html.Span("Danceability", style={'color': SPOTIFY_GREEN, 'fontWeight': 'bold'}),
                " with ",
                html.Span("Energy", style={'color': SPOTIFY_GREEN, 'fontWeight': 'bold'}),
                " to discover what makes a song perfect for dancing!"
            ], style=EXPLANATION_STYLE),
            html.Div([
                html.Label('Choose what to show on the X-axis:', 
                          style={'color': TEXT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.1em'}),
                dcc.Dropdown(
                    id='x-feature',
                    options=[
                        {'label': create_feature_label(feature), 'value': feature}
                        for feature in [
                            'Danceability',
                            'Energy',
                            'Loudness (dB)',
                            'Speechiness',
                            'Acousticness',
                            'Liveness',
                            'Valence',
                            'Beats Per Minute (BPM)'
                        ]
                    ],
                    value='Energy',
                    style={
                        'backgroundColor': PLOT_BGCOLOR,
                        'color': 'white',
                        'border': f'1px solid {GRID_COLOR}',
                        'marginBottom': '10px'
                    },
                    className='dropdown-dark'
                ),
                html.Label('Choose what to show on the Y-axis:', 
                          style={'color': TEXT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.1em'}),
                dcc.Dropdown(
                    id='y-feature',
                    options=[
                        {'label': create_feature_label(feature), 'value': feature}
                        for feature in [
                            'Danceability',
                            'Energy',
                            'Loudness (dB)',
                            'Speechiness',
                            'Acousticness',
                            'Liveness',
                            'Valence',
                            'Beats Per Minute (BPM)'
                        ]
                    ],
                    value='Danceability',
                    style={
                        'backgroundColor': PLOT_BGCOLOR,
                        'color': 'white',
                        'border': f'1px solid {GRID_COLOR}'
                    },
                    className='dropdown-dark'
                ),
            ], style={'width': '100%', 'maxWidth': '1400px', 'margin': '0 auto'}),
            dcc.Graph(id='feature-correlation')
        ], style={
            'padding': '30px',
            'backgroundColor': 'rgba(43, 43, 43, 0.7)',
            'borderRadius': '15px',
            'border': f'1px solid {GRID_COLOR}',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'marginBottom': '40px'
        }),
        
        # Chart-Topping Artists Section
        html.Div([
            html.H3('Chart-Topping Artists', style={
                **HEADER_STYLE,
                'fontSize': '1.8em',
                'textAlign': 'center',
                'marginBottom': '25px'
            }),
            html.P([
                "Discover the ",
                html.Span("most influential artists", style=HIGHLIGHT_STYLE),
                " in our collection! These are the creators who have multiple hits in the top 2000 songs."
            ], style=EXPLANATION_STYLE),
            dcc.Graph(id='top-artists')
        ], style={
            'padding': '30px',
            'backgroundColor': 'rgba(43, 43, 43, 0.7)',
            'borderRadius': '15px',
            'border': f'1px solid {GRID_COLOR}',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'marginBottom': '40px'
        }),
        
        # Popularity Trend Section
        html.Div([
            html.H3('Popularity Across Time', style={
                **HEADER_STYLE,
                'fontSize': '1.8em',
                'textAlign': 'center',
                'marginBottom': '25px'
            }),
            html.P([
                "Explore how song popularity evolves through time! Each dot represents a song, while the ",
                html.Span("green trend line", style={'color': SPOTIFY_GREEN, 'fontWeight': 'bold'}),
                " shows the average popularity for each year.",
                html.Br(), html.Br(),
                html.Span("Popularity Score Guide:", style={'textDecoration': 'underline', 'color': SPOTIFY_GREEN}),
                html.Br(),
                html.Span("• 80-100: ", style=HIGHLIGHT_STYLE), "Massive hits everyone knows", html.Br(),
                html.Span("• 60-79: ", style=HIGHLIGHT_STYLE), "Very popular songs", html.Br(),
                html.Span("• 40-59: ", style=HIGHLIGHT_STYLE), "Well-known songs", html.Br(),
                html.Span("• 20-39: ", style=HIGHLIGHT_STYLE), "Moderately known songs", html.Br(),
                html.Span("• 0-19: ", style=HIGHLIGHT_STYLE), "Less known songs"
            ], style=EXPLANATION_STYLE),
            html.Label('Filter by Genre (you can select multiple):', 
                      style={'color': TEXT_COLOR, 'fontWeight': 'bold', 'fontSize': '1.1em'}),
            dcc.Dropdown(
                id='genre-filter',
                options=[
                    {'label': genre, 'value': genre} 
                    for genre in sorted(df['Top Genre'].unique())
                ],
                value='All',
                multi=True,
                style={
                    'backgroundColor': PLOT_BGCOLOR,
                    'color': 'white',
                    'border': f'1px solid {GRID_COLOR}',
                    'width': '100%',
                    'maxWidth': '1400px',
                    'margin': '0 auto'
                },
                className='dropdown-dark',
                placeholder='Select genres...'
            ),
            dcc.Graph(id='popularity-trend')
        ], style={
            'padding': '30px',
            'backgroundColor': 'rgba(43, 43, 43, 0.7)',
            'borderRadius': '15px',
            'border': f'1px solid {GRID_COLOR}',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        })
    ], style={
        'width': '100%',
        'maxWidth': '1800px',
        'margin': '40px auto',
        'padding': '20px'
    })
], style={'backgroundColor': BACKGROUND_COLOR, 'padding': '20px', 'width': '100%', 'margin': '0 auto'})

# CSS for dropdowns
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .dropdown-dark .Select-control {
                background-color: #2B2B2B;
                border: 1px solid #404040;
            }
            .dropdown-dark .Select-menu-outer {
                background-color: #2B2B2B;
                border: 1px solid #404040;
                z-index: 1000;
            }
            .dropdown-dark .Select-value-label {
                color: white !important;
            }
            .dropdown-dark .Select-option {
                background-color: #2B2B2B;
                color: white;
                padding: 8px 10px;
            }
            .dropdown-dark .Select-option:hover {
                background-color: #1DB954;
                color: white;
            }
            .dropdown-dark .Select-option.is-selected {
                background-color: #1DB954;
                color: white;
            }
            .dropdown-dark .Select-option.is-focused {
                background-color: #1DB954;
                color: white;
            }
            .dropdown-dark .Select-value {
                color: white !important;
                line-height: 34px !important;
                background-color: #1DB954 !important;
                border: none !important;
                border-radius: 2px !important;
                margin: 2px !important;
            }
            .dropdown-dark .Select-value span {
                color: white !important;
            }
            .dropdown-dark .Select-multi-value-wrapper {
                padding: 2px;
            }
            .dropdown-dark .Select-placeholder {
                color: #CCCCCC !important;
            }
            .dropdown-dark .Select-input > input {
                color: white;
            }
            .dropdown-dark .Select-arrow-zone {
                color: white;
            }
            .dropdown-dark .Select-clear-zone {
                color: white;
            }
            .dropdown-dark .Select-value-icon {
                border-right: none !important;
                background-color: rgba(255,255,255,0.1) !important;
            }
            .dropdown-dark .Select-value-icon:hover {
                background-color: rgba(255,255,255,0.2) !important;
                color: white !important;
            }
            .VirtualizedSelectFocusedOption {
                background-color: #1DB954 !important;
            }
            .VirtualizedSelectOption {
                color: white;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Callbacks
@callback(
    Output('genre-pie', 'figure'),
    [Input('genre-filter', 'value'),
     Input('genre-count-slider', 'value')]
)
def update_genre_pie(_, num_genres):
    genre_counts = df['Top Genre'].value_counts().head(num_genres)
    
    base_colors = [
        '#1DB954', '#1ED760', '#4B917D', '#FF6B6B', '#4A90E2',
        '#9B59B6', '#F1C40F', '#E67E22', '#E74C3C', '#3498DB'
    ]
    
    if num_genres > len(base_colors):
        from colour import Color
        colors = []
        for i in range(len(base_colors) - 1):
            c1 = Color(base_colors[i])
            c2 = Color(base_colors[i + 1])
            colors.extend([c.hex for c in c1.range_to(c2, num_genres // len(base_colors) + 1)])
        colors = colors[:num_genres]
    else:
        colors = base_colors[:num_genres]
    
    fig = px.pie(values=genre_counts.values, 
                 names=genre_counts.index,
                 title=f'Top {num_genres} Music Genres',
                 color_discrete_sequence=colors)
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont=dict(color='white', size=16, family='Helvetica'),
        hovertemplate="<b>Genre: %{label}</b><br>Number of Songs: %{value}<br>Percentage: %{percent}<extra></extra>",
        marker=dict(line=dict(color=BACKGROUND_COLOR, width=2))
    )
    
    fig.update_layout(
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PAPER_BGCOLOR,
        font=dict(color=TEXT_COLOR, family='Helvetica'),
        title=dict(text=f'Distribution of Top {num_genres} Music Genres', font=dict(size=24, color=TEXT_COLOR), y=0.95),
        height=600,
        margin=dict(t=80, b=20, l=20, r=20),
        showlegend=False,
        annotations=[dict(
            text=f"Showing top {num_genres} out of 149 total genres",
            x=0.5, y=-0.1,
            showarrow=False,
            font=dict(size=14, color=TEXT_COLOR),
            xref="paper", yref="paper"
        )]
    )
    return fig

@callback(
    Output('year-histogram', 'figure'),
    Input('genre-filter', 'value')
)
def update_year_histogram(selected_genres):
    filtered_df = df if not selected_genres or 'All' in selected_genres else df[df['Top Genre'].isin(selected_genres)]
    
    fig = go.Figure(data=[go.Histogram(
        x=filtered_df['Year'],
        nbinsx=30,
        marker_color=SPOTIFY_GREEN,
        hovertemplate="Year: %{x}<br>Number of Songs: %{y}<extra></extra>"
    )])
    
    fig.update_layout(
        title='Distribution of Songs by Year',
        xaxis_title='Year',
        yaxis_title='Number of Songs',
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PAPER_BGCOLOR,
        font=dict(color=TEXT_COLOR),
        title_font_color=TEXT_COLOR,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR)
    )
    return fig

@callback(
    Output('feature-correlation', 'figure'),
    [Input('x-feature', 'value'),
     Input('y-feature', 'value'),
     Input('genre-filter', 'value')]
)
def update_feature_correlation(x_feature, y_feature, selected_genres):
    filtered_df = df if not selected_genres or 'All' in selected_genres else df[df['Top Genre'].isin(selected_genres)]
    
    fig = px.scatter(filtered_df, 
                    x=x_feature, 
                    y=y_feature,
                    color='Top Genre',
                    hover_data=['Title', 'Artist'],
                    color_discrete_sequence=px.colors.qualitative.Set3)
    
    fig.update_traces(
        marker=dict(size=8),
        hovertemplate="<b>%{customdata[0]}</b><br>" +
                     "Artist: %{customdata[1]}<br>" +
                     f"{x_feature}: %{{x}}<br>" +
                     f"{y_feature}: %{{y}}<br>" +
                     "Genre: %{marker.color}<extra></extra>"
    )
    
    fig.update_layout(
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PAPER_BGCOLOR,
        font=dict(color=TEXT_COLOR),
        title_font_color=TEXT_COLOR,
        height=700,
        xaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=False,
            title=dict(text=x_feature, font=dict(size=14))
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=False,
            title=dict(text=y_feature, font=dict(size=14))
        ),
        legend=dict(
            title_text='Genre',
            itemsizing='constant',
            font=dict(size=12),
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.98
        ),
        margin=dict(t=50, b=50)
    )
    return fig

@callback(
    Output('top-artists', 'figure'),
    Input('genre-filter', 'value')
)
def update_top_artists(selected_genres):
    filtered_df = df if not selected_genres or 'All' in selected_genres else df[df['Top Genre'].isin(selected_genres)]
    top_artists = filtered_df['Artist'].value_counts().head(15)
    
    fig = go.Figure(data=[go.Bar(
        x=top_artists.index,
        y=top_artists.values,
        marker_color=SPOTIFY_GREEN,
        hovertemplate="Artist: %{x}<br>Number of Songs: %{y}<extra></extra>"
    )])
    
    fig.update_layout(
        title='Top 15 Artists by Number of Songs',
        xaxis_title='Artist',
        yaxis_title='Number of Songs',
        xaxis_tickangle=45,
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PAPER_BGCOLOR,
        font=dict(color=TEXT_COLOR),
        title_font_color=TEXT_COLOR,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR)
    )
    return fig

@callback(
    Output('popularity-trend', 'figure'),
    Input('genre-filter', 'value')
)
def update_popularity_trend(selected_genres):
    filtered_df = df if not selected_genres or 'All' in selected_genres else df[df['Top Genre'].isin(selected_genres)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=filtered_df['Year'],
        y=filtered_df['Popularity'],
        mode='markers',
        marker=dict(
            color=filtered_df['Popularity'],
            colorscale=[[0, '#2B2B2B'], [1, SPOTIFY_GREEN]],
            size=8,
            showscale=True,
            colorbar=dict(
                title='Popularity Score',
                titleside='right',
                tickmode='array',
                ticktext=['0-19', '20-39', '40-59', '60-79', '80-100'],
                tickvals=[10, 30, 50, 70, 90],
                ticks='outside'
            )
        ),
        hovertemplate="<b>%{text}</b><br>" +
                     "Artist: %{customdata}<br>" +
                     "Year: %{x}<br>" +
                     "Popularity: %{y}<extra></extra>",
        text=filtered_df['Title'],
        customdata=filtered_df['Artist']
    ))
    
    year_avg = filtered_df.groupby('Year')['Popularity'].mean().reset_index()
    fig.add_trace(go.Scatter(
        x=year_avg['Year'],
        y=year_avg['Popularity'],
        mode='lines',
        line=dict(color=SPOTIFY_GREEN, width=3),
        name='Average Popularity',
        hovertemplate="Year: %{x}<br>Average Popularity: %{y:.1f}<extra></extra>"
    ))
    
    fig.update_layout(
        title='Song Popularity Over Time',
        xaxis_title='Release Year',
        yaxis_title='Popularity Score',
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PAPER_BGCOLOR,
        font=dict(color=TEXT_COLOR),
        title_font_color=TEXT_COLOR,
        height=600,
        showlegend=False,
        xaxis=dict(
            gridcolor=GRID_COLOR,
            tickmode='linear',
            dtick=5
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            range=[0, 100],
            tickmode='array',
            tickvals=[0, 20, 40, 60, 80, 100]
        )
    )
    return fig

@callback(
    Output('radar-chart', 'figure'),
    [Input('cluster-selector', 'value')]
)
def update_radar_chart(selected_cluster):
    try:
        cluster_data = df[df['Cluster'] == selected_cluster].copy()
        
        radar_features = ['Acousticness', 'Liveness', 'Popularity', 'Energy', 'Danceability', 'Valence']
        mean_values = cluster_data[radar_features].mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=mean_values,
            theta=radar_features,
            fill='toself',
            name='Cluster Characteristics',
            line=dict(color=SPOTIFY_GREEN),
            fillcolor=f'rgba(29, 185, 84, 0.3)'
        ))

        fig.update_layout(
            showlegend=False,
            plot_bgcolor=PLOT_BGCOLOR,
            paper_bgcolor=PAPER_BGCOLOR,
            font=dict(color=TEXT_COLOR),
            polar=dict(
                bgcolor=PLOT_BGCOLOR,
                radialaxis=dict(
                    visible=True, 
                    range=[0, 100], 
                    gridcolor=GRID_COLOR,
                    color=TEXT_COLOR
                ),
                angularaxis=dict(
                    gridcolor=GRID_COLOR,
                    color=TEXT_COLOR
                )
            ),
            margin=dict(t=0, b=0, l=50, r=50),  # Reduce margins
            height=400  # Control the height
        )
        
        return fig

    except Exception as e:
        print(f"Error in update_radar_chart: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

@callback(
    [Output('songs-chart', 'figure'),
     Output('preview-paths', 'data')],
    [Input('cluster-selector', 'value'),
     Input('cluster-page', 'data')]
)
def update_songs_chart(selected_cluster, page_number):
    try:
        if page_number is None:
            page_number = 0
            
        cluster_data = df[df['Cluster'] == selected_cluster].copy()
        total_songs = len(cluster_data)
        total_pages = (total_songs + 9) // 10
        page_number = max(0, min(page_number, total_pages - 1))
        
        start_idx = page_number * 10
        top_songs = cluster_data.sort_values('Popularity', ascending=False).iloc[start_idx:start_idx + 10]

        # Get preview paths
        preview_paths = audio_previews(top_songs)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=top_songs['Popularity'],
            y=[f"  {row['Title']}" for _, row in top_songs.iterrows()],
            orientation='h',
            marker_color=SPOTIFY_GREEN,
            text=top_songs['Artist'],
            textposition='auto',
            customdata=list(zip(top_songs['Title'], top_songs['Artist'])),
            hovertemplate="%{customdata[0]} by %{customdata[1]}<br>Popularity: %{x}<extra></extra>"
        ))

        fig.update_layout(
            showlegend=False,
            plot_bgcolor=PLOT_BGCOLOR,
            paper_bgcolor=PAPER_BGCOLOR,
            font=dict(color=TEXT_COLOR),
            xaxis=dict(
                title='Popularity Score',
                gridcolor=GRID_COLOR,
                color=TEXT_COLOR,
                range=[0, 100]
            ),
            yaxis=dict(
                title='',
                gridcolor=GRID_COLOR,
                color=TEXT_COLOR,
                automargin=True
            ),
            margin=dict(t=0, b=50, l=150, r=50),
            height=400
        )
        
        return fig, preview_paths

    except Exception as e:
        print(f"Error in update_songs_chart: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

@callback(
    [Output('audio-controls', 'children'),
     Output('nav-buttons', 'children')],
    [Input('cluster-selector', 'value'),
     Input('cluster-page', 'data')]
)
def update_controls(selected_cluster, page_number):
    try:
        if page_number is None:
            page_number = 0
            
        cluster_data = df[df['Cluster'] == selected_cluster].copy()
        total_songs = len(cluster_data)
        total_pages = (total_songs + 9) // 10
        page_number = max(0, min(page_number, total_pages - 1))
        
        start_idx = page_number * 10
        top_songs = cluster_data.sort_values('Popularity', ascending=False).iloc[start_idx:start_idx + 10]
        
        preview_paths = audio_previews(top_songs)
        
        # Create audio controls - now in reverse order to match graph
        audio_controls = html.Div([
            html.Div([
                html.Span(
                    row['Title'],
                    style={'color': TEXT_COLOR, 'marginRight': '10px'}
                ),
                html.Span(
                    f"by {row['Artist']}",
                    style={'color': TEXT_COLOR, 'opacity': '0.7', 'marginRight': '10px'}
                ),
                html.Audio(
                    id={'type': 'song-preview', 'index': idx},
                    src=f"/audio_previews/{os.path.basename(preview_paths[row['Title']])}" if row['Title'] in preview_paths else "",
                    controls=True,  # Show the native audio controls
                    style={
                        'height': '30px',
                        'verticalAlign': 'middle'
                    },
                    **{'data-title': row['Title']}
                )
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'marginBottom': '15px',
                'backgroundColor': PLOT_BGCOLOR,
                'padding': '10px',
                'borderRadius': '5px'
            }) for idx, (_, row) in enumerate(top_songs.iloc[::-1].iterrows()) if row['Title'] in preview_paths
        ], style={
            'maxWidth': '800px',
            'margin': '0 auto',
            'padding': '20px'
        })

        # Create navigation buttons
        nav_buttons = html.Div([
            html.Button(
                "← Previous Songs",
                id='prev-button',
                style={
                    'backgroundColor': 'transparent',
                    'border': 'none',
                    'color': SPOTIFY_GREEN if page_number > 0 else 'gray',
                    'cursor': 'pointer' if page_number > 0 else 'default',
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'padding': '8px 15px',
                    'marginRight': '20px'
                },
                disabled=page_number <= 0
            ),
            html.Span(
                f"Page {page_number + 1} of {total_pages}",
                style={
                    'color': TEXT_COLOR,
                    'fontSize': '14px',
                    'margin': '0 20px'
                }
            ),
            html.Button(
                "Next Songs →",
                id='next-button',
                style={
                    'backgroundColor': 'transparent',
                    'border': 'none',
                    'color': SPOTIFY_GREEN if (page_number + 1) * 10 < total_pages * 10 else 'gray',
                    'cursor': 'pointer' if (page_number + 1) * 10 < total_pages * 10 else 'default',
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'padding': '8px 15px',
                    'marginLeft': '20px'
                },
                disabled=(page_number + 1) * 10 >= total_pages * 10
            )
        ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'})

        return audio_controls, nav_buttons

    except Exception as e:
        print(f"Error in update_controls: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

@callback(
    Output('cluster-page', 'data'),
    [Input('prev-button', 'n_clicks'),
     Input('next-button', 'n_clicks'),
     Input('cluster-selector', 'value')],
    [State('cluster-page', 'data')],
    prevent_initial_call=True
)
def update_page(prev_clicks, next_clicks, selected_cluster, current_page):
    from dash import ctx
    if not ctx.triggered:
        raise PreventUpdate
        
    trigger_id = ctx.triggered_id
    
    if current_page is None:
        current_page = 0
    
    if trigger_id == 'cluster-selector':
        return 0
        
    total_songs = len(df[df['Cluster'] == selected_cluster])
    total_pages = (total_songs + 9) // 10
    
    if trigger_id == 'prev-button' and current_page > 0:
        return max(0, current_page - 1)
    elif trigger_id == 'next-button' and current_page < total_pages - 1:
        return min(total_pages - 1, current_page + 1)
    
    return current_page

# Add this to serve the audio files
@app.server.route('/audio_previews/<path:path>')
def serve_audio(path):
    return send_from_directory('audio_previews', path)

if __name__ == '__main__':
    # Get port from environment variable or use 8050 as default
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
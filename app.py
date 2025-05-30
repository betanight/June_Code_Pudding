from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import seaborn as sns

# Initialize the Dash app
app = Dash(__name__)

# Load and preprocess the data
df = pd.read_csv('data/Spotify-2000.csv')

# Define theme colors
BACKGROUND_COLOR = '#1E1E1E'
TEXT_COLOR = '#FFFFFF'
SPOTIFY_GREEN = '#1DB954'
GRID_COLOR = '#333333'
PLOT_BGCOLOR = '#2B2B2B'
PAPER_BGCOLOR = '#1E1E1E'

# Define styles
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
    'opacity': 0.8
}

# Helper function for feature labels
def create_feature_label(feature_name):
    """Create a more descriptive label for features"""
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

# Create the layout with multiple sections
app.layout = html.Div([
    # Header
    html.H1('Spotify 2000 Songs Analysis Dashboard', 
            style={
                'textAlign': 'center', 
                'color': SPOTIFY_GREEN, 
                'marginBottom': 30,
                'paddingTop': 20,
                'fontFamily': 'Helvetica'
            }),
    
    html.P(
        "Welcome to the Spotify Songs Analysis Dashboard! This tool helps you explore the top 2000 songs on Spotify. "
        "Each visualization below shows different aspects of the music data. Use the interactive features to explore what interests you!",
        style=EXPLANATION_STYLE
    ),
    
    # First row with genre distribution and year distribution
    html.Div([
        html.Div([
            html.H3('Most Popular Music Genres', style=HEADER_STYLE),
            html.P(
                "This pie chart shows the distribution of genres in the dataset. "
                "Use the slider below to control how many top genres to display.",
                style=EXPLANATION_STYLE
            ),
            html.Div([
                html.Label('Number of genres to display:', style={'color': TEXT_COLOR, 'marginBottom': '10px'}),
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
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3('How Many Songs Were Released Each Year?', style=HEADER_STYLE),
            html.P(
                "This bar chart shows the number of songs released each year. "
                "Taller bars mean more songs were released in that year.",
                style=EXPLANATION_STYLE
            ),
            dcc.Graph(id='year-histogram')
        ], style={'width': '48%', 'display': 'inline-block'})
    ]),
    
    # Feature correlation section
    html.Div([
        html.H3('Explore Song Characteristics', style=HEADER_STYLE),
        html.P(
            "Compare different song features to find patterns! For example, try comparing 'Danceability' with 'Energy' "
            "to see if more energetic songs are also more danceable. Each dot represents one song, colored by its genre.",
            style=EXPLANATION_STYLE
        ),
        html.Label('Choose what to show on the X-axis:', style={'color': TEXT_COLOR}),
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
                'border': f'1px solid {GRID_COLOR}'
            },
            className='dropdown-dark'
        ),
        html.Label('Choose what to show on the Y-axis:', style={'color': TEXT_COLOR, 'marginTop': 20}),
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
        dcc.Graph(id='feature-correlation')
    ]),
    
    # Top Artists section
    html.Div([
        html.H3('Most Featured Artists', style=HEADER_STYLE),
        html.P(
            "This chart shows which artists have the most songs in the top 2000. "
            "The taller the bar, the more songs that artist has in the collection.",
            style=EXPLANATION_STYLE
        ),
        dcc.Graph(id='top-artists')
    ]),
    
    # Popularity vs Year with Genre Filter
    html.Div([
        html.H3('How Popular Are Songs From Different Years?', style=HEADER_STYLE),
        html.P([
            "Each dot represents a song, with its position showing when it was released (left-right) and how popular it is (up-down). ",
            "The green line shows the average popularity of songs from each year. ",
            html.Br(), html.Br(),
            "Popularity Score Explained:", html.Br(),
            "• 80-100: Massive hits everyone knows", html.Br(),
            "• 60-79: Very popular songs", html.Br(),
            "• 40-59: Well-known songs", html.Br(),
            "• 20-39: Moderately known songs", html.Br(),
            "• 0-19: Less known songs"
        ], style=EXPLANATION_STYLE),
        html.Label('Filter by Genre (you can select multiple):', style={'color': TEXT_COLOR}),
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
                'minWidth': '200px',
                'width': '100%'
            },
            className='dropdown-dark',
            placeholder='Select genres...'
        ),
        dcc.Graph(id='popularity-trend')
    ])
], style={'backgroundColor': BACKGROUND_COLOR, 'padding': '20px'})

# Add custom CSS to style the dropdowns
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

# Callback for genre pie chart
@callback(
    Output('genre-pie', 'figure'),
    [Input('genre-filter', 'value'),
     Input('genre-count-slider', 'value')]
)
def update_genre_pie(_, num_genres):
    genre_counts = df['Top Genre'].value_counts().head(num_genres)
    
    # Custom color palette with high contrast and vibrant colors
    base_colors = [
        '#1DB954',  # Spotify green
        '#1ED760',  # Lighter green
        '#4B917D',  # Teal
        '#FF6B6B',  # Coral
        '#4A90E2',  # Blue
        '#9B59B6',  # Purple
        '#F1C40F',  # Yellow
        '#E67E22',  # Orange
        '#E74C3C',  # Red
        '#3498DB'   # Light blue
    ]
    
    # Generate more colors if needed by interpolating between existing colors
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
        textfont=dict(
            color='white',
            size=16,
            family='Helvetica'
        ),
        hovertemplate="<b>Genre: %{label}</b><br>" +
                     "Number of Songs: %{value}<br>" +
                     "Percentage: %{percent}<extra></extra>",
        marker=dict(line=dict(color=BACKGROUND_COLOR, width=2))
    )
    
    fig.update_layout(
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PAPER_BGCOLOR,
        font=dict(
            color=TEXT_COLOR,
            family='Helvetica'
        ),
        title=dict(
            text=f'Distribution of Top {num_genres} Music Genres',
            font=dict(
                size=24,
                color=TEXT_COLOR
            ),
            y=0.95
        ),
        height=600,
        margin=dict(t=80, b=20, l=20, r=20),
        showlegend=False,
        annotations=[
            dict(
                text=f"Showing top {num_genres} out of 149 total genres",
                x=0.5,
                y=-0.1,
                showarrow=False,
                font=dict(
                    size=14,
                    color=TEXT_COLOR
                ),
                xref="paper",
                yref="paper"
            )
        ]
    )
    return fig

# Callback for year histogram
@callback(
    Output('year-histogram', 'figure'),
    Input('genre-filter', 'value')
)
def update_year_histogram(selected_genres):
    if not selected_genres or 'All' in selected_genres:
        filtered_df = df
    else:
        filtered_df = df[df['Top Genre'].isin(selected_genres)]
    
    fig = go.Figure(data=[
        go.Histogram(
            x=filtered_df['Year'],
            nbinsx=30,
            marker_color=SPOTIFY_GREEN,
            hovertemplate="Year: %{x}<br>Number of Songs: %{y}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        title='Songs Released by Year',
        xaxis_title='Release Year',
        yaxis_title='Number of Songs',
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PAPER_BGCOLOR,
        font=dict(color=TEXT_COLOR),
        title_font_color=TEXT_COLOR,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        bargap=0.2
    )
    return fig

# Callback for feature correlation
@callback(
    Output('feature-correlation', 'figure'),
    [Input('x-feature', 'value'),
     Input('y-feature', 'value'),
     Input('genre-filter', 'value')]
)
def update_feature_correlation(x_feature, y_feature, selected_genres):
    if not selected_genres or 'All' in selected_genres:
        filtered_df = df
    else:
        filtered_df = df[df['Top Genre'].isin(selected_genres)]
    
    fig = px.scatter(filtered_df, 
                    x=x_feature, 
                    y=y_feature,
                    color='Top Genre',
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hover_data=['Title', 'Artist', 'Top Genre'],
                    title=f'How {x_feature} Relates to {y_feature}')
    
    # Update hover template
    fig.update_traces(
        marker=dict(
            size=6,
            opacity=0.7
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>" +
            "Artist: %{customdata[1]}<br>" +
            "Genre: %{customdata[2]}<br>" +
            "<br>" +
            "<b>Values:</b><br>" +
            "%{x}<br>" +
            "%{y}<br>" +
            "<extra></extra>"
        )
    )
    
    # Add descriptive labels for loudness values
    if x_feature == 'Loudness (dB)':
        ticktext = [
            '-25 (Very Quiet)',
            '-20 (Quiet)',
            '-15 (Moderate)',
            '-10 (Loud)',
            '-5 (Very Loud)',
            '0 (Maximum)'
        ]
        tickvals = [-25, -20, -15, -10, -5, 0]
        
        fig.update_layout(
            xaxis=dict(
                ticktext=ticktext,
                tickvals=tickvals,
                tickmode='array'
            )
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
            title=dict(
                text=x_feature,
                font=dict(size=14)
            )
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=False,
            title=dict(
                text=y_feature,
                font=dict(size=14)
            )
        ),
        legend=dict(
            title_text='Genre',
            itemsizing='constant',
            font=dict(size=12),
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02
        ),
        margin=dict(
            l=80,
            r=200,
            t=100,
            b=80
        ),
        hoverlabel=dict(
            bgcolor='rgba(0,0,0,0.8)',
            font=dict(color='white')
        )
    )
    return fig

# Callback for top artists
@callback(
    Output('top-artists', 'figure'),
    Input('genre-filter', 'value')
)
def update_top_artists(selected_genres):
    if not selected_genres or 'All' in selected_genres:
        filtered_df = df
    else:
        filtered_df = df[df['Top Genre'].isin(selected_genres)]
    
    top_artists = filtered_df['Artist'].value_counts().head(15)
    
    fig = go.Figure(data=[
        go.Bar(
            x=top_artists.index,
            y=top_artists.values,
            marker_color=SPOTIFY_GREEN,
            hovertemplate="Artist: %{x}<br>Number of Songs: %{y}<extra></extra>"
        )
    ])
    
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

# Callback for popularity trend
@callback(
    Output('popularity-trend', 'figure'),
    Input('genre-filter', 'value')
)
def update_popularity_trend(selected_genres):
    if not selected_genres or 'All' in selected_genres:
        filtered_df = df
    else:
        filtered_df = df[df['Top Genre'].isin(selected_genres)]
    
    fig = go.Figure()
    
    # Add scatter plot
    fig.add_trace(go.Scatter(
        x=filtered_df['Year'],
        y=filtered_df['Popularity'],
        mode='markers',
        name='Individual Songs',
        marker=dict(
            color=filtered_df['Top Genre'].astype('category').cat.codes,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title='Genres',
                titleside='right',
                titlefont=dict(color=TEXT_COLOR),
                tickfont=dict(color=TEXT_COLOR)
            ),
            size=8,
            opacity=0.7
        ),
        text=filtered_df.apply(
            lambda x: f"'{x['Title']}' by {x['Artist']}<br>"
                     f"Released in {x['Year']}<br>"
                     f"Genre: {x['Top Genre']}<br>"
                     f"Popularity Score: {x['Popularity']}/100",
            axis=1
        ),
        hovertemplate="%{text}<extra></extra>"
    ))
    
    # Calculate and add mean popularity line
    yearly_mean = filtered_df.groupby('Year')['Popularity'].mean().reset_index()
    fig.add_trace(go.Scatter(
        x=yearly_mean['Year'],
        y=yearly_mean['Popularity'],
        mode='lines',
        name='Average Popularity',
        line=dict(color=SPOTIFY_GREEN, width=3),
        hovertemplate="Year: %{x}<br>" +
                     "Average Popularity: %{y:.1f}/100<br>" +
                     "<extra></extra>"
    ))
    
    # Add reference areas for popularity ranges
    popularity_ranges = [
        (80, 100, "Massive Hits"),
        (60, 80, "Very Popular"),
        (40, 60, "Well Known"),
        (20, 40, "Moderately Known"),
        (0, 20, "Less Known")
    ]
    
    for start, end, label in popularity_ranges:
        fig.add_hrect(
            y0=start,
            y1=end,
            fillcolor="rgba(255,255,255,0.1)",
            layer="below",
            line_width=0,
            annotation_text=label,
            annotation_position="right",
            annotation=dict(
                font_size=10,
                font_color="rgba(255,255,255,0.5)"
            )
        )
    
    fig.update_layout(
        title=dict(
            text='Song Popularity Over Time',
            font=dict(size=24, color=TEXT_COLOR)
        ),
        xaxis_title=dict(
            text='Release Year',
            font=dict(size=16, color=TEXT_COLOR)
        ),
        yaxis_title=dict(
            text='Popularity Score (0-100)',
            font=dict(size=16, color=TEXT_COLOR)
        ),
        hovermode='closest',
        showlegend=True,
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PAPER_BGCOLOR,
        font=dict(color=TEXT_COLOR),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            title_standoff=20
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            title_standoff=20,
            range=[0, 100]  # Fix y-axis range
        ),
        legend=dict(
            font=dict(color=TEXT_COLOR),
            bgcolor='rgba(0,0,0,0)',
            x=1.02,
            y=0.98
        )
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

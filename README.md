# Spotify 2000 Songs Analysis Dashboard

An interactive data visualization dashboard analyzing Spotify's top 2000 songs, built with Plotly Dash. The project combines machine learning (K-means clustering) with audio preview functionality to create an engaging exploration of music trends, genres, and song characteristics.

## Project Overview

This project evolved through several key development stages:

1. **Data Analysis & Cleaning**: Initial exploration of the Spotify dataset to understand patterns and relationships between song features.
2. **Machine Learning Integration**: Implementation of K-means clustering to group songs into meaningful categories.
3. **Audio Integration**: Addition of song preview functionality using the Deezer API.
4. **Dashboard Development**: Creation of an interactive web interface combining all components.

## Repository Structure

```
June_Code_Pudding/
├── src/                  # Source code directory
│   ├── app.py           # Main dashboard application
│   └── audio_preview.py # Audio preview functionality
│
├── data/                # Data directory
│   └── Spotify-2000.csv # Main dataset
│
├── notebooks/           # Analysis notebooks
│   ├── eli_analysis_viktor.ipynb  # Advanced feature analysis
│   ├── Gio_Audio_Previews.ipynb   # Audio preview development
│   └── sohini_kmeans.ipynb        # Clustering implementation
│
├── deploy/              # Deployment configuration
│   ├── Procfile        # Process file for web servers
│   └── render.yaml     # Render platform configuration
│
└── requirements.txt     # Project dependencies
```

### Core Components

  - **`app.py`**: Main dashboard application that integrates all components:
    - Interactive visualizations
    - Audio preview integration
    - Cluster-based recommendations
    - Real-time data filtering

  - **`audio_preview.py`**: Handles audio functionality:
    - Deezer API integration
    - Preview file management
    - Caching system
    - Error handling

### Development and Analysis

- **Notebooks**: Jupyter notebooks showing the development process:
  - Feature analysis and correlation studies
  - K-means clustering implementation
  - Audio preview system prototyping

- **Data**: Contains the Spotify dataset with:
  - Song metadata
  - Audio features
  - Popularity metrics
  - Genre classifications

### Deployment

- **Configuration Files**: Located in `deploy/`:
  - Render platform settings
  - Process management
  - Environment configuration

## Features

### 1. Music Style Discovery
- Interactive cluster-based song recommendations
- Radar charts showing cluster characteristics
- Audio previews for immediate listening

### 2. Genre Analysis
- Dynamic pie chart of genre distribution
- Historical timeline of music releases
- Adjustable genre display (10 to 149 genres)

### 3. Song Characteristics Explorer
- Interactive feature correlation plots
- Top artists visualization
- Popularity trends across time
- Multi-genre filtering capabilities

### 4. Data Insights
- Comprehensive song metadata
- Audio feature analysis
- Popularity scoring system

## Data Analysis Process

### Initial Exploration
![Feature Relationships](images/featurexpopularity.png)
*Analysis of relationships between song features and popularity*

### Feature Correlation
![Correlation Heatmap](images/heatmap.png)
*Heatmap showing relationships between different song characteristics*

### Clustering Analysis
![K-means Clustering](images/kmeans.png)
*K-means clustering results showing distinct song groups*

## Setup Instructions

### For Notebook Development

If you want to work with the Jupyter notebooks for data analysis and development:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/betanight/June_Code_Pudding.git
   cd June_Code_Pudding
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch Jupyter Notebook**
   ```bash
   jupyter notebook
   ```

### For Running the Dashboard Application

If you want to run the dashboard application:

1. **Clone the Repository** (if you haven't already)
   ```bash
   git clone https://github.com/betanight/June_Code_Pudding.git
   cd June_Code_Pudding
   ```

2. **If you were in a virtual environment, deactivate it**
   ```bash
   # macOS/Linux/Windows
   deactivate
   ```

3. **Install Dependencies Globally**
   ```bash
   # macOS/Linux
   pip3 install -r requirements.txt

   # Windows
   pip install -r requirements.txt
   ```

4. **Run the Dashboard**
   ```bash
   # macOS/Linux
   python3 src/app.py

   # Windows
   python src/app.py
   ```

5. **Access the Application**
   - Open your browser
   - Visit `http://localhost:8050`
   - Start exploring the data!

Note: The application is designed to run without a virtual environment to ensure proper system-wide access to audio functionality and dependencies.

## Technical Implementation

### Dashboard Components
- **Plotly Dash**: Core framework for interactive visualizations
- **Deezer API**: Integration for audio preview functionality
- **Scikit-learn**: K-means clustering implementation
- **Pandas & NumPy**: Data processing and analysis

### Song Features Analyzed
- **Audio Characteristics**: BPM, Energy, Danceability, Loudness, Valence
- **Metadata**: Artist, Genre, Year, Popularity
- **Derived Features**: Cluster assignments, Genre groupings

### Popularity Scoring (0-100)
- **80-100**: Massive hits everyone knows
- **60-79**: Very popular songs
- **40-59**: Well-known songs
- **20-39**: Moderately known songs
- **0-19**: Less known songs

## Deployment

The dashboard is deployed on Render and automatically updates with new commits to the main branch. Visit the live version at [Spotify Analysis Dashboard](https://june-code-pudding-9.onrender.com).

(*May be slow due to using the free version*)

## Future Enhancements
- Real-time Spotify API integration
- Additional clustering algorithms
- Extended audio preview capabilities
- User preference learning

## Acknowledgments

- Spotify Dataset from Kaggle
- Deezer API for audio previews
- Plotly Dash community for visualization components

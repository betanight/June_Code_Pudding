# Spotify Songs Analysis Dashboard

This project analyzes Spotify song data and presents insights through an interactive Plotly Dash dashboard. The analysis is first conducted in a Jupyter notebook to explore the data and determine the most insightful visualizations.

![Genre Distribution Preview](images/pie_chart.png)

## Project Structure

- `notebooks/`: Directory containing all analysis notebooks
  - `eli_analysis.ipynb`: Initial exploratory data analysis that helped define project goals and identify key insights about song feature relationships
  - `eli_analysis_viktor.ipynb`: Advanced analysis building upon initial findings with deeper feature exploration
  - `sohini_kmeans.ipynb`: Implementation of K-means clustering to generate new features for enhancing dashboard recommendations

- `requirements.txt`: Python dependencies required for the project

- `data/`: Includes the dataset from Kaggle

## Dashboard Features

- **Genre Distribution Visualization**
  - Interactive pie chart showing genre breakdown
  - Adjustable view from top 10 to all 149 genres
  - Clear color coding and hover information

- **Popularity Trends Analysis**
  - Track song popularity across different years
  - Visual popularity ranges (Massive Hits to Less Known)
  - Genre filtering capabilities
  - Trend line showing average popularity

- **Feature Correlation Explorer**
  - Compare different song characteristics
  - Interactive scatter plots
  - Detailed hover information for each song

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/betanight/June_Code_Pudding.git
   cd June_Code_Pudding
   ```

2. **Create and Activate Virtual Environment (Optional but Recommended for notebook)**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Dashboard**
   ```bash
   python app.py
   ```

5. **Access the Dashboard**
   - Open your web browser
   - Navigate to `http://127.0.0.1:8050`
   - Start exploring the data!

## Data Features Explained

### Track Information
- **Title**: Name of the Track
- **Artist**: Name of the Artist
- **Top Genre**: Genre of the track
- **Year**: Release Year of the track
- **Length**: The duration of the song

### Audio Features
- **Beats per Minute (BPM)**: The tempo of the song
- **Energy**: The higher the value, the more energetic the song
- **Danceability**: The higher the value, the easier it is to dance to this song
- **Loudness (dB)**: The higher the value, the louder the song
- **Valence**: The higher the value, the more positive mood for the song
- **Acoustic**: The higher the value, the more acoustic the song is
- **Speechiness**: The higher the value, the more spoken words the song contains

### Popularity Score (0-100)
- 80-100: Massive hits everyone knows
- 60-79: Very popular songs
- 40-59: Well-known songs
- 20-39: Moderately known songs
- 0-19: Less known songs

## Analysis Examples

### Relationship between Features and Popularity:

![Features Relationship with Popularity](images/featurexpopularity.png)

### Heatmap of Feature Correlation:

![Heatmap](images/heatmap.png)

## Tech Stack

- Dash
- Plotly
- Pandas
- NumPy
- Scikit-learn
- Seaborn

## Next Steps
1. Explore and clean the Spotify dataset
2. Create various visualizations to understand the data
3. Select the most insightful visualizations for the dashboard
4. Implement the Plotly Dash dashboard

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements or find any bugs.

import pandas as pd
import numpy as np
import librosa
import requests
import os
import deezer

def audio_previews(current_songs_df):
    """
    Get audio previews for currently displayed songs.
    
    Args:
        current_songs_df: DataFrame with 'Title' and 'Artist' columns
    
    Returns:
        dict: Song titles mapped to their preview file paths
    """
    client = deezer.Client()
    download_dir = "audio_previews"
    os.makedirs(download_dir, exist_ok=True)
    preview_paths = {}

    for _, row in current_songs_df.iterrows():
        title = row['Title']
        artist = row['Artist']
        search_query = f"{title} {artist}"
        
        search_results = client.search(search_query)
        
        if search_results:
            track = search_results[0]
            preview_url = track.preview
            
            if preview_url:
                filename = f"{title}_{artist}.mp3".replace(" ", "_")
                filepath = os.path.join(download_dir, filename)

                try:
                    if not os.path.exists(filepath):
                        response = requests.get(preview_url, stream=True)
                        response.raise_for_status()

                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        print(f"Downloaded preview for '{title}' successfully!")
                    
                    preview_paths[title] = filepath
                
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading preview for '{title}': {e}")
                except Exception as e:
                    print(f"An unexpected error occurred for '{title}': {e}")
            else:
                print(f"No preview URL available for {title}")
        else:
            print(f"No preview found for {title}")

    return preview_paths
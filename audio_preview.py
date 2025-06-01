# define function for audio previews
def audio_previews(df):
    import requests
    import os
    import deezer

    top_popular = df.nlargest(10, 'Popularity')[['Title', 'Artist', 'Popularity']]
    top_songs = top_popular['Title'].tolist()

    # Initialize Deezer client
    client = deezer.Client() #


    # Create an empty list to store track data
    track_data = []

    # Search for each song and get its preview URL
    for title in top_songs:
        search_results = client.search(title) #
    
        # Check if any tracks were found
        if search_results:
            # Get the first track from the search results
            track = search_results[0] 
        
            # Append track title and preview URL to the list
            track_data.append({"Title": track.title, "Preview URL": track.preview}) #

    # Create a Pandas DataFrame from the track data
    # global data
    data = pd.DataFrame(track_data)

    # Print the DataFrame
    # df


    # Create a directory to save the downloaded files
    download_dir = "audio_previews"
    os.makedirs(download_dir, exist_ok=True) # Create the directory if it doesn't exist

    # Loop through each row of the DataFrame and download the audio
    for index, row in data.iterrows():
        track_title = row['Title']
        preview_url = row['Preview URL']

        # Create a basic filename from the track title (you might want to sanitize this further)
        filename = f"{track_title}.mp3"  # Adjust file extension if needed
        filepath = os.path.join(download_dir, filename)

        try:
            # Download the audio file
            response = requests.get(preview_url, stream=True)
            response.raise_for_status()  # Check for bad status codes

            # Save the audio content to the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded '{filename}' successfully!")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading '{filename}' from {preview_url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred for '{filename}': {e}")


            pass
    random_idx = np.random.randint(0, data.shape[0])

    # select a random song from the dataset
    song = data.loc[random_idx, :]

    # load the file and print its sampling rate 
    file_path = f"audio_previews/"
    file_path = file_path  + song["Title"] + '.mp3'
    audio, sample_rate = librosa.load(file_path)
    # print info about this song
    print(' ')
    print(f"Sampling rate: {sample_rate}")
    print(song)

    # output the audio
    display(ipd.Audio(file_path))
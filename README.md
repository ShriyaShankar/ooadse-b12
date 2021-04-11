## YouTube Player

### The project contains 3 features - Video Manager, Playlist Manager and the Recommender

- Run `python3 videos.py` to open Video Manager. It contains: index.html, upload.html, delete_video.html, uploaded_video.html
- Run `python3 playlists.py` to open Playlist Manager. It contains: manage_playlist.html, create_playlist.html, delete_playlist.html, display_playlists.html, your_playlist.html
- Run ```python3 recommendation_system.py <dataset name> <video title>``` to execute the recommendation system. The recommender calculates similarity and relevance based on multiple factors: 
  - Title of video - done using cosine similarity and TfIdf vectorization
  - Views
  - Likes
  - Dislikes (negative influence)


### Note:
1. Ensure you have installed the requirements by running `pip3 install -r requirements.txt`
2. Ensure you have created the required database and tables in MySQL (you may check out database.txt)

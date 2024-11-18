import pickle
import streamlit as st
import requests

# Set Streamlit to wide mode
st.set_page_config(layout="wide")

# Custom CSS for card flip and styling
st.markdown("""
    <style>
    /* Main app background and header styling */
    .stApp {
        background: linear-gradient(145deg, #141414, #1c1c1c);
        color: #FFFFFF;
    }
    h1, h2, h3 {
        color: #E50914;
        font-family: 'Helvetica', sans-serif;
        font-weight: bold;
    }
    
    /* Dropdown menu styling */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #333;
        color: #FFFFFF;
    }

    /* Movie card layout */
    .movie-card-container {
        perspective: 1000px;
        display: inline-block;
        margin: 20px;  /* Increase margin for spacing */
    }
    .movie-card {
        width: 250px;  /* Increase width */
        height: 450px; /* Increase height to accommodate larger text */
        position: relative;
        transition: transform 0.6s;
        transform-style: preserve-3d;
        cursor: pointer;
        border-radius: 12px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.4);
    }
    .movie-card:hover {
        transform: scale(1.1) rotateY(180deg);  /* Slightly larger scale */
        box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.8);
    }
    
    /* Card front and back styling */
    .movie-card-front, .movie-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        border-radius: 12px;
        padding: 20px;  /* Padding inside the card */
    }
    .movie-card-front {
        background-color: #333;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;
        padding: 25px;  /* More padding */
    }
    .movie-card-back {
        background-color: rgba(0, 0, 0, 0.85);  /* Semi-transparent black for better contrast */
        color: #E5E5E5;
        transform: rotateY(180deg);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        padding: 15px;  /* Padding on the back */
        overflow-y: hidden;
        position: relative;
    }
    .movie-poster {
        width: 100%;
        height: 100%;
        object-fit: cover;  /* Ensures image fully covers the card */
        border-radius: 12px;
    }
    .movie-title {
        font-size: 18px;  /* Larger font size for the title */
        color: #E5E5E5;
        font-weight: bold;
        margin-top: 8px;
        text-align: center;
    }
    .movie-info {
        font-size: 14px;  /* Slightly larger font size */
        text-align: center;
        color: #CCCCCC;
        margin-top: 5px;
    }
    /* Description styling on the back */
    .movie-description {
        font-size: 14px;
        color: #E5E5E5;
        text-align: justify;  /* Justified alignment for better readability */
        margin-top: 10px;
        line-height: 1.4;
        word-wrap: break-word;  /* Allow long words to break and wrap onto new lines */
        max-height: 140px;  /* Control max height of description */
        overflow: hidden;
        position: relative;
        padding-right: 20px;
        padding-left: 20px;
        display: -webkit-box;
        -webkit-line-clamp: 5;  /* Limit to 5 lines */
        -webkit-box-orient: vertical;
    }
    .movie-description::after {
        content: "";  /* Add ellipsis to indicate more content */
        position: absolute;
        bottom: 5px;
        right: 5px;
        font-size: 14px;
        color: #E5E5E5;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to fetch movie details
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', None)
    full_poster_path = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750"
    
    # Extract details for the flip card back content
    release_date = data.get('release_date', 'N/A')
    rating = data.get('vote_average', 'N/A')
    overview = data.get('overview', 'No description available.')
    
    return {
        "poster_path": full_poster_path,
        "release_date": release_date,
        "rating": rating,
        "overview": overview
    }

# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_details = []
    
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        movie_details = fetch_movie_details(movie_id)
        movie_title = movies.iloc[i[0]].title  # Get the recommended movie title
        recommended_movie_details.append({"movie_title": movie_title, **movie_details})
    
    return recommended_movie_details

# App header
st.header("🎬 Free Guys' Movie Recommender System")

# Load movie data
movies = pickle.load(open('model/movie_list.pkl','rb'))
similarity = pickle.load(open('model/movie_similarity.pkl','rb'))

# Movie dropdown
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Select a movie you like",
    movie_list
)

# Show recommendations
if st.button('Show Recommendation'):
    recommended_movie_details = recommend(selected_movie)
    
    # Display recommendations in a flip-card layout
    st.subheader("Recommended for You")
    cols = st.columns(5)
    
    for i, col in enumerate(cols):
        movie = recommended_movie_details[i]
        with col:
            st.markdown(f"""
                <div class="movie-card-container">
                    <div class="movie-card">
                        <div class="movie-card-front">
                            <p class="movie-title">{movie['movie_title']}</p>  <!-- Movie title on the front -->
                            <img src="{movie['poster_path']}" class="movie-poster">
                        </div>
                        <div class="movie-card-back">
                            <p class="movie-title">{movie['movie_title']}</p>
                            <p class="movie-info"><b>Release:</b> {movie['release_date']}</p>
                            <p class="movie-info"><b>Rating:</b> {movie['rating']}</p>
                            <p class="movie-description">{movie['overview']}</p>  <!-- Updated description style -->
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

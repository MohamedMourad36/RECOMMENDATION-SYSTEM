import pandas as pd
from scipy.spatial.distance import cosine
import tkinter as tk
from tkinter import ttk, messagebox


# Sample Data (Modify as needed)
users_df = pd.DataFrame({
    "user_id": [1, 2, 3, 4],
    "name": ["Alice", "Bob", "Charlie", "Diana"]
})

movies_df = pd.DataFrame({
    "movie_id": [100, 101, 102, 103],
    "title": ["Comedy A", "Action B", "Thriller C", "Drama D"],
    "genre": ["Comedy", "Action", "Thriller", "Drama"]
})

ratings_df = pd.DataFrame({
    "user_id": [1, 1, 2, 3, 4],
    "movie_id": [100, 102, 100, 101, 103],
    "rating": [4, 5, 3, 4, 5]
})


def cosine_similarity(user1, user2, ratings_df):
    """
    Calculates cosine similarity between two users based on ratings.
    """
    # Get the movies both users have rated
    common_movies = ratings_df[ratings_df['user_id'] == user1].merge(
        ratings_df[ratings_df['user_id'] == user2], on='movie_id', how='inner')

    # Check if either user has no ratings
    if common_movies.empty:
        return 0

    # Calculate the cosine similarity
    return 1 - cosine(common_movies['rating_x'], common_movies['rating_y'])


def predict_rating(user_id, movie_id, ratings_df, k=3):
    """
    Predicts a user's rating for a movie using collaborative filtering.
    """
    # Get all users who have rated the movie
    users_who_rated = ratings_df[ratings_df['movie_id'] == movie_id]['user_id'].unique()

    # Calculate similarity with the active user
    similarities = {user: cosine_similarity(user_id, user, ratings_df) for user in users_who_rated if user != user_id}

    # Sort users by similarity
    sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)

    # Get top k similar users
    top_users = sorted_similarities[:k]

    # Handle no similar users
    if not top_users:
        return ratings_df['rating'].mean()  # Return average rating as default

    # Calculate the weighted average rating
    weighted_ratings = sum(ratings_df[(ratings_df['user_id'] == user) & (ratings_df['movie_id'] == movie_id)]['rating'].values[0] * similarity for user, similarity in top_users)
    sum_of_weights = sum(similarity for user, similarity in top_users)

    return weighted_ratings / sum_of_weights if sum_of_weights > 0 else ratings_df['rating'].mean()


def recommend_movies(user_id, ratings_df, movies_df, k=5):
    """
    Recommends movies for a user based on predicted ratings (Collaborative Filtering).
    """
    # Find movies that the user hasn't rated yet
    rated_movies = ratings_df[ratings_df['user_id'] == user_id]['movie_id'].unique()
    unrated_movies = movies_df[~movies_df['movie_id'].isin(rated_movies)]

    # Predict ratings for unrated movies
    predictions = {movie_id: predict_rating(user_id, movie_id, ratings_df) for movie_id in unrated_movies['movie_id']}

    # Filter out None values from predictions
    predictions = {key: value for key, value in predictions.items() if value is not None}

    # Sort movies by predicted rating
    sorted_predictions = sorted(predictions.items(), key=lambda item: item[1], reverse=True)

    # Get top k recommendations
    top_recommendations = sorted_predictions[:k]

    # Return the movie titles and predicted ratings
    return [(movies_df[movies_df['movie_id'] == movie_id]['title'].values[0], rating) for movie_id, rating in top_recommendations]


# GUI implementation using Tkinter
def get_recommendations():
    selected_user = user_combobox.get()
    if not selected_user:
        messagebox.showerror("Error", "Please select a user")
        return
    
    user_id = users_df[users_df['name'] == selected_user]['user_id'].values[0]
    recommendations = recommend_movies(user_id, ratings_df, movies_df, k=5)
    
    recommendations_text = "\n".join([f"{title}: {rating:.2f}" for title, rating in recommendations])
    recommendations_label.config(text=recommendations_text)


root = tk.Tk()
root.title("Movie Recommendation System")

tk.Label(root, text="Select User:").grid(row=0, column=0, padx=10, pady=10)
user_combobox = ttk.Combobox(root, values=users_df['name'].tolist())
user_combobox.grid(row=0, column=1, padx=10, pady=10)

recommend_button = tk.Button(root, text="Get Recommendations", command=get_recommendations)
recommend_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

recommendations_label = tk.Label(root, text="", justify=tk.LEFT)
recommendations_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()

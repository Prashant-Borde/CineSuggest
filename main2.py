from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from models import *
from flask_caching import Cache
import requests
from bs4 import BeautifulSoup


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key



# Configure caching
app.config['CACHE_TYPE'] = 'simple'  # Simple in-memory cache
app.config['CACHE_DEFAULT_TIMEOUT'] = 3000  # Default cache timeout (in seconds)
cache = Cache(app)




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_email = cache.get('user_email')
        if not user_email:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function





def create_sim():
    # Fetch all movies from the database
    movies = db_session.query(Movie).all()
    data = pd.DataFrame([{
        'movie_title': movie.movie_title,
        'comb': movie.comb
    } for movie in movies])
    # Creating a count matrix
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    # Creating a similarity score matrix
    sim = cosine_similarity(count_matrix)
    return data, sim

def rcmd(m):
    m = m.lower()
    data, sim = create_sim()
    if m not in data['movie_title'].str.lower().values:
        return 'This movie is not in our database.\nPlease check if you spelled it correctly.'
    else:
        i = data.loc[data['movie_title'].str.lower() == m].index[0]
        lst = list(enumerate(sim[i]))
        lst = sorted(lst, key=lambda x: x[1], reverse=True)
        lst = lst[1:11]
        # return [data['movie_title'].iloc[i] for i, _ in lst]
        # making an empty list that will containg all 10 movie recommendations
        l = []
        for i in range(len(lst)):
            a = lst[i][0]
            l.append(data['movie_title'][a])
        return l


@app.route("/")
@login_required
def home():
    return render_template('home.html')

@app.route("/recommend")
def recommend():
    movie = request.args.get('movie')
    r = rcmd(movie)
    movie = movie.upper()
    if type(r)==type('string'):
        return render_template('recommend.html',movie=movie,r=r,t='s')
    else:
        return render_template('recommend.html',movie=movie,r=r,t='l')

# @app.route("/recommend")
# @login_required
# def recommend():
#     movie = request.args.get('movie')
#     recommendations = rcmd(movie)
#     movie = movie.upper()
#     if isinstance(recommendations, str):
#         return render_template('recommend.html', movie=movie, recommendations=recommendations, t='s')
#     else:
#         return render_template('recommend.html', movie=movie, recommendations=recommendations, t='l')


# @app.route("/recommend")
# @login_required
# def recommend():
#     movie = request.args.get('movie')
#     recommendations = rcmd(movie)
#     movie = movie.upper()
#     if isinstance(recommendations, str):
#         return render_template('recommend.html', movie=movie, recommendations=recommendations, t='s')
#     else:
#         return render_template('recommend.html', movie=movie, recommendations=recommendations, t='l')

@app.route("/movies", methods=['GET'])
@login_required
def get_movies():
    try:
        movies = db_session.query(Movie).all()
        movie_titles = [movie.movie_title for movie in movies]
        return jsonify(movie_titles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=['GET', 'POST'])
def login():
    if cache.get('user_email') and request.method == "GET":
        return redirect('/')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        user = db_session.query(User).filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            # Store the email in the cache
            cache.set('user_email', email)
            # Create a response and set a cookie for authentication
            resp = redirect(url_for('home'))
            resp.set_cookie('user_email', email)
            return resp
        else:
            return jsonify({"message": "Invalid email or password"}), 401

    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if cache.get('user_email') and request.method == "GET":
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            return jsonify({"message": "All fields are required"}), 400
        
        if password != confirm_password:
            return jsonify({"message": "Passwords do not match"}), 400
        
        if db_session.query(User).filter_by(email=email).first():
            return jsonify({"message": "Email already registered"}), 400
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db_session.add(new_user)
        db_session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

# @app.route("/logout")
# @login_required
# def logout():
#     cache.delete('user_email')
#     return redirect(url_for('login'))

@app.route("/logout", methods=['POST'])
@login_required
def logout():
    cache.delete('user_email')
    return redirect(url_for('login'))




# @app.route("/movie/<movie_title>")
# @login_required
# def movie_details(movie_title):
#     # Search YouTube for the movie trailer
#     query = f"{movie_title} trailer"
#     url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Extract video titles and links
#     videos = []
#     for video in soup.find_all('a', href=True):
#         if '/watch' in video['href']:
#             title = video.get('title')  # Ensure the title is not None
#             if title and len(videos) < 10:  # Limit to top 10 results
#                 videos.append({
#                     'title': title,
#                     'url': f"https://www.youtube.com{video['href']}"
#                 })

#     return render_template('movie_details.html', movie_title=movie_title, videos=videos)



if __name__ == '__main__':
    app.run(debug=True)

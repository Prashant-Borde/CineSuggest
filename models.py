from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

# Define the SQLite database URL
DATABASE_URL = "sqlite:///movies.db"

# Create an engine
engine = create_engine(DATABASE_URL)

# Define the base class for declarative models
Base = declarative_base()

# Define the Movie table
class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    actor_1_name = Column(String)
    actor_2_name = Column(String)
    actor_3_name = Column(String)
    director_name = Column(String)
    genres = Column(String)
    movie_title = Column(String)
    comb = Column(String)

# Define the User table
class User(Base):
    __tablename__ = 'users'
    
    username = Column(String)
    email = Column(String, primary_key=True)
    password_hash = Column(String)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
db_session = Session()

# Insert data into the Movie table
# new_movie = Movie(
#     actor_1_name="CCH Pounder",
#     actor_2_name="Joel David Moore",
#     actor_3_name="Wes Studi",
#     director_name="James Cameron",
#     genres="Action|Adventure|Fantasy|Sci-Fi",
#     movie_title="avatar",
#     comb="CCH Pounder Joel David Moore Wes Studi James Cameron Action|Adventure|Fantasy|Sci-Fi"
# )

# session.add(new_movie)

# Insert a new user into the User table
# new_user = User(username="prashant@gmail.com")
# new_user.set_password("123")  # Set password for the user

# session.add(new_user)
# session.commit()

# # Commit the session to save the data
# try:
#     session.commit()
#     print("Data inserted successfully.")
# except IntegrityError:
#     session.rollback()
#     print("An error occurred, data might already exist.")

# # Close the session
# session.close()

# # Load CSV data
# import pandas as pd
# csv_file = 'data.csv'  # Path to your CSV file
# data = pd.read_csv(csv_file)

# # Ensure that the columns match the database table columns
# data = data.rename(columns={
#     'actor_1_name': 'actor_1_name',
#     'actor_2_name': 'actor_2_name',
#     'actor_3_name': 'actor_3_name',
#     'director_name': 'director_name',
#     'genres': 'genres',
#     'movie_title': 'movie_title',
#     'comb': 'comb'
# })

# # Insert data into the Movie table
# for index, row in data.iterrows():
#     movie = Movie(
#         actor_1_name=row['actor_1_name'],
#         actor_2_name=row['actor_2_name'],
#         actor_3_name=row['actor_3_name'],
#         director_name=row['director_name'],
#         genres=row['genres'],
#         movie_title=row['movie_title'],
#         comb=row['comb']
#     )
#     session.add(movie)

# # Commit the session to save the data
# session.commit()

# print("Data successfully migrated from CSV to SQLite.")

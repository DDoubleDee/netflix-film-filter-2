import pandas as pd
import sqlalchemy as db
from flask_login import UserMixin


class FileScripts:
    def read_from_csv(self, file_name):
        self.file_data = pd.read_csv(file_name)  # Reads csv file
        self.file_data.index.name = 'id'  # Renames 'index' to 'id' for my convenience
        self.file_data['title'] = self.file_data['title'].astype('string')  # Converts netflix title to string
        self.file_data['show_id'] = self.file_data['show_id'].astype('string')  # Converts netflix show id to string

    def separate_by_rating(self):
        self.ratings = self.file_data['rating'].unique()  # This value contains a list of all ratings
        self.data_by_rating = []  # This list will contain all dataframes separated in the same order as in 'ratings'
        for rating in self.ratings:  # This goes through 'ratings' and appends dataframes returned by .loc[]
            self.data_by_rating.append(self.file_data.loc[self.file_data['rating'] == rating])


class DataBaseScripts:
    # Creates an engine, connects to the database and grabs metadata, also creates users table if it doesn't exist
    def __init__(self, conn_info):
        self.engine = db.create_engine(conn_info)
        self.metadata = db.MetaData()
        self.connection = self.engine.connect()
        self.users = db.Table(
            'users', self.metadata,
            db.Column('id', db.Integer, primary_key=True),
            db.Column('email', db.String, unique=True),
            db.Column('password', db.String),
            db.Column('nickname', db.String)
        )
        self.users.create(self.engine, checkfirst=True)
        self.userq = db.select(self.users)  # Default user query for shorter code

    def write_to_sql(self, file_data):
        file_data.to_sql('netflixlist', con=self.engine, if_exists='replace')  # Sends data to database

    def get_user(self, email='', index=''):
        if email != '':
            user = self.connection.execute(self.userq.where(self.users.columns.email == email)).fetchone()
        else:
            user = self.connection.execute(self.userq.where(self.users.columns.id == index)).fetchone()
        return user

    def create_user(self, nickname, email, password):
        if self.connection.execute(self.userq.where(self.users.columns.nickname == nickname)).fetchone() \
            is not None or \
                self.connection.execute(self.userq.where(self.users.columns.email == email)).fetchone() is not None:
            return False
        else:
            self.connection.execute(db.insert(self.users).values(nickname=nickname, email=email, password=password))
            return True

    def get_data(self, show_type=''):
        table = db.Table('netflixlist', self.metadata, autoload=True, autoload_with=self.engine)  # Load table from db
        query = db.select(table)  # Set up default query
        if show_type != '':
            query = db.select(table).where(table.columns.type == show_type)
        return pd.read_sql_query(query, self.connection)


def sort_data_and_search(data, sorting_by='', reverse=False, search_in='title', search=''):
    if sorting_by != '':  # Check if sorting was enabled
        data = data.sort_values(by=[sorting_by], ascending=reverse)  # Use pandas .sort_values to sort by desired col
    if search != '':  # Check if search field is not empty
        data = data.loc[data[search_in].str.lower().str.contains(search.lower(), na=False)]
        # Use pandas .loc and .str.contains to find matching values
    return data


class User(UserMixin):
    def __init__(self, userid, scripts):
        self.user = scripts.get_user(index=userid)
        self.id = self.user[0]
        self.email = self.user[1]
        self.password = self.user[2]
        self.nickname = self.user[3]

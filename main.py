from dotenv import load_dotenv
from mainscript import FileScripts, DataBaseScripts, User, sort_data_and_search
from flask import Flask, render_template, redirect, url_for, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os

load_dotenv()  # load .env
file_script = FileScripts()  # initialize scripts for input file management
data_base = DataBaseScripts(os.getenv('CONNECTION_URL'))  # initialize database scripts
file_script.read_from_csv('netflix.csv')  # read input csv file
data_base.write_to_sql(file_script.file_data)  # write input dataframe to sql
mlist = sort_data_and_search(data_base.get_data(),  # get a default list from sql
                             sorting_by='',  # sort by column name, empty by default
                             search='',  # user search input, empty by default
                             reverse=False,  # reverse sort, if false sort is descending, if true sort is ascending
                             search_in='title')  # search in what column, title by default

app = Flask(__name__)  # initialize Flask class
login_manager = LoginManager()  # initialize login manager
login_manager.init_app(app)  # initialize login manager in flask app
app.secret_key = os.getenv('SECRET_KEY')  # get secret key from .env


@login_manager.user_loader
def load_user(userid):
    return User(userid, data_base)  # callback for reloading user


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        sorting_by = request.form.get('sortby')  # What column to sort by
        search_field = request.form.get('searchbar')  # User searchbar input
        reverse = True if request.form.get('reversesort') is 1 else False  # Reverse order of sort
        search_where = request.form.get('searchwhere')  # What column to search in
        filter_by_type = request.form.get('filterer')  # What type of show to show
        sort_data_and_search(data_base.get_data(show_type=filter_by_type),
                             sorting_by=sorting_by,
                             search=search_field,
                             reverse=reverse,
                             search_in=search_where)
        return render_template("home.html", mlist=mlist)
    else:
        return render_template("home.html", mlist=mlist)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        user = data_base.get_user(email=request.form.get('email'))  # get user data by email
        if user is not None:  # check if user exists
            if check_password_hash(user[2], password):  # check password hash with werkzeug
                user = User(user[0], data_base)  # initialize user class
                login_user(user)  # login user to login manager
                return redirect(request.args.get('next'))
            else:
                return abort(401)
    else:
        return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        password = generate_password_hash(request.form.get('password'))  # use werkzeug to generate hash
        if data_base.create_user(nickname, email, password) is True:  # create user if it doesn't exist
            return render_template("login.html")
        else:  # return back to register page if username or email already exists
            return render_template("register.html")
    else:
        return render_template("register.html")


@app.route("/contact")
@login_required
def contact():
    return render_template("contact.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


if __name__ == "__main__":
    app.run(debug=True)

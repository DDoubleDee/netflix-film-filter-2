from dotenv import load_dotenv
from mainscript import FileScripts, DataBaseScripts, sort_data_and_search
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager
import os


load_dotenv()
file_script = FileScripts()
data_base = DataBaseScripts(os.getenv('CONNECTION_URL'))
file_script.read_from_csv('netflix.csv')
data_base.write_to_sql(file_script.file_data)
mlist = sort_data_and_search(data_base.get_data(), sorting_by='release_year', search='', reverse=False, search_in='title')

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.getenv('SECRET_KEY')


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        sorting_by = request.form.get('sortby')  # What column to sort by
        search_field = request.form.get('searchfield')  # User searchbar input
        reverse = request.form.get('reversesort')  # Reverse order of sort
        search_where = request.form.get('searchwhere')  # What column to search in
        sort_data_and_search(data_base.get_data(), sorting_by=sorting_by, search=search_field, no_reverse=reverse, search_in=search_where)
        return render_template("home.html", mlist=mlist)
    else:
        return render_template("home.html", mlist=mlist)


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/logout")
def logout():
    return redirect(url_for('login'))


@app.route("/profile/login", methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@app.route("/profile/register", methods=['GET', 'POST'])
def register():
    return render_template("register.html")


@app.route("/contact")
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

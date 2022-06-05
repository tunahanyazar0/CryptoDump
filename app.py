import json
import smtplib
from functools import wraps
import urllib.parse
import plotly.express as px
from cs50 import SQL
import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import timedelta
import plotly.graph_objects as go
from fbprophet import Prophet
from fbprophet.plot import plot_plotly, plot_components_plotly
import warnings
from flask import Flask, redirect, render_template, session, request, send_file, make_response, url_for, Response
import requests 
from flask_session import Session
import plotly
import matplotlib.pyplot as plt
import os

def lookup(symbol):

    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None
def usd(value):
    return f"${value:,.2f}"

#news api
API_KEY = os.environ.get("NEWS_API")
app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

db = SQL("sqlite:///users.db")

@app.route("/", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    else:
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", message="must provide username")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("apology.html", message="must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ? and password= ?", request.form.get("username"), request.form.get("password"))
        if len(rows) != 1:
            return render_template("apology.html", message="invalid username and/or password")

        session["user_id"] = rows[0]["id"]
        #redirection
        return redirect("/prophecy")

@app.route("/prophecy", methods=["GET", "POST"])
@login_required
def prophecy():
    if request.method == "GET":
        return render_template("prophecy.html")
    else:
        symbol = request.form.get("symbol")
        symbol = symbol.upper()

        if symbol == None or symbol not in ["BTC", "ETH", "LINK", "XRP","SOL", "AVAX", "DOGE", "SHIB", "MANA"]:
            return render_template("apology.html", message="Your requested coin is not suitable !")

        else:    
            warnings.filterwarnings('ignore')
            pd.options.display.float_format = '${:,.2f}'.format

            today = datetime.today().strftime('%Y-%m-%d')
            start_date = '2014-09-17'

            df = yf.download(f'{symbol}-USD',start_date, today)

            df.reset_index(inplace=True)

            df = df[["Date", "Open"]]

            new_names = {
                        "Date": "ds",
                        "Open": "y",
                        }
            df.rename(columns=new_names, inplace=True)

            x = df["ds"]
            y = df["y"]

            m = Prophet(
                    seasonality_mode="multiplicative"
                )
            m.fit(df)

            future = m.make_future_dataframe(periods = 365)
            forecast = m.predict(future)
            forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            result = plot_plotly(m, forecast)


            graphJSON = json.dumps(result, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('result_prophecy.html', graphJSON=graphJSON, name=symbol)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        cash = int(request.form.get("cash"))

        rows = db.execute("SELECT * FROM users WHERE username = ?",username)
        if username == None or password == None or confirm == None:
            return render_template("apology.html", message="Username or password is not inputted!")
        elif password != confirm:
            return render_template("apology.html", message="Password and confirmation is not matching !")
        elif len(rows) != 0:
            return render_template("apology.html", message="This user is already exists !")
        elif cash <0:
            return render_template("apology.html", message="Your amount of cash is lower than 0!")
        else:

            db.execute("INSERT INTO users (username, password, cash) VALUES (?, ?, ?)",username, password, cash)

            rows = db.execute("SELECT * FROM users WHERE username = ?",username)
            session["user_id"] = rows[0]["id"]
            return redirect("/prophecy")

#TODO
@app.route("/news")
@login_required
def news():
    topics = ["TSLA","MSFT","AAPL","FB","Crypto","Stock","Elon Musk","ADA","Luna","USD","BTC","ETH","SOL"]
    today = datetime.today().strftime('%Y-%m-%d')

    titles = []
    descs = []

    responses = []

    for topic in topics:
        url = ('https://newsapi.org/v2/everything?'
            f'q={topic}&'
            f'from={today}&'
            'sortBy=popularity&'
            f'apiKey={API_KEY}')
        
        response = requests.get(url)
        response = response.json()

        responses.append(response)

    for i in range(len(topics)):
        for k in range(0,3):
            titles.append(responses[i]["articles"][k]["title"])
            descs.append(response["articles"][k]["description"])

    result = zip(titles, descs)

    return render_template("news_result.html", news=result, date=today)

        

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    userid = session["user_id"]
    if request.method == "GET":
        rows = db.execute("SELECT * FROM personal_shares WHERE person_id = ?", userid)
        return render_template("sell.html", rows = rows )

    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if shares.isnumeric() == False:
            return render_template("apology.html", message="You should have inputted proper share number")

        shares = int(shares)

        result = lookup(symbol)
        price = result["price"]

        rows = db.execute("SELECT * FROM personal_shares WHERE person_id = ?", userid)

        for row in rows:
            if row["name"] == result["name"]:
                if int(row["shares"]) >= shares:
                    new_share = int(row["shares"]) - shares
                    amount = shares * price

                    rows2 = db.execute("SELECT cash FROM users WHERE id = ?", userid)
                    new_cash = rows2[0]["cash"] + amount

                    db.execute("UPDATE personal_shares SET shares = ? WHERE person_id = ? and name = ?", new_share, userid, result["name"])
                    db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, userid)

                    return redirect("/portfolio")

                else:
                    return render_template("apology.html", message="You don't have that much of this !")
            else:
                return render_template("apology.html", message="An error occurred !")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "GET":
        return render_template("buy.html")
    # lookup return list of dictionaries or None

    else:
        symbol = request.form.get("symbol")
        share = request.form.get("shares")
        result = lookup(symbol)

        if  not symbol:
            return render_template("apology.html", message="You have not inputted symbol and/or share")
        elif result == None:
            return render_template("apology.html", message="You should have inputted proper symbol")
        elif (int(share) > 0) == False:
            return render_template("apology.html", message="You should have inputted a share greater than 0")
            
        else:
            userid = session["user_id"]
            rows1 = db.execute("SELECT cash FROM users WHERE id = ?",userid)
            expanditure = result["price"] * share

            if expanditure > int(rows1[0]["cash"]):
                return render_template("apology.html", message="You shouldn't have inputted a share greater than your amount of cash")
            else:
                result_cash = int(rows1[0]["cash"]) - expanditure
                db.execute("UPDATE users SET cash = ? WHERE id = ?", result_cash, userid)

                rows = db.execute("SELECT * FROM personal_shares WHERE name = ?", result["name"])

                if len(rows) > 0:
                    shares = int(rows[0]["shares"])
                    total = int(rows[0]["total"])
                    new_shares = shares + share
                    new_total = total + expanditure

                    db.execute("UPDATE personal_shares SET shares = ? , total = ? WHERE name = ?", new_shares , new_total, result["name"])

                else:
                    db.execute("INSERT INTO personal_shares VALUES (?, ?, ?, ?, ?, ?)", userid, symbol.upper(), result["name"], share, result["price"] , expanditure)

                return redirect("/portfolio")
    
@app.route("/portfolio")
@login_required
def portfolio():
    id = session["user_id"]
    rows = db.execute("SELECT * FROM personal_shares WHERE person_id = ?", id)
    rows2 = db.execute("SELECT cash FROM users WHERE id = ?", id)


    return render_template("portfolio.html", shares = rows, cash=usd(int(rows2[0]["cash"])))


@app.route("/market")
@login_required
def market():
    symbols = ["TSLA", "MSFT", "AXP", "MMM", "AAPL", "GOOGL", "AMZN", "FB", "TSM", "NVDA", "JNJ", "DXCM", "JPM", "PG",
    "AAP", "AFIB", "AFL", "AGRO", "AHPA", "ALF", "ALG", "AMD", "NIO", "NU", "DIDI", "ITUB", "AAL", "F", "AMC", "SWN", "AUY", "PBR",
    "T", "SOFI", "STNE", "INTC", "SNAP", "PLTR"]
    
    result = []

    for symbol in symbols: 
        res = yf.Ticker(symbol)
        data = res.history(period="1d")
    
        result.append(data)

    result2 = zip(symbols, result)

    return render_template("prices.html", stocks=result2)


@app.route("/mail", methods=["GET", "POST"])
def mail():
    if request.method == "GET":
        return render_template("sendmail.html")
    else:
        content = request.form.get("content")
        sender = request.form.get("sender")

        if not content:
            return render_template("apology.html", message="You have input your text first!")

        my_email = os.environ.get("MAIL")
        my_password = os.environ.get("PASSWORD")

        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(my_email, my_password)
            connection.sendmail(my_email, "tunahanyazar0@gmail.com", msg=f"Subject:Sender={sender}\n\n{content}")
        
        return redirect("/login")

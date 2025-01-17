import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


COMPETITION_PLACES_SUCCESFULLY_BOOKED_MESSAGE = "Great-booking complete!"
NOT_ENOUGH_POINTS_MESSAGE = "Not enough points !"
UNABLE_TO_BOOK_MORE_THAN_12_PLACES_MESSAGE = "You are unable to book more than 12 places"
PAST_COMPETITION_ERROR_MESSAGE = "You are unable to book places from past competitions !"


def loadClubs():
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    try:
        club = [club for club in clubs if club["email"] == request.form["email"]][0]
    except IndexError:
        error_message = "Email not found !"
        return render_template("index.html", error_message=error_message)
    else:
        return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    foundClub = [c for c in clubs if c["name"] == club][0]
    foundCompetition = [c for c in competitions if c["name"] == competition][0]
    competition_date = datetime.strptime(foundCompetition["date"], "%Y-%m-%d %H:%M:%S")
    if foundClub and foundCompetition:
        if competition_date > datetime.today():
            return render_template(
                "booking.html", club=foundClub, competition=foundCompetition
            )
        else:
            flash(PAST_COMPETITION_ERROR_MESSAGE)
            return render_template(
                "welcome.html", club=foundClub, competitions=competitions
            )
    else:
        flash("Something went wrong-please try again")
        return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competition = [c for c in competitions if c["name"] == request.form["competition"]][
        0
    ]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    club_points = int(club["points"])
    number_of_competition_places = int(competition["numberOfPlaces"])
    placesRequired = int(request.form["places"])

    if placesRequired > club_points:
        flash(NOT_ENOUGH_POINTS_MESSAGE)
        return render_template("welcome.html", club=club, competitions=competitions)

    else:
        if placesRequired > 12:
            flash(UNABLE_TO_BOOK_MORE_THAN_12_PLACES_MESSAGE)
            return render_template("welcome.html", club=club, competitions=competitions)

        else:
            club["points"] = club_points - placesRequired
            competition["numberOfPlaces"] = number_of_competition_places - placesRequired

            flash(COMPETITION_PLACES_SUCCESFULLY_BOOKED_MESSAGE)
            return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/list_of_clubs")
def list_of_clubs():
    return render_template("list_of_clubs.html", clubs=clubs)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))

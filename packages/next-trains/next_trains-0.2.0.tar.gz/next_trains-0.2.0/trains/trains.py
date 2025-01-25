# SPDX-License-Identifier: AGPL-3.0-or-later
"""An imagining of a combined Arrivals and Departure board."""

from os import getenv
from typing import Any

import arrow
import requests
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv
from flask import Flask, render_template

Train = tuple[str, str, str, str, str]

load_dotenv()
RAIL_DATA_API_KEY = getenv("RAIL_DATA_API_KEY")
if not RAIL_DATA_API_KEY:
    raise ValueError("Missing RAIL_DATA_API_KEY environment variable")

DEFAULT_CRS = getenv("DEFAULT_CRS", "INV")

app = Flask(__name__)
wrapped_app = WsgiToAsgi(app)


def get_train_data(crs: str, now: str) -> Any:
    """
    Fetches train data for a given CRS (station code) and a specific datetime.

    This function sends a GET request to the RailData API to retrieve live
    train arrival and departure information for a specified station and time.
    The data is extracted and returned in JSON format.

    :param crs: The station code (CRS) for which the train information is
                retrieved.
    :param now: The specific datetime in the required YYYYMMDDTHHmmss format.
    :return: A JSON object containing the trains fetched from the RailData
             API.
    """
    req_url = (
        f"https://api1.raildata.org.uk/"
        f"1010-live-arrival-and-departure-boards---staff-version1_0/LDBSVWS/"
        f"api/20220120/GetArrivalDepartureBoardByCRS/"
        f"{crs}/{now}"
    )
    headers = {"User-Agent": "MikeCoats-NextTrains", "x-apikey": RAIL_DATA_API_KEY}

    response = requests.request("GET", req_url, headers=headers, timeout=5)

    data = response.json()
    services = data.get("trainServices", {})

    return services


def format_arriving_train(train_data: Any) -> Train:
    """
    Formats an arriving train, including its location, platform information,
    and arrival time.

    :param train_data: A JSON object containing arriving train information.
    :type train_data: Any
    :return: A tuple containing the text "Arriving from", the train's arrival
             location name, platform information as a string (if the platform
             is not hidden) and the arrival time in humanized and ISO 8601
             formats.
    :rtype: Train

    """
    location = train_data["origin"][0]["locationName"]
    platform = (
        "Platform " + train_data["platform"]
        if train_data["platformIsHidden"] is False
        else ""
    )
    arrival_ts = (
        train_data["ata"]
        if train_data["ataSpecified"]
        else train_data["eta"] if train_data["etaSpecified"] else train_data["sta"]
    )
    arrival = arrow.get(arrival_ts, "YYYY-MM-DDTHH:mm:ss")

    return (
        "Arriving from",
        location,
        platform,
        arrival.format(arrow.FORMAT_W3C),
        arrival.humanize(granularity="minute"),
    )


def format_departing_train(train_data: Any) -> Train:
    """
    Formats a departing train, including its location, platform information,
    and arrival time.

    :param train_data: A JSON object containing departing train information.
    :type train_data: Any
    :return: A tuple containing the text "Departing for", the train's
             destination location name, platform information as a string (if
             the platform is not hidden) and the departure time in humanized
             and ISO 8601 formats.
    :rtype: Train
    """
    location = train_data["destination"][0]["locationName"]
    platform = (
        "Platform " + train_data["platform"]
        if train_data["platformIsHidden"] is False
        else ""
    )
    departure_ts = (
        train_data["atd"]
        if train_data["atdSpecified"]
        else train_data["etd"] if train_data["etdSpecified"] else train_data["std"]
    )
    departure = arrow.get(departure_ts, "YYYY-MM-DDTHH:mm:ss")

    return (
        "Departing for",
        location,
        platform,
        departure.format(arrow.FORMAT_W3C),
        departure.humanize(granularity="minute"),
    )


def train_key(train: Train) -> str:
    """
    Extract a key suitable for sorting Trains in a list. A list of trains is
    usually sorted by date and time, so Arrow's W3C format timestamp is used
    for sorting.

    :param train: A train from which to extract a sorting key.
    :type train: Train
    :return: An alphanum sortable key.
    :rtype: str
    """
    return train[3]


def parse_train_data(trains_data: Any) -> list[Train]:
    """
    Parses and processes train data by categorizing trains into arriving and
    departing, formatting them accordingly, and sorting the resulting list.

    :param trains_data: JSON object containing train information, including
                        details about their arrivals and departures.
    :type trains_data: Any
    :return: A sorted list of formatted arriving and departing trains.
    :rtype: list[Train]
    """
    arriving_data = [train for train in trains_data if train["activities"] == "TF"]
    departing_data = [train for train in trains_data if train["activities"] == "TB"]

    arriving_trains = [format_arriving_train(train) for train in arriving_data]
    departing_trains = [format_departing_train(train) for train in departing_data]
    the_trains = arriving_trains + departing_trains
    the_trains.sort(key=train_key)
    return the_trains


@app.route("/", methods=["GET", "HEAD"])
@app.route("/<crs>")
def greet(crs=DEFAULT_CRS):
    """
    Handles the '/' and '/<crs>' routes to display train information.

    This function processes the given CRS (station code) or defaults to 'INV',
    fetches train data for the current time, parses the retrieved data, and
    renders the homepage template with the list of trains and the current time.

    :param crs: Station code (three-character CRS code). Defaults to 'INV'.
    :type crs: str
    :return: Rendered homepage template with train information and current
             time.
    :rtype: str
    """
    now = arrow.utcnow()
    train_data = get_train_data(crs, now.format("YYYYMMDDTHHmmss"))
    the_trains = parse_train_data(train_data)

    return render_template("home.html", trains=the_trains, now=now.format("HH:mm:ss"))


def trains():
    """Launch the server, when called from pyproject.toml script, 'trains'."""
    uvicorn.run("trains.trains:wrapped_app", host="0.0.0.0", port=8007)


def main():
    """Launch the server, when called directly from 'python trains/trains.py'."""
    uvicorn.run("trains:wrapped_app", host="0.0.0.0", port=8007)


if __name__ == "__main__":
    main()

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#SETUP FOR THE DATABASE
engine = create_engine("sqlite:///hawaii.sqlite")

#TURN OLD DATABASE INTO NEW
Base = automap_base()

#REFLECTING THE TABLES
Base.prepare(engine, reflect=True)

#SAVING REFERENCES ONTO EACH TABLE
Measurement = Base.classes.measurement
Station = Base.classes.station

# CREATE LINK FROM PYTHON TO ENGINE
session = Session(engine)

#SETUP FOR FLASK
app = Flask(__name__)


#FLASK ROUTES

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #DATE & PRECIPITATION FOR THE LAST YEAR
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    #CONVERT TO A LIST
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    #DATE FROM ONE YEAR AGO TO LAST DATE IN THE DATABASE
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #TOBS FROM LAST YEAR
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    #MAKING IT INTO A LIST
    temps = list(np.ravel(results))

    #THE RESULTS (RETURN THE RESULTS)
    return jsonify(temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

#REPEAT AS DONE ABOVE 
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run()

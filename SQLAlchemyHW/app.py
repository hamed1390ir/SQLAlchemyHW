import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Reflect Tables into SQLAlchemy ORM
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)




app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"List of available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    ## Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Calculate the date 1 year ago from the last data point in the database
    One_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    my_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= One_year_ago).all()
    # Dict with date as the key and prcp as the value
    result = {date: prcp for date, prcp in my_data}
    
    ## Return the JSON representation of your dictionary.
    return jsonify(result)


@app.route("/api/v1.0/stations")
def stations():
    # Design a query to show the stations available in this dataset
    data = session.query(Station.station).all()
    stations = list(np.ravel(data))
    ## Return a JSON list of stations from the dataset
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    ## query for the dates and temperature observations from a year from the last data point.
    One_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    data = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= One_year_ago).all()

    ## Return a JSON list of Temperature Observations (tobs) for the previous year
    temp_monthly = list(np.ravel(data))
    return jsonify(temp_monthly)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start, end):
    
    sel_stat = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    ## When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    if not end:
        data = session.query(*sel_stat).filter(Measurement.date >= start).all()
        myStats = list(np.ravel(data))
        ## Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range
        return jsonify(myStats)
    ## When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    else:
        data = session.query(*sel_stat).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        myStats = list(np.ravel(data))
        ## Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range
        return jsonify(myStats)


if __name__ == '__main__':
    app.run()

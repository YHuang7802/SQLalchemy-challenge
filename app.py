import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement

station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


# * Homepage.
# * List all available routes.
@app.route("/")
def home():
    return(
        f"Welcome to the Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
        

# * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# * Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation data"""
    # Query all dates and precipitation
    results = session.query(measurement.date, measurement.prcp).all()

    session.close()

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['precipitation'] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

# * Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(station.name).all()

    session.close()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)

# * Query the dates and temperature observations of the most active station for the previous year of data.
# * Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    results = session.query(measurement.date, measurement.tobs).filter(measurement.station == "USC00519281", func.strftime("%Y-%m-%d",measurement.date) >= dt.date(2016,8,23)).all()

    session.close()

    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['temperature'] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)


# * Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
# * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than or equal to the start date.
@app.route("/api/v1.0/start<start>")
def start(date):
    date= dt.datetime.strptime('%Y-%m-%d')
    
    session = Session(engine)

    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(func.strftime("%Y-%m-%d",measurement.date) >= date).all()

    session.close()

    start_date = list(np.ravel(results))
    return jsonify(start_date)

# def trip1(start):

#  # go back one year from start date and go to end of data for Min/Avg/Max temp   
#     start_date= dt.datetime.strptime(start, '%Y-%m-%d')
#     last_year = dt.timedelta(days=365)
#     start = start_date-last_year
#     end =  dt.date(2017, 8, 23)
#     trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
#         filter(Measurements.date >= start).filter(Measurements.date <= end).all()
#     trip = list(np.ravel(trip_data))
#     return jsonify(trip)

# * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates from the start date through the end date (inclusive).
@app.route("/api/v1.0/range<start>/<end>")
def range(date):
    date= dt.datetime.strptime(date, '%Y-%m-%d')
    end =  dt.date(2017, 8, 23)
    
    session = Session(engine)

    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(func.strftime("%Y-%m-%d",measurement.date) >= date).filter(func.strftime("%Y-%m-%d",measurement.date) <= end).all()

    session.close()

    start_date = list(np.ravel(results))
    return jsonify(start_date)




if __name__ == "__main__":
    app.run(debug=True)
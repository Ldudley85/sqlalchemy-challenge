# Import the dependencies.
from flask import Flask, jsonify, request
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np

#################################################
# Database Setup
#################################################
# engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# create app
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# / - start at homepage and list all available routes
@app.route("/")
def homepage():
    """List all available routes."""
    return (f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

#2) /api/v1.0/precipitation - Convert the query results from your precipitation analysis 
# (i.e. retrieve only the last 12 months of data) to a dictionary 
# using date as the key and prcp as the value. 
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation data for previous year"""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prior_yr_precip_query = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= last_year).all()

    prior_prcp = {date: prcp for date, prcp in precipitation}
    return jsonify(prior_prcp)

#3)/api/v1.0/stations - return a JSON list of stations from dataset
@app.route("/api/v1.0/stations")
def stations():
    """Station List"""
    stations = session.query(Station.name, Station.station).all()
    station_list = list(np.ravel(stations))
    return jsonify(station_list)

#4)/api/v1.0/tobs - dates and temperature observations 
# of the most-active station for the previous year of data
# Return a JSON list of temperature observations for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    """Most active station temperature observations - prior year"""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station_py = (session.query(Measurement.station, Measurement.tobs)
             .filter(Measurement.date >= last_year)
             .filter(Measurement.station == 'USC00519281')
             .all())
    py_tobs = list(np.ravel(most_active_station_py))
    return jsonify(py_tobs)
#5) /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or 
# equal to the start date.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates 
# from the start date to the end date, inclusive.

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def summary(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    # Select statement
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # return for dates since start
        temps_since_start= session.query(*select).\
            filter(Measurement.date >= start).all()
        
        temps_start_list = list(np.ravel(temps_since_start))
        return jsonify(temps_start_list)

        # return for start to end date, inclusive
    temps_between = session.query(*select).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
   
    temps_between_list = list(np.ravel(temps_between))
    return jsonify(temps_between_list)

session.close()

if __name__ == '__main__':
    app.run()



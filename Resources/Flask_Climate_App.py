

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc, asc


from flask import Flask, jsonify

app = Flask(__name__)

#################################################
#######  Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


####################################################################
#########  Variables
####################################################################


prcp_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > '2016-08-23').all()

station_data = session.query(Station.id, Station.station, Station.name).all()

tobs_data = session.query(Measurement.date, func.sum(Measurement.tobs)).\
    filter(Measurement.date > '2016-08-23').\
    group_by(Measurement.date).\
    order_by(asc(Measurement.date)).all()


####################################################################
#########  Flask Routes
####################################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date> where start_date = YYYYMMDD <br/> "
        f"/api/v1.0/<start_date>/<end_date> where start_date/end_date = YYYYMMDD<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns date and precipitation for the past year"""
    return jsonify (prcp_data)


@app.route("/api/v1.0/stations")
def stations():
    """Returns a list of stations"""
    return jsonify (station_data)


@app.route("/api/v1.0/tobs")
def tobs():
    """Returns a list of dates and temperature observations from a year from the last data point."""
    return jsonify (tobs_data)

@app.route("/api/v1.0/<start_date>")
def calc_start(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
                
    Returns:
        TMIN, TAVE, and TMAX
    """
    date2 = str(start_date)

    date3 = ("'" + date2[0:4] + "-" + date2[4:6] + "-" + date2[6:8] + "'")
    
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date == date3).all()
    
    return jsonify (temps)
    


@app.route("/api/v1.0/<start_date>/<end_date>")

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    date_start = str(start_date)
    date_start_2 = ("'" + date_start[0:4] + "-" + date_start[4:6] + "-" + date_start[6:8] + "'")

    date_end = str(end_date)
    date_end_2 = ("'" + date_end[0:4] + "-" + date_end[4:6] + "-" + date_end[6:8] + "'")
    
    temps1 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= date_start_2).filter(Measurement.date <= date_end_2).all()

    return jsonify (temps1) 



if __name__ == '__main__':
    app.run(debug=True)

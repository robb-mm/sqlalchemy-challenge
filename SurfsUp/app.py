# Import the dependencies.
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all the available routes."""

    return (
        f"List of all available routes.<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    result = session.query(measurement.station, measurement.date, measurement.prcp).\
        filter(measurement.date >= '2016-08-23').all()

    ret = {}
    for s, d, p in result:
        if s not in ret:
            ret[s] = {d : p}
        else:
            ret[s].update({d : p})
    return ret

@app.route("/api/v1.0/stations")
def stations():
    result = session.query(station.station).order_by(station.station).all()
    return list(np.ravel(result))

@app.route("/api/v1.0/tobs")
def tobs():
    result = session.query(measurement.date, measurement.tobs).\
                where(measurement.station=='USC00519281', measurement.date>='2016-08-18').all()
    
    return dict(result)

@app.route("/api/v1.0/<start>")
def temperature_from(start):
    result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).where(measurement.date>=start).all()

    ret = {}
    for tmin, tave, tmax in result:
        ret['1. min temp'] = tmin
        ret['2. ave temp'] = tave
        ret['3. max temp'] = tmax
    return ret

@app.route("/api/v1.0/<start>/<end>")
def temperature_between(start, end):
    result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                where(measurement.date>=start, measurement.date<=end).all()

    ret = {}
    for tmin, tave, tmax in result:
        ret['1. min temp'] = tmin
        ret['2. ave temp'] = tave
        ret['3. max temp'] = tmax
    
    return (
        # f"Start Date: {start}  End Date: {end}<br/>{jsonify(ret)}"
        ret
    )

    # return (f"{start}, {end}")

if __name__ == "__main__":
    app.run(debug=True)

import numpy as np

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
# save a reference to tables
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>Form:YYYY-MM-DD<br/>"
        f"/api/v1.0/<start>/<end><br/>Form:YYYY-MM-DD<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[f"{date}"] = prcp
        
        precipitation.append(precipitation_dict)
    
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def station():

    session = Session(engine)
    results = session.query(Station.station).all()

    session.close()

    stations = list(results)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    allstations = session.query(Measurement.station, func.count(Measurement.tobs)).\
        order_by(func.count(Measurement.tobs).desc()).all()

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == allstations[0][0]).filter(Measurement.date >= '2016-08-23').all()


    mostactive = []
    for date, temp in results:  
        mostactive_dict = {}
        mostactive_dict["date"] = date
        mostactive_dict["Temperature"] = temp
        mostactive.append(mostactive_dict)


    
    return jsonify(mostactive)


@app.route("/api/v1.0/<start>")
def start(start):
    
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()

    temps = {"TMIN": results[0][0], "TMAX": results[0][1], "TAVG": results[0][2]}
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temps = {"TMIN": results[0][0], "TMAX": results[0][1], "TAVG": results[0][2]}
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)

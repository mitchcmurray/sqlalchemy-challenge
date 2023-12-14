# Import the dependencies
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta 

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Get the most recent date from the database
most_recent_date = session.query(func.max(Measurement.date)).scalar()
most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')

# Calculate the date one year ago from the last date in the dataset
one_year_ago = most_recent_date - timedelta(days=365)

# Calculate the most active stations
active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route('/')
def homepage():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year ago from the last date in the dataset
    one_year_ago = most_recent_date - datetime.timedelta(days=365)

    # Query to retrieve last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary using date as the key and precipitation as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Query to retrieve list of stations
    stations = session.query(Station.station).all()

    # Convert the query results to a list of station names
    station_list = [station for (station,) in stations]

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Get the most active station ID (assuming it's the first station in the result)
    most_active_station = active_stations[0][0] if active_stations else None

    if most_active_station:
        # Calculate the date one year ago from the last date in the dataset
        one_year_ago = most_recent_date - datetime.timedelta(days=365)

        # Query to retrieve temperature observations of the most active station for the previous year of data
        temperature_data = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == most_active_station).\
            filter(Measurement.date >= one_year_ago).all()

        # Convert the query results to a list of dictionaries containing date and temperature
        temperature_list = [{'Date': date, 'Temperature': tobs} for date, tobs in temperature_data]

        return jsonify(temperature_list)
    else:
        return jsonify({'error': 'No active stations found.'})
    

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Gizem.2002@localhost:5432/airline_api_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# JWT config
app.config["JWT_SECRET_KEY"] = "super-secret-key"  
jwt = JWTManager(app)

# Swagger config
app.config['SWAGGER'] = {
    'uiversion': 3
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Airline API",
        "description": "API for managing flights, tickets, check-ins, and more.",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}
swagger = Swagger(app, template=swagger_template)


@app.route('/api/v1/flights', methods=['POST'])
@jwt_required()
def add_flight():
    """
    Add a new flight
    ---
    tags:
      - Flights
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - date_from
            - date_to
            - airport_from
            - airport_to
            - duration
            - capacity
          properties:
            date_from:
              type: string
              example: 2025-06-01
            date_to:
              type: string
              example: 2025-06-01
            airport_from:
              type: string
              example: IST
            airport_to:
              type: string
              example: AYT
            duration:
              type: integer
              example: 90
            capacity:
              type: integer
              example: 180
    responses:
      201:
        description: Flight added successfully
      400:
        description: Invalid input
      500:
        description: Internal server error
    """
    data = request.get_json()
    
    try:
        required_fields = ["date_from", "date_to", "airport_from", "airport_to", "duration", "capacity"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' field is required"}), 400

        
        new_flight = Flight(
            date_from=data["date_from"],
            date_to=data["date_to"],
            airport_from=data["airport_from"],
            airport_to=data["airport_to"],
            duration=data["duration"],
            capacity=data["capacity"]
        )

        db.session.add(new_flight)
        db.session.commit()

        return jsonify({
            "message": "Flight added successfully!",
            "data": {
                "id": new_flight.id,
                "airport_from": new_flight.airport_from,
                "airport_to": new_flight.airport_to,
                "date_from": new_flight.date_from,
                "date_to": new_flight.date_to,
                "duration": new_flight.duration,
                "capacity": new_flight.capacity
            }
        }), 201

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

class Flight(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)
    date_from = db.Column(db.String, nullable=False)
    date_to = db.Column(db.String, nullable=False)
    airport_from = db.Column(db.String, nullable=False)
    airport_to = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(10), nullable=False)  
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    passenger_name = db.Column(db.String(100), nullable=False)

class Checkin(db.Model):
    __tablename__ = 'checkins'
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    passenger_name = db.Column(db.String(100), nullable=False)
    seat_number = db.Column(db.Integer)


@app.route('/api/v1/flights', methods=['GET'])
@jwt_required(optional=True)  
def get_flights():
    """
    Get paginated list of flights
    ---
    tags:
      - Flights
    parameters:
      - name: page
        in: query
        type: integer
        format: int32
        required: false
        default: 1
        description: Page number for pagination
    responses:
      200:
        description: A paginated list of flights
        schema:
          type: object
          properties:
            page:
              type: integer
            total_pages:
              type: integer
            total_flights:
              type: integer
            flights:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  airport_from:
                    type: string
                  airport_to:
                    type: string
                  date_from:
                    type: string
                  date_to:
                    type: string
                  duration:
                    type: integer
                  capacity:
                    type: integer
    """
    page = request.args.get('page', default=1, type=int)
    per_page = 10

    flights = Flight.query.paginate(page=page, per_page=per_page, error_out=False)

    data = [{
        "id": f.id,
        "airport_from": f.airport_from,
        "airport_to": f.airport_to,
        "date_from": f.date_from,  
        "date_to": f.date_to,
        "duration": f.duration,
        "capacity": f.capacity
    } for f in flights.items]

    return jsonify({
        "page": page,
        "total_pages": flights.pages,
        "total_flights": flights.total,
        "flights": data
    })



@app.route('/api/v1/tickets', methods=['POST'])
@jwt_required()
def buy_ticket():
    """
    Buy a ticket for a flight
    ---
    tags:
      - Tickets
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - flight_id
            - passenger_name
          properties:
            flight_id:
              type: integer
              example: 1
            passenger_name:
              type: string
              example: Gizem Tanis
    responses:
      201:
        description: Ticket purchased successfully
      400:
        description: Invalid input
      409:
        description: Flight is sold out
    """
    data = request.get_json()
    flight_id = data.get("flight_id")
    passenger_name = data.get("passenger_name")

    
    if not isinstance(passenger_name, str) or len(passenger_name.strip()) == 0 or len(passenger_name) > 100:
        return jsonify({"error": "Invalid passenger name"}), 400

    if flight_id is None or not isinstance(flight_id, int):
        return jsonify({"error": "Invalid flight ID"}), 400

   
    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"error": "Invalid flight ID"}), 400

   
    if flight.capacity <= 0:
        return jsonify({"message": "Flight is sold out!"}), 409

    
    flight.capacity -= 1

    
    ticket_number = f"T{Ticket.query.count() + 1:03d}"

    
    new_ticket = Ticket(
        ticket_number=ticket_number,
        flight_id=flight_id,
        passenger_name=passenger_name
    )

    db.session.add(new_ticket)
    db.session.commit()

    return jsonify({
        "message": "Ticket purchased successfully!",
        "ticket": {
            "ticket_number": new_ticket.ticket_number,
            "flight_id": flight_id,
            "passenger_name": passenger_name
        }
    }), 201



@app.route('/api/v1/tickets', methods=['DELETE'])
@jwt_required()
def cancel_ticket():
    """
    Cancel a purchased ticket
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - flight_id
            - passenger_name
          properties:
            flight_id:
              type: integer
              example: 1
            passenger_name:
              type: string
              example: Gizem Tanis
    responses:
      200:
        description: Ticket cancelled successfully
      400:
        description: Invalid input or flight not found
      404:
        description: Ticket not found
    """
    data = request.get_json()
    flight_id = data.get("flight_id")
    passenger_name = data.get("passenger_name")

    
    if not isinstance(passenger_name, str) or not passenger_name.strip():
        return jsonify({"error": "Invalid passenger name"}), 400
    if not isinstance(flight_id, int):
        return jsonify({"error": "Invalid flight ID"}), 400

    
    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"error": "Flight not found"}), 400

    
    ticket = Ticket.query.filter_by(flight_id=flight_id, passenger_name=passenger_name).first()
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    
    db.session.delete(ticket)
    flight.capacity += 1
    db.session.commit()

    return jsonify({"message": "Ticket cancelled successfully"}), 200


@app.route('/api/v1/checkin', methods=['POST'])
@jwt_required()
def check_in():
    """
    Perform check-in for a passenger
    ---
    tags:
      - Check-in
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - flight_id
            - passenger_name
          properties:
            flight_id:
              type: integer
              example: 1
            passenger_name:
              type: string
              example: Gizem Tanis
    responses:
      200:
        description: Check-in successful
      400:
        description: Invalid input or flight ID
      404:
        description: No valid ticket found for passenger
    """
    data = request.get_json()
    flight_id = data.get("flight_id")
    passenger_name = data.get("passenger_name")

   
    if not isinstance(flight_id, int) or not isinstance(passenger_name, str) or not passenger_name.strip():
        return jsonify({"error": "Invalid input"}), 400

  
    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"error": "Invalid flight ID"}), 400

   
    ticket = Ticket.query.filter_by(flight_id=flight_id, passenger_name=passenger_name).first()
    if not ticket:
        return jsonify({"error": "No valid ticket found for passenger"}), 404

    
    existing = Checkin.query.filter_by(flight_id=flight_id, passenger_name=passenger_name).first()
    if existing:
        return jsonify({
            "message": "Passenger already checked in",
            "seat_number": existing.seat_number
        }), 200

   
    seat_number = Checkin.query.filter_by(flight_id=flight_id).count() + 1

  
    checkin = Checkin(
        flight_id=flight_id,
        passenger_name=passenger_name,
        seat_number=seat_number
    )
    db.session.add(checkin)
    db.session.commit()

    return jsonify({
        "message": "Check-in successful!",
        "seat_number": seat_number
    }), 200



@app.route('/api/v1/passengers', methods=['GET'])
@jwt_required()
def get_passenger_list():
    """
    Get passenger list for a flight
    ---
    tags:
      - Passengers
    security:
      - Bearer: []
    parameters:
      - name: flight_id
        in: query
        type: integer
        required: true
        description: ID of the flight
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number for pagination
    responses:
      200:
        description: List of checked-in passengers for the flight
        schema:
          type: object
          properties:
            flight_id:
              type: integer
              example: 1
            page:
              type: integer
            total_pages:
              type: integer
            total_passengers:
              type: integer
            passengers:
              type: array
              items:
                type: object
                properties:
                  passenger_name:
                    type: string
                    example: Gizem Tanis
                  seat_number:
                    type: integer
                    example: 1
      400:
        description: Invalid flight ID
    """
    flight_id = request.args.get("flight_id", type=int)
    page = request.args.get("page", default=1, type=int)
    per_page = 10

    if flight_id is None or flight_id <= 0:
        return jsonify({"error": "Invalid flight ID"}), 400

    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"error": "Flight not found"}), 400

    checkins = Checkin.query.filter_by(flight_id=flight_id).paginate(page=page, per_page=per_page, error_out=False)

    passenger_list = [
        {
            "passenger_name": c.passenger_name,
            "seat_number": c.seat_number
        }
        for c in checkins.items
    ]

    return jsonify({
        "flight_id": flight_id,
        "page": page,
        "total_pages": checkins.pages,
        "total_passengers": checkins.total,
        "passengers": passenger_list
    }), 200


@app.route('/login', methods=['POST'])
def login():
    """
    User login to receive JWT token
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: 1234
    responses:
      200:
        description: JWT token returned
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJ0eXAiOiJKV1QiLCJh..."
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    
    if username == "admin" and password == "1234":
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)

  AirLine API - Flask RESTful Web Service 

This project is a simple airline ticket management RESTful API developed 
using Flask, PostgreSQL, SQLAlchemy, JWT Authentication, and Flasgger 
for Swagger UI documentation. 
It enables flight management, ticket booking, passenger check-ins, and 
retrieving passenger lists.

  Project Overview

The Airline API allows: adding and querying flights, buying and canceling tickets,
checking in passengers, viewing passenger lists for specific flights
Authentication is required for most operations, and responses are documented using Swagger UI.

  Technologies Used

Python 3.9
Flask (Web framework)
Flask-JWT-Extended (Token-based authentication)
SQLAlchemy (ORM for PostgreSQL)
PostgreSQL (Database)
Flasgger (Swagger UI integration)

   Setup & Installation
Python Version: 3.9
Port: 5000
Database URL: postgresql://postgres:Gizem.2002@localhost:5432/airline_api_db
JWT Secret: Set in app.config["JWT_SECRET_KEY"] = "super-secret-key"
Swagger UI: Accessible at http://127.0.0.1:5000/apidocs after running the app
Default Admin Credentials (for login): 
{
  "username": "admin",
  "password": "1234"
}


   Authentication

Token is retrieved via the /login endpoint using hardcoded credentials:
{
  "username": "admin",
  "password": "1234"
}

Use the returned JWT token for protected routes:
Authorization: Bearer <your_token>

  Swagger UI Access
  
Once the server is running, open your browser at:
  http://127.0.0.1:5000/apidocs
Here you can test all endpoints with example requests and responses.

  API Features
  
Endpoint                    Description                       Auth    Paging

POST /api/v1/flights        Add a new flight                   ✔       ✖️ 
GET /api/v1/flights         List flights with pagination      ✖️        ✔
POST /api/v1/tickets        Buy a ticket                       ✔       ✖️ 
DELETE /api/v1/tickets      Cancel a ticket                    ✔       ✖️ 
POST /api/v1/checkin        Passenger check-in                ✖️       ✖️ 
GET /api/v1/passengers      List passengers by flight          ✔        ✔


 ER Diagram 
 
![Görüntü](https://github.com/user-attachments/assets/048196a0-6645-47a5-90d3-e9041f973786)

This ER diagram represents the core data models and their relationships in the Airline API system.
The flights table stores basic flight information such as dates, origin/destination airports, duration, and capacity.
The tickets table represents the tickets sold for each flight and is linked to the flights table through the flight_id foreign key.
The checkins table tracks the passenger check-in process and is also linked to the flights table via flight_id.
All relationships are one-to-many, meaning one flight can have multiple tickets and check-ins.

  Notes

Authentication is required using JWT for secure endpoints.
Pagination is implemented for /flights and /passengers endpoints.
Example requests and responses are documented in Swagger UI.
Ensure PostgreSQL is running and a database named airline_api_db is created.

- Author: Gizem Tanış - Computer Engineering Student

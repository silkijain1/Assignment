Writing the README File:

Install dependencies:
bash

pip install -r requirements.txt 
Set up the database:
Make sure PostgreSQL is running.
Update the database URI in app.py to connect to your PostgreSQL instance.
Run migrations to create the database tables:
bash

flask db upgrade 
Running the API
Start the Flask server:
bash

python app.py 
The API will be accessible at http://localhost:5000.
Endpoints
POST /register: Register a new user with a username and password.
POST /login: Login with username and password to receive an authorization token.
POST /trains/add: Add a new train with source, destination, and total seats (Admin only).
GET /trains/availability: Get seat availability for trains between specified source and destination.
POST /bookings/book: Book a seat on a particular train.
GET /bookings/details/<booking_id>: Get details of a specific booking.
Authentication
All endpoints except /register and /login require an Authorization header with a valid JWT token obtained after logging in.
Role-Based Access Control
Admin users can access /trains/add endpoint to add new trains.
Regular users can book seats but cannot add trains.

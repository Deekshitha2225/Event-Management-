from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from pymongo.errors import ConnectionFailure

app = Flask(__name__)

try:
    # Set up MongoDB client
    client = MongoClient("mongodb://localhost:27017/")
    db = client.event_management  # Replace with your database name
    events_collection = db.events  # Replace with your collection name
except ConnectionFailure as e:
    print(f"Error connecting to MongoDB: {e}")
    client = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        if client:
            try:
                event = {
                    'name': request.form['name'],
                    'date': request.form['date'],
                    'location': request.form['location'],
                    'description': request.form['description']
                }
                events_collection.insert_one(event)
                return redirect(url_for('view_events'))
            except Exception as e:
                print(f"Error adding event: {e}")
                return "Error adding event", 500  # Internal Server Error
        else:
            return "Database connection error", 500  # Internal Server Error

    return render_template('add_event.html')

@app.route('/view_events')
def view_events():
    if client:
        try:
            events = events_collection.find()
            return render_template('view_events.html', events=events)
        except Exception as e:
            print(f"Error fetching events: {e}")
            return "Error fetching events", 500  # Internal Server Error
    else:
        return "Database connection error", 500  # Internal Server Error

@app.route('/edit_event/<event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if request.method == 'POST':
        if client:
            try:
                updated_event = {
                    'name': request.form['name'],
                    'date': request.form['date'],
                    'location': request.form['location'],
                    'description': request.form['description']
                }
                events_collection.update_one({'_id': ObjectId(event_id)}, {'$set': updated_event})
                return redirect(url_for('view_events'))
            except Exception as e:
                print(f"Error updating event: {e}")
                return "Error updating event", 500  # Internal Server Error
        else:
            return "Database connection error", 500  # Internal Server Error

    try:
        event = events_collection.find_one({'_id': ObjectId(event_id)})
        if event:
            return render_template('edit_event.html', event=event)
        else:
            return "Event not found", 404
    except Exception as e:
        print(f"Error fetching event: {e}")
        return "Error fetching event", 500  # Internal Server Error

@app.route('/delete_event/<event_id>', methods=['POST'])
def delete_event(event_id):
    if client:
        try:
            events_collection.delete_one({'_id': ObjectId(event_id)})
            return redirect(url_for('view_events'))
        except Exception as e:
            print(f"Error deleting event: {e}")
            return "Error deleting event", 500  # Internal Server Error
    else:
        return "Database connection error", 500  # Internal Server Error

if __name__ == '__main__':
    app.run(debug=True)

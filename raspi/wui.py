from flask import Flask, request, redirect, url_for
import requests
import json
import os

app = Flask(__name__)

# Assuming the backend server runs on this address
BACKEND_URL = "http://localhost:5000"


@app.route('/')
def home():
    # Get sessions from the backend
    response = requests.get(f"{BACKEND_URL}/sessions")
    sessions = response.json()

    # Simple HTML page with sessions listed
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hiking Sessions</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            h1 { color: #333; }
            .session { 
                border: 1px solid #ddd; 
                padding: 10px; 
                margin-bottom: 10px; 
                border-radius: 5px;
            }
            .session-actions { margin-top: 10px; }
            button { 
                background-color: #4CAF50; 
                color: white; 
                border: none; 
                padding: 5px 10px; 
                cursor: pointer; 
                border-radius: 3px; 
            }
            .delete-btn { background-color: #f44336; }
            .add-form {
                margin-bottom: 20px;
                padding: 15px;
                background-color: #f8f8f8;
                border-radius: 5px;
            }
            input, button[type="submit"] {
                margin: 5px 0;
                padding: 8px;
            }
        </style>
    </head>
    <body>
        <h1>Hiking Sessions</h1>

        <div class="add-form">
            <h2>Add New Session</h2>
            <form action="/add_session" method="post">
                <div>
                    <input type="text" name="name" placeholder="Session Name" required>
                </div>
                <div>
                    <input type="text" name="location" placeholder="Location" required>
                </div>
                <div>
                    <input type="date" name="date" required>
                </div>
                <div>
                    <button type="submit">Add Session</button>
                </div>
            </form>
        </div>

        <h2>Current Sessions</h2>
    """

    # Add each session to the HTML
    for session in sessions:
        html += f"""
        <div class="session">
            <h3>{session.get('name', 'Unnamed Session')}</h3>
            <p>Location: {session.get('location', 'Unknown')}</p>
            <p>Date: {session.get('date', 'No date')}</p>
            <div class="session-actions">
                <a href="/view_session/{session.get('id')}"><button>View Details</button></a>
                <a href="/delete_session/{session.get('id')}"><button class="delete-btn">Delete</button></a>
            </div>
        </div>
        """

    html += """
    </body>
    </html>
    """

    return html


@app.route('/view_session/<id>')
def view_session(id):
    # Get specific session details
    response = requests.get(f"{BACKEND_URL}/sessions/{id}")
    session = response.json()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Session Details</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            h1 { color: #333; }
            .session-details { 
                border: 1px solid #ddd; 
                padding: 20px; 
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            .back-btn {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                cursor: pointer;
                border-radius: 3px;
                text-decoration: none;
                display: inline-block;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Session Details</h1>

        <div class="session-details">
    """

    # Display all session details
    for key, value in session.items():
        html += f"<p><strong>{key}:</strong> {value}</p>"

    html += """
        </div>

        <a href="/" class="back-btn">Back to All Sessions</a>
    </body>
    </html>
    """

    return html


@app.route('/delete_session/<id>')
def delete_session(id):
    # Delete the session
    requests.get(f"{BACKEND_URL}/sessions/{id}/delete")
    return redirect(url_for('home'))


@app.route('/add_session', methods=['POST'])
def add_session():
    # This would require your backend to have an endpoint to add sessions
    # For now, this is a placeholder that will redirect back to home
    # You would need to implement the appropriate backend endpoint

    # Example of how this might work if backend supported it:
    # name = request.form.get('name')
    # location = request.form.get('location')
    # date = request.form.get('date')
    #
    # session_data = {
    #     'name': name,
    #     'location': location,
    #     'date': date
    # }
    #
    # requests.post(f"{BACKEND_URL}/sessions/add", json=session_data)

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
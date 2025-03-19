from flask import Flask, render_template, jsonify, Response, request, redirect, url_for

import db
import hike

app = Flask(__name__)
hdb = db.HubDatabase()


# Original backend routes
@app.route('/api/')
def get_home_api():
    sessions = hdb.get_sessions()
    return render_template('home.html', sessions=sessions)


@app.route('/api/sessions')
def get_sessions_api():
    sessions = hdb.get_sessions()
    sessions = list(map(lambda s: hike.to_list(s), sessions))
    print(sessions)
    return jsonify(sessions)


@app.route('/api/sessions/<id>')
def get_session_by_id_api(id):
    session = hdb.get_session(id)
    return jsonify(hike.to_list(session))


@app.route('/api/sessions/<id>/delete')
def delete_session_api(id):
    hdb.delete(id)
    print(f'DELETED SESSION WITH ID: {id}')
    return Response(status=202)


# New UI routes with improved user-friendly design
@app.route('/')
def home():
    # Get sessions directly from the database
    sessions = hdb.get_sessions()
    sessions = list(map(lambda s: hike.to_list(s), sessions))

    # HTML with improved card-based design
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESD-Hike Tracker</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            body {
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
                color: #212529;
            }
            h1, h2 {
                color: #2c3e50;
                text-align: left;
            }
            h1 {
                margin-bottom: 0;
            }
            .tagline {
                text-align: center;
                color: #7f8c8d;
                margin-top: 5px;
                margin-bottom: 30px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .card-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 20px;
            }
            .card {
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.15);
            }
            .card-header {
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                padding: 15px;
                font-weight: bold;
                font-size: 0.9em;
                display: flex;
                justify-content: space-between;
            }
            .session-id {
                opacity: 0.7;
                font-size: 0.8em;
            }
            .card-body {
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .stat-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                width: 100%;
                margin-bottom: 15px;
            }
            .stat-box {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 10px;
                text-align: center;
            }
            .stat-value {
                font-size: 1.8em;
                font-weight: bold;
                color: #2c3e50;
                margin: 5px 0;
            }
            .stat-label {
                font-size: 0.8em;
                color: #7f8c8d;
                text-transform: uppercase;
            }
            .progress-container {
                width: 120px;
                height: 120px;
                position: relative;
                margin: 0 auto;
            }
            .progress-circle-bg {
                width: 100%;
                height: 100%;
                border-radius: 50%;
                border: 10px solid #e9ecef;
                box-sizing: border-box;
            }
            .progress-circle {
                position: absolute;
                top: 0;
                left: 0;
            }
            .progress-circle-value {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 1.5em;
                font-weight: bold;
                color: #2c3e50;
            }
            .card-footer {
                display: flex;
                border-top: 1px solid #e9ecef;
            }
            .card-action {
                flex: 1;
                padding: 10px;
                text-align: center;
                text-decoration: none;
                color: #2c3e50;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            .card-action:hover {
                background-color: #f8f9fa;
            }
            .card-action.delete {
                color: #e74c3c;
            }
            .card-action.view {
                color: #3498db;
            }
            .add-form-container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 30px;
                max-width: 500px;
                background-color: #FFEFEF;
            }
            .form-title {
                color: #2c3e50;
                margin-top: 0;
                margin-bottom: 20px;
                text-align: left;
            }
            .form-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #2c3e50;
            }
            input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 1em;
            }
            .btn {
                display: inline-block;
                background: #3498db;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1em;
                font-weight: bold;
                transition: background-color 0.3s;
                width: 100%;
            }
            .btn:hover {
                background: #2980b9;
            }
            .no-sessions {
                text-align: center;
                padding: 50px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .full-width {
                grid-column: 1 / -1;
            }

            @media (max-width: 768px) {
                .form-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESD-Hike Tracker</h1>
            <br>
            <div class="add-form-container">
                <h3 class="form-title">Debug Write to DB</h3>
                <form action="/add_session" method="post">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="km">Distance (km)</label>
                            <input type="number" id="km" name="km" min="0" step="0.1" required>
                        </div>
                        <div class="form-group">
                            <label for="steps">Steps</label>
                            <input type="number" id="steps" name="steps" min="0" required>
                        </div>
                        <div class="form-group">
                            <label for="kcal">Calories (kcal)</label>
                            <input type="number" id="kcal" name="kcal" min="0" required>
                        </div>
                        <div class="form-group full-width">
                            <button type="submit" class="btn">Save Hike</button>
                        </div>
                    </div>
                </form>
            </div>

            <h2>Your Hikes</h2>
    """

    if not sessions:
        html += """
            <div class="no-sessions">
                <h3>No hikes recorded yet</h3>
                <p>Use the form above to log your first hike!</p>
            </div>
        """
    else:
        html += """
            <div class="card-grid">
        """

        # Add each session as a card
        for session in sessions:
            # Calculate progress percentage based on steps (10000 steps is considered a full day)
            step_percentage = min(session[2] / 10000 * 100, 100)
            circle_color = "#3498db"  # Default blue

            # Change color based on percentage
            if step_percentage >= 100:
                circle_color = "#27ae60"  # Green for 100%+
            elif step_percentage >= 75:
                circle_color = "#2ecc71"  # Light green for 75%+
            elif step_percentage >= 50:
                circle_color = "#f39c12"  # Orange for 50%+
            elif step_percentage >= 25:
                circle_color = "#e67e22"  # Light orange for 25%+
            else:
                circle_color = "#e74c3c"  # Red for <25%

            html += f"""
            <div class="card">
                <div class="card-header">
                    <span>Hike #{session[0]}</span>
                </div>
                <div class="card-body">
                    <div class="stat-grid">
                        <div class="stat-box">
                            <div class="stat-value">{session[1]}</div>
                            <div class="stat-label">Kilometers</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{session[3]}</div>
                            <div class="stat-label">Calories</div>
                        </div>
                    </div>

                    <div class="progress-container">
                        <div class="progress-circle-bg"></div>
                        <svg class="progress-circle" width="120" height="120" viewBox="0 0 120 120">
                            <circle cx="60" cy="60" r="54" fill="none" stroke="{circle_color}" stroke-width="12" 
                                    stroke-dasharray="{3.4 * min(step_percentage, 100)}, 339.5" />
                        </svg>
                        <div class="progress-circle-value">{session[2]}</div>
                    </div>
                    <div class="stat-label" style="margin-top: 5px;">Steps</div>
                </div>
                <div class="card-footer">
                    <a href="/view_session/{session[0]}" class="card-action view">View Details</a>
                    <a href="/delete_session/{session[0]}" class="card-action delete">Delete</a>
                </div>
            </div>
            """

        html += """
            </div>
        """

    html += """
        </div>
    </body>
    </html>
    """

    return html


@app.route('/view_session/<id>')
def view_session(id):
    # Get specific session details directly from database
    session = hdb.get_session(int(id))
    session_data = hike.to_list(session)

    # Calculate progress percentage based on steps (10000 steps is considered a full day)
    step_percentage = min(session_data[2] / 10000 * 100, 100)

    # Determine circle color based on percentage
    circle_color = "#3498db"  # Default blue
    if step_percentage >= 100:
        circle_color = "#27ae60"  # Green for 100%+
    elif step_percentage >= 75:
        circle_color = "#2ecc71"  # Light green for 75%+
    elif step_percentage >= 50:
        circle_color = "#f39c12"  # Orange for 50%+
    elif step_percentage >= 25:
        circle_color = "#e67e22"  # Light orange for 25%+
    else:
        circle_color = "#e74c3c"  # Red for <25%

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hike Details</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            body {{
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
                color: #212529;
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
            }}
            .detail-card {{
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .card-header {{
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                padding: 20px;
                font-size: 1.2em;
                text-align: center;
            }}
            .session-id {{
                opacity: 0.7;
                font-size: 0.8em;
                display: block;
                margin-top: 5px;
            }}
            .card-body {{
                padding: 30px;
            }}
            .stat-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-box {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
            }}
            .stat-value {{
                font-size: 2.5em;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0;
            }}
            .stat-label {{
                font-size: 0.9em;
                color: #7f8c8d;
                text-transform: uppercase;
            }}
            .progress-container {{
                width: 200px;
                height: 200px;
                position: relative;
                margin: 0 auto 30px auto;
            }}
            .progress-circle-bg {{
                width: 100%;
                height: 100%;
                border-radius: 50%;
                border: 15px solid #e9ecef;
                box-sizing: border-box;
            }}
            .progress-circle {{
                position: absolute;
                top: 0;
                left: 0;
            }}
            .progress-circle-value {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 2.5em;
                font-weight: bold;
                color: #2c3e50;
            }}
            .progress-label {{
                display: block;
                text-align: center;
                margin-top: 8px;
                font-size: 0.9em;
                color: #7f8c8d;
                text-transform: uppercase;
            }}
            .back-btn {{
                display: inline-block;
                background: #3498db;
                color: white;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 5px;
                margin-top: 20px;
                font-weight: bold;
                transition: background-color 0.3s;
            }}
            .back-btn:hover {{
                background: #2980b9;
            }}
            .actions {{
                display: flex;
                justify-content: space-between;
                margin-top: 30px;
            }}
            .delete-btn {{
                background: #e74c3c;
            }}
            .delete-btn:hover {{
                background: #c0392b;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hike Details</h1>

            <div class="detail-card">
                <div class="card-header">
                    <span>Hike Summary</span>
                    <span class="session-id">ID: {session_data[0]}</span>
                </div>
                <div class="card-body">
                    <div class="progress-container">
                        <div class="progress-circle-bg"></div>
                        <svg class="progress-circle" width="200" height="200" viewBox="0 0 200 200">
                            <circle cx="100" cy="100" r="92" fill="none" stroke="{circle_color}" stroke-width="16" 
                                    stroke-dasharray="{5.7 * min(step_percentage, 100)}, 578.3" />
                        </svg>
                        <div class="progress-circle-value">{session_data[2]}</div>
                        <span class="progress-label">Steps</span>
                    </div>

                    <div class="stat-grid">
                        <div class="stat-box">
                            <div class="stat-label">Distance</div>
                            <div class="stat-value">{session_data[1]}</div>
                            <div class="stat-label">kilometers</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Calories Burned</div>
                            <div class="stat-value">{session_data[3]}</div>
                            <div class="stat-label">kcal</div>
                        </div>
                    </div>

                    <div class="actions">
                        <a href="/" class="back-btn">Back to All Hikes</a>
                        <a href="/delete_session/{session_data[0]}" class="back-btn delete-btn">Delete Hike</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return html


@app.route('/delete_session/<id>')
def delete_session(id):
    # Delete the session directly using the database
    hdb.delete(int(id))
    return redirect(url_for('home'))


@app.route('/add_session', methods=['POST'])
def add_session():
    # Get form data
    km = int(request.form.get('km', 0))
    steps = int(request.form.get('steps', 0))
    kcal = int(request.form.get('kcal', 0))

    # Create a new session
    new_session = hike.HikeSession()

    # Set the attributes
    new_session.km = km
    new_session.steps = steps
    new_session.kcal = kcal  # Use the kcal value directly from the form

    # Save the session
    hdb.save(new_session)

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
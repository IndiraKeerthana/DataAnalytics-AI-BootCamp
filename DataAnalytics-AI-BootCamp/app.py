from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import ollama

app = Flask(__name__)


# Function to create database and table
def create_database():
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            complaint TEXT NOT NULL,
            ai_reply TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Function to save complaint into database
def save_complaint(name, email, complaint, ai_reply):
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO complaints (name, email, complaint, ai_reply, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        email,
        complaint,
        ai_reply,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# Function to get all complaints from database
def get_all_complaints():
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, complaint, ai_reply, created_at
        FROM complaints
        ORDER BY id DESC
    """)

    complaints = cursor.fetchall()
    conn.close()

    return complaints


# Function to generate AI reply using Ollama
def generate_ai_reply(name, email, complaint):
    # 1. Create prompt
    prompt = f"""
You are a professional customer support assistant.

Create a polite complaint response email using the details below:

Name: {name}
Email: {email}
Complaint: {complaint}

Format the response exactly like this:

Subject: Response Regarding Your Complaint

Dear {name},

We apologize for the inconvenience caused. We understand your concern regarding the issue mentioned in your complaint.

Our support team will review the matter and get back to you shortly.

Thank you for your patience.

Regards,  
Customer Support Team
"""

    # 2. Send request to Ollama
    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # 3. Extract AI response text
    ai_reply = response["message"]["content"]

    # 4. Return reply
    return ai_reply


# Main route
@app.route("/", methods=["GET", "POST"])
def home():
    ai_reply = ""

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        complaint = request.form["complaint"]

        # AI integration happens here
        ai_reply = generate_ai_reply(name, email, complaint)

        # Save complaint and AI reply into database
        save_complaint(name, email, complaint, ai_reply)

    complaints = get_all_complaints()

    return render_template(
        "index.html",
        ai_reply=ai_reply,
        complaints=complaints
    )


# Run the app
if __name__ == "__main__":
    create_database()
    app.run(debug=True)
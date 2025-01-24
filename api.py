from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, text
from chatbot.chatbot import get_response 

app = Flask(__name__, template_folder='templates', static_folder='static')

DATABASE_URL = "postgresql+psycopg2://admin:Aikittam1@localhost:5432/samsung_phones"
engine = create_engine(DATABASE_URL, echo=True)

@app.route('/')
def index():
    """
    Serve the frontend.
    """
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"DEBUG: Error rendering index.html: {e}")
        return "Error loading the page.", 500

@app.route('/phones', methods=['GET'])
def list_phones():
    """
    Endpoint to list all phone models in the database.
    """
    try:
        query = "SELECT model_name FROM phone_specs"
        with engine.connect() as connection:
            result = connection.execute(text(query)).fetchall()
            phones = [row[0] for row in result]
            return jsonify({"phones": phones}), 200
    except Exception as e:
        print(f"DEBUG: Error occurred in /phones: {e}")
        return jsonify({"error": "Something went wrong while retrieving phone models."}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint to handle chatbot messages.
    """
    try:
        user_input = request.json.get("message", "").strip()
        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        response = get_response(user_input)
        print(f"DEBUG: Chatbot response: {response}")  

        return jsonify({"response": response}), 200
    except Exception as e:
        print(f"DEBUG: Error occurred in /chat: {e}")
        return jsonify({"error": "Something went wrong"}), 500


if __name__ == "__main__":
    app.run(debug=True)

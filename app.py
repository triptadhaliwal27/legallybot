import os
from flask import Flask, render_template, request, jsonify, session
from chatbot import handle_conversation
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__)
app.secret_key = os.urandom(24) #sets a secret key for sessions
CORS(app)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


#top leval route
@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    try: 
        print("Received POST request to /chat")  # Debug log
        data = request.json #retrieves user input
        print(f"Request data: {data}")  # Debug log
        user_input = data.get('message', '').strip()
        state = data.get('state', '').strip()
        print(f"User input: {user_input}")  # Debug log
        print(f"State from request: {state}")  # Debug log

        if not user_input:
            print("Error: Missing user_input")  # Debug log
            return jsonify({'error': 'Missing user_input'}), 400

        #initialize ses sion variables
        if 'in_ollama_mode' not in session:
            session['in_ollama_mode'] = False
        if 'context' not in session:
            session['context'] = ''
        if 'current_context' not in session:
            session['current_context'] = ''
        if 'state' not in session:
            session['state'] = ''

        print(f"Session before processing: {session}")  # Debug log

        if not state and not session['state']:
            print("Asking user for state")  # Debug log
            return jsonify({'response': 'What state are you in?'})
        
        if state:
            session['state'] = state
            print(f"Updated session state: {session['state']}")  # Debug log

        #retrieve session state
        in_ollama_mode = session['in_ollama_mode']
        context = session['context']
        current_context = session['current_context']
        state = session['state']

        #calls chatbot logic
        print("Calling chatbot logic...")  # Debug log
        result, in_ollama_mode, context, current_context = handle_conversation(user_input, context, state, in_ollama_mode, current_context)
        print(f"Chatbot response: {result}")  # Debug log

        #update the session variables with new state
        session['in_ollama_mode'] = in_ollama_mode
        session['context'] = context
        session['current_context'] = current_context
        print(f"Session after processing: {session}")  # Debug log

        return jsonify({'response': result, 'context': context, 'in_ollama_mode': in_ollama_mode, 'current_context': current_context})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error' : 'An error occurred while processing your request'})
    
#start conversation
if __name__ == '__main__':
    app.run()

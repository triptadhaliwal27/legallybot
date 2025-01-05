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
        user_input = data.get('message', '').strip()
        state = data.get('state', '').strip()
        print(f"Request data: {data}")  # Debug log
        print(f"User input: {user_input}")  # Debug log
        print(f"State from request: {state}")  # Debug log

        #initialize session variables if not yet initialized
        if 'initialized' not in session:
            session['in_ollama_mode'] = False
            session['context'] = ''
            session['state'] = ''
            session['current_context'] = ''
            session['initialized'] = True
            return jsonify({'response': 'What state are you in?', 'needs_state': True})

        #set the state
        if not session['state'] and state:
            session['state'] = state
            return jsonify({
                'response': f'Thanks! You\'ve set your state to {state}. What are you legal concerns?',
                'state_confirmed': True
            })
        
        if not session['state']:
            return jsonify({'response': 'What state are you in?', 'needs_state': True})
        
        
        #retrieve session state
        in_ollama_mode = session['in_ollama_mode']
        context = session['context']
        current_context = session['current_context']

        #calls chatbot logic
        print("Calling chatbot logic...")  # Debug log
        result, in_ollama_mode, context, current_context = handle_conversation(user_input, context, session['state'], in_ollama_mode, current_context)
        print(f"Chatbot response: {result}")  # Debug log

        #update the session variables with new state
        session['in_ollama_mode'] = in_ollama_mode
        session['context'] = context
        session['current_context'] = current_context
        session.modified = True
        print(f"Session after processing: {session}")  # Debug log

        return jsonify({'response': result, 'context': context, 'in_ollama_mode': in_ollama_mode, 'current_context': current_context})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error' : 'An error occurred while processing your request'})
    
#start conversation
if __name__ == '__main__':
    app.run()

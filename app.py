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
        print("\n=== New Chat Request ===")
        print("Received POST request to /chat")
        print("Session contents:", dict(session))  # Print entire session
        
        data = request.json
        user_input = data.get('message', '').strip()
        state = data.get('state', '').strip()
        print(f"Request data: {data}")
        print(f"User input: {user_input}")
        print(f"State from request: {state}")

        # Check initialization
        if 'initialized' not in session:
            print("Initializing new session")
            session['in_ollama_mode'] = False
            session['context'] = ''
            session['state'] = ''
            session['current_context'] = ''
            session['initialized'] = True
            response = {'response': 'What state are you in?', 'needs_state': True}
            print("Sending initial response:", response)
            return jsonify(response)

        # Handle state setting
        if not session.get('state'):
            if not state:
                print(f"Assuming user input as state: {user_input}")
                state = user_input
            if state:
                print(f"Setting state to: {state}")
                session['state'] = state
                session.modified = True
                response = {
                    'response': f'Thanks! You\'ve set your state to {state}. What are your legal concerns?',
                    'state_confirmed': True
                }
                print("Sending state confirmation:", response)
                return jsonify(response)
            else:
                print("No state provided")
                response = {'response': 'What state are you in?', 'needs_state': True}
                print("Requesting state:", response)
                return jsonify(response)

        print("Proceeding with chatbot logic...")
        in_ollama_mode = session.get('in_ollama_mode', False)
        context = session.get('context', '')
        current_context = session.get('current_context', '')

        result, in_ollama_mode, context, current_context = handle_conversation(
            user_input, 
            context, 
            session['state'], 
            in_ollama_mode, 
            current_context
        )

        # Save updated session state
        session['in_ollama_mode'] = in_ollama_mode
        session['context'] = context
        session['current_context'] = current_context

        # Return the chatbot's response to the frontend
        response = {'response': result}
        print("Chatbot response:", response)
        return jsonify(response)
 
    except Exception as e:
        print(f"Error in chat route: {e}")
        import traceback
        print(traceback.format_exc())  # Print full error traceback
        return jsonify({'error': 'An error occurred while processing your request'})
    
#start conversation
if __name__ == '__main__':
    app.run()

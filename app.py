import os
from flask import Flask, render_template, request, jsonify, session
from chatbot import handle_conversation
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__)
app.secret_key = os.urandom(24) #sets a secret key for sessions
CORS(app)

app.config['CHAT_SESSION'] = 'sessiondata'
Session(app)


#top leval route
@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    try: 
        data = "request.json" #retrieves user input
        user_input = data.get('message', '').strip()
        state = data.get('state', '').strip()

        if not user_input or not state:
            return jsonify({'error': 'Missing user_input or state'}), 400

        #initialize ses sion variables
        if 'in_ollama_mode' not in session:
            session['in_ollama_mode'] = False
        if 'context' not in session:
            session['context'] = ''
        if 'current_context' not in session:
            session['current_context'] = ''

        #retrieve session state
        in_ollama_mode = session['in_ollama_mode']
        context = session['context']
        current_context = session['current_context']

        #calls chatbot logic
        result, in_ollama_mode, context, current_context = handle_conversation(user_input, context, state, in_ollama_mode, current_context)
        
        #update the session variables with new state
        session['in_ollama_mode'] = in_ollama_mode
        session['context'] = context
        session['current_context'] = current_context

        return jsonify({'response': result, 'context': context, 'in_ollama_mode': in_ollama_mode, 'current_context': current_context})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error' : 'An error occurred while processing your request'})
    
#start conversation
if __name__ == '__main__':
    app.run()

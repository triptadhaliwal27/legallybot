import os
from flask import Flask, render_template, request, jsonify, session
from chatbot import handle_conversation

app = Flask(__name__)
app.secret_key = os.urandom(24) #sets a secret key for sessions

#top leval route
@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/get', methods=['GET', 'POST'])
def chat():
    user_input = request.form.get("msg") #retrieves user input
    state = request.form.get('state', '')

    if not user_input or not state:
        return jsonify({'error': 'Missing user_input or state'}, 400)

    #session initialization

    if 'in_ollama_mode' not in session:
        session['in_ollama_mode'] = False
    if 'context' not in session:
        session['context'] = ''
    if 'current_context' not in session:
        session['current_context'] = ''

    in_ollama_mode = session['in_ollama_mode']
    context = session['context']
    current_context = session['current_context']

    result, in_ollama_mode, context, current_context = handle_conversation(user_input, context, state, in_ollama_mode, current_context)
    #update the session variables
    session['in_ollama_mode'] = in_ollama_mode
    session['context'] = context
    session['current_context'] = current_context

    return jsonify({'response': result})

#start conversation
if __name__ == '__main__':
    app.run()

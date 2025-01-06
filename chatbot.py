import random
import json
import pickle
import numpy as np

import nltk
from nltk.stem import WordNetLemmatizer

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

import tensorflow
load_model = tensorflow.keras.models.load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

intent_model = load_model('chatbot_model.keras')

#initialize ollama model
ollama_model = OllamaLLM(model="llama3.2")

template = '''
You are a legal chatbot specializing in providing legal information for users in {state}. 

Guidelines:
1. Provide concise, focused answers to the user's questions.
2. If appropriate, ask a follow-up question to gather more information or guide the user to the next step.
3. Avoid providing all possible details at once—stick to the specific query and offer follow-ups if needed.

Here is the conversation history: {context}

Question: {question}

Answer:
'''

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | ollama_model #chains the two operations, passes prompt to the model

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence) #token the sentence
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words] #lemmatize the tokenized sentence
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence, context):
    combined_input = f"{context}{sentence}".strip()
    bow = bag_of_words(combined_input)
    res = intent_model.predict(np.array([bow])) #array of probabilities for each class (probability that it belongs to that intent)
    res = res[0]
    ERROR_THRESHOLD = 0.25 #if the probability is less than 25% we won't take it in
    #CONTEXT_BIAS = 0.2 #boosting confidence for intents that match the context

    result = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    result.sort(key= lambda x: x[1], reverse=True) #sort by probability in reverse order (highest first)
    return_list = []
    for r in result:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})

    # if context:
    #     for intent in return_list:
    #         if intent['intent'] == context:
    #             intent['probability'] = str(float(intent['probability']) + CONTEXT_BIAS)
    
    return_list.sort(key=lambda x: float(x['probability']), reverse=True)
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent'] #picking the intent with the highest probability
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag: #find the appropriate intent from the list of intents and choose a random response
            result = random.choice(i['response']) 
            break
    return result

def summarize_context(context):
    try:
        summary_template = '''
        Summarize the following conversation history concisely: 

        {context}

        Summary:
        '''

        summary_prompt = ChatPromptTemplate.from_template(summary_template)
        summary_chain = summary_prompt | ollama_model
        result = summary_chain.invoke({"context":context})
        return result.strip()
    except Exception as e:
        print("Error in summarizing the context", e)
        return("Previous conversation history unavailable")

def context_update(context, user_input, result, max_turns = 6):
    context += f"\nUser: {user_input} \nAI: {result}"
    context_lines = context.split("\n")
    if len(context_lines) > max_turns * 2: #each turn has two lines
        older_context_lines = context_lines[:-(max_turns*2)]
        recent_context_lines = context_lines[-(max_turns*2):]

        older_context = "\n".join(older_context_lines) #puts this back into one string
        summary = summarize_context(older_context)

        context = f"Summary of previous conversation: {summary}" + "\n".join(recent_context_lines)

    return context;

def ollama_query(context, user_input, state):
    try: 
        result = chain.invoke({"context":context, "question": user_input, "state": state})
        context = context_update(context, user_input, result)
        return context, result
    except Exception as e:
        print("Error interacting with the Ollama model: ", e)
        return context, "Sorry, I could not process your request"


def handle_conversation(user_input, context, state, in_ollama_mode, current_context):
    print("Welcome to LegallyBot!")
    #state = input("Please enter your state (e.g., New Jersey): ").strip()
    print("What are your legal concerns?")
    BASIC_INTENTS = ['greetings', 'goodbye', 'thanks', 'ask_for_name']

    
    result = None
    ints = None
    #user_input = input("You: " ).strip()
    
    #debugging
    print(f"DEBUG: Predicted intents: {ints}")  # Debugging
    print(f"DEBUG: User input: {user_input}")


    # if not user_input:
    #     use_input = input("Sorry, I didn't catch that. You: ")

    '''
        # need to check the current context of the ollama by putting it into predict classes, 
        # and if the new context is different from the current context at any point, 
        # and if the threshold is under 0.9 (i.e., the intent is not in my list of intents
        or low confidence)
        # need to stay in ollama mode
        #
        # otherwise send it to my model
    '''
    
    if in_ollama_mode:
        print("DEBUG: conversation in ollama mode")
        context, result = ollama_query(context, user_input, state)
        try:
            ints = predict_class(user_input, current_context) #Predict the intent of the user's message
            print(f"DEBUG: Predicted intents in ollama mode: {ints}")  # Debugging
        except Exception as e:
            print(f"Error predicting intent in ollama mode: {e}")
            ints = []  # Set `ints` to an empty list if prediction fails


        if ints and float(ints[0]['probability']) > 0.9 and ints[0]['intent'] in BASIC_INTENTS:
            print(f"DEBUG: Basic intent, exiting ollama mode: {result}")
            in_ollama_mode = False
            result = get_response(ints, intents) #pass in intents and probabilities to get response
            context = context_update(context, user_input, result)
            
        else:
            print("DEBUG: Staying in Ollama mode")
            context, result = ollama_query(context, user_input, state)

    else:
        try:
            ints = predict_class(user_input, current_context) #Predict the intent of the user's message
            print(f"DEBUG: Predicted intents: {ints}")  # Debugging
        except Exception as e:
            print(f"Error predicting intent: {e}")
            ints = []  # Set `ints` to an empty list if prediction fails
    
        if len(ints) > 1 and (float(ints[0]['probability']) - float(ints[1]['probability'])) < 0.1:
                print("DEBUG: Requesting clarification")
                context, result = ollama_query(context, user_input, state)
                in_ollama_mode = True

        #use home-made model if the intent with the highest probability has a probability higher than confidence thresholf of 0.8
        #high confidence
        elif ints and float(ints[0]['probability']) > 0.9: 
            result = get_response(ints, intents) #pass in intents and probabilities to get response
            print(f"DEBUG: Intent-based response: {result}")
            context = context_update(context, user_input, result)
            current_context = ints[0]['intent']
        
        #low confidence
        else: 
            print("DEBUG: Falling back to Ollama (no intent detected)")
            context, result = ollama_query(context, user_input, state)
            in_ollama_mode = True
    
    if result is None:
        result = "I'm sorry, I couldn't understand your request. Could you please rephrase?"
        print("DEBUG: Default fallback response triggered")

    #print("LegallyBot: ", result)

    #if user put a goodbye/quit message or ollama generated a bye response
    if ints and ints[0]['intent'] == "goodbye" and float(ints[0]['probability']) > 0.95:
        return "Goodbye!", in_ollama_mode, context, current_context
    
    return result, in_ollama_mode, context, current_context
    

# try:
#     handle_conversation()
# except Exception as e:
#     print("An error has occured: ", e)
#     with open("error_log.txt", "a") as log_file:
#             log_file.write(f"Error: {e}\n")
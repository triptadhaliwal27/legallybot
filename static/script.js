//retrieves the relevant div by ID
const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

//add user messages to chat window (dynamically adds divs for message)
function addMessage(sender, text) {
    const bubble = document.createElement('div');
    bubble.classList.add('chat-bubble', sender); //add css classes styling the bubble for sender
    bubble.textContent = text;
    chatWindow.appendChild(bubble); //adds bubble to the chat window
    chatWindow.scrollTop = chatWindow.scrollHeight; //scrolls to bottom of chat window
}

//function to send messages
async function sendMessage() {
    const message = userInput.value().trim(); //get user input
    if (!message) return;

    addMessage('user', message); //add message to the chat window
    userInput.value(''); //clears input box

    const payload = {
        message: message,
        state: state || ""
    };

    try {
        //make a HTTP POST request to /chat endpoint
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' //signifies that the request body contains json data
            },
            body: JSON.stringify(payload)
        })

        const data = await response.json(); //awaits json to return response

        //add the bot's response
        if (data.response) {
            addMessage('bot', data.response);
        }
        else if (data.error) {
            addMessage('bot', `Error: ${data.error}`);
        }
    }
    catch (error) {
        console.error('Error communicating with backend:', error);
        addMessage('bot', 'An error occurred. Please try again later.');

    }


sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

}

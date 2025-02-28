# Legal Chatbot - AI-Powered Legal Assistance

## Overview
This project is an AI-driven legal chatbot designed to provide users with preliminary legal information tailored to their jurisdiction. By leveraging both a custom-trained machine learning model and a locally deployed Large Language Model (LLM), the chatbot can answer a wide range of legal inquiries with enhanced accuracy and scalability.

## Problem Statement
Access to legal information can often be expensive, time-consuming, and complex. Many individuals seek preliminary legal guidance before consulting an attorney, but reliable and jurisdiction-specific legal resources are not always readily available. This chatbot bridges that gap by offering jurisdiction-based legal insights in an accessible and private manner. 

## Key Features
- **Custom Machine Learning Model**: Designed, built, and trained a proprietary AI model to classify and respond to common legal queries.
- **Local LLM Integration (Ollama 3.2)**: Expanded chatbot capabilities using a local Large Language Model, allowing for more sophisticated legal responses and scalability.
- **Jurisdiction-Specific Legal Information**: The chatbot tailors responses based on the user’s state to provide accurate legal guidance.
- **Full-Stack Implementation**:
  - **Backend**: Python-based backend handling model inference, training, and API endpoints.
  - **Frontend**: Built with JavaScript, HTML, and CSS for an interactive user experience.
- **Privacy-Focused Design**: Running a local model ensures that sensitive legal inquiries remain private, avoiding the risks associated with cloud-based AI services.

## Installation & Setup
### Prerequisites
Ensure you have the following installed on your machine:
- Python 3.8+
- Flask
- TensorFlow
- NLTK
- NumPy
- Requests
- Ollama 3.2 (Required for local LLM integration)

### Installing Ollama 3.2
Ollama 3.2 is required for local LLM integration but must be installed separately from this project.

1. Visit the [Ollama website](https://ollama.ai) and follow their installation instructions for your operating system.
2. Once installed, ensure Ollama is available on your system; the chatbot will automatically start the service when needed.

### Setting Up the Project
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/legal-chatbot.git
   cd legal-chatbot
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Train the custom model (optional, if you want to retrain):
   ```sh
   python3 training.py
   ```
4. Start the chatbot server:
   ```sh
   python3 app.py
   ```

## Usage
1. Open your web browser and navigate to `http://localhost:5000`.
2. Enter your state when prompted to receive jurisdiction-specific responses.
3. Ask legal questions, and the chatbot will provide relevant answers.

## Impact
This chatbot enhances accessibility to legal information by providing:
- **Scalable Legal Guidance**: Users receive jurisdiction-specific responses without needing a lawyer for basic inquiries.
- **Enhanced Privacy**: Running a local model eliminates concerns about data security when asking legal questions.
- **AI-Powered Accuracy**: The combination of a custom-trained model and an LLM ensures a balance of precision and scalability.

## Future Improvements
- Expanding jurisdiction-specific training data for more refined responses.
- Implementing real-time legal updates based on changes in state laws.
- Enhancing UI/UX for a more seamless user experience.

## Contributors
- Tripta Dhaliwal - Developer

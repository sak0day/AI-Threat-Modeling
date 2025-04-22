# 🔐 STRIDE Threat Modeling App

This is a Streamlit-based web application that allows users to upload a PDF document (e.g., PRD or system design) and optionally provide a GitHub repository URL. The app uses Google Gemini's generative AI capabilities to analyze the provided inputs and generate a comprehensive STRIDE-based threat model.

## Features

- **PDF Analysis**: Upload a PDF document, and the app extracts text and analyzes it for threat modeling.
- **GitHub Repository Integration**: Optionally provide a GitHub repository URL (public or private) to include code context in the threat model.
- **STRIDE Framework**: Generates a threat model using the STRIDE methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
- **PASTA Framework**: Optionally includes a PASTA (Process for Attack Simulation and Threat Analysis) threat model.
- **Downloadable Report**: Download the generated threat model as a text file.

## Prerequisites

1. **Python**: Ensure Python 3.8 or higher is installed.
2. **Dependencies**: Install the required Python packages listed in the `requirements.txt` file.
3. **Google Gemini API Key**: Add your Gemini API key to a `.env` file in the root directory:

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/stride-threat-modeling.git
cd stride-threat-modeling

2. Install dependencies:
   pip install -r requirements.txt
3. Create a .env file and add your Gemini API key:
   echo 'GEMINI_API_KEY="your_api_key_here"' > .env

## Usage
1. Run the app:
   streamlit run {filename}.py

2. Open the app in your browser at http://localhost:8501.

3. Upload a PDF document and optionally provide a GitHub repository URL and Personal Access Token (for private repos).

4. View the generated STRIDE threat model report in the app or download it as a text file.





# Adaptive Learning Model

This project consists of a backend (Python) for an adaptive learning model and a frontend (HTML, CSS, JavaScript) for user interaction.

## Frontend

The frontend is a simple webpage that allows users to enter a User ID and trigger a "Generate" action.

### How to run the Frontend

To view the frontend and see changes live, you can start a local web server:

1.  Open your terminal or command prompt.
2.  Navigate to the `Frontend` directory: `cd D:\Adaptive_Learning_model_V2\Frontend`
3.  Run a simple Python web server: `python -m http.server 8000 --bind 127.0.0.1`
4.  Open your web browser and go to `http://127.0.0.1:8000`

Alternatively, you can still open the `index.html` file directly in your browser by double-clicking it.

## Backend

The backend contains the core logic for the adaptive learning model, including data loading, roadmap generation, and test generation.

### How to run the Backend

1.  Open a new terminal or command prompt.
2.  Navigate to the `Backend/Model` directory: `cd D:\Adaptive_Learning_model_V2\Backend\Model`
3.  Install the required Python packages: `pip install -r requirements.txt` (if you haven't already)
4.  Start the Flask server: `python server.py`

### Key Backend Components:

*   `Backend/Model/Roadmap_generator.py`: Generates personalized learning roadmaps.
*   `Backend/Model/Topicwise_Test_generator.py`: Generates topic-wise tests (questionnaires).
*   `Backend/Model/Adaptive_Model.py`: Analyzes test scores and adapts the learning roadmap.

More detailed instructions for running and interacting with the backend will be added as development progresses.

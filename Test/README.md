
# Synthetic Dataset for Adaptive Learning Framework Evaluation

This document provides an overview of the synthetic dataset generated to evaluate the adaptive learning framework. It explains how to access the data, interpret the results, and regenerate the dataset.

## Introduction

The synthetic dataset simulates the learning journeys of 10 users with different personas over 20 sessions. Two sets of data were generated:

*   **Adaptive:** The simulation with the adaptive learning logic enabled.
*   **Non-Adaptive:** The simulation with the adaptive learning logic disabled.

This allows for a comparative analysis of the impact of the adaptive framework on learning outcomes, engagement, and other key metrics.

## File Descriptions

The following files and directories are located in the `Test` directory:

*   `synthetic_dataset_adaptive.csv`: The full dataset for the adaptive simulation in CSV format.
*   `synthetic_dataset_no_adaptive.csv`: The full dataset for the non-adaptive simulation in CSV format.
*   `synthetic_data/`: A directory containing the raw JSON data for each user and each simulation run.
*   `generate_synthetic_data.py`: The Python script used to generate the synthetic data.
*   `analyze_data.py`: The Python script used to analyze the data and generate the summary table and narrative.
*   `README.md`: This file.

## Data Dictionary

The CSV files contain the following columns:

| Column | Description |
|---|---|
| user_id | Unique identifier for the user. |
| persona | The user's learning persona (e.g., High Achiever, Struggling Learner). |
| session_id | The session number (1-20). |
| subtopic_id | The identifier for the subtopic covered in the session. |
| difficulty_level | The difficulty of the subtopic (0.3-0.9). |
| adaptations_triggered | Whether an adaptation was triggered in the session (1 or 0). |
| feedback_quality | The quality of the feedback provided in the session (0.5-0.9). |
| learning_rate | The change in accuracy from the previous session. |
| content_type_preference | The user's preferred content type (text or visual). |
| score | The user's accuracy in the session's test (0-1). |
| engagement_level | The user's engagement level in the session (0.1-1.0). |
| motivation | The user's motivation level in the session (0.1-1.5). |
| cognitive_load | The cognitive load experienced by the user in the session. |
| reaction_to_feedback | The user's reaction to the feedback provided. |
| growth_index | The user's performance growth in the session. |
| retention_rate | The user's retention of knowledge from the previous session. |
| adaptation_efficiency | The efficiency of the adaptation in improving the learning rate. |
| stability_score | The standard deviation of the user's scores over time. |
| adaptation_status | The status of the adaptation (needs_review, mastered, or none). |

## How to Access the Data

The `synthetic_dataset_adaptive.csv` and `synthetic_dataset_no_adaptive.csv` files can be opened with any spreadsheet program (e.g., Microsoft Excel, Google Sheets) or a text editor. They can also be loaded into a pandas DataFrame in Python for more advanced analysis.

## Interpreting the Results

The `analyze_data.py` script prints a comparative summary table and a research narrative to the console. 

*   **Comparative Summary Table:** This table shows the mean values for key metrics for each learner persona, comparing the adaptive and non-adaptive simulations side-by-side. This allows for a quick comparison of the overall performance and engagement of each group under the two conditions.

*   **Comparative Research Narrative:** This narrative provides a detailed analysis of the results, interpreting the impact of the adaptive logic on different learner types and discussing the implications for the design of adaptive learning systems.

## How to Regenerate the Data

To regenerate the synthetic dataset and the analysis, you can run the following Python scripts from the command line in the root directory of the project:

1.  **Generate the data:**
    ```
    python D:\Adaptive_Learning_model_V2\Test\generate_synthetic_data.py
    ```

2.  **Analyze the data:**
    ```
    python D:\Adaptive_Learning_model_V2\Test\analyze_data.py
    ```

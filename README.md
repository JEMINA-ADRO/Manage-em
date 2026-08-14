# Manage 'em

**Developed by JEMINA J (10607)**

## Overview

The Smart Task Management System is a Streamlit-based task management application that allows users to create, view, edit, delete, search, filter, sort, and track tasks.

The application uses SQLite for persistent task storage and integrates a locally running Qwen3-4B language model for AI-assisted task management.

## Features

* Add new tasks
* Edit existing tasks
* Delete tasks
* Mark tasks as Pending or Completed
* Set task deadlines with date and time
* Assign Low, Medium, or High priority
* Search tasks by name
* Filter tasks by deadline, priority, and status
* Sort tasks by Task ID, name, deadline, priority, and status
* Persistent SQLite database storage
* Dashboard showing:

  * Total tasks
  * Pending tasks
  * Completed tasks
  * High-priority pending tasks
  * Task completion progress

## AI Features

### 1\. AI Task Summary

The application uses the Qwen3-4B language model to analyze the current task list.

The AI:

* Separates pending and completed tasks
* Identifies the most urgent pending task
* Considers task priority and deadline
* Recommends an order in which pending tasks should be completed
* Generates a natural-language task summary

Completed tasks are excluded from the recommended work order.

### 2\. AI Quick Add

Tasks can also be created using natural language.

Example:

```text
Finish the report tomorrow at 6 PM high priority
```

The AI converts this into structured task information such as:

```text
Task: Finish the report
Deadline: Resolved date at 18:00
Priority: High
Status: Pending
```

The system also supports relative and calendar-based time expressions such as:

```text
Call the client in 45 minutes
Submit the document in 2 days at 10 AM
Attend the meeting next Monday at 10 AM
```

The language model interprets the user's instruction, while Python performs exact duration-based datetime calculations.

If no deadline is provided, the application assigns a default deadline of one hour from the current time.

## Technology Stack

* Python
* Streamlit
* SQLite
* PyTorch
* Hugging Face Transformers
* Qwen3-4B

## Project Structure

```text
App_Service/
│
├── app.py
├── ai_service.py
├── test_ai.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    └── config.toml
```

### Files

**app.py**  
Contains the Streamlit user interface, SQLite database operations, task management functions, filtering, sorting, dashboard, and integration of AI features.

**ai\_service.py**  
Contains AI model loading, task analysis, task summarization, and natural-language task parsing functions.

**test\_ai.py**  
Contains test cases used to verify AI task interpretation and task analysis.

**requirements.txt**  
Contains the Python package dependencies required to run the project.

**.streamlit/config.toml**  
Contains Streamlit project configuration.

## Database

The application uses SQLite.

The `tasks` table contains:

|Field|Description|
|-|-|
|id|Unique task identifier|
|name|Task description|
|deadline|Task deadline|
|priority|Low, Medium, or High|
|status|Pending or Completed|

The database is created automatically when the application runs for the first time.

## Installation

### 1\. Clone the repository

```bash
git clone <repository-url>
cd App\\\_Service
```

### 2\. Create a virtual environment

```bash
python -m venv venv
```

### 3\. Activate the virtual environment

Windows:

```bash
venv\\\\Scripts\\\\activate
```

### 4\. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Running the Application

Run:

```bash
python -m streamlit run app.py
```

The application will open in the web browser.

## AI Model

The application uses:

```text
Qwen/Qwen3-4B
```

through Hugging Face Transformers.

The model runs locally and does not require a paid AI API.

The model files are not stored in this GitHub repository. They are downloaded by Hugging Face when required and stored in the local Hugging Face cache.

The first AI operation may therefore take longer while the model is downloaded or loaded into memory.

Streamlit uses `st.cache\\\_resource` so the loaded model can be reused during the application session.

## Application Architecture

```text
                         User
                           │
                           ▼
                  ┌─────────────────┐
                  │  Streamlit UI   │
                  │     app.py      │
                  └────────┬────────┘
                           │
              ┌────────────┼─────────────┐
              │            │             │
              ▼            ▼             ▼
          Task CRUD     Dashboard    AI Features
              │                          │
              ▼                          ▼
        ┌───────────┐              ┌──────────────┐
        │  SQLite   │              │ ai\\\_service.py│
        │ tasks.db  │              └───────┬──────┘
        └───────────┘                      │
                                           ▼
                                    ┌─────────────┐
                                    │  Qwen3-4B   │
                                    │ Local Model │
                                    └─────────────┘
```

## AI Quick Add Flow

```text
Natural-language task
        │
        ▼
     Qwen3-4B
        │
        ▼
Structured task information
        │
        ├── Task name
        ├── Priority
        ├── Status
        └── Deadline information
                │
                ▼
       Python datetime handling
                │
                ▼
          SQLite database
```

## Testing

The application was tested for:

* Task creation
* Task editing
* Task deletion
* Status changes
* Database persistence
* Searching
* Filtering
* Sorting
* Dashboard calculations
* Completion percentage
* AI task summarization
* AI priority recommendations
* Natural-language task creation
* Relative deadlines
* Weekday-based deadlines
* Tasks without explicitly specified deadlines

## Limitations

* The Qwen3-4B model requires substantial memory compared with smaller language models.
* Initial model download and loading may take time.
* The application currently uses a local SQLite database.
* The current version is designed primarily for a single-user task management workflow.

## Future Improvements

Possible future improvements include:

* User authentication
* Task categories and tags
* Email or reminder notifications
* Multi-user database support
* Cloud-hosted AI inference
* Additional dashboard visualizations

## AI Usage Disclosure



Generative AI tools were used during the development of this project.

ChatGPT was used as a development assistant for:

* Explaining Streamlit, SQLite, and AI integration concepts
* Debugging implementation issues
* Reviewing and refining code
* Designing test cases
* Assisting with project documentation



All AI-assisted content was modified, reviewed, and validated by the author.


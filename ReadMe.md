# Email rules



## Requirements

- Python 3.9 or higher
- Virtual Environment
- **Google Account**: You'll need a Google account to access the Gmail API.
- **Google Cloud Platform (GCP) Account**: You need to have a GCP account to create a project and enable the Gmail API.



## Installation

1. **Clone the repository:**

   ```bash
   git clone git@github.com:sarathak/emailrules.git
1. Navigate to the project directory:

    ````bash
    cd <project_directory>

1. Create a virtual environment:

    ````bash
    python3 -m venv venv
1. Activate the virtual environment:

    ```bash
    source venv/bin/activate
1. Install project dependencies:

    ```bash
    pip install -r requirements.txt


## Setup Instructions

Follow these steps to set up Gmail API:

### 1. Create a Project on Google Cloud Platform (GCP)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project selector dropdown and create a new project.
3. Give your project a name and click **Create**.

### 2. Enable the Gmail API

1. In the Google Cloud Console, navigate to the **APIs & Services > Library** page.
2. Search for "Gmail API" and click on it.
3. Click the **Enable** button.

### 3. Set up OAuth 2.0 Credentials

1. In the Google Cloud Console, navigate to the **APIs & Services > Credentials** page.
2. Click on **Create Credentials > OAuth client ID**.
3. Select "Desktop app" as the application type.
4. Give your OAuth client a name.
5. Click **Create**.
6. After creation, click on the OAuth client you just created from the list.
7. Download credential file and putin to project directory as credentials.json

## Run application

### 1. Fetch emails from api and store in database:
   
   ```bash
   python fetch_emails.py
````   
   
   
### 2. Execute rules
1. Create rules as `rules.json` in project directory:
   ```json
   [
      {
         "description": "Rule 1",
         "conditions": "all",
         "properties": [
            {
               "field": "from",
               "predicate": "contains",
               "value": "info@join.netflix.com"
            }
         ],
         "actions": [
            {
               "operation": "move",
               "destination": "bin"
            }
         ]
      }
   ]
   
   ```   
2. Execute script file
   ```bash
   python execute_rules.py
   ```

## Run Unit tests
   ```bash
   python tests.py
   
   ```
   
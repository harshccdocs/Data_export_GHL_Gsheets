# Data_export_GHL_Gsheets
# GHL Data Cleaner and Cross-Referencer

This Python script helps:
- Clean phone numbers from a GHL CSV export.
- Upload cleaned data to Google Sheets.
- Cross-reference appointments with GHL data.
- Mark matched and unmatched leads.

---

## Features
- Cleans up phone numbers (`+1` and non-digits removed).
- Uploads cleaned opportunities data to Google Sheets.
- Cross-references data from appointment sheets and GHL exports.
- Marks each lead as `Matched` or `Unmatched`.

---

## Setup

1. Clone this repository:
    ```bash
    git clone https://github.com/your-repo-name.git
    cd your-repo-name
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set your Google API credentials:
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
    ```

---

## Usage

Run the script:
```bash
python your_script_name.py

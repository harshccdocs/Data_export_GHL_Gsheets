import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import os

# Google Sheets authentication
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    json_keyfile = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')  # Now loaded from environment variable
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    return client

# Clean phone numbers (remove '1' or '+1' from the beginning)
def clean_phone_numbers(data, column_name):
    def clean_phone(x):
        if pd.isna(x):
            return x
        cleaned = ''.join(filter(str.isdigit, str(x)))
        if cleaned.startswith('1'):
            cleaned = cleaned[1:]
        return cleaned

    data[column_name] = data[column_name].apply(clean_phone)
    return data

# Read and clean the GHL export data
def clean_ghl_data(file_path, columns_to_keep):
    data = pd.read_csv(file_path)
    data = data[columns_to_keep]
    data = clean_phone_numbers(data, 'phone')
    data = data.fillna('')
    return data

# Upload cleaned data to Google Sheets
def upload_to_google_sheets(data, spreadsheet_id, worksheet_name):
    client = authenticate_google_sheets()
    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
    sheet.clear()
    sheet.update([data.columns.values.tolist()] + data.values.tolist())
    print(f"Data uploaded to {worksheet_name} successfully!")

# Cross-reference two sheets
def cross_reference_data(spreadsheet_id):
    client = authenticate_google_sheets()
    sheet = client.open_by_key(spreadsheet_id)

    def get_worksheet_by_name(sheet, name):
        for ws in sheet.worksheets():
            if ws.title.lower() == name.lower():
                return ws
        return None

    appointment_sheet = get_worksheet_by_name(sheet, 'Appointment sheet')
    if not appointment_sheet:
        appointment_sheet = sheet.add_worksheet(title='Appointment sheet', rows="100", cols="20")

    ghl_export_sheet = get_worksheet_by_name(sheet, 'GHL export')
    if not ghl_export_sheet:
        ghl_export_sheet = sheet.add_worksheet(title='GHL export', rows="100", cols="20")

    appointment_data = pd.DataFrame(appointment_sheet.get_all_records())
    ghl_data = pd.DataFrame(ghl_export_sheet.get_all_records())

    print("\nAppointment Sheet columns:", appointment_data.columns.tolist())
    print("GHL Export columns:", ghl_data.columns.tolist())

    if appointment_data.empty or ghl_data.empty:
        print("Warning: One or both sheets are empty. Please add data to both sheets before cross-referencing.")
        return

    appointment_data = clean_phone_numbers(appointment_data, 'Phone')
    ghl_data = clean_phone_numbers(ghl_data, 'phone')

    cross_referenced_data = pd.merge(appointment_data, ghl_data[['phone', 'Contact Name']],
                                     left_on='Phone', right_on='phone', how='left', suffixes=('_appointment', '_ghl'))

    cross_reference_sheet = get_worksheet_by_name(sheet, 'Cross-reference results')
    if not cross_reference_sheet:
        cross_reference_sheet = sheet.add_worksheet(title='Cross-reference results', rows="100", cols="20")
    cross_reference_sheet.clear()

    cross_referenced_data['Match_Status'] = cross_referenced_data.apply(
        lambda row: 'Matched' if row.get('Leads Name') == row.get('Contact Name') and row.get('Phone') == row.get('phone')
        else 'Unmatched', axis=1)

    output_df = cross_referenced_data[['Agent Name', 'Leads Name', 'Phone', 'Contact Name', 'phone', 'Match_Status']]
    output_df = output_df.fillna('')

    cross_reference_sheet.update([output_df.columns.values.tolist()] + output_df.values.tolist())
    print("Cross-referencing completed and results uploaded.")

# Main function
def main():
    file_path = input("Enter the path to the new GHL export CSV file: ")
    spreadsheet_id = input("Enter your Google Spreadsheet ID: ")  # Now dynamic input instead hardcoded
    worksheet_name_opportunities = 'GHL export'

    columns_to_keep = ['Opportunity Name', 'Contact Name', 'phone', 'email', 'stage', 'source',
                       'assigned', 'Followers', 'Notes', 'tags', 'status', 'Disposition', 'Setter']

    cleaned_data = clean_ghl_data(file_path, columns_to_keep)
    upload_to_google_sheets(cleaned_data, spreadsheet_id, worksheet_name_opportunities)
    cross_reference_data(spreadsheet_id)

if __name__ == "__main__":
    main()

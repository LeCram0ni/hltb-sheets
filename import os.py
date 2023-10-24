from time import sleep
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1c7ccXCJUaw7idXht-UOJkomjpd-SGYrxx8g6gLuRNSw"
xpath = "/html/body/div[1]/div/main/div/div/div[5]/ul/li[1]/div/div[2]/div/div"
hltb = "https://howlongtobeat.com/?q="

def main():
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()
        resultssheet = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="1!A2:A7").execute()
        values = resultssheet.get("values", [])

        for index, row in enumerate(values,2):  # Start at row 2
           # print(row)
            title = row[0]
            url = hltb+title

            chrome_options = Options()
            chrome_options.add_argument("--headless")

            driver = Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
            driver.get(url)
            #wait for search query
            sleep(1.5)

            results = driver.find_elements(By.XPATH, xpath)

            for result in results:
                
                pattern = re.compile(r'\d{1,4}.?')
                matches = pattern.finditer(result.text)

                times=[]

                for match in matches:
                    times.append(match[0].replace(' ',''))
                    print(times)
           
                value = times[0]

                value2 = times[1] if len(times) > 1 else ''

                value3 = times[2] if len(times) > 2 else ''

                if not value2:
                    value2 = ""
                if not value3:
                    value3 = ""

                # try:
                #     value = times[0]
                # except IndexError:
                #     value = times[0]

                # try:
                #     value2 = times[1]
                # except IndexError:
                #     value2 = ''

                # try:
                #     value3 = times[2]
                # except IndexError:
                #     value3 = ''
                
                range_start = f"B{index}"  # Update row dynamically
                range_end = f"D{index}"    # Update row dynamically

                values_service = sheets.values()

                request = values_service.update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{range_start}:{range_end}",  # Update the range to the new row
                    valueInputOption="RAW",
                    body={"values": [[value,value2,value3]]}
                )
                
                response = request.execute()

                # request = values_service.update(
                #         spreadsheetId=SPREADSHEET_ID,
                #         range=f"1!C"+str(i)+":C"+str(i),
                #         valueInputOption="RAW",
                #         body={"values": [[value2]]}
                # )
                # response = request.execute()

                # request = values_service.update(
                #         spreadsheetId=SPREADSHEET_ID,
                #         range=f"1!D"+str(i)+":D"+str(i),  # Adjust the sheet name and cell range as needed
                #         valueInputOption="RAW",
                #         body={"values": [[value3]]}
                # )
                # response = request.execute()   


    except HttpError as error:
        print(error)
    
if __name__ == "__main__":
    main()
    #'https://script.google.com/macros/s/AKfycbzwWH9c27i0FwsNTf6rgaffK8KuYrk5zyfVa967atmbIm_wsUfaPQequRi6MSZiPQgn-w/exec?text=testest'
    
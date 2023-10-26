import re
import os
import functools 
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

SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1c7ccXCJUaw7idXht-UOJkomjpd-SGYrxx8g6gLuRNSw"

xpath_hltb = "/html/body/div[1]/div/main/div/div/div[5]/ul/li[1]/div/div[2]/*[not(self::h3)]" #not game title because of year numbers
xpath_ta = "/html/body/form/div[2]/div[2]/main/div[3]/div[2]/div/table/tbody/tr/td[5]"

hltb = "https://howlongtobeat.com/?q="
ta = "https://www.trueachievements.com/gamer/marcipan/games"

# row 1 : Name , Main, Main+Extra, Completionist
# row 2 : first title

start = str(2) #start row
end = str(100) #end row

def main():
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPE)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPE)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()
        resultssheet = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="1!A"+start+":B"+end).execute()
        values = resultssheet.get("values", [])
    
        for index, row in enumerate(values,int(start)):  # Start at row start
            
            title = row[0]

            if len(row)<2: # if no time has been found / if only title has been found 
                
                if(index<10):
                    print("# "+str(index)+" TIME? "+title)
                else:
                    print("#"+str(index)+" TIME? "+title)

                url = hltb+title

                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

                driver = Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
                driver.get(url)
                
                sleep(1.5) #wait for search query on hltb

                results = driver.find_elements(By.XPATH, xpath_hltb)

                for result in results:

                #  print("result")
                #  print(result.text)
                #  print("-------------")
                    
                    pattern = re.compile(r'\d{1,4}.?')
                    matches = pattern.finditer(result.text)

                    times=[]

                    # times: all found times
                    # times3: all found times + fill up empty, always length 3

                    for match in matches:
                        times.append(match[0].replace('½','.5').replace(' ',''))

                    num_elements = len(times[:3])           # Use the first 3 elements
                    times3 = times[:num_elements]           # Create the array with up to 3 entries
                    times3 += ["0"] * (3 - len(times3))     # Fill the rest with "empty" to have exactly 3 elements
                
                    value = times3[0]
                    value2 = times3[1]
                    value3 = times3[2]

                    times = []
                    times3 = []
                        
                    range_start = f"B{index}"  # Update row dynamically
                    range_end = f"D{index}"    # Update row dynamically

                    values_service = sheets.values()

                    request = values_service.update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"{range_start}:{range_end}",  # Update the range to the new row
                        valueInputOption="RAW",
                        body={"values": [[float(value),float(value2),float(value3)]]}
                    )
                        
                    response = request.execute()

            else:
                if(index<10):
                    print("# "+str(index)+" SKIP: "+title)
                else:
                    print("#"+str(index)+" SKIP: "+title)

        #driver.quit()

    except HttpError as error:
        print(error)
    
if __name__ == "__main__":
    main()
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
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC

SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "SPREADSHEETID"

xpath_hltb = "/html/body/div[1]/div/main/div/div/div[5]/ul/li[1]/div/div[2]/*[not(self::h3)]" # exclude game title because of year numbers
xpath_ta = "/html/body/form/div[2]/div[2]/main/div[3]/div[2]/div/table/tbody/tr/td[5]"


#show ALL games: AJAXList.Buttons('oGamerGamesListA')
#trigger javascript


hltb = "https://howlongtobeat.com/?q="
ta = "https://www.trueachievements.com/gamer/USERNAME/games"

# row 1 : Name , Main, Main+Extra, Completionist
# row 2 : first title

start = str(2) #start row
end = str(2) #end row

updateZero = False

if(updateZero):
    updateZero = "0"

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
        resultssheet = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="1!A"+start+":E"+end).execute()
        values = resultssheet.get("values", [])
    

# R O W

        for index, row in enumerate(values,int(start)):  # Start at row start

            title = row[0]
            #edit = ""

            if len(row[0])==0:
                break

            # if no time has been found / if only title has been found OR if times = 0 if updatezero is true
            elif row[1] == "" or row[1] == updateZero: 

                #edit = "time"

                if(index<10):
                    print("# "+str(index)+" TIME? "+title)
                else:
                    print("#"+str(index)+" TIME? "+title)

                url = hltb+title

                chrome_options = Options()
                #chrome_options.add_argument("--headless")
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
                
                    t1 = times3[0]
                    t2 = times3[1]
                    t3 = times3[2]

                    times = []
                    times3 = []
                        
                    range_start = f"B{index}" 
                    range_end = f"D{index}"    

                    values_service = sheets.values()

                    request = values_service.update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"{range_start}:{range_end}",  # Update the range to the new row
                        valueInputOption="RAW",
                        body={"values": [[float(t1),float(t2),float(t3)]]}
                    )
                        
                    response = request.execute()

            # if < 5 in final program
            elif len(row) < 6:

                if(index<10):
                    print("# "+str(index)+" GSCR? "+title)
                else:
                    print("#"+str(index)+" GSCR? "+title)
                
                url = ta

                chrome_options = Options()
                #chrome_options.add_argument("--headless")
                chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

                driver = Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
                driver.get(url)

                print("starting_Driver")
                click_button = driver.find_element(by=By.XPATH, value='//*[@id="oGamerGamesListContent"]/div[1]/ul/li[1]/a')
                #print(click_button.text)
                #sleep(10)
                #cookieButton = driver.find_element(by=By.XPATH, value='/html/body/div/div[2]/div[3]/button[3]')
                #sleep(7)
                cookieButton = driver.find_element(by=By.XPATH, value='//*[@id="notice"]/div[3]/button[3]')

                #sleep(10)
                cookieButton.click()
                click_button.click()


                #js = 'alert("Hello World")'
                #driver.execute_script(js)

                #script = "AJAXList.Buttons('oGamerGamesListA'); " \
                #         "return false;"

                #driver.execute_async_script(script)
                
                sleep(1.5) 

                results = driver.find_elements(By.XPATH, xpath_ta)

                for result in results:

                    print("result")
                    print(result.text)
                    print("-------------")
                    
                    pattern = re.compile(r'\(\d{1,3}\)|\(\d\,\d{3}\)')
                    matches = pattern.finditer(result.text)

                    scores=[]

                    for match in matches:
                        scores.append(match[0].replace('(','').replace(')',''))
                        
                    gs = scores
                    print(scores)
                    scores = []
                        
                    range_start = f"E{index}"  # Update row dynamically
                    range_end = f"E{index}"    # Update row dynamically

                    values_service = sheets.values()

                    request = values_service.update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"{range_start}:{range_end}",  # Update the range to the new row
                        valueInputOption="RAW",
                        body={"values": [[str(gs)]]}
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

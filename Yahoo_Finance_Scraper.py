from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
from datetime import datetime
import pandas as pd
import warnings
import unidecode
warnings.filterwarnings('ignore')

def initialize_bot():

    ## Setting up chrome driver for the bot
    chrome_options  = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    #prefs = {'download.default_directory' : path}
    #chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--log-level=3')
    driver_path = ChromeDriverManager().install()
    chrome_options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(driver_path, options=chrome_options)
    

    return driver

def scrape_stocks(driver, symbol, stamp, path):
    
    wait60 = wait(driver, 30)
    URL = 'https://finance.yahoo.com/'
    driver.get(URL)
    button = wait60.until(EC.presence_of_element_located((By.XPATH, "//input[@id='yfin-usr-qry' and @type='text' and @name='yfin-usr-qry']")))
    button.click()
    button.send_keys(symbol)
    button.send_keys(Keys.ENTER)
    try:
        tabs = wait(driver, 60).until(EC.presence_of_all_elements_located((By.XPATH, '//a[@class="Lh(44px) Ta(c) Bdbw(3px) Bdbs(s) Px(12px) C($linkColor) Bdbc($seperatorColor) D(b) Td(n) selected_Bdbc($linkColor) selected_C($primaryColor) selected_Fw(b) " and @role="tab"]')))
        for tab in tabs:
            if 'Historical Data' in tab.text:
                tab.click()
                break
    except:
        print('Warning: Skipping Invalid Symbol "{}"'.format(symbol))
        return False
    # Manual table extraction
    for i in range(5):
            htmlelement= driver.find_element_by_tag_name('html')
            htmlelement.send_keys(Keys.END)
            time.sleep(1)
    table = wait60.until(EC.presence_of_element_located((By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table')))
    html = table.get_attribute('outerHTML')
    html = unidecode.unidecode(html)
    df = pd.read_html(html)[0]
    nrows = df.shape[0]
    df = df.drop(nrows-1, axis=0)
    filename = '{}_{}.csv'.format(symbol, stamp)
    df.to_csv(path + '\\' + filename, index=False, encoding='UTF-8')
    ###############################################################################
    #wait60.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/section/div[1]/div[2]/span[2]/a"))).click()
    time.sleep(2)

    return True

def update_log(file, message):

    file.write(message)
    file.write('\n')


def clear_screen():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux
    else:
        _ = os.system('clear')

os.system("color")
COLOR = {"HEADER": "\033[95m", "BLUE": "\033[94m", "GREEN": "\033[92m",
            "RED": "\033[91m", "ENDC": "\033[0m", "YELLOW" :'\033[33m'}


if __name__ == '__main__':

    stamp = datetime.now().strftime("%m_%d_%Y_%H_%M")
    path = os.getcwd() + '\\' + 'scraped_data' + '\\' + stamp
    if not os.path.isdir(path):
        os.makedirs(path)
    start_time = time.time()
    driver = initialize_bot()
    clear_screen()
    nfail = 0
    nscraped = 0
    done = False    
    logfile = open(path + '\\' + 'log.txt', 'a', newline='')
    logfile2 = open(path + '\\' + 'log.csv', 'a', newline='')
    logfile2.write('Symbol,Status')
    logfile2.write('\n')
    logfile2.close()
    line = 'Script started in {} on {}.'.format(datetime.now().strftime("%I:%M %p"), datetime.now().strftime("%m/%d/%Y"))
    update_log(logfile, line)
    update_log(logfile, '-'*100)
    df1 = pd.read_csv('stocks.csv')
    nrows = df1.shape[0]
    symbols = df1.iloc[:, 0].values.tolist()
    print('-'*50)
    print('Scraping Stocks Data, Please Wait ...')
    print('-'*50)
    while True:
        try:
            df2 = pd.read_csv(path + '\\' + 'log.csv')
            start = df2.shape[0]
            for i in range(start, nrows):
                # skipping the stock after ten scraping attempts with failure
                if nfail > 10: 
                    nfail = 0
                    print('Skipping symbol number {} ...'.format(i+1))
                    update_log(logfile, '-'*100)
                    line = 'Failed to scrape symbol "{}".'.format(symbols[i])
                    update_log(logfile, line)
                    update_log(logfile, '-'*100)
                    logfile2 = open(path + '\\' + 'log.csv', 'a', newline='')
                    logfile2.write('{}, Failure'.format(symbols[i]))
                    logfile2.write('\n')
                    logfile2.close()
                    continue
                status = scrape_stocks(driver, symbols[i], stamp, path)
                if status:
                    line = 'Symbol "{}" is scraped successfully.'.format(symbols[i])
                    update_log(logfile, line)
                    logfile2 = open(path + '\\' + 'log.csv', 'a', newline='')
                    logfile2.write('{}, Success'.format(symbols[i]))
                    logfile2.write('\n')
                    nscraped += 1
                    nfail = 0
                else:
                    line = 'Failed to scrape symbol "{}".'.format(symbols[i])
                    update_log(logfile, line)
                    logfile2 = open(path + '\\' + 'log.csv', 'a', newline='')
                    logfile2.write('{}, Failure'.format(symbols[i]))
                    logfile2.write('\n')

                logfile2.close()
                
            # renaming files (with download button)
            #time.sleep(5)
            #files = os.listdir(path)
            #for file in files:
            #    if 'log' in file: continue
            #    os.rename(path + '\\' + file, path + '\\' + '{}_{}.csv'.format(file[:-4], stamp))
            done = True
            break
        except:
            print('-'*50)
            print('Failure In Scraping The Data! Retrying ...')
            print('-'*50)
            #exit(1)
            nfail += 1
            driver.quit()
            time.sleep(5)
            driver = initialize_bot()

    if done:
        print('-'*50)
        line = 'Data is scraped successfully! Total scraping time is {:.1f} mins'.format((time.time() - start_time)/60)
        print(line)
        update_log(logfile, '-'*100)
        update_log(logfile, line)
        update_log(logfile, '-'*100)
        print('-'*50)
        line = "{} symbols are scraped of {}".format(nscraped, nrows)
        print(line)
        print('-'*50)
        update_log(logfile, line)
        update_log(logfile, '-'*100)
        logfile.close()
        driver.quit()


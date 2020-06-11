from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
from time import sleep
import argparse
import re
import sys
import random


def init_web_driver(email):
    chromedriver_autoinstaller.install()

    options = webdriver.ChromeOptions()
    options.add_argument('user-data-dir=C:\\Tmp\\pltools\\{0}'.format(email.lower()))
    options.add_argument('--disable-extensions')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-notifications')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('prefs', {'profile.default_content_setting_values.notifications': 2})

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(7)

    driver.get('https://sellercentral.amazon.com/orders-v3/ref=xx_myo_dnav_xx?page=1')
    while len(driver.find_elements_by_css_selector('#myo-search-input')) == 0:
        print('Please login manually to initialize')
        sleep(5)
        continue
    return driver


def get_fba_tracking(driver, email, input, output):
    driver.get('https://sellercentral.amazon.com/orders-v3/search?date-range=last-30&q=SFPL&qt=orderid')
    sleep(3)
    
    f = open(input, 'r')
    w = open(output, 'w')
    gs = open('google-sheet-paste.txt', 'w')
    success = 0
    dict = {'UPSM': 'UPS Mail Innovations'}
    w.write('carrier-code\tcarrier-name\ttracking-number\torder-id\tship-date\n')
    for line in f:
        parts = line.split()
        if len(parts) < 3:
            gs.write('\n')
            continue
        
        confirm_date, fba_order_id, customer_order_id = parts[0].strip(), parts[1].strip(), parts[2].strip()
        try:
            url = f'https://sellercentral.amazon.com/orders-v3/search?page=1&q={fba_order_id}&qt=orderid&date-range=last-30'
            driver.get(url)
            sleep(2)

            anchors = driver.find_elements_by_css_selector('#orders-table tbody > tr > td div.cell-body-title > a')
            if anchors is None or len(anchors) == 0:
                print(f'Cannot find order #{fba_order_id}')
                gs.write(f'{fba_order_id}\t\t\n')
            else:
                fba_order_url = anchors[0].get_attribute('href')
                driver.get(fba_order_url)
                sleep(2)

                ta = driver.find_elements_by_css_selector("a[href*='https://www.swiship.com/track']")
                if ta is None or len(ta) == 0:
                    print(f'Cannot find tracking for oder #{fba_order_id}')
                    gs.write(f'{fba_order_id}\t\t\n')
                else:
                    if len(ta) > 1:
                        print(f'WARNING: {fba_order_id}/{customer_order_id} have multiple tracking numbers! We will use the first one only.')
                    
                    html = driver.find_element_by_id('shipment-tables').get_attribute('innerHTML')
                    carrier = ''.join(re.findall(r'Carrier:.*<br>', html)).replace('Carrier:', '').replace('<br>', '').strip()
                    if carrier in dict.keys():
                        carrier = dict[carrier]

                    tracking_id = ta[0].get_attribute('href').replace('https://www.swiship.com/track?id=', '').replace('&loc=en_US', '')
                    print(f'{fba_order_id}\t{customer_order_id}\t{carrier}\t{tracking_id}\t{confirm_date}T07:00:00Z')
                    gs.write(f'{fba_order_id}\t{carrier}\t{tracking_id}\n')
                    if 'Amazon' in carrier:
                        w.write(f'Other\t{carrier}\t{tracking_id}\t{customer_order_id}\t{confirm_date}T07:00:00Z\n')
                    else:
                        w.write(f'{carrier}\t\t{tracking_id}\t{customer_order_id}\t{confirm_date}T07:00:00Z\n')
        except KeyboardInterrupt:
            print('Bye~')
            break
        except:
            print('Unexpected error occurred:', sys.exc_info()[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--email", type=str, help="Seller account email")
    parser.add_argument("-i", "--input", type=str, default="fba-order-ids.txt", help="Input fba/customer order ids")
    parser.add_argument("-o", "--output", type=str, default="trackings.txt", help="Output tracking files")
    args = parser.parse_args()
    print(args)

    driver = init_web_driver(args.email)
    try:
        get_fba_tracking(driver, args.email, args.input, args.output)
    finally:
        driver.quit()
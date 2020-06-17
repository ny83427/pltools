import argparse
import re
import sys
from time import sleep

import seller_central_base


def get_fba_tracking(driver, input, output):
    driver.get('https://sellercentral.amazon.com/orders-v3/search?date-range=last-30&q=SFPL&qt=orderid')
    sleep(3)

    f = open(input, 'r')
    w = open(output, 'w')
    gs = open('google-sheet-paste.txt', 'w')
    carrier_names = {'UPSM': 'UPS Mail Innovations'}
    w.write('carrier-code\tcarrier-name\ttracking-number\torder-id\tship-date\n')
    for line in f:
        parts = line.split()
        if len(parts) < 3:
            gs.write('\n')
            continue

        confirm_date, fba_order_id, customer_order_id = parts[0], parts[1], parts[-1]
        if re.match(r'\d{3}-\d{7}-\d{7}\Z', customer_order_id) is None:
            print(f'WARNING: Source Amazon order id {customer_order_id} is invalid!')
            gs.write('\n')
            continue

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
                        print(f'WARNING: {fba_order_id}/{customer_order_id} have multiple tracking numbers!')

                    html = driver.find_element_by_id('shipment-tables').get_attribute('innerHTML')
                    carrier = re.findall(r'Carrier:.*<br>', html)[0].replace('Carrier:', '').replace('<br>', '').strip()
                    if carrier in carrier_names.keys():
                        carrier = carrier_names[carrier]

                    tracking_id = ta[0].get_attribute('href').replace('https://www.swiship.com/track?id=', '').replace('&loc=en_US', '')
                    print(f'{fba_order_id}\t{customer_order_id}\t{carrier}\t{tracking_id}\t{confirm_date}T07:00:00Z')
                    gs.write(f'{fba_order_id}\t{carrier}\t{tracking_id}\n')
                    # Carrier not in dropdown list
                    if 'Amazon' in carrier:
                        w.write(f'Other\t{carrier}\t{tracking_id}\t{customer_order_id}\t{confirm_date}T07:00:00Z\n')
                    else:
                        w.write(f'{carrier}\t\t{tracking_id}\t{customer_order_id}\t{confirm_date}T07:00:00Z\n')
        except KeyboardInterrupt:
            print('Bye~')
            break
        except:
            print(f'{fba_order_id} - Unexpected error occurred:', sys.exc_info()[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--email", type=str, help="Seller account email")
    parser.add_argument("-r", "--reuse", type=bool, help="Reuse Amazon Management Profile?")
    parser.add_argument("-i", "--input", type=str, default="fba-order-ids.txt", help="FBA/customer order ids")
    parser.add_argument("-o", "--output", type=str, default="trackings.txt", help="Shipping confirmation file")
    args = parser.parse_args()
    print(args)

    driver = seller_central_base.init_web_driver(args.email, args.reuse)
    try:
        get_fba_tracking(driver, args.input, args.output)
    finally:
        driver.quit()

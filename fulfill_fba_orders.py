import argparse
import re
import sys
from time import sleep

from selenium.webdriver.support.ui import Select

import seller_central_base


def load_us_states():
    states = {}
    f = open('us-states.txt', 'r')
    for line in f:
        parts = line.split('\t')
        states[parts[0].lower().strip()] = parts[1].strip()
    return states


US_STATES = load_us_states()


def fulfill(driver, sku, orders_to_fulfill, fulfill_report):
    f = open(orders_to_fulfill, 'r')
    w = open(fulfill_report, 'w')
    success, total = 0, 0
    for line in f:
        order = line.split('\t')
        try:
            if is_fulfilled(driver, order[0]):
                print(f'{order[0]} was fulfilled already!')
                success += 1
                continue

            total += 1
            driver.get(f'https://sellercentral.amazon.com/inventory/ref=xx_invmgr_dnav_xx?tbla_myitable=sort:%7B%22sortOrder%22%3A%22DESCENDING%22%2C%22sortedColumnId%22%3A%22date%22%7D;search:{sku};pagination:1;')
            sleep(1)

            driver.find_elements_by_css_selector('span.a-button-splitdropdown button.a-button-text')
            sleep(1)

            dd_menus = driver.find_elements_by_css_selector('li.a-dropdown-item')
            for dm in dd_menus:
                dm_title = dm.get_attribute('innerText').lower()
                if 'create' in dm_title and 'fulfillment' in dm_title and 'order' in dm_title:
                    dm.click()
                    break

            if place_order(driver, order):
                success += 1
        except KeyboardInterrupt:
            print('Bye~')
            break
        except:
            print(f'{order[0]} - Unexpected error occurred:', sys.exc_info()[0])

    print(f'{success} of {total} orders fulfilled successfully.')
    return total - success


def place_order(driver, order):
    # lxhair141 111-9168333-9961051 Sheila Pelfrey 2259 SAINT JOSEPH RD CHIPLEY FL 32428-5716 US +1 210-728-4548 ext. 63000
    region_codes = driver.find_elements_by_name('regionCode')
    if region_codes is None or len(region_codes) == 0:
        return False

    fill_field(driver.find_element_by_name('orderId'), order[0])
    fill_field(driver.find_elements_by_name('sellables.0'), order[1])
    fill_field(driver.find_element_by_name('fullName'), order[2])
    fill_field(driver.find_element_by_name('line1'), order[3])
    fill_field(driver.find_element_by_name('line2'), order[4])
    fill_field(driver.find_element_by_name('city'), order[5])

    select = Select(driver.find_element_by_id('regionCode'))
    us_state = re.sub('[^A-Z]', '', order[6].upper())
    if len(us_state) > 2:
        us_state = US_STATES[us_state.lower()]
    select.select_by_value(us_state)

    fill_field(driver.find_element_by_name('postalCode'), order[7])
    # Currently we only fulfill US orders
    # fill_field(driver.find_element_by_name('countryCode'), order[8])
    phone = order[9].replace('+1', '')
    if ' .ext' in phone:
        phone = phone.replace(' .ext', '(') + ')'
    fill_field(driver.find_element_by_name('phoneNumber'), phone)

    driver.find_element_by_name('Continue').click()
    sleep(2)

    driver.find_element_by_name('Place Order').click()
    sleep(3)

    # Check success indicator or search by order id directly
    return is_fulfilled(driver, order[0])


def fill_field(elem, value):
    elem.clear()
    elem.send_keys(value)


def is_fulfilled(driver, fba_order_id):
    url = f'https://sellercentral.amazon.com/orders-v3/search?page=1&q={fba_order_id}&qt=orderid&date-range=last-30'
    driver.get(url)
    sleep(2)

    anchors = driver.find_elements_by_css_selector('#orders-table tbody > tr > td div.cell-body-title > a')
    return anchors is not None and len(anchors) > 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--email", type=str, help="Seller account email")
    parser.add_argument("-s", "--sku", type=str, help="SKU of listing")
    parser.add_argument("-r", "--reuse", type=bool, help="Reuse Amazon Management Profile?")
    parser.add_argument("-i", "--input", type=str, default="orders-to-fulfill.txt", help="Source orders to fulfill")
    parser.add_argument("-o", "--output", type=str, default="fulfill-results.txt", help="Order fulfill results")
    args = parser.parse_args()
    print(args)

    driver = seller_central_base.init_web_driver(args.email, args.reuse)
    try:
        fulfill(driver, args.sku, args.input, args.output)
    finally:
        driver.quit()

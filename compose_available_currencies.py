# -*- coding: utf-8 -*-
from src.utils import (write_json_to_file,
                       load_json_from_file,
                       load_json_from_url,                       
                       print_stats)

import src.config as config

CHECK_URL = 'https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms='

def run():
    lst = []
    currencyDct = load_json_from_file('data/currencies_list.json')
    print "Currencies loaded: " + str(len(currencyDct))
    i = 0
    for code in currencyDct.keys():
        i += 1
        url = CHECK_URL + code
        print (i, code)
        priceData = load_json_from_url(url)
        if u'Response' in priceData and priceData[u'Response'] == u'Error':
            print "ERROR: " + code
        else:
            currency = currencyDct[code]
            # print currency
            lst += [currency]
        
        print "----"
    print "Currencies OK: " + str(len(lst))
    write_json_to_file(lst, 'result/currency_list/currency_list.json')
    print "Currencies written to file "


if __name__ == "__main__":
    run()

# -*- coding: utf-8 -*-
from src.utils import (write_json_to_file,
                       load_json_from_url,
                       load_json_from_file,
                       print_stats)

import src.config as config




def get_all_ERC20_tickers():
    lst = []
    tokens_dct = load_json_from_file(config.TOKENS_LIST_FILENAME)[u'tokens']
    print_stats(tokens_dct)
    for token_addr in tokens_dct:
        if tokens_dct[token_addr][u'has_cc_ticker']:
            ticker = tokens_dct[token_addr][u'cc_ticker']
            lst.append(ticker)
    return lst

def get_cap_dct(tickers):
    dct = {}
    for ticker in tickers:
        print ticker
        url = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms={tickers}&tsyms=USD".format(tickers=ticker)
        print "getting ticker: ", url
        data = load_json_from_url(url)
        if not data.get(u'HasWarning') and data.get(u'Response') != u"Error":
            data = data[u'RAW']
            mark_cap = data[ticker][u'USD'][u'MKTCAP']
            price = data[ticker][u'USD'][u'PRICE']
            # print "price: ", price
            qnty = mark_cap/float(price)
            qnty = int(round(qnty))
            # print "qnty; ", qnty
            low_price = float(data[ticker][u'USD'][u'LOW24HOUR'])
            high_price = float(data[ticker][u'USD'][u'HIGH24HOUR'])

            if low_price != high_price:
                print "lh: ", low_price, qnty
                mark_cap_calc = low_price * qnty
                print "mark_cap_calc", mark_cap_calc
                dct[ticker] = mark_cap_calc             
            else:
                print "NO PRICE CHANGE! Skipping ", ticker
                dct[ticker] = 0
            
        else:
            print "WARNING ", data
        print "-" * 10
    print "got market cap for tokens: ", len(dct)
    return dct


def run():
    ''' Generate file with top tokens depending on market cap.
    1. Load all erc20 tokens from json file.
    2. Leave only tokens with CC ticker
    2. Get Market Cap for each token.
    3. Write list of top N tokens to json file.
    '''
    # 1. Getting all tokens from file
    tickers = get_all_ERC20_tickers()  # all erc20 tickers
    print "tickers len: ", len(tickers)
    cap_dct = get_cap_dct(tickers)

    sorted_by_cap = sorted(cap_dct.items(),
                           key=lambda (ticker, cap): cap,
                           reverse=True)
    print sorted_by_cap

    tickers_with_price = filter(lambda (ticker, price):
                                price > 10**6, sorted_by_cap)
    print "all tokens len: ", len(tickers_with_price)

    # enhance with CoinMarketCap Data
    
    # print "all tokens with price len: ", len()
    top_tokens = map(lambda (token, cap): token,
                     # sorted_by_cap[:config.TOP_TOKENS_LIMIT])
                     tickers_with_price)
    
    print "top tokens len: ", len(top_tokens)
    write_json_to_file(top_tokens, config.TOP_TOKENS_FILENAME)
    print "\n\Top nTokens List is saved to file."
    

    return None


if __name__ == "__main__":
    run()

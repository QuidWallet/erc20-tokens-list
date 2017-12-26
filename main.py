 # -*- coding: utf-8 -*-
import urllib, json
import requests


MEW_TOKENS_URL = "https://raw.githubusercontent.com/kvhnuke/etherwallet/mercury/app/scripts/tokens/ethTokens.json"
CRYPTOCOMPARE_TOKENS_URL = "https://min-api.cryptocompare.com/data/all/coinlist"
TOKENS_LIST_FILENAME = "tokens/tokens.json"
TOKENS_EXCEPTIONS_FILENAME = "tokens/exceptions.json"


def load_json_from_url(url):
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data


def load_json_from_file(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
        return data


def write_json_to_file(data, filename):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)


    
def main():
    '''    
    Загрузка данных в память:
    а) Список токенов mew - загружается по ссылке 
    б) Список токенов на cryptocompare - загружается по ссылке
    в) Рабочий список токенов для прилаги (если есть)
    г) Cписок исключений

    Добавление новых токенов.
    Токены из Списка Mew, которых нет в Рабочем Списке, добавляются в Рабочий Список. Для этих токенов обновляется updated_version

    Авто-проставление тикеров.
    Для токенов в Рабочем Списке, у которых не проставлен тикер, но они есть в Списке CC, проставляется тикер (как символ).  Для этих токенов обновляется updated_version

    Проставление ручных исключений
     Для токенов из Списка Исключений, если тикер в Списке Исключений не совпадает с тикером в Рабочем Списке, то тикер проставляется из Списка Исключений.  Для этих токенов обновляется updated_version

    Загрузка иконок из списка CC
    Для всех токенов которые были изменены в этой версии, загрузить иконки в папку для оригинальных иконок и сжать их в 3х размерах под разные разрешения.  Для этих токенов обновляется updated_version

    Коммит в репозиторий для обновления + обновление кода приложения для следующих версий
    '''

    def load_data():        
        print("Stating Tokenizer.")
        print("-" * 10 + "\n\n")
        print("1. GETTING TOKENS DATA...\n")
        print("-" * 10)
        print("A. MEW token list...")    
        mew_tokens = load_json_from_url(MEW_TOKENS_URL)
        print("A. done.\n")
        
        print("B. CryptoCompare token list...")
        cc_tokens = load_json_from_url(CRYPTOCOMPARE_TOKENS_URL)[u'Data']
        print("B. done.\n")
        
        print("C. Token list from file...")
        tokens_dct = load_json_from_file(TOKENS_LIST_FILENAME)
        print("C. done.\n")
        
        print("D. Exceptions from file...")
        exceptions_dct = load_json_from_file(TOKENS_EXCEPTIONS_FILENAME)
        print("D. done.\n\n")
        print("1. DONE.")
        print("-" * 10 + "\n\n")
        return (mew_tokens, cc_tokens, tokens_dct, exceptions_dct)

    
    def add_new_tokens(mew_tokens, tokens_dct):
        for token in mew_tokens:
            token_address = token[u'address']
            if token_address not in tokens_dct:
                print "\nAdding new Token: "
                print token
                
                tokens_dct[token_address] = {
                    u'symbol': token[u'symbol'],
                    u'decimal': token[u'decimal'],
                }
        return tokens_dct

    
    def update_cc_tickers(tokens_dct, cc_tokens):
        for address in tokens_dct:
            token = tokens_dct[address]
            
            token_ticker = token[u'symbol'].upper()
            
            if not token.get(u'has_cc_ticker'):
                print("\n\nNo ticker:")
                print(token)
                #print(cc_tokens.get(token_symbol), "N/A")
                if token_ticker in cc_tokens:
                    token[u'has_cc_ticker'] = True
                    token[u'cc_ticker'] = token_ticker
                    token[u'ImageUrl'] = cc_tokens[token_ticker].get(u'ImageUrl', '')
                    token[u'name'] = cc_tokens[token_ticker].get(u'Name', '')                    
                else:
                    token[u'has_cc_ticker'] = False
                    token[u'cc_ticker'] = ""
                
                tokens_dct[address] = token
        return tokens_dct
    
    
    def consider_mapping(tokens_dct, exceptions_dct):
        for exception in exceptions_dct:
            address = exception[u'address']
            exception_ticker = exception[u'cc_ticker']
            token = tokens_dct[address]

            #print address, token
            token_ticker = token[u'cc_ticker']

            if token_ticker != exception_ticker: 
                print "Found exception to update. Changing:  '" + token_ticker + "' -> '" + exception_ticker + "'"
                token[u'has_cc_ticker'] = True
                token[u'cc_ticker'] = exception_ticker
                token[u'ImageUrl'] = cc_tokens[exception_ticker].get(u'ImageUrl', '')
                token[u'name'] = cc_tokens[exception_ticker].get(u'Name', '')                    
                tokens_dct[address] = token
        return tokens_dct

    def download_icons(tokens_dct):
        for token_addr in tokens_dct:
            token = tokens_dct[token_addr]
            if token[u'has_cc_ticker'] and token[u'ImageUrl'] and len(token[u'ImageUrl']) > 1:
                icon_filename = "tokens/icons/" + token_addr + ".png"
                icon_url = "https://www.cryptocompare.com/" + token[u'ImageUrl']
                print icon_url
                #urllib.urlretrieve(icon_url, icon_filename)
                r = requests.get(icon_url, allow_redirects=True)
                open(icon_filename, 'wb').write(r.content)
                
                #f = open(icon_filename,'wb')
                #f.write(urllib.urlopen(icon_filename).read())
                #f.close()
    
    def print_stats(tokens_dct):
        print "\n\n"
        print "*" * 10 
        print "Number of tokens: " + str(len(tokens_dct))
        i = 0
        for token_addr in tokens_dct:
            if tokens_dct[token_addr][u'has_cc_ticker']:
                i += 1
        print "Number of tokens with price: " + str(i)
        print "*" * 10 

        
    # 1. Loading data from web and files to memory
    (mew_tokens, cc_tokens, tokens_dct, exceptions_dct) = load_data()

    print_stats(tokens_dct)
    
    # 2. Adding new tokens
    print "\n\n2. Adding new tokens..."    
    tokens_dct = add_new_tokens(mew_tokens, tokens_dct)
    print "\ntokens added"
    print "-" * 10

    # 3. Updating CryptoCompare tokens
    print "\n\n3. Updating CryptoCompare tokens..."    
    tokens_dct = update_cc_tickers(tokens_dct, cc_tokens)
    print "\nCC tokens updated"
    print "-" * 10
    
    # 4. Considering exceptions
    print "\n\n4. Considering exceptions..."    
    tokens_dct = consider_mapping(tokens_dct, exceptions_dct)
    print "\nCC tokens updated"
    print "-" * 10
    
    # 3. write json to file
    write_json_to_file(tokens_dct, TOKENS_LIST_FILENAME)
    print "\n\nTokens List is saved to file."

    download_icons(tokens_dct)
    print_stats(tokens_dct)

    return


    
    
if __name__ == "__main__":
    main()

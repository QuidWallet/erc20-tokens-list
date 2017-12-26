 # -*- coding: utf-8 -*-
import urllib, json


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
            #print address, token
            token_ticker = token[u'symbol'].upper()
            
            if not token.get(u'has_cc_ticker', False):
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
    
    # 1. Loading data from web and files to memory
    (mew_tokens, cc_tokens, tokens_dct, exceptions_dct) = load_data()
    
    # 2. Adding new tokens
    tokens_dct = add_new_tokens(mew_tokens, tokens_dct)

    # 3. Updating CryptoCompare tokens
    tokens_dct = update_cc_tickers(tokens_dct, cc_tokens)
    
    # 3. write json to file
    write_json_to_file(tokens_dct, TOKENS_LIST_FILENAME)
    print "\n\nTokens List is saved to file."
    
    return


    
    
if __name__ == "__main__":
    main()

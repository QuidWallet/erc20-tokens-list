# -*- coding: utf-8 -*-
from src.utils import (
    load_json_from_url,
    write_json_to_file,
    write_string_to_file,
    print_stats)

import src.download_icons
import src.tokens_list
import src.config as config

def checkCrytocomapareApiForToken(tokens_dct):
    for tokenAddr in tokens_dct.keys():
        token = tokens_dct[tokenAddr]
        if token[u'has_cc_ticker']:
            print ""
            ticker = token[u'cc_ticker']
            print "checking price... ", ticker
            url = "https://min-api.cryptocompare.com/data/price?fsym={ticker}&tsyms=USD".format(ticker=ticker)
            data = load_json_from_url(url)
            if not data.get(u'HasWarning') and data.get(u'Response') != u"Error":
                print ticker, data
            else:
                print "NO DATA FOR TICKER ", ticker
                tokens_dct[tokenAddr][u'has_cc_ticker'] = False
            print ""

def getInfofromCMC(tokens_dct):
    # 5. load coinmarket cap data
    print "loading Coin Market Cap data..."
    cmcResult = load_json_from_url('https://api.coinmarketcap.com/v1/ticker/?limit=0')
    print "Got CMC result", len(cmcResult)
    cmcDct = {}
    for token in cmcResult:
        if token[u'symbol'] not in cmcDct:
            cmcDct[token[u'symbol']] = token    
    
    for tokenAddr in tokens_dct.keys():
        token = tokens_dct[tokenAddr]    
        symbol = token[u'symbol']
        if symbol in cmcDct:
            cmcToken = cmcDct[symbol]
            token[u'available_supply'] = cmcToken[u'available_supply']
            token[u'total_supply'] = cmcToken[u'total_supply']
            token[u'max_supply'] = cmcToken[u'max_supply']
            token[u'name'] = cmcToken[u'name']    

def createTokenIconsLoader(tokens_dct):
    contentStart = '''
export function getLocalIcon(contractAddress) {
    let nextState;
    switch (contractAddress) {
    case "0x000_ether":
        return require('quid-wallet/app/views/assets/icons/ether.png');
        break;
'''
    tokenPaths = ''
    for tokenAddr in tokens_dct:
        token = tokens_dct[tokenAddr]
        if token[u'has_cc_ticker']:
            tokenPaths += '''
    case "''' +  tokenAddr + '''":
        return require('quid-wallet/app/views/assets/tokens/icons/''' + tokenAddr + '''.png');
        break;
'''
    
    contentEnd = '''
    default:
        return false;
        break;
    }\n
    return false;
}
'''
    content = contentStart + tokenPaths + contentEnd
    write_string_to_file(content, 'result/tokens/localTokenIcons.js')
    print " getLocalIcons.js composed "
    

def run():
    ''' Загрузка данных в память:
    а) Список токенов mew - загружается по ссылке
    б) Список токенов на cryptocompare - загружается по ссылке
    в) Рабочий список токенов для прилаги (если есть)
    г) Cписок исключений

    Добавление новых токенов.
    Токены из Списка Mew, которых нет в Рабочем Списке, добавляются в Рабочий
    Список. Для этих токенов обновляется updated_version

    Авто-проставление тикеров.
    Для токенов в Рабочем Списке, у которых не проставлен тикер, но они есть в
    Списке CC, проставляется тикер (как символ).
    Для этих токенов обновляется updated_version

    Проставление ручных исключений
     Для токенов из Списка Исключений, если тикер в Списке Исключений не
    совпадает с тикером в Рабочем Списке, то тикер проставляется
    из Списка Исключений.  Для этих токенов обновляется updated_version

    Загрузка иконок из списка CC
    Для всех токенов которые были изменены в этой версии, загрузить иконки в
    папку для оригинальных иконок и сжать их в 3х размерах
    под разные разрешения.  Для этих токенов обновляется updated_version

    Коммит в репозиторий для обновления + обновление кода приложения
    для следующих версий
    '''
    
    # 1. Loading data from web and files to memory
    (mew_tokens, cc_tokens,
     tokens_dct, exceptions_dct, list_version) = src.tokens_list.load_data()

    print_stats(tokens_dct)

    # incremening list version
    list_version += 1

    # 2. Adding new tokens
    tokens_dct = src.tokens_list.add_new_tokens(mew_tokens,
                                                tokens_dct,
                                                list_version)

    # 3. Updating CryptoCompare tokens
    tokens_dct = src.tokens_list.update_cc_tickers(tokens_dct,
                                                   cc_tokens,
                                                   list_version)

    # 4. Considering exceptions
    tokens_dct = src.tokens_list.consider_mapping(tokens_dct,
                                                  exceptions_dct,
                                                  cc_tokens,
                                                  list_version)

    print_stats(tokens_dct)

    checkCrytocomapareApiForToken(tokens_dct)
    getInfofromCMC(tokens_dct)
    createTokenIconsLoader(tokens_dct)

    
    print "downloading icons..."
    src.download_icons.download_icons(tokens_dct, list_version)
    print "icons downloaded."

    
    # 3. write tokens to json file
    tokens_data = {
        "version": list_version,
        "tokens": tokens_dct
    }
    
    write_json_to_file(tokens_data, config.TOKENS_LIST_FILENAME)
    print "\n\nTokens List is saved to file."
    
    return None


if __name__ == "__main__":
    run()
    # createTokenIconsLoader({'a': 3, 'b': 4})

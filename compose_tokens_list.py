# -*- coding: utf-8 -*-
from src.utils import (write_json_to_file,
                       print_stats)

import src.download_icons
import src.tokens_list
import src.config as config


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

    # 3. write tokens to json file
    tokens_data = {
        "version": list_version,
        "tokens": tokens_dct
    }
    write_json_to_file(tokens_data, config.TOKENS_LIST_FILENAME)
    print "\n\nTokens List is saved to file."

    src.download_icons.download_icons(tokens_dct, list_version)
    print_stats(tokens_dct)

    return None


if __name__ == "__main__":
    run()

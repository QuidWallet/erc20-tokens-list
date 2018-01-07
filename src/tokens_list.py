from src.utils import (load_json_from_url,
                       load_json_from_file)
import src.config as config

def load_data():
    print("Stating Tokenizer.")
    print("-" * 10 + "\n\n")
    print("1. GETTING TOKENS DATA...\n")
    print("-" * 10)
    print("A. MEW token list...")
    mew_tokens = load_json_from_url(config.MEW_TOKENS_URL)

    print("A1. Updating mew token file with custom tokens...")
    tokens_data = load_json_from_file(config.CUSTOM_TOKENS_FILENAME)

    mew_tokens += tokens_data
    
    print("A. done.\n")

    print("B. CryptoCompare token list...")
    cc_tokens = load_json_from_url(config.CRYPTOCOMPARE_TOKENS_URL)[u'Data']
    print("B. done.\n")
    
    print("C. Token list from file...")
    tokens_data = load_json_from_file(config.TOKENS_LIST_FILENAME)
    tokens_dct = tokens_data[u'tokens']
    list_version = tokens_data[u'version']
    print("C. done.\n")
    
    print("D. Exceptions from file...")
    exceptions_dct = load_json_from_file(config.TOKENS_EXCEPTIONS_FILENAME)
    print("D. done.\n\n")
    print("1. DONE.")
    print("-" * 10 + "\n\n")
    return (mew_tokens,
            cc_tokens,
            tokens_dct,
            exceptions_dct,
            list_version)


def add_new_tokens(mew_tokens, tokens_dct, version):        
    print "\n\n2. Adding new tokens..."
    for token in mew_tokens:
        token_address = token[u'address'].lower()
        if token_address not in tokens_dct:
            print "\nAdding new Token: "
            print token
            tokens_dct[token_address] = {
                u'symbol': token[u'symbol'],
                u'decimal': token[u'decimal'],
                u'last_change_v': version
            }

    print "\ntokens added"
    print "-" * 10
    return tokens_dct


def update_cc_tickers(tokens_dct, cc_tokens, version):
    print "\n\n3. Updating CryptoCompare tokens..."
    for address in tokens_dct:
        token = tokens_dct[address]
        token_ticker = token[u'symbol'].upper()
        if not token.get(u'has_cc_ticker'):
            print("\n\nNo ticker:")
            print(token)
            if token_ticker in cc_tokens:
                token[u'has_cc_ticker'] = True
                token[u'cc_ticker'] = token_ticker
                token[u'ImageUrl'] = cc_tokens[token_ticker].get(
                    u'ImageUrl', '')
                token[u'name'] = cc_tokens[token_ticker].get(u'Name', '')
                token[u'last_change_v'] = version
            else:
                token[u'has_cc_ticker'] = False
                token[u'cc_ticker'] = ""
            tokens_dct[address] = token
    print "\nCC tokens updated"
    print "-" * 10
    return tokens_dct


def consider_mapping(tokens_dct, exceptions_dct, cc_tokens, version):
    print "\n\n4. Considering exceptions..."

    for exception in exceptions_dct:
        address = exception[u'address'].lower()
        exception_ticker = exception[u'cc_ticker']
        token = tokens_dct[address]

        # print address, token
        token_ticker = token[u'cc_ticker']

        if token_ticker != exception_ticker:
            print ("Found exception to update. Changing:  '" +
                   token_ticker +
                   "' -> '" + exception_ticker + "'")
            token[u'has_cc_ticker'] = True
            token[u'cc_ticker'] = exception_ticker
            token[u'ImageUrl'] = cc_tokens[exception_ticker].get(
                u'ImageUrl', '')
            token[u'name'] = cc_tokens[exception_ticker].get(u'Name', '')
            token[u'last_change_v'] = version
            tokens_dct[address] = token
    print "\nCC tokens updated"
    print "-" * 10
    return tokens_dct

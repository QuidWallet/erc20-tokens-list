import urllib
import json


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

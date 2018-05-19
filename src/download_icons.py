import requests
import os
import src.config as config


def download_icons(tokens_dct, version):
    for token_addr in tokens_dct:
        token = tokens_dct[token_addr]
        if (token[u'has_cc_ticker'] # and token[u'last_change_v'] >= version
            and token.get(u'ImageUrl', False) and len(token.get(u'ImageUrl', "")) > 1):
            #if True:
            icon_filename = "tokens/icons-src/" + token_addr + ".png"
            icon_url = ("https://www.cryptocompare.com/" +
                        token[u'ImageUrl'])
            print icon_url
            # download image
            r = requests.get(icon_url, allow_redirects=True)
            open(icon_filename, 'wb').write(r.content)

            # resize 1x
            icon_1x = "result/tokens/icons/" + token_addr + ".png"
            resize_img_cmd_1x = "sips -Z {height} {icon}\
            --out {filename}".format(
                height=config.TOKEN_ICON_HEIGHT,
                icon=icon_filename,
                filename=icon_1x
            )
            os.system(resize_img_cmd_1x)
            
            # resize 2x
            icon_2x = "result/tokens/icons/" + token_addr + "@2x.png"
            resize_img_cmd_2x = "sips -Z {height} {icon}\
            --out {filename}".format(
                height=config.TOKEN_ICON_HEIGHT*2,
                icon=icon_filename,
                filename=icon_2x
            )
            os.system(resize_img_cmd_2x)
            
            # resize 3x
            icon_3x = "result/tokens/icons/" + token_addr + "@3x.png"
            resize_img_cmd_3x = "sips -Z {height} {icon}\
            --out {filename}".format(
                height=config.TOKEN_ICON_HEIGHT*3,
                icon=icon_filename,
                filename=icon_3x
            )
            os.system(resize_img_cmd_3x)

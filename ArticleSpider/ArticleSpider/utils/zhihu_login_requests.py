from DecryptLogin import login
from PIL import Image
from DecryptLogin import login
import pytesseract
import pytesseract as pya
from aip import AipOcr
APP_ID = '23577965'
API_KEY = '3eLQ212cGHwqr7NsPDTkatKY'
SECRET_KEY = 'b3ADX93f7PEoHis3y9RyMgSGPhKG2LTm'

# 创建一个百度AI的OCR客户端,这个客户端用于 代我们和百度AI后台之间的通信

# 读取本地图片


def cracker(imagepath):
    img = Image.open(imagepath)
    # 识别验证码图片
    img.data()
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    # fp = open('C:\\Users/张献强\\Desktop\\search-engine\\ArticleSpider\\ArticleSpider\\utils\\captcha.jpg', 'rb').read()
    # s1 = client.basicGeneral(fp)
    # print(s1)
    # fp2 = open('C:/Users/张献强/Desktop/search-engine/ArticleSpider/ArticleSpider/utils/captcha.jpg', 'rb').read()
    # s2 = client.basicGeneral(fp2)
    # print(s2)
    # # 高精度识别
    # s3 = client.basicAccurate(fp)
    # print(s3)
    im = Image.open('C:/Users/张献强/Desktop/search-engine/ArticleSpider/ArticleSpider/utils/captcha.jpg')
    result = pytesseract.image_to_string(im)
    print(result)
    return result


lg = login.Login()
infos_return, session = lg.zhihu("14767752312", "110112119zxq", 'pc', crack_captcha_func=cracker)

# def cracker(imagepath):
#     return 'LOVE'
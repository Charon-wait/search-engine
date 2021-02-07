
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time, random
from scrapy.selector import Selector
import time

def get_tracks1(distance):
    # 初速度
    v = 0
    # 单位时间为0.3s来统计轨迹，轨迹即0.3s内的位移
    t = 0.3
    # 位移/轨迹列表
    tracks = []
    # 当前的位移
    current = 0
    # 到达mid值开始减速
    mid = distance * 4 / 5
    while current < distance:
        if current < mid:
            # 加速度越小，单位时间内的位移越小，模拟的轨迹就越多越详细
            a = 2
        else:
            a = -3
        # 初速度
        v0 = v
        # 0.3s时间内的位移
        s = v0 * t + 0.5 * a * (t ** 2)
        # 当前位置
        current += s
        # 添加到轨迹列表
        tracks.append(round(s))
        # 速度已经达到V，该速度作为下次的初速度
        v = v0 + a * t
    return tracks


# 计算滑块位移距离
def get_diff_location(image1, image2):
    # （0,340）（0,340）为滑块图片区域，可根据实际情况修改
    for i in range(0, 340):
        for j in range(0, 198):
            # 遍历原图与缺口图像素值寻找缺口位置
            if is_similar(image1, image2, i, j) == False:
                return i
    return -1


# 对比RGB值得到缺口位置
def is_similar(image1, image2, x, y):
    pixel1 = image1.getpixel((x, y))
    pixel2 = image2.getpixel((x, y))
    # 截图像素也许存在误差，50作为容差范围
    if abs(pixel1[0] - pixel2[0]) >= 50 and abs(pixel1[1] - pixel2[1]) >= 50 and abs(pixel1[2] - pixel2[2]) >= 50:
        return False
    return True
def login():
        driver = webdriver.Chrome()
        driver.get('https://www.zhihu.com/signin?next=%2F')
        t_selector = Selector(text=driver.page_source)
        driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[1]/div[2]').click()
        driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[2]/div/label/input').send_keys('14767752312')
        # 输入密码
        driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input').send_keys('110112119zxq')
        # 点击登录
        driver.find_element_by_xpath('//div/form/button').click()
        # 等待2s使验证弹窗加载完成
        time.sleep(2)
        #找到滑块按钮
        slider = driver.find_element_by_xpath('//div[@class="yidun_slider"]')
        # 点击鼠标左键，不松开
        ActionChains(driver).click_and_hold(slider).perform()

        #print(driver.page_source)
        # 拖动到最右边，为了后续方便对比
        ActionChains(driver).move_by_offset(xoffset=280, yoffset=0).perform()
        # 定位到弹出的验证窗口
        y_element = driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/div')
        # print(y_element.location)
        # print(y_element.size)
        # 获取左上，右，左下的坐标确定一个图片范围
        left = y_element.location['x']
        top = y_element.location['y']
        right = left + y_element.size['width']
        bottom = top + y_element.size['height']
        # 全窗口截图
        driver.save_screenshot('a.png')
        # 打开截图的图片
        im = Image.open('a.png')
        # 局部截图
        im = im.crop((left + 196, top + 1169.2, right + 196, bottom - 30))
        # 保存有缺口的验证图片
        im.save('b.png')
        # 放开鼠标
        ActionChains(driver).release(slider).perform()
        time.sleep(2)
        # 定位到可以显示无缺图片的位置
        block = driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[1]')
        # 修改其属性值，使显示无缺图片
        driver.execute_script('arguments[0].style = "display: block; opacity: 1;"', block)
        time.sleep(2)
        # 全窗口截图
        driver.save_screenshot('a.png')
        # 打开截图的图片
        im = Image.open('a.png')
        # 局部截图
        im = im.crop((left + 160, top + 55, right + 225, bottom - 30))
        # 保存无缺口的验证图片
        im.save('c.png')

        time.sleep(0.5)

        # 打开获取的两个图片
        imageb = Image.open('b.png')
        imagec = Image.open('c.png')
        # 获取缺口位置
        visualstack = get_diff_location(imagec, imageb)
        # 减去左边图片空白像素值
        print(visualstack - 10)
        # 点击鼠标左键，不松开
        ActionChains(driver).click_and_hold(slider).perform()
        # 先快速拖动圆球到中间位置
        ActionChains(driver).move_by_offset(xoffset=visualstack / 2, yoffset=0).perform()
        # 根据轨迹拖动圆球
        track_list = get_tracks1((visualstack / 2 - 48))
        for track in track_list:
            ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()
        # 放开圆球
        time.sleep(0.8)
        ActionChains(driver).release(slider).perform()
        print(driver.page_source)
        time.sleep(4)
        if '你的昵称' in driver.page_source:
            print('登录成功')
            print(driver.get_cookies())
        else:
            driver.close()
            login()


if __name__ == '__main__':
    login()
#driver.quit()
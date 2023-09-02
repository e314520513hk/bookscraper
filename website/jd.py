from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from opencc import OpenCC
from logmanager import log
from bs4 import BeautifulSoup
import sys
import lxml.html.clean as clean

cc = OpenCC('s2tw')
def scrape(driver,isbn):
    book_info = {}
    driver.get("https://search.jd.com/Search?keyword="+isbn)
    
    
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup.select('#J_goodsList > ul > li:nth-child(1) > div > div.p-img > a')[0])
    # sys.exit()
    
    # print(driver.find_element(By.XPATH, '//*[contains(text(),"自营")]/..').get_attribute('class'))

    sleep(3)
    try:
        book_found = False

        WebDriverWait(driver, 3, 0.1).until(
                                EC.visibility_of_element_located((By.XPATH, "//div[@id='J_goodsList']/ul/li/div/div"))  )  			
        
        
        for idx,ele in enumerate(driver.find_elements(By.XPATH, "//div[@id='J_goodsList']/ul/li/div/div")):
            

            if "自营" in ele.text:
                book_found= True
                ele = ele.find_element(By.XPATH,'//*[@id="J_goodsList"]/ul/li['+str(idx)+']/div/div[1]/a/img')
                #action chain object
                action = ActionChains(driver)
                # move to element operation
                action.move_to_element(ele).perform()
                sleep(1)
                ele.click()
                break
		
        if not book_found:
            
            for ele in driver.find_elements(By.XPATH, "//div[@id='J_goodsList']/ul/li/div/div"):
                
                if "世紀書緣專營店" in cc.convert(ele.text):
                    book_found= True
                    #action chain object
                    action = ActionChains(driver)
                    # move to element operation
                    action.move_to_element(ele).click().perform()
                    break
                
        if not book_found:
            raise Exception("No book found.")
            
        sleep(2)
            
        #get current window handle
        p = driver.current_window_handle
        #get first child window
        chwd = driver.window_handles
        
        for w in chwd:
            #switch focus to child window
            if(w!=p):
                driver.switch_to.window(w)
        WebDriverWait(driver, 4, 0.1).until(
                            EC.visibility_of_element_located((By.XPATH, "//img[@id='spec-img']"))  )  		
        sleep(1)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        
        book_info['book_name'] = get_bookname(soup)
        
        book_info['imglink'] = get_imgurl(driver)
        book_info['author'] = get_author(soup)
        book_info['publish'] = get_publish(soup)
        book_info['kaiban'] = get_kaiban(soup)
        book_info['publish_date'] = get_publish_date(soup)
        book_info['ISBN'] = get_isbn(soup)
        book_info['banden'] = get_banden(soup)
        book_info['title'] = get_title(soup)
        try:
            book_info['introduction'] = get_introduction(soup)
        except:  
            book_info['introduction'] = ""
        book_info['page_number'] = get_page_number(soup)
        
        driver.close()   
        driver.switch_to.window(p)
        sleep(1)
        return book_info
    except Exception as ex:
        raise Exception(f"error occured in scrape() in jd.{ex.__str__()}")

def get_bookname(soup):
    
    try:
        book_name = soup.select('div.itemInfo-wrap > div.sku-name')[0].text.strip()
        return cc.convert(book_name)
    except:
        
        return ""

def get_imgurl(driver):
    try:
        WebDriverWait(driver, 3, 0.1).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, '#spec-img'))    )    

        return driver.find_element(By.CSS_SELECTOR, '#spec-img').get_attribute('src').replace('.avif','')
    except:
        return ""
def get_author(soup):
    try:
        author = ""
		
        #return cc.convert(soup.select(".p-author>a")[0]])
        for a in soup.select(".p-author>a"):
                author = author + a.text + " "
        return cc.convert(author)
    except:
        return ""

def get_publish(soup):
    try:

        return cc.convert(soup.select(".p-parameter > ul > li:-soup-contains('出版社：')")[0]['title'])
    except:
        return ""
def get_page_number(soup):
    try:
        return soup.select(".p-parameter > ul > li:-soup-contains('页数：')")[0]['title']
    except:
        return ""

def get_kaiban(soup):
    try:
        kaiban = int(soup.select(".p-parameter > ul > li:-soup-contains('开本：')")[0]['title'].replace("开","").strip())
        
        if kaiban < 32:
            return '1'
        else:
            return '2'
    except:
        return ""    

def get_isbn(soup):
    try:
        return soup.select(".p-parameter > ul > li:-soup-contains('ISBN：')")[0]['title']
    except:
        return ""    

def get_publish_date(soup):
    try:
        publish_date = soup.select(".p-parameter > ul > li:-soup-contains('出版时间：')")[0]['title'].split("-")
        return publish_date[0]+publish_date[1]
    except:
        return ""    
    
def get_banden(soup):
    try:
        banden = soup.select(".p-parameter > ul > li:-soup-contains('包装：')")[0]['title']
        if banden == '平装':
            return '0'
        else:
            return '1'
        
    except:
        return ""    
def get_title(soup):
    try:
        return  soup.select(".p-parameter > ul > li:-soup-contains('丛书名：')")[0]['title']
        
    except:
        return ""   
def get_introduction(soup):
    try:
        soup = remove_tags(soup,['img','br','a'])
        
        introduction = parse_introduction(soup.select("#J-detail-content")[0])
        introduction = remove_all_attr(introduction)
        return introduction
    except:
        return ""
    
def remove_tags(soup,tags):

    for data in soup(tags):
        
        # Remove tags
        data.decompose()
  
    # return data by retrieving the tag content
    return soup

def remove_all_attr(code):
    safe_attrs = clean.defs.safe_attrs
    cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=[])
    cleansed = cleaner.clean_html(code)
    return cleansed

def parse_introduction(detail):

    detail = str(detail)
    first_position = detail.find('<div')
    detail = detail[first_position:]
    last_position = detail.rfind('</div>')
    detail= detail[0:last_position+6]
    
    detail = detail.replace('<p><br/></p>','')
    detail = detail.replace('<p></p>','')
    detail = detail.replace('\\n','')
    
    detail = detail.replace("查看全部↓","")
    detail = detail.replace("收起全部↑","")
    detail = detail.replace("顯示部分信息","")
    detail = detail.replace("內容虛線","")
    detail = detail.replace("部分目錄","")
    detail = detail.replace("內頁插圖","")
    detail = detail.replace("●","")
    detail = detail.replace("部分目錄","")
    detail = detail.replace("  "," ")
    detail = detail.replace("  "," ")
    detail = detail.replace("  "," ")
    detail = detail.replace("  "," ")
    detail = detail.replace("  "," ")
    detail = detail.replace(",","，")
    detail = detail.replace("鬼穀","鬼谷")
    detail = detail.replace("穀歌","谷歌")
    detail = detail.replace("矽","硅")
    detail = detail.replace("硅穀","硅谷")
    detail = detail.replace("幹擾","干擾")
    detail = detail.replace("幹燥","乾燥")
    detail = detail.replace("傅裡葉","傅里葉")
    detail = detail.replace("關系","關係")
    detail = detail.replace("",".")
    detail = detail.replace("免費在線讀","<b>免費在線讀</b>")
    detail = detail.replace("前言序言","<b>前言序言</b>")
    detail = detail.replace("精彩書評","<b>精彩書評</b>")
    detail = detail.replace("精彩書摘","<b>精彩書摘</b>")
    detail = detail.replace("主編推薦","<b>編輯推薦</b>")
    detail = detail.replace("編輯推薦","<b>編輯推薦</b>")
    detail = detail.replace("內容簡介","<b>內容簡介</b>")
    detail = detail.replace("內容介紹","<b>內容簡介</b>")
    detail = detail.replace("目錄","<b>目錄</b>")
    detail = detail.replace("前言/序言","<b>前言/序言</b>")
    detail = detail.replace("譯者簡介","<b>譯者簡介</b>")
    detail = detail.replace("作者簡介","<b>作者簡介</b>")
    detail = detail.replace("作者介紹","<b>作者簡介</b>")
    detail = detail.replace("<b><b>","<b>")
    detail = detail.replace("<b><b>","<b>")
    detail = detail.replace("> ",">")
    detail = detail.replace(" <","<")
    detail = detail.replace("> <","><")
    detail = detail.replace("內頁插圖","")
    detail = detail.replace("產品特色","")
    detail = detail.replace("１","1")
    detail = detail.replace("２","2")
    detail = detail.replace("３","3")
    detail = detail.replace("４","4")
    detail = detail.replace("５","5")
    detail = detail.replace("６","6")
    detail = detail.replace("７","7")
    detail = detail.replace("８","8")
    detail = detail.replace("９","9")
    detail = detail.replace("０","0")
    detail = detail.replace(">部分",">第一部分")
    detail = detail.replace(">篇",">第一篇")
    detail = detail.replace(">章",">第一章")
    detail = detail.replace(">節",">第一節")
    detail = detail.replace("<br />","<br>")
    detail = detail.replace("showde","")
    detail = detail.replace("<br><b>目錄</b><br><目錄</b><br>","<p><b>目錄</b><p>目錄<br>")
    detail = detail.replace("<br><b>目錄</b><br><目錄</b>","<p><b>目錄</b><p>目錄")
    detail = detail.replace("<p><b>目錄</b><p><b>目錄</b>","<p><b>目錄</b><p>目錄")
    detail = detail.replace("<<p><b>目錄</b><p><b>目錄</b><br>","<p><b>目錄</b><p>目錄<br>")
    detail = detail.replace("</p><p><b>目錄</b></p><p><b>目錄</b><br>","<p><b>目錄</b><p>目錄<br>")
    detail = detail.replace("<br><p>","<p>")
    detail = detail.replace("<br><b>","<p><b>")
    detail = detail.replace("．",".")
    detail = detail.replace("…","")

    detail = ''.join(detail.splitlines())
		
    detail = detail.strip()
   
    detail = cc.convert(detail)		
    return detail
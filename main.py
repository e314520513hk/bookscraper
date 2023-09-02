from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import os
import sys
import traceback
import configparser
import json
from datetime import datetime
from website import jd,opac
from logmanager import log
from dataset import sugarhost
from selenium.webdriver.common.keys import Keys
import tkinter as tk
from bs4 import BeautifulSoup
import threading

class Application(tk.Frame):
    def __init__(self,master):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        # self.execute()
    def createWidgets(self):
        
        
        
        self.label = tk.Label(self)
        self.label["text"] = "匯入方式"
        self.label.grid(row=4, column=0, sticky=tk.N+tk.W)

        self.status_msg = tk.Label(self,fg='#f00')        
        self.status_msg["text"] = ""
        self.status_msg.grid(row=3, column=0, sticky=tk.N+tk.W)

        self.import_method = ("書號區間","訂單編號","isbn","isbnlist.txt匯入")
        self.selected_method = tk.StringVar()
        self.selected_method.set("書號區間")
        self.selected_method.trace("w", self.menuChanged)
        self.optionmenu = tk.OptionMenu(self, self.selected_method, *self.import_method)
        self.optionmenu.grid(row=5, column=0, sticky=tk.N+tk.W)
        
        vcmd = (self.register(self.validate),'%P','%d','%W')
        self.text_from = tk.Entry(self,validate = 'key', validatecommand = vcmd)
        self.text_from.grid(row=7, column=0, sticky=tk.N+tk.W)
        
        # self.label = tk.Label(self)
        # self.label["text"] = "~"
        # self.label.grid(row=7, column=1, sticky=tk.N+tk.W)

        self.text_to = tk.Entry(self,validate = 'key', validatecommand = vcmd)
        self.text_to.grid(row=7, column=2, sticky=tk.N+tk.W)
        # self.text = tk.Text(self)
        # self.text["height"] = 10
        # self.text["width"] = 50
        # self.text.grid(row=9, column=0, sticky=tk.N+tk.W)

        self.button = tk.Button(self)
        self.button["text"] = "執行"
        self.button.config(command=lambda:self.thread_it(self.execute))
        self.button.grid(row=10, column=0, sticky=tk.N+tk.W)
    def thread_it(self,func):
        t = threading.Thread(target=func)
        t.setDaemon(True)
        t.start()
    def menuChanged(self,*args):
        if self.selected_method.get() == "書號區間":
            self.text_from.grid(row=7, column=0, sticky=tk.N+tk.W)
            self.text_to.grid(row=7, column=2, sticky=tk.N+tk.W)   

        elif self.selected_method.get() in ["訂單編號","isbn"]:
            self.text_from.grid(row=7, column=0, sticky=tk.N+tk.W)
            self.text_to.grid_remove()

        else:
            self.text_from.grid_remove()
            self.text_to.grid_remove()

    def validate(self,P,d,W):
        
        
        if str.isdigit(P) or P == '':
            return True
        else:
            return False

    def execute(self):
        ymdhis = datetime.today().strftime('%Y%m%d%H%M%S')
        
        try:
 

            if self.selected_method.get() == '書號區間':
                if self.text_from.get() == '' or self.text_to.get() == '':
                    self.status_msg['text'] = "警告!未指定isbn區間."
                    return
                if int(self.text_to.get()) < int(self.text_from.get()):
                    self.status_msg['text'] = "警告!右邊輸入欄位必須>=左邊輸入欄位."
                    return
                res = sugarhost.query(f"SELECT GROUP_CONCAT(ISBN SEPARATOR ',') AS ISBNLIST FROM `china_book` WHERE ISBN NOT IN ('','.',0) AND book_no BETWEEN {self.text_from.get()} AND {self.text_to.get()} ")
            
                if len(res) == 0:
                    self.status_msg['text'] = "ˊ指定的書號找不到ISBN"
                    return
                isbnlist = res[0]['ISBNLIST'].split(",")

            elif self.selected_method.get() == 'isbn':
                isbnlist = []
                isbnlist.append(self.text_from.get())

            elif self.selected_method.get() == '訂單編號':
                isbnlist = []
                res = sugarhost.query(f"select book_no from order_content where order_no = {self.text_from.get()}")
                if not res:
                    self.status_msg['text'] = "無此訂單編號"
                    return
                if len(res) == 0:
                    self.status_msg['text'] = "無此訂單編號"
                    return
                
                if len(res) == 1:
                    res = sugarhost.query(f"select ISBN from china_book where book_no = {res[0]['book_no']}")
                    if len(res) == 0:
                        self.status_msg['text'] = "無此訂單編號關聯的書籍"
                        return
                    isbnlist.append(res[0]['ISBN'])

                if len(res) > 1:
                    book_nos = ''
                    for order_info in res:
                        book_nos += str(order_info['book_no']) + ","
                    
                    res = sugarhost.query(f"select ISBN from china_book where book_no in ({book_nos[:-1]})")  
                    if len(res) == 0:
                        self.status_msg['text'] = "無此訂單編號關聯的書籍"
                        return
                    for china_book in res:
                        isbnlist.append(china_book['ISBN'])


            else:
                with open('isbnlist.txt','r') as isbnlist:
                    isbnlist = isbnlist.read().splitlines()
            
                if len(isbnlist)<=0:
                    raise Exception("isbnlist is empty.")
                    
                
            self.status_msg['text'] = "爬蟲進行中..."    
            self.button['state'] = "disabled"
            s = Service(r"./chromedriver")
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.page_load_strategy = 'eager'
            # options.add_argument('--headless')  # 啟動Headless 無頭
            # options.add_argument('--disable-gpu') #關閉GPU 避免某些系統或是網頁出錯
            driver = webdriver.Chrome(options=options, service=s)
            driver.set_window_size(1920, 1080)
            # driver.implicitly_wait(100)
            baseUrl = 'https://item.jd.com'

            
            driver.get(baseUrl)
            sleep(5)
            
            print("請先登入(10分鐘內)")
            WebDriverWait(driver, 600, 0.1).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, '.icon-plus-nickname')))  
            
            for isbn in isbnlist:
                isbn = str(isbn)
                
                try:
                    isbn = isbn.strip()

                    if not isbn.isnumeric():
                        raise TypeError(f"isbn:{isbn} must be numeric.")
                    
                    jd_bookinfo = jd.scrape(driver,isbn)
                    opac_bookinfo = opac.scrape(driver,isbn)
                    
                    import_book(jd_bookinfo,opac_bookinfo)
                    
                except TypeError as ex:
                    log.err_log(f"isbn: {isbn} failed to import. {ex.__str__()}")
                    log.isbn_fail_log(isbn,ymdhis)

                except sugarhostException as ex: 
                    log.err_log(f"isbn: {isbn} failed to import. {ex.__str__()}")
                    log.isbn_fail_log(isbn,ymdhis)

                except Exception as ex:
                    log.err_log(f"isbn: {isbn} failed to import. {ex.__str__()}")
                    log.isbn_fail_log(isbn,ymdhis)
                
                sleep(2)
            self.status_msg['text'] = "爬蟲程序結束" 
            self.button['state'] = "normal"
            sys.exit()
                    
        except Exception as ex:
            self.status_msg['text'] = "爬蟲程序結束" 
            self.button['state'] = "normal"
            if  type(ex).__name__ == 'NoSuchWindowException':
                sys.exit("window already closed")
            log.err_log(ex)

    
class sugarhostException(Exception):
    def __init__(self,msg):
        self.msg = msg
    
    def __str__(self):
        return f"sugarhost error: {self.msg}"




def searchTaiwanItemNo(china_item_no):
    
    if len(china_item_no) <=0:
        return False
    
    res = sugarhost.query(f"select distinct * from china_book where china_item='{china_item_no}'")
    
    if len(res) > 0:
        return res[0]['item']
    
    return searchTaiwanItemNo(china_item_no[0:-1])

def import_book(jd,opac):
    
    keyin_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        if jd['ISBN'] == '' or jd['book_name'] == '' or jd['publish'] == '' or jd['author'] == '':
            raise Exception('required fields are not satisfied.')
        
        rows = sugarhost.query(f"select book_no from china_book where ISBN='{jd['ISBN']}'")

        if len(rows) >0:
            columns = ''
            for key,value in jd.items():

                if value == '' or value == 0 or key == 'ISBN':
                    continue
                if type(value).__name__ == 'str':
                    columns += f"{key}='{value}',"
                elif type(value).__name__ == 'int':
                    columns += f"{key}={value},"
            columns = columns[:-1]
            
            if not sugarhost.update(f"update china_book set {columns} where ISBN='{jd['ISBN']}'"):
                raise sugarhostException('error occured during updating book info.')
            
        else:
            if opac['price'] == 0:
                raise Exception('no price found on opac.')
            res = sugarhost.query("select max(book_no)+1 as new_book_no from china_book")
            if not res:
                raise sugarhostException('error occured during getting max serial number.')
            
            book_no = str(res[0]['new_book_no'])
            
            china_book = {
                "book_no":book_no,
                "book_name":jd['book_name'],
                "author":jd['author'],
                "publish":jd['publish'],
                "publish_date":jd['publish_date'],
                "ISBN":jd['ISBN'],
                "item":str(searchTaiwanItemNo(opac['china_item'])),
                "china_item":opac['china_item'],
                "page_number":jd['page_number'],
                "kaiban":jd['kaiban'],
                "banden":jd['banden'],
                "price":str(int(float(opac['price']))*10),
                "china_price":opac['price'],
                "title":jd['title'],
                "introduction":jd['introduction'],
                "imglink":jd['imglink'],
                "keyin_date":keyin_date,
                "is_active":"1"
            }
            columns = ','.join(list(china_book.keys()))
            values = "','".join(china_book.values())
            
            if not sugarhost.insert(f"insert into china_book({columns}) values('{values}')"):
                raise sugarhostException('error occured during inserting book info.')
        return True
    
    except Exception as ex:
        raise Exception(ex)
        
    

# log.err_log("program is starting")
# q = sugarhost.query('SELECT * FROM `china_book` WHERE `ISBN` LIKE "9787302590354"')
# log.err_log(q)
# print(q)

# for row in q:
#     print(row["book_name"])
#     log.err_log(row["book_name"])



# def alert_is_present(driver):
#     try:
#         alert = driver.switch_to.alert
#         alert.text
#         return alert
#     except:
#         return False



def main():
	root = tk.Tk()
	app = Application(root)
	root.mainloop()

if __name__ == '__main__':
    main()
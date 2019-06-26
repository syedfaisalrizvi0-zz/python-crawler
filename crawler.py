# python  simple web crawler.....................
from flask import Flask,url_for
import mysql.connector
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import time
import json
start = time.time()
class crawler:
    def __init__(self):
        conn = mysql.connector.connect(
            user="root",
            password="",
            database="crawler"
        )
        self.con  = conn.cursor()
        self.conn = conn

    def domain_checker(self,domain):
        base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(domain))
        if base_url != domain:
            return False
        if base_url == domain:
            return True
    
    def double_entry(self,url,table):
        con  = self.con
        entrysql ="SELECT * FROM `{}` WHERE `url`='{}'".format(table,url) 
        con.execute(entrysql)
        if len(con.fetchall()) > 0:
            return False
        else:
            return True
    
    def get_domain(self,url):
        base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
        return base_url
    
    def make_link(self,url,base_url):
        if (url.find('http://') and url.find('https://')) == -1:
            url = base_url+url.replace("'","")
            return url
        else:
            return url
    
    def take_entry(self):
        conn = self.conn
        con = self.con
        print('taiking entry...')
        sql = "SELECT * FROM `entry` WHERE `status`='{}'".format(0)
        con.execute(sql)
        entry_data_all = con.fetchall()
        for link in entry_data_all:
            entry_data = link[1]
            entry_id = link[0]
            domain_soup = BeautifulSoup(requests.get(entry_data).text,'html.parser')
            if self.domain_checker(entry_data) ==True:
                typee = 0
            else:
                typee = 1
            print('scraping main entry..')
            try:
                title =domain_soup.title.text
                title = title.replace("'"," ")
            except:
                title =""
                print('title not found..')
            try:
                dis = domain_soup.select('meta[name="description"]')[0]['content']
                dis = dis.replace("'"," ")
            except:
                dis = ""
                print('meta Discription not fount')
            try:
                keywords = domain_soup.select('meta[name="keywords"]')[0]['content']
                keywords = keywords.replace("'"," ")
            except:
                keywords = ""
                print('Keywords not found..')
            sql1 = "INSERT INTO `crawl`(`entryid`, `url`, `title`, `dis`, `keywords`,`type`) VALUES ('{}','{}','{}','{}','{}','{}')".format(entry_id,entry_data,title,str(dis),keywords,typee)
            print(sql1)
            con.execute(sql1)
            conn.commit()
            print('main entry saved...')
            for link in domain_soup.find_all('a'):
                print('Colllecting links  form Page ')
                try:
                    base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(entry_data))
                    url = link['href']
                    if (url.find('http://') and url.find('https://')) == -1:
                        url = base_url+url.replace("'","")
                    else:
                        print('')
                except:
                    print('Somthing error????')
                print(url)
                if self.double_entry(url,"entry") == True:
                    try:
                        next_entry_sql = "INSERT  INTO `entry`(`url`,`status`) VALUES('{}','{}')".format(str(url),0)
                        con.execute(next_entry_sql)
                        conn.commit()
                        print('next another saved..')
                    except mysql.connector.Error as err:
                        print("Something went wrong: {}".format(err))
                else:
                    print('Site Already crawled')
            try:
                end_sql = "UPDATE `entry` SET `status`='{}'  WHERE `id`='{}'".format(1,entry_id)
                con.execute(end_sql)
                conn.commit()
                print('Entry updated')
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
            end = time.time()
            print('time'+str(end - start))
        
    def search(self,data):
        con = self.con 
        conn = self.conn
        search_sql  ="SELECT * FROM `crawl` WHERE `title` OR `dis` LIKE '%{}%' ".format(data)
        con.execute(search_sql)
        data = con.fetchall()
        return data
    def sitemap(self,url):
        con = self.con
        conn  =self.conn
        for a in BeautifulSoup(requests.get(url).text,"html.parser").find_all('a',href=True):
            link = self.make_link(a['href'],url)
            sitemap_sql = "".format()
if __name__ == '__main__':
    obj = crawler()
    obj.sitemap('https://www.fatbit.com/profie')
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import json
import dbConnect.dbConnector as couchbase

class Crawler:

    def __init__(self):
        #init webdriver (hiding)
        _option = webdriver.ChromeOptions()
        _option.add_argument('headless')
        _option.add_argument('window-size=1920x1080')
        _option.add_argument('disable-gpu')
        self._driver = webdriver.Chrome('chromedriver', chrome_options=_option)

        #get db user config
        with open('./util/dbConfig.json') as file_data:
            self._dbData = json.load(file_data)

        #init dbConnector
        print(self._dbData['username'])
        self._db = couchbase.DbConnect(self._dbData['username'], self._dbData['password'], self._dbData['bucket_name'])


        #user - _class / _id / nickname / reviews / isDummy
        self._user={
            '_class':'com.food_tripper.momuck.web.domain.User',
            'reviews':[],
            'isDummy':True
        }

        #restaurant - skip
        self._restaurant = {}

        #review - _class / _id / userid / restaurantid / rate / text
        self._review={
            '_class':'com.food_tripper.momuck.web.domain.Review'
        }

    #key modify (korean -> english)
    def _keyParsing(self, key):
        return{
            '주소':'address',
            '전화번호':'callNumber',
            '음식 종류':'category',
            '가격대':'price',
            '메뉴':'menu',
            '주차':'parking',
            '휴일':'holiday',
            '영업시간':'workTime',
            '쉬는시간':'breakTime',
            '마지막주문':'lastOrder'
        }.get(key, key)

    def _getReviewAndUserData(self, element, restaurant):
        _username = ''.join(str(element.find(class_='user big').find('figcaption').string).split())
        _userrate = ''.join(str(element.find(class_='icon-rating').find('strong').string).split())
        try:
            _content = ''.join(element.find(class_='short_review more_review_bind review_content').text.strip())
        except Exception as ex:
            _content = ''.join(element.find(class_='review_content ng-binding').text.strip())
        self._user['nickname'] = _username
        self._review['content'] = _content
        self._review['rate'] = _userrate #TODO : convert text formed rate TO number formed rate
        self._db.insertReview(self._review, self._user, restaurant)

    def _getRestaurantData(self, link):
        #open restaurant page
        self._driver.get('https://www.mangoplate.com' + link)

        #if restaurant already inserted -> needless to crwal
        check = BeautifulSoup(self._driver.page_source, 'html.parser')
        if(self._db.isExistRestaurant(check.find(class_='restaurant_name').string)):
            return

        #get all reviews
        _count = 5; #max number of reviews (at least5)
        try:
            while (self._driver.find_element_by_class_name('btn-reivews-more')):
                self._driver.find_element_by_class_name('btn-reivews-more').click() #click more review button
                self._driver.implicitly_wait(1) #wait page loaded
                _count+=5
        except Exception: #if button hide (all reviews shown)
            print(_count)

        _html = self._driver.page_source
        _soup = BeautifulSoup(_html, 'html.parser')

        self._restaurant.clear() #each restaurant data are different (ex. a:last order, but b isn't have last order)
        self._restaurant['_class']='com.food_tripper.momuck.web.domain.Restaurant' #used by Spring server
        self._restaurant['reviews']=[] #init reviews array

        #get restaurant name & score
        self._restaurant['restaurantName'] = _soup.find(class_='restaurant_name').string
        # if don't have score yet
        if(_soup.find(class_='rate-point') == None):
            self._restaurant['averageScore'] = None
        else:
            self._restaurant['averageScore'] = _soup.find(class_='rate-point').find('span').string

        #crawl restaurant data
        for element in _soup.find_all('tr'):
            if(element.find('td').string == None):
                if(element.find('td').find('span') != None):
                    self._restaurant[self._keyParsing(element.find('th').string)] = element.find('td').find('span').string
            else:
                self._restaurant[self._keyParsing(element.find('th').string)] = element.find('td').string

        #insert data into couchbase
        self._db.insertRestaurantData(self._restaurant)

        #crawl restaurant review data (+ dummy user)
        for element in _soup.find_all(class_='default_review ReviewItem'):
            self._getReviewAndUserData(element, self._restaurant)
        #hided reviews (when shown more button clicked)
        for element in _soup.find_all(class_='review-item ReviewItem'):
            self._getReviewAndUserData(element, self._restaurant)

    def crawlRestaurant(self):
        #open crwaling website
        with urllib.request.urlopen('https://www.mangoplate.com') as response:
            html = response.read()
            soup = BeautifulSoup(html,'html.parser')

        #find restaurant urls
        for element in soup.find_all(class_='restaurant-item'):
            # parsing restaurant info with urls
            for link in element.find_all('a'):
                self._getRestaurantData(link['href'])

    def __del__(self):
        self._driver.quit() #driver release
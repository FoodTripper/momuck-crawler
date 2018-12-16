from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator
import time

class DbConnect:

    #init
    def __init__(self, username, password, bucket_name):
        self._cluster = Cluster('couchbase://idc0.wiselight.kr:8091')
        self._authenticator = PasswordAuthenticator(username, password)
        self._cluster.authenticate(self._authenticator)
        self._bucket = self._cluster.open_bucket(bucket_name)
        print('connect')
        self._userIndex=self._setIndex('user')
        self._reviewIndex=self._setIndex('review')
        self._restaurantIndex=self._setIndex('restaurant')
        print(self._userIndex)
        print(self._reviewIndex)
        print(self._restaurantIndex)
        print('index initialize')

    def _setIndex(self, entity):
        try:
            for i in self._bucket.n1ql_query('SELECT count(_id) as _id FROM `momuck_dev` WHERE _id LIKE \'' + entity + ':%\''):
                index = i['_id']
                if(index == None):
                    print('raise')
                    raise Exception
            return index
        except Exception:
            return 0;

    def isExistRestaurant(self, restaurantName):
        try:
            for i in self._bucket.n1ql_query('SELECT restaurantName FROM `momuck_dev` WHERE restaurantName=\'' + restaurantName + '\''):
                name = i['restaurantName']
            name = str(name)
            return True #already exist -> not insert
        except Exception:
            return False #not exist -> insert

    def insertRestaurantData(self, restaurant):
        if(not self.isExistRestaurant(restaurant['restaurantName'])): #not exist -> insert
            index = str('restaurant:' + str(self._restaurantIndex))
            restaurant['_id']=index
            self._bucket.upsert(index, restaurant)
            self._restaurantIndex+=1

    def _getRestaurantId(self, restaurantName):
        # indexing review's restaurant id
        # return restaurant id
        try:
            for i in self._bucket.n1ql_query('SELECT _id FROM `momuck_dev` WHERE restaurantName=\'' + restaurantName + '\''):
                return i['_id']
        except Exception:
            print('getRestaurantId')
            return None

    def _updateRestaurant(self, reviewId, restaurantId):
        try:
            for i in self._bucket.n1ql_query('UPDATE `momuck_dev` SET reviews=array_insert(reviews, array_length(reviews), \'' + reviewId + '\') WHERE _id=\'' + restaurantId + '\''):
                print('updateRestaurant')
        except Exception:
            print('updateRestaurant_Exception')
        #update `momuck_dev` set uptest=['uptest1'] where test='test1' = update query
        #update `momuck_dev` set uptest=array_insert(uptest, -1,'test???') where test='test1' = update query (insert add)
        #update `momuck_dev` set uptest=array_insert(uptest, array_length(uptest),'test???') where test='test1' = concat back (same upside)

    def _isExistUser(self, userName):
        try:
            nickname = ''
            for i in self._bucket.n1ql_query('SELECT nickname FROM `momuck_dev` WHERE nickname=\'' + userName + '\''):
                nickname = i['nickname']
            if(nickname.__len__()==0):
                raise  Exception
            return True #already exist -> not insert
        except Exception:
            return  False #not exist -> insert

    def _insertUser(self, user):
        index = str('user:' + str(self._userIndex))
        user['_id']=index
        self._bucket.upsert(index, user)
        self._userIndex+=1
        print('insert user')
        #needless to check (call by insert review - already checked)

    def _getUserId(self, userName):
        # indexing review's userId
        # return user id
        try:
            for i in self._bucket.n1ql_query('SELECT _id FROM `momuck_dev` WHERE nickname=\'' + userName + '\''):
                return i['_id']
        except Exception:
            print('getUserId')
            return None

    def _updateUser(self, reviewId, userId):
        try:
            for i in self._bucket.n1ql_query('UPDATE `momuck_dev` SET reviews=array_insert(reviews, array_length(reviews), \'' + reviewId + '\') WHERE _id=\'' + userId + '\''):
                print('updateUser')
        except Exception:
            print('updateUser_Exception')

    def insertReview(self, review, user, restaurant):
        print(self._isExistUser(user['nickname']))
        if(not self._isExistUser(user['nickname'])): #not exist -> insert
            self._insertUser(user)
        time.sleep(0.3)
        #user create done. insert review -> update user & restaurant
        index = str('review:' + str(self._reviewIndex))
        review['userId']=self._getUserId(user['nickname'])
        review['restaurantId']=self._getRestaurantId(restaurant['restaurantName'])
        review['_id']=index
        print(index + ', ' + review['restaurantId'] + ', ' + review['userId'])
        self._bucket.upsert(index, review)
        self._updateRestaurant(index, review['restaurantId'])
        self._updateUser(index, review['userId'])
        self._reviewIndex+=1

        #checking user exist
        #exist -> insert review -> update user & restaurant
        #not -> create user -> insert review -> update user & restaurant

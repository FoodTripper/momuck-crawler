import unittest
import dbConnect.dbConnector as db
# from couchbase import Couchbase
from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator

cluster=Cluster('couchbase://idc0.wiselight.kr:8091')
authenticator=PasswordAuthenticator('momuck_dev','1q2w3e')
print(authenticator)
print(cluster)
cluster.authenticate(authenticator)
bucket=cluster.open_bucket('momuck_dev')

try:
    rv = bucket.get('0')
    print(rv.value)
except Exception as ex:
    print('exception')

print('out?')

# for i in bucket.n1ql_query('select test from `momuck_dev` where test like \'atest%\' order by test desc limit 1'):
#     print(i['test'])


# test = 'test'
# for i in bucket.n1ql_query('select test from `momuck_dev` where test like \''+test+'%\' order by test desc limit 1'):
#     a = i['test']
#
# a = a.replace('test', '')
# a = str(a)
#
# print(a)
# print(type(a))

a ={
    'asdf' : 'asdf'
}

b={
    'ssss' : 'ssss'
}

c = a['asdf']

print(c.__len__())


# bucket.upsert('test', {'name':'test'})
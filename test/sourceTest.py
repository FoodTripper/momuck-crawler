import json

with open('../util/dbConfig.json') as file_data:
    data = json.load(file_data)

print(data['username'])
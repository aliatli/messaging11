import pymongo
'''
client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hg8mo.mongodb.net/deneme?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")

db = client.test

'''

class Persistency:

    def __init__(self):
        self.name  = 'mongo'
        self.client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hg8mo.mongodb.net/deneme?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
        self.db = self.client.deneme
        self.col = self.db.col

    def save_message(self, message):
        self.col.insert_one(message)
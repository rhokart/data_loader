
import pymongo

def MongoConn():
    client = pymongo.MongoClient("mongodb+srv://numeroclick1:kBq5myBBYZb0E25w@cluster0.6dirr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    database = client["rhokart"]
    return database



class MongoConfig:
    def __init__(self):
        pass
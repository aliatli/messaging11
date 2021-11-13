import json
import pymongo

# class that handles communication with mongodb
class Persistency:
    """
    {"HISTORY_DEPTH":"ALL", "SEARCH_STRING":"", "DIRECTION":"BOTH"}
    """

    def __init__(self):
        self.name = 'mongo'
        # mongo atlas cluster client
        self.client = pymongo.MongoClient(
            "mongodb+srv://admin:admin@cluster0.hg8mo.mongodb.net/deneme?retryWrites=true&"
            "w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
        self.db = self.client.deneme
        self.collection = self.db.messages

    # save message to mongo
    def save_message(self, message):
        message['_id'] = self.collection.count() + 1
        self.collection.insert_one(message)

    # figure out how many documents we skip
    def get_skip_size(self, dict_message):
        # total num of inserted messages
        document_size = self.collection.count()
        # how many documents from the beginning do we skip
        try:
            skip_size = 0 if dict_message['HISTORY_DEPTH'] == 'ALL' else document_size - int(
                dict_message['HISTORY_DEPTH'])
        except Exception as e:
            return None
        return {'$gt': skip_size}

    # construct query for SEARCH_STRING in case insensitive manner
    def get_search_string_query(self, dict_message):
        # do not put a condition for this type
        if len(dict_message['SEARCH_STRING']) == 0:
            return None
        else:
            return {'$regex': dict_message['SEARCH_STRING'], '$options': 'i'}

    # get query for ip,port matching for a client
    def get_connection_query(self, query_sub_message, original_message):
        conditions = []
        # sent or received
        if query_sub_message['DIRECTION'] == 'BOTH':
            conditions.append({'SENDER': original_message['SENDER']})
            conditions.append({'RECEIVER': original_message['SENDER']})
        # sent messages
        elif query_sub_message['DIRECTION'] == 'UP':
            conditions.append({'SENDER': original_message['SENDER']})
        # received messages
        elif query_sub_message['DIRECTION'] == 'DOWN':
            conditions.append({'RECEIVER': original_message['SENDER']})
        else:
            return None

        return conditions

    # execute filter
    def filter_message(self, original_message):
        # unwrap message
        original_message_body_dict = json.loads(original_message['BODY'])
        result = []
        # construct individual
        skip_size = self.get_skip_size(original_message_body_dict)
        string_query = self.get_search_string_query(original_message_body_dict)
        connection_query = self.get_connection_query(original_message_body_dict, original_message)

        # if connection_query is None, somehow do nothing
        if connection_query is None or skip_size is None:
            print('The query is crafted erroneously!')
            return

        # execute the filter
        if string_query is None:
            posts = self.collection.find({'_id': skip_size, '$or': connection_query})
        else:
            posts = self.collection.find({'_id': skip_size, 'BODY': string_query, '$or': connection_query})

        # aggregate and return
        for post in posts:
            result.append(post)
        return result

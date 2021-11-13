import json
import struct
import time

# UTF-8 is supposed to handle all kinds of characters
FORMAT = 'UTF-8'


# convert text message to dict with meta-data
def convert_to_dict(socket, message, message_type):
    # python native representation
    dictionary_representation = {'TYPE': message_type,
                                 'EPOCH_TIME': int(time.time()),
                                 'SENDER': socket.getsockname(),
                                 'RECEIVER': socket.getpeername(),
                                 'BODY': message}
    return dictionary_representation


# convert text message to json with meta-data
def convert_to_json(socket, message, message_type):
    # convert it to json object
    return json.dumps(convert_to_dict(socket, message, message_type), ensure_ascii=False)


# check if query string is valid json
def check_valid_json(msg):
    try:
        json.loads(msg)
    except ValueError as e:
        print(e.args)
        return False
    return True


# check if json is a valid query
# example {"HISTORY_DEPTH":"10", "DIRECTION":"BOTH", "SEARCH_STRING":"a"}
def check_valid_query(msg):
    dict_obj = json.loads(msg)

    # it must have these fields.
    if dict_obj.get('HISTORY_DEPTH') is None \
            or dict_obj.get('SEARCH_STRING') is None \
            or dict_obj.get('DIRECTION') is None \
            or len(dict_obj.keys()) != 3:
        return False

    # history depth can be non-negative integer or 'ALL'
    if not dict_obj['HISTORY_DEPTH'].isdigit() and not dict_obj['HISTORY_DEPTH'] == 'ALL':
        return False
    if dict_obj['HISTORY_DEPTH'].isdigit() and int(dict_obj['HISTORY_DEPTH']) == 0:
        return False

    # direction can have up, down and both values only
    if dict_obj['DIRECTION'] != 'UP' and dict_obj['DIRECTION'] != 'DOWN' and dict_obj['DIRECTION'] != 'BOTH':
        return False

    # search_string can have any value, empty string means to not apply this filter
    return True


# function that does sending
def send_message(socket, json_msg):
    while True:
        # encode json with utf-8
        message = bytes(f"{json_msg}", FORMAT)
        # Prefix each message with a 4-byte length (network byte order)
        message = struct.pack('>I', len(message)) + message
        socket.send(message)
        break

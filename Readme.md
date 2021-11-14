# Instructions
## Installation

Following instructions have been tested on Ubuntu 18.04.



- sudo apt install python3 &&
- sudo apt install python3-pip &&
- sudo apt install python3-tk
- pip3 install pymongo[srv]

The persistency layer uses mongodb database which runs on mongodb atlas cluster with approximately 500MB of free space, therefore, no additional steps should be needed.

## Execution
You can run the client and server with:
 
    python3 server.py <server_port>

    python3 client.py <server_ip> <server_port>
    
 Spawning the client will result in opening the chat window for both peers. You can start more than one client to see that client cannot query another client's messages, this results in opening new window for the server as well for this newly created client.
 
    



## Query Format
The format of the query is as follows:

    {"HISTORY_DEPTH":["ALL" | "{positive integer}"], "SEARCH_STRING":[""| "{any UTF-8 string}"], "DIRECTION":["BOTH"|"UP"|"DOWN"]}
- Note: {positive integer} and {any UTF-8 string} must be enclosed with quotation marks(" ").
- Note: you can use double escape (\ \ \") for quotes.

In order to fetch all messages that are either received or sent, one can use the following query:
    
    {"HISTORY_DEPTH":"ALL", "SEARCH_STRING":"", "DIRECTION":"BOTH"}

The idea is to use the most generic values for the query, which is behaviorally equivalent to not applying any filter with the exception that the resulting messages are either received or sent by the searching peer.

One can use default values for each filter in any combination, for instance:
    
    {"HISTORY_DEPTH":"ALL", "SEARCH_STRING":"hello", "DIRECTION":"UP"}
    {"HISTORY_DEPTH":"ALL", "SEARCH_STRING":"", "DIRECTION":"UP"}
    and etc.

The result of the search is saved to a file in json format and the name of the file is printed on the GUI
The message bodies are printed to terminal.

In case the entered query does not conform the format, error messages with likely reasons are printed on the terminal.




#coding: utf-8

import socket
import base64
import hashlib
import struct
import threading


class websocket_thread(threading.Thread):
    'ceshi,ceshi2'
    def __init__(self, connection):
        super(websocket_thread, self).__init__()
        self.connection = connection
        print("web_socket_thread inited")



    def run(self):
        while True:
            try:
                data = self.connection.recv(1024)
                if 0 == len(data):
                    continue
            except Exception as e:
                print("exception : " + str(e))
                break
            print(data)
            data = self.parse_data(data)
            if len(data) == 0 :
                continue
            # message = self.username + " : " + data
            # notify(message)
            print("client : " + data)
            self.sendMessage(str(data))



    def parse_data(self, data):
        v = data[1] & 0x7f
        if v == 0x7e:
            p = 4
        elif v == 0x7f:
            p = 10
        else:
            p = 2
        mask = data[p: p+4]
        data = data[p+4:]
        print(data)
        i = 0
        raw_str = ""
        for d in data:
            raw_str += chr(d ^ mask[i%4])
            i += 1
        return raw_str
        # return ''.join([chr(str(v ^ ord(mask[k % 4])) for k, v in enumerate(data)])


    def sendMessage(self, message):
        msgLen = len(message)
        backMsgList = []
        backMsgList.append(struct.pack('B', 129))

        if msgLen <= 125:
            backMsgList.append(struct.pack('b', msgLen))
        elif msgLen <=65535:
            backMsgList.append(struct.pack('b', 126))
            backMsgList.append(struct.pack('>h', msgLen))
        elif msgLen <= (2^64-1):
            backMsgList.append(struct.pack('b', 127))
            backMsgList.append(struct.pack('>h', msgLen))
        else :
            print("the message is too long to send in a time")
            return
        message_byte = bytes()
        print(type(backMsgList[0]))
        for c in backMsgList:
            # if type(c) != bytes:
            # print(bytes(c, encoding="utf8"))
            message_byte += c
        message_byte += bytes(message, encoding="utf8")
        print("message_str : ", str(message_byte))
        
        # print("message_byte : ", bytes(message_str, encoding="utf8"))
        # print(message_str[0], message_str[4:])
        # self.connection.send(bytes("0x810x010x63", encoding="utf8"))
        self.connection.send(message_byte)

def deal_recv(con):
    try:
        allData = con.recv(1024)
        if not len(allData):
            print("no data")
            return False
    except:
        print("exception")
        return False
    print("recv data")
    codeLen = ord(allData[1]) & 127
    if codeLen == 126:
        mask = allData[4:8]
        data = allData[8:]
    elif codeLen == 127:
        mask = allData[10:14]
        data = allData[14:]
    else :
        mask = allData[2:6]
        data = allData[6:]
    raw_str = ""
    i = 0
    for d in data:
        raw_str += chr(d ^ ord(mask[i%4]))
        i += 1
    print(raw_str)

def send_data(con, data):
    if data:
        data = str(data)
    else:
        print("not data to send")
        return False
    token = bytes("\x81", encoding="utf8")
    length = len(data)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xffff:
        token += struct.pack("!BH", 126, length)
    else :
        token += struct.pack("!BQ", 127, length)
    data = "%s%s" % (token, data)
    con.send(bytes(data, encoding="utf8"))
    print("send data done")

if __name__ == "__main__":
    # class websocketServer:
    #     def __init__(self):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = ("127.0.0.1", 8124)
    serverSocket.bind(host)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.listen(5)
    print("server running")
    while True:
        print("getting connection")
        clientSocket, addressInfo = serverSocket.accept()
        print("get connected")
        receivedData = str(clientSocket.recv(2048))
        print(receivedData)
        entities = receivedData.split("\\r\\n")
        # print(entities[9].split(":")[1].strip())
        origin = str(entities[7].split(":", 1)[1])
        # print(origin)
        Sec_WebSocket_Key = entities[11].split(":")[1].strip() + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        print("key ", Sec_WebSocket_Key)
        response_key = base64.b64encode(hashlib.sha1(bytes(Sec_WebSocket_Key, encoding="utf8")).digest())
        response = "HTTP/1.1 101 Web Socket Protocol Handshake\r\n\
                    Access-Control-Allow-Credentials: true\r\n\
                    Access-Control-Allow-Headers: x-websocket-protocol\\r\\n\
                    Access-Control-Allow-Headers: x-websocket-version\r\n\
                    Access-Control-Allow-Headers: x-websocket-extensions\r\n\
                    Access-Control-Allow-Headers: authorization\r\n\
                    Access-Control-Allow-Headers: content-type\r\n\
                    Access-Control-Allow-Origin: http://localhost\r\n\
                    Upgrade: websocket\r\n\
                    Connection: Upgrade\r\n\
                    Sec-WebSocket-Version: 13\r\n\
                    Sec-WebSocket-Accept: " + str(response_key) +"\r\n\
                    WebSocket-Origin:"+origin+"\r\n\
                    Pragma: no-cache\r\n\
                    Cache-Control: no-cache\r\n\r\n"
        response_key_str = str(response_key)
        response_key_str = response_key_str[2:30]
        # print(response_key_str)
        response_key_entity = "Sec-WebSocket-Accept: " + response_key_str +"\r\n"
        clientSocket.send(bytes("HTTP/1.1 101 Web Socket Protocol Handshake\r\n", encoding="utf8"))
        clientSocket.send(bytes("Upgrade: websocket\r\n", encoding="utf8"))
        clientSocket.send(bytes(response_key_entity, encoding="utf8"))
        clientSocket.send(bytes("Connection: Upgrade\r\n\r\n", encoding="utf8"))

        # clientSocket.send(bytes("\r\n", encoding="utf8"))
        # clientSocket.send(bytes(response, encoding="utf8"))

        print("send the hand shake data")
        # send_data(clientSocket, "ppppppppp\r\n")
        # clientSocket.close()
        websocket_thread(clientSocket).start()
        # clientSocket.send(bytes("sssssssssss", encoding="utf8"))
        # break



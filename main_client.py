
#Copyright (c) 2022 Tomato Lycoris

from pythonosc import udp_client
from lib.OscMmvcClient import * 
from lib.OscMmvcServer import * 


if __name__ == "__main__":
    server = OscMmvcClient("127.0.0.1",9001)
    client = OscMmvcServer("127.0.0.1",9000,server)
    server.SetServer()
    client.MoveThreading()
    try:
        server.server.serve_forever()
    except KeyboardInterrupt:
        client.MOVE_THREADING = False
        client.thread.join(1)

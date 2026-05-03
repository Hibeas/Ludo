import socket
import threading
import json
from game_logic import Pawn
from round import GameManager
import constants
import sys

HOST='0.0.0.0'
PORT=6767
MAX_PLAYERS=2

class LudoServer:
    def __init__(self):
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST,PORT))
        self.server.listen(MAX_PLAYERS)

        self.game_manager=GameManager(players=['blue','green'])
        self.pawns= {
            'blue': [Pawn('blue',i,constants.BLUE_START[i-1], load_image=False) for i in range(1,5)],
            'green': [Pawn('green',i,constants.GREEN_START[i-1], load_image=False) for i in range(1,5)]
        }

        self.clients=[]
        self.lock=threading.Lock()
    
    def sendMessage(self,message):
        data=json.dumps(message).encode('utf-8')
        for client in self.clients:
            try:
                client.sendall(data)
            except:
                self.clients.remove(client)

    def getState(self):
        all_pawns_data=[]
        for  color in self.pawns:
            for p in self.pawns[color]:
                all_pawns_data.append(p.to_dict())

        return {
            "type": "UPDATE",
            "current_turn": self.game_manager.get_current_player(),
            "game_state": self.game_manager.state,
            "pawns": all_pawns_data
        }
    
    def handleClient(self, conn, addr, player_color):
        print(f"CLIENT {player_color} HAS CONNECTED!")
        self.clients.append(conn)

        connected=True
        while connected:
            try:
                data=conn.recv(1024).decode('utf-8')
                if not data:
                    break
            except:
                connected=False

        conn.close()
        if conn in self.clients:
            self.clients.remove(conn)
        print(f"PLAYER {addr} HAS BEEN DISCONNECTED!")
    
    def run(self):
        print(f"SERVER STARTED ON PORT {PORT}")
        accept_thread=threading.Thread(target=self.acceptConnection, daemon=True)
        accept_thread.start()

        while True:
            cmd=input()
            if cmd.lower()=='exit':
                print("SHUTTING SERVER DOWN!")
                self.sendMessage({"type": "SERVER_STOPPED", "message": "Server is closing."})
                for client in self.clients:
                    client.close()
                self.server.close()
                sys.exit()

    def acceptConnection(self):
        player_colors=['blue','green']
        try:
            while len(self.clients)<MAX_PLAYERS:
                conn,addr=self.server.accept()
                color=player_colors[len(self.clients)]
                thread=threading.Thread(target=self.handleClient, args=(conn, addr, color))
                thread.start()
        except:
            pass

if __name__=="__main__":
    server=LudoServer()
    server.run()
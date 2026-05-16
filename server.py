import socket
import threading
import json
from game_logic import Pawn
from round import GameManager
import constants
import sys
import random

#TCP logic
HOST='0.0.0.0'
PORT=6767
MAX_PLAYERS=2

class LudoServer:
    #server initialization
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
    
    #sending a message to all clients
    def sendMessage(self,message):
        data=json.dumps(message).encode('utf-8')
        for client in self.clients:
            try:
                client.sendall(data)
            except:
                self.clients.remove(client)

    #getting state of all pawns (updating the board)
    def getState(self):
        all_pawns_data=[]
        for color in self.pawns:
            for p in self.pawns[color]:
                all_pawns_data.append(p.to_dict())

        return {
            "type": "UPDATE",
            "current_turn": self.game_manager.get_current_player(),
            "game_state": self.game_manager.state,
            "pawns": all_pawns_data
        }
    
    #handling client connection
    def handleClient(self, conn, addr, player_color):
        print(f"CLIENT {player_color} HAS CONNECTED!")
        self.clients.append(conn)

        connected=True
        #during the game
        while connected:
            try:
                data=conn.recv(1024).decode('utf-8')
                if not data:
                    break
                mess=json.loads(data)
                #moving a pawn
                if mess["action"]=="MOVE":
                    with self.lock:
                        #cheating-green tries to move blue or vice versa
                        if player_color != self.game_manager.get_current_player():
                            print(F"DON'T CHEAT {player_color}!")
                            continue
                        p_id=mess["pawn_id"]
                        steps=getattr(self,'last_roll',0)

                        #checks which pawn is moving
                        pawn_moving=next(p for p in self.pawns[player_color] if p.pawn_id==p_id)

                        all_pawns=self.pawns['blue']+self.pawns['green']
                        #actually moving a pawn
                        if pawn_moving.move(steps,all_pawns):
                            self.game_manager.next_turn()
                            self.last_roll = 0
                            self.sendMessage(self.getState())
                #rolling a dice
                elif mess["action"]=="ROLL":
                    with self.lock:
                        if player_color==self.game_manager.get_current_player():
                            #forced value-6/1 (for presentation purposes only!)
                            forced_value=mess.get("forced_val")
                            if forced_value:
                                dice_val=forced_value
                            else:
                                dice_val=random.randint(1,6) #this is not a forced value
                            self.last_roll=dice_val
                            self.sendMessage({
                                "type": "DICE_RESULT",
                                "value": dice_val,
                                "player": player_color,
                                "is_forced":forced_value is not None
                            })
                #skip-pressing s
                elif mess["action"]=="SKIP":
                    with self.lock:
                        if player_color==self.game_manager.get_current_player():
                            self.game_manager.next_turn()
                            self.sendMessage(self.getState())
            except json.JSONDecodeError:
                print("WRONG DATA FORMAT IN JSON!")
            except Exception as e:
                print(e)
                connected=False

        #closing the connection
        conn.close()
        if conn in self.clients:
            self.clients.remove(conn)
        print(f"PLAYER {addr} HAS BEEN DISCONNECTED!")
    
    #running the server
    def run(self):
        print(f"SERVER STARTED ON PORT {PORT}")
        accept_thread=threading.Thread(target=self.acceptConnection, daemon=True)
        accept_thread.start()

        #waiting for "exit" command which shuts down the server
        while True:
            cmd=input()
            if cmd.lower()=='exit':
                print("SHUTTING SERVER DOWN!")
                self.sendMessage({"type": "SERVER_STOPPED", "message": "Server is closing."})
                for client in self.clients:
                    client.close()
                self.server.close()
                sys.exit()

    #acception a connection from client
    def acceptConnection(self):
        player_colors=['blue','green']
        try:
            #only while we have less than 2 players
            while len(self.clients)<MAX_PLAYERS:
                conn,addr=self.server.accept()
                color=player_colors[len(self.clients)]
                conn.sendall(json.dumps({"type": "ASSIGNED_COLOR", "color": color}).encode('utf-8'))
                thread=threading.Thread(target=self.handleClient, args=(conn, addr, color))
                thread.start()
        except:
            pass

#very simple main
if __name__=="__main__":
    server=LudoServer()
    server.run()
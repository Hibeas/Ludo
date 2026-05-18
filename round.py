class GameManager:
    #initialization
    def __init__(self, players):
        self.players = players 
        self.current_player_index = 0
        self.state = "WAITING_FOR_ROLL" # States: ROLLING, MOVING, END_TURN

    #getting current player (color)
    def getCurrentPlayer(self):
        return self.players[self.current_player_index]

    # changing player
    def nextTurn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.state = "WAITING_FOR_ROLL"
        print(f"It is now {self.getCurrentPlayer()}'s turn!")
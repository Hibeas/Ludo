class GameManager:
    def __init__(self, players):
        self.players = players 
        self.current_player_index = 0
        self.state = "WAITING_FOR_ROLL" # States: ROLLING, MOVING, END_TURN

    def get_current_player(self):
        return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.state = "WAITING_FOR_ROLL"
        print(f"It is now {self.get_current_player()}'s turn!")
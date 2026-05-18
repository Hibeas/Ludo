import pygame
from game_logic import Pawn, Dice
import constants
import threading
import socket
import json

def refreshPawnStacks(pawns_list):
	pos_map = {}
	for p in pawns_list:
		if p.position > 0:
			idx = p.board_index
			if idx not in pos_map: pos_map[idx] = []
			pos_map[idx].append(p)
		else:
			p.updateImage(1) # Reset those in yard or home

	for idx, stacked in pos_map.items():
		count = len(stacked)
		for p in stacked:
			p.updateImage(count)
            

#TCP connection
HOST='127.0.0.1'
PORT=6767

# Pygame setup
pygame.init()
pygame.display.set_caption('Ludo Game')
clock = pygame.time.Clock()
game_status = True
pygame.font.init()

main_font = pygame.font.SysFont("Arial", 24)
title_font = pygame.font.SysFont("Arial", 32, bold=True)

#individual client color
my_color = None
winner_color = None
walkover = False

#drawing the game window
def drawInfoPanel(surface, turn, dice_val, waiting):
    sidebar_rect = pygame.Rect(800, 0, constants.SIDEBAR_WIDTH, 800)
    pygame.draw.rect(surface, (40, 40, 40), sidebar_rect)
    pygame.draw.line(surface, (200, 200, 200), (800, 0), (800, 800), 3) 

    color_map = {"blue": (100, 100, 255), "green": (100, 255, 100)}
    if winner_color:
        victory_box = pygame.Rect(810, 20, 280, 200)
        pygame.draw.rect(surface, (50, 20, 20) if winner_color == "blue" else (20, 50, 20), victory_box)
        pygame.draw.rect(surface, (255, 215, 0), victory_box, 3)
        
        win_title = title_font.render("VICTORY!", True, (255, 215, 0))
        win_text = main_font.render(f"PLAYER {winner_color.upper()}", True, (255, 255, 255))
        win_desc = main_font.render("HAS WON THE GAME!", True, (255, 255, 255))
        if walkover:
            win_walkover = main_font.render("Through Walkover!", True, (255, 100, 100))
        
        surface.blit(win_title, (830, 40))
        surface.blit(win_text, (830, 90))
        surface.blit(win_desc, (830, 130))
        if walkover:
            surface.blit(win_walkover, (830, 170))
        return

    if my_color:
        me_text=main_font.render(f"YOU ARE: {my_color.upper()}",True,color_map[my_color])
        surface.blit(me_text, (820, 10))
    turn_text = title_font.render(f"TURN: {turn.upper()}", True, color_map[turn])
    surface.blit(turn_text, (820, 50))

    if not waiting:
        status = "Press SPACE to Roll"
    else:
        status = f"Rolled: {dice_val}! Click a pawn."
    
    instr_text = main_font.render(status, True, (255, 255, 255))
    surface.blit(instr_text, (820, 120))

    controls = [
        "How to play:",
        "- Roll a 6 to start",
        "- Click pawn to move",
        "- Press 'S' to skip turn",
        "",
        "Debug keys:",
        "1 or 6: Force roll"
    ]
    
    for i, line in enumerate(controls):
        line_text = main_font.render(line, True, (180, 180, 180))
        surface.blit(line_text, (820, 250 + (i * 35)))
    if current_turn==my_color:
        msg=main_font.render("YOUR TURN!",True,(0,255,0))
        surface.blit(msg,(820,100))

# listening to server messages
def listenToServer(client_socket):
	global current_turn,all_pawns,waiting_for_move, my_color, steps, game_status, winner_color, walkover
	buffer = ""

	while True:
		try:
			data=client_socket.recv(4096)
			if not data:
				print("Lost connection.")
				game_status=False
				break
			buffer += data.decode('utf-8')
			while "\n" in buffer:
				line, buffer = buffer.split("\n", 1)
                
				if not line.strip(): 
					continue
				mess = json.loads(line)
				#handling connection break
				if mess["type"] == "SERVER_STOPPED":
					print(f"Game Over: {mess['message']}")
					game_status = False
					break
				
				elif mess["type"] == "DISCONNECTED":
					print(f"Opponent disconnected: {mess['message']}")
					global waiting_for_move
					if mess.get("color") == "blue":
						winner_color = "green"
					else:
						winner_color = "blue"
					walkover = True
					waiting_for_move = False 
				elif mess["type"] == "GAME_WON":
					print(mess["message"])
					winner_color = mess["winner"]
					waiting_for_move = False
				#assigning color (blue/green)
				if mess["type"]=="ASSIGNED_COLOR":
					my_color=mess["color"]
				#getting dice result
				elif mess["type"]=="DICE_RESULT":
					my_dice.final_server_value=mess["value"]
					#for forced value-1/6 (just for presentation purposes)
					if mess.get("is_forced"):
						my_dice.current_value=mess["value"]
						my_dice.is_rolling=False
						my_dice.new_value=True
					# normal roll
					else:
						my_dice.startRoll()
					if mess["player"]==my_color:
						waiting_for_move=True
					steps=mess["value"]
				#updating the board
				elif mess["type"]=="UPDATE":
					for pawn_data in mess["pawns"]:
						for local in all_pawns:
							if local.color==pawn_data["color"] and local.pawn_id==pawn_data["pawn_id"]:
								local.position=pawn_data["new_pos"]
								local.board_index=pawn_data["board_index"]
								local.updateScreenPos(local.board_index)
					refreshPawnStacks(blue_pawns)
					refreshPawnStacks(green_pawns)

					current_turn=mess["current_turn"]
					waiting_for_move=False
					steps=0
		except Exception as e:
			print(f"Network error in client loop: {e}")
			break


# Game assets and objects
screen_surface = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
board_image = pygame.image.load("assets/board.png").convert()
board_image = pygame.transform.scale(board_image, (constants.GAME_WIDTH, constants.SCREEN_HEIGHT))
my_dice = Dice((400, 400))
green_pawns = [Pawn("green", i, constants.GREEN_START[i-1], load_image=True) for i in range(1, 5)]
blue_pawns = [Pawn("blue", i, constants.BLUE_START[i-1], load_image=True) for i in range(1, 5)]
all_pawns = green_pawns + blue_pawns
rolled_value = 0
current_turn = "blue"
waiting_for_move = False

#TCP connection
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
    threading.Thread(target=listenToServer,args=(client,),daemon=True).start()
except Exception as e:
    print(f"Could not connect to server at {HOST}:{PORT} - {e}")
    game_status = False

#actual game
while game_status:
	events = pygame.event.get()
	#different keys
	for event in events:
		if event.type == pygame.QUIT:
			game_status = False
		if not winner_color:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and current_turn==my_color and not waiting_for_move:
					client.sendall((json.dumps({"action": "ROLL"}) + "\n").encode('utf-8'))
				if event.key == pygame.K_1 and current_turn==my_color and not waiting_for_move:
					client.sendall((json.dumps({"action": "ROLL", "forced_val": 1}) + "\n").encode('utf-8'))
				if event.key == pygame.K_6 and current_turn==my_color and not waiting_for_move:
					client.sendall((json.dumps({"action": "ROLL", "forced_val": 6}) + "\n").encode('utf-8'))
				if event.key == pygame.K_s and current_turn==my_color and waiting_for_move:
					client.sendall((json.dumps({"action": "SKIP"}) + "\n").encode('utf-8'))
		
		
			if event.type == pygame.MOUSEBUTTONDOWN and waiting_for_move:
				mouse_pos = event.pos
				
				active_pawns = blue_pawns if current_turn == "blue" else green_pawns
				
				#moving a pawn by clicking it
				for pawn in active_pawns:
					if pawn.rect.collidepoint(mouse_pos):
						move_request={
							"action": "MOVE",
							"pawn_id": pawn.pawn_id
						}
						client.sendall((json.dumps(move_request) + "\n").encode('utf-8'))
						break
	dice_score = my_dice.update() 
	#waiting for a move
	if not my_dice.is_rolling and my_dice.current_value > 0 and my_dice.new_value: 
		steps = my_dice.current_value
		my_dice.new_value = False
		waiting_for_move = True	
		print(f"Waiting for {current_turn} to click a pawn. Rolled: {my_dice.current_value}")

	screen_surface.blit(board_image, (0, 0))

	for pawn in all_pawns:
		pawn.draw(screen_surface)
	my_dice.draw(screen_surface)
	drawInfoPanel(screen_surface, current_turn, my_dice.current_value, waiting_for_move)
	pygame.display.update()
	clock.tick(60)


print("Closing the game...")
pygame.quit()
quit()
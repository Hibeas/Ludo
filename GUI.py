import pygame
from game_logic import Pawn, Dice
import constants
import threading
import socket
import json

def refresh_pawn_stacks(pawns_list):
    pos_map = {}
    for p in pawns_list:
        if p.position > 0 and not p.is_home:
            idx = p.board_index
            if idx not in pos_map: pos_map[idx] = []
            pos_map[idx].append(p)
        else:
            p.update_image(1) # Reset those in yard or home

    for idx, stacked in pos_map.items():
        count = len(stacked)
        for p in stacked:
            p.update_image(count)
            


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

my_color = None

def draw_info_panel(surface, turn, dice_val, waiting):
    sidebar_rect = pygame.Rect(800, 0, constants.SIDEBAR_WIDTH, 800)
    pygame.draw.rect(surface, (40, 40, 40), sidebar_rect)
    pygame.draw.line(surface, (200, 200, 200), (800, 0), (800, 800), 3) 

    color_map = {"blue": (100, 100, 255), "green": (100, 255, 100)}
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

def listenToServer(client_socket):
	global current_turn,all_pawns,waiting_for_move, my_color, steps
	while True:
		try:
			data=client_socket.recv(4096).decode('utf-8')
			if not data:
				break
			mess=json.loads(data)

			if mess["type"]=="ASSIGNED_COLOR":
				my_color=mess["color"]
			elif mess["type"]=="DICE_RESULT":
				my_dice.final_server_value=mess["value"]
				if mess.get("is_forced"):
					my_dice.current_value=mess["value"]
					my_dice.is_rolling=False
					my_dice.new_value=True
				else:
					my_dice.start_roll()
				if mess["player"]==my_color:
					waiting_for_move=True
				steps=mess["value"]
			elif mess["type"]=="UPDATE":
				for pawn_data in mess["pawns"]:
					for local in all_pawns:
						if local.color==pawn_data["color"] and local.pawn_id==pawn_data["pawn_id"]:
							local.position=pawn_data["new_pos"]
							local.board_index=pawn_data["board_index"]
							local.update_screen_pos(local.board_index)
				refresh_pawn_stacks(blue_pawns)
				refresh_pawn_stacks(green_pawns)

				current_turn=mess["current_turn"]
				waiting_for_move=False
				steps=0
		except:
			break
#okay we need to now whos turn it is if its on one pc it will jsut change the turn after the player rolls the dice and moves but if its on two pcs we need to send the 
# data to the other pc and then change the turn there as well. we will sent it using dictionariues and json 


#what need to be done - check czy zbiajnie dziala na 2 pionki na sobie, add ile pionkow na polu jesli >2 (zeby pokazac ze sa 2 piuonki na sobie), adnimation better graphic ext, and winning


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

#ALSO TCP!!!!!
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

threading.Thread(target=listenToServer,args=(client,),daemon=True).start()

while game_status:
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			game_status = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE and current_turn==my_color and not waiting_for_move:
				client.sendall(json.dumps({"action": "ROLL"}).encode('utf-8'))
			if event.key == pygame.K_1 and current_turn==my_color and not waiting_for_move:
				client.sendall(json.dumps({"action": "ROLL", "forced_val": 1}).encode('utf-8'))
			if event.key == pygame.K_6 and current_turn==my_color and not waiting_for_move:
				client.sendall(json.dumps({"action": "ROLL", "forced_val": 6}).encode('utf-8'))
			if event.key == pygame.K_s and current_turn==my_color and waiting_for_move:
				client.sendall(json.dumps({"action": "SKIP"}).encode('utf-8'))
    
    
		if event.type == pygame.MOUSEBUTTONDOWN and waiting_for_move:
			mouse_pos = event.pos
			
			active_pawns = blue_pawns if current_turn == "blue" else green_pawns
			
			for pawn in active_pawns:
				if pawn.rect.collidepoint(mouse_pos):
					move_requet={
						"action": "MOVE",
						"pawn_id": pawn.pawn_id
					}
					client.sendall(json.dumps(move_requet).encode('utf-8'))
					break
	dice_score = my_dice.update() 
	if not my_dice.is_rolling and my_dice.current_value > 0 and my_dice.new_value: 
		steps = my_dice.current_value
		my_dice.new_value = False
		waiting_for_move = True	
		print(f"Waiting for {current_turn} to click a pawn. Rolled: {my_dice.current_value}")

	screen_surface.blit(board_image, (0, 0))

	for pawn in all_pawns:
		pawn.draw(screen_surface)
	my_dice.draw(screen_surface)
	draw_info_panel(screen_surface, current_turn, my_dice.current_value, waiting_for_move)
	pygame.display.update()
	clock.tick(60)


print("Closing the game...")
pygame.quit()
quit()
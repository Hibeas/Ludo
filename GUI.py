import pygame
from game_logic import Pawn, Dice
import constants


# Pygame setup
pygame.init()
pygame.display.set_caption('Ludo Game')
clock = pygame.time.Clock()
game_status = True
pygame.font.init()

main_font = pygame.font.SysFont("Arial", 24)
title_font = pygame.font.SysFont("Arial", 32, bold=True)

def draw_info_panel(surface, turn, dice_val, waiting):
    sidebar_rect = pygame.Rect(800, 0, constants.SIDEBAR_WIDTH, 800)
    pygame.draw.rect(surface, (40, 40, 40), sidebar_rect)
    pygame.draw.line(surface, (200, 200, 200), (800, 0), (800, 800), 3) 

    color_map = {"blue": (100, 100, 255), "green": (100, 255, 100)}
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

#okay we need to now whos turn it is if its on one pc it will jsut change the turn after the player rolls the dice and moves but if its on two pcs we need to send the 
# data to the other pc and then change the turn there as well. we will sent it using dictionariues and json 


#what need to be done - add zbijanie


# Game assets and objects
screen_surface = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
board_image = pygame.image.load("assets/board.png").convert()
board_image = pygame.transform.scale(board_image, (constants.GAME_WIDTH, constants.SCREEN_HEIGHT))
my_dice = Dice((400, 400))
green_pawns = [Pawn("green", i, constants.GREEN_START[i-1]) for i in range(5)]
blue_pawns = [Pawn("blue", i, constants.BLUE_START[i-1]) for i in range(5)]
all_pawns = green_pawns + blue_pawns
rolled_value = 0
current_turn = "blue"
waiting_for_move = False

while game_status:
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			game_status = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE and not waiting_for_move:
				if not my_dice.is_rolling: 
					my_dice.start_roll()
			if event.key == pygame.K_1:
				my_dice.new_value = True	
				my_dice.current_value   = 1
			if event.key == pygame.K_6:
				my_dice.new_value = True	
				my_dice.current_value   = 6
			if event.key == pygame.K_s and waiting_for_move:
				print(f"{current_turn} skipped their turn.")
				current_turn = "green" if current_turn == "blue" else "blue"
				waiting_for_move = False
				rolled_value = 0
    
    
		if event.type == pygame.MOUSEBUTTONDOWN and waiting_for_move:
			mouse_pos = event.pos
			
			active_pawns = blue_pawns if current_turn == "blue" else green_pawns
			
			for pawn in active_pawns:
				if pawn.rect.collidepoint(mouse_pos):
					has_moved = pawn.move(steps)
					
					if has_moved:
						print(f"{current_turn} moved pawn {pawn.pawn_id}")
						
						current_turn = "green" if current_turn == "blue" else "blue"
						rolled_value = 0
						waiting_for_move = False
						break
					else:
						print("Invalid move! Try a different pawn or press 'S' to skip.")
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
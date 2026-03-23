import pygame
from game_logic import Pawn, Dice

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
screen_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

board_image = pygame.image.load("assets/board.png").convert()
board_image = pygame.transform.scale(board_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

my_dice = Dice((400, 400))
green_pawns = [Pawn("green", i, (50 + i*40, 50)) for i in range(5)]
blue_pawns = [Pawn("blue", i, (50 + i*40, 500)) for i in range(5)]
all_pawns = green_pawns + blue_pawns

pygame.display.set_caption('Ludo Game')

clock = pygame.time.Clock()



game_status = True
while game_status:
	screen_surface.fill((0, 0, 0))
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			game_status = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				if not my_dice.is_rolling: 
					my_dice.start_roll()
	my_dice.update()            
	screen_surface.blit(board_image, (0, 0))
	for pawn in all_pawns:
		pawn.draw(screen_surface)
	my_dice.draw(screen_surface)
	pygame.display.update()
	clock.tick(60)

print("Closing the game...")
pygame.quit()
quit()
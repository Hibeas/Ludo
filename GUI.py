import pygame
from game_logic import Pawn, Dice

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800



BLUE_HOME = [(165, 700), (222, 640), (100, 640), (165, 575)]
GREEN_HOME = [(577, 163), (699, 163), (642, 224), (642, 98)]



BOARD = [
	#start with blue start 0, Red start at 13, green start at 26, yellow start at 39
	(342, 713), (342, 663), (342, 613), (342, 563), (342, 513),
	(287, 458), (237, 458), (187, 458), (137, 458), (87, 458), (37, 458),
	(37, 403), (37, 341), (87, 341), (137, 341), (187, 341), (237, 341), (287, 341),
	(342, 286), (342, 236), (342, 186), (342, 136), (342, 86), (342, 36),
	(399, 36), (458, 36), (458, 86), (458, 136), (458, 186), (458, 236), (458, 286),
	(513, 341), (563, 341), (613, 341), (663, 341), (713, 341), (763, 341),
	(763, 403), (763, 458), (713, 458), (663, 458), (613, 458), (563, 458), (513, 458),
	(458, 513), (458, 563), (458, 613), (458, 663), (458, 713), (458, 764), (399, 764), (342, 764)
]


screen_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

board_image = pygame.image.load("assets/board.png").convert()
board_image = pygame.transform.scale(board_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

my_dice = Dice((400, 400))
green_pawns = [Pawn("green", i, GREEN_HOME[i-1]) for i in range(5)]
blue_pawns = [Pawn("blue", i, BLUE_HOME[i-1]) for i in range(5)]
all_pawns = green_pawns + blue_pawns

test_pawn = Pawn("blue", 1, BLUE_HOME[0])

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
	test_pawn.auto_walk(BOARD)
	test_pawn.draw(screen_surface)
	for pawn in all_pawns:
		pawn.draw(screen_surface)
	my_dice.draw(screen_surface)
	pygame.display.update()
	clock.tick(60)

print("Closing the game...")
pygame.quit()
quit()
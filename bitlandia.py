import pygame

#initialise pygame
pygame.init()

#game window dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700

#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bitlandia')

#game loop
run = True
while run:

	#event handler
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False


pygame.quit()
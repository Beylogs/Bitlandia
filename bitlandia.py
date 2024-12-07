#import
import pygame
import random
import os
from pygame import mixer
from spritesheet import SpriteSheet
from enemy import Enemy

#initialize pygame
pygame.init()

#game window dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bitlandia')

#set frame rate
clock = pygame.time.Clock()
FPS = 70

#load music and sounds
pygame.mixer.music.load('assets/music/backgrounMusic.mp3')
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1, 0.0)
jump_fx = pygame.mixer.Sound('assets/music/jump.mp3')
jump_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('assets/music/death.mp3')
death_fx.set_volume(0.5)
score_item_fx = pygame.mixer.Sound('assets/music/scoreItem.wav')  # Load score item sound effect
score_item_fx.set_volume(0.5)  # Adjust volume as needed
super_jump_item_fx = pygame.mixer.Sound('assets/music/superjumpItem.wav')  # Load super jump sound effect
super_jump_item_fx.set_volume(0.5)  # Adjust volume as needed

#game variables
SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
start_game = True
score = 0
fade_counter = 0

#score multiplier and super jump variables
score_multiplier = 1
multiplier_timer = 0
super_jump_active = False

if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0

#define colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PANEL = (153, 217, 234)

#define font
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)

#load images
bitlandia_image = pygame.image.load('assets/images/character/run/character_berie_run_1.png').convert_alpha()
bg_image = pygame.image.load('assets/images/background/bgta.png').convert_alpha()
platform_image = pygame.image.load('assets/images/platform/tilemap2.png').convert_alpha()
item_image = pygame.image.load('assets/images/item/score.png').convert_alpha()
super_jump_image = pygame.image.load('assets/images/item/super jump.png').convert_alpha()
#bird spritesheet
bird_sheet_img = pygame.image.load('assets/images/enemy/bird.png').convert_alpha()
bird_sheet = SpriteSheet(bird_sheet_img)

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#function for drawing info panel
# Function for drawing info panel
def draw_panel():
    pygame.draw.rect(screen,BLACK, (0, 0, SCREEN_WIDTH, 30))
    pygame.draw.line(screen, WHITE, (0, 30), (SCREEN_WIDTH, 30), 2)
    draw_text('SCORE: ' + str(score), font_small, WHITE, 0, 0)

    # Display multiplier and super jump status
    if score_multiplier > 1:
        # Draw "2x SCORE" text
        draw_text('2x SCORE', font_small, WHITE, SCREEN_WIDTH - 200, 0)

        # Adjusted font size for multiplier timer and position it next to "2x SCORE"
        font_timer = pygame.font.SysFont('Lucida Sans', 18)  # Smaller font size
        # Adjust position to be just to the right of "2x SCORE"
        draw_text(f'TIMER: {multiplier_timer // 60}', font_timer, WHITE, SCREEN_WIDTH - 75, 0)  # Adjusted position

    if super_jump_active:
        draw_text('SUPER JUMP READY!', font_small, WHITE, SCREEN_WIDTH - 220, 20)

#function for drawing the background
def draw_bg(bg_scroll):
    screen.blit(bg_image, (0, 0 + bg_scroll))
    screen.blit(bg_image, (0, -600 + bg_scroll))

#player class
class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(bitlandia_image, (45, 45))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False

    def move(self):
        global super_jump_active  # Declare as global to modify it

        #reset variables
        scroll = 0
        dx = 0
        dy = 0

        #process keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx = -10
            self.flip = True
        if key[pygame.K_RIGHT]:
            dx = 10
            self.flip = False

        #gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        #ensure player doesn't go off the edge of the screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        #check collision with platforms
        for platform in platform_group:
            #collision in the y direction
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if above the platform
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        # Trigger super jump effect if active
                        if super_jump_active:
                            self.vel_y = -40  # Super jump height
                            super_jump_active = False  # Reset after one use
                        else:
                            self.vel_y = -20  # Normal jump height
                        jump_fx.play()

        #check if the player has bounced to the top of the screen
        if self.rect.top <= SCROLL_THRESH:
            #if player is jumping
            if self.vel_y < 0:
                scroll = -dy

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy + scroll
  
        #update mask
        self.mask = pygame.mask.from_surface(self.image)

        return scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))

#platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 20))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        # If platform is moving, update its position
        if self.moving:
            self.rect.x += self.direction * self.speed
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.direction *= -1  # Reverse direction at edges

        # Update platform's vertical position
        self.rect.y += scroll

        # Remove platform if it goes off-screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

#item classes
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(item_image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, scroll):
        self.rect.y += scroll
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class SuperJumpItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(super_jump_image, (60, 60))  # Larger size
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, scroll):
        self.rect.y += scroll
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            
class StartButton():
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font_big
        self.color = (0, 255, 0)  # Green color for the button
        self.hover_color = (0, 200, 0)  # Darker green when hovered

    def draw(self):
        # Change color on hover
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw the text on the button
        draw_text(self.text, self.font, WHITE, self.rect.centerx - self.font.size(self.text)[0] // 2, self.rect.centery - self.font.size(self.text)[1] // 2)

    def is_clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        if self.rect.collidepoint(mouse_x, mouse_y) and mouse_click:
            return True
        return False



#player instance




#create sprite groups
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
super_jump_group = pygame.sprite.Group()

#create starting platform
platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
platform_group.add(platform)

#game loop
run = True
bitlandia = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
start_button = StartButton(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, 'START GAME')

while run:
    clock.tick(FPS)

    # If the game is in the "start screen" state, display the start button
    if start_game:
        # Use the bg_image (bgta) as the background
        screen.blit(bg_image, (0, 0))  # Fill the screen with the background image
        start_button.draw()  # Draw the start button

        # If the button is clicked, start the game
        if start_button.is_clicked():
            start_game = False  # Transition to the game loop

    # The main game loop (after start button is clicked)
    elif not game_over:
        scroll = bitlandia.move()

        #draw background
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)

        #generate platforms
        if len(platform_group) < MAX_PLATFORMS:
            p_w = random.randint(40, 60)
            p_x = random.randint(0, SCREEN_WIDTH - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            p_type = random.randint(1, 2)
            if p_type == 1 and score > 500:
                p_moving = True
            else:
                p_moving = False
            platform = Platform(p_x, p_y, p_w, p_moving)
            platform_group.add(platform)

            # Spawn score item
            if score > 500 and not p_moving and random.randint(1, 2) == 1:
                item = Item(p_x + p_w // 2, p_y - 10)
                item_group.add(item)

            # Spawn super jump item
            if score > 500 and not p_moving and random.randint(1, 2) == 1:
                super_jump_item = SuperJumpItem(p_x + p_w // 2, p_y - 10)
                super_jump_group.add(super_jump_item)

        #update platforms
        platform_group.update(scroll)

        #update items
        item_group.update(scroll)
        super_jump_group.update(scroll)

        # Check for item collection
        for item in item_group:
            if bitlandia.rect.colliderect(item.rect):
                score_multiplier = 2
                multiplier_timer = 300
                item.kill()
                score_item_fx.play()  # Play the score item sound effect

        # Check for super jump collection
        for item in super_jump_group:
            if bitlandia.rect.colliderect(item.rect):
                super_jump_active = True  # Activate super jump for one jump
                item.kill()
                super_jump_item_fx.play()  # Play the super jump sound effect

        #update multiplier timer
        if multiplier_timer > 0:
            multiplier_timer -= 1
        else:
            score_multiplier = 1

        #generate enemies
        if len(enemy_group) == 0 and score > 1500:
            enemy = Enemy(SCREEN_WIDTH, 100, bird_sheet, 1.5)
            enemy_group.add(enemy)

        #update enemies
        enemy_group.update(scroll, SCREEN_WIDTH)

        #update score
        if scroll > 0:
            score += scroll * score_multiplier

        #draw line at previous high score
        pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
        draw_text('HIGH SCORE', font_small, WHITE, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH)

        #draw sprites
        platform_group.draw(screen)
        enemy_group.draw(screen)
        item_group.draw(screen)
        super_jump_group.draw(screen)
        bitlandia.draw()

        #draw panel
        draw_panel()

        #check game over
        if bitlandia.rect.top > SCREEN_HEIGHT:
            game_over = True
            death_fx.play()
        #check for collision with enemies
        if pygame.sprite.spritecollide(bitlandia, enemy_group, False):
            if pygame.sprite.spritecollide(bitlandia, enemy_group, False, pygame.sprite.collide_mask):
                game_over = True
                death_fx.play()
    else:
        if fade_counter < SCREEN_WIDTH:
            fade_counter += 5
            for y in range(0, 6, 2):
                pygame.draw.rect(screen, BLACK, (0, y * 100, fade_counter, 100))
                pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_counter, (y + 1) * 100, SCREEN_WIDTH, 100))
        else:
            draw_text('GAME OVER!', font_big, WHITE, 130, 200)
            draw_text('SCORE: ' + str(score), font_big, WHITE, 130, 250)
            draw_text('PRESS SPACE TO PLAY AGAIN', font_big, WHITE, 40, 300)
            #update high score
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                #reset variables
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                score_multiplier = 1
                super_jump_active = False
                #reposition bitlandia
                bitlandia.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
                #reset enemies
                enemy_group.empty()
                #reset platforms
                platform_group.empty()
                #reset items
                item_group.empty()
                super_jump_group.empty()
                #create starting platform
                platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
                platform_group.add(platform)

    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            #update high score
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            run = False

    #update display window
    pygame.display.update()

pygame.quit()

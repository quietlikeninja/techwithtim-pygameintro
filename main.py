import pygame
import os
pygame.font.init()
pygame.mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 500
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FPS = 60
VELOCITY = 5
BULLET_VELOCITY = 7
MAX_BULLETS = 5
pygame.display.set_caption("First Game!")

#Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BURNT_ORANGE = (255, 128, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

BORDER = pygame.Rect(SCREEN_WIDTH//2-5, 0, 10, SCREEN_HEIGHT)

BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Grenade+1.mp3'))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Gun+Silencer.mp3'))

HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)

SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 60, 40
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_yellow.png'))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE,(SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)
RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_red.png'))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE,(SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

SPACE = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'space.png')), (SCREEN_WIDTH, SCREEN_HEIGHT))

#create Explosion class
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(os.path.join('Assets', f'exp{num}.png'))
			img = pygame.transform.scale(img, (50, 50))
			self.images.append(img)
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.counter = 0

	def update(self):
		explosion_speed = 4
		#update explosion animation
		self.counter += 1

		if self.counter >= explosion_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]

		#if the animation is complete, reset animation index
		if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
			self.kill()

def draw_window(red, yellow, yellow_bullets, red_bullets, yellow_health, red_health, explosion_group):
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BURNT_ORANGE, BORDER)

    yellow_health_text = HEALTH_FONT.render("Health: " + str(yellow_health), 1, WHITE)
    red_health_text = HEALTH_FONT.render("Health: " + str(red_health), 1, WHITE)
    WIN.blit(yellow_health_text, (10, 10))
    WIN.blit(red_health_text, (SCREEN_WIDTH - red_health_text.get_width() - 10, 10))

    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))

    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    for bullet in red_bullets:
        pygame.draw.rect(WIN, RED, bullet)

    explosion_group.draw(WIN)
    explosion_group.update()

    pygame.display.update()

def yellow_handle_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_a] and yellow.x - VELOCITY >= 0: # Yellow Left
        yellow.x -= VELOCITY
    elif keys_pressed[pygame.K_d] and yellow.x + VELOCITY + yellow.width <= BORDER.x: # Yellow Right
        yellow.x += VELOCITY
    elif keys_pressed[pygame.K_w] and yellow.y - VELOCITY >= 0: # Yellow Up
        yellow.y -= VELOCITY
    elif keys_pressed[pygame.K_s] and yellow.y + VELOCITY + yellow.height <= SCREEN_HEIGHT: # Yellow Down
        yellow.y += VELOCITY

def red_handle_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red.x - VELOCITY >= BORDER.x + BORDER.width: # Red Left
        red.x -= VELOCITY
    elif keys_pressed[pygame.K_RIGHT] and red.x + VELOCITY + red.width <= SCREEN_WIDTH: # Red Right
        red.x += VELOCITY
    elif keys_pressed[pygame.K_UP] and red.y - VELOCITY >= 0: # Red Up
        red.y -= VELOCITY
    elif keys_pressed[pygame.K_DOWN] and red.y + VELOCITY + red.height <= SCREEN_HEIGHT: # Red Down
        red.y += VELOCITY

def handle_bullets(yellow_bullets, red_bullets, yellow, red):
    for bullet in yellow_bullets:
        bullet.x += BULLET_VELOCITY
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT, {"bullet_hit_x": bullet.x, "bullet_hit_y": bullet.y}))
            yellow_bullets.remove(bullet)
        elif bullet.x > SCREEN_WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets:
        bullet.x -= BULLET_VELOCITY
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT, {"bullet_hit_x": bullet.x, "bullet_hit_y": bullet.y}))
            red_bullets.remove(bullet)
        elif bullet.x < 0:
            red_bullets.remove(bullet)

def draw_winner(text):
    draw_text = WINNER_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (SCREEN_WIDTH//2 - draw_text.get_width()//2, SCREEN_HEIGHT//2 - draw_text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(5000)

def main():
    yellow = pygame.Rect(200, 220, SPACESHIP_HEIGHT, SPACESHIP_WIDTH)
    red = pygame.Rect(700, 220, SPACESHIP_HEIGHT, SPACESHIP_WIDTH)

    yellow_bullets = []
    red_bullets = []

    yellow_health = 10
    red_health = 10

    clock = pygame.time.Clock()

    explosion_group = pygame.sprite.Group()

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                explosion = Explosion(pos[0], pos[1])
                explosion_group.add(explosion)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height//2-2, 10, 4)
                    yellow_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

                if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(red.x, red.y + red.height//2-2, 10, 4)
                    red_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()
        
            if event.type == YELLOW_HIT:
                yellow_health -= 1
                explosion = Explosion(event.bullet_hit_x, event.bullet_hit_y)
                explosion_group.add(explosion)
                BULLET_HIT_SOUND.play()

            if event.type == RED_HIT:
                red_health -= 1
                explosion = Explosion(event.bullet_hit_x, event.bullet_hit_y)
                explosion_group.add(explosion)
                BULLET_HIT_SOUND.play()

        winner_text = ""
        if red_health <= 0:
            winner_text = "Yellow Wins!"

        if yellow_health <= 0:
            winner_text = "Red Wins!"

        keys_pressed  = pygame.key.get_pressed()
        yellow_handle_movement(keys_pressed, yellow)
        red_handle_movement(keys_pressed, red)
        handle_bullets(yellow_bullets, red_bullets, yellow, red)
        draw_window(red, yellow, yellow_bullets, red_bullets, yellow_health, red_health, explosion_group)

        if winner_text != "":
            draw_winner(winner_text)
            break

    main()

if __name__ == "__main__":
    main()
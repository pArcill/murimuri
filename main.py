# import the pygame module, so you can use it
import pygame
import random
import Textrect

WIDTH, HEIGHT = 1920, 1080
TPS = 120
FIELDSIZE = (1024,512)
PRIMARY_COLOR = (255,235,254)

DEFAULT_SPEED = 4
HITBOX_WIDTH = 4
MUSIC_VOLUME = 0.5

SHOW_HITBOXES = False

GAME_END = False

## Player
PLAYER_SIZE = 125
PLAYER_SPEED = DEFAULT_SPEED

## Ball
BALL_SIZE = 120
BALL_SPEED = DEFAULT_SPEED

minPos = (WIDTH//2-FIELDSIZE[0]//2, HEIGHT//2-FIELDSIZE[1]//2)
maxPos = (WIDTH//2+FIELDSIZE[0]//2, HEIGHT//2+FIELDSIZE[1]//2)

# draw the corners of the map
def drawCorners(screen):
	pygame.draw.circle(screen, (255, 0, 0), minPos, 5)					# 2. Quadrant
	pygame.draw.circle(screen, (0, 255, 0), (minPos[0], maxPos[1]), 5)	# 1. Quadrant
	pygame.draw.circle(screen, (255, 0, 0), maxPos, 5)					# 4. Quadrant
	pygame.draw.circle(screen, (0, 255, 0), (maxPos[0], minPos[1]), 5)	# 3. Quadrant

# Get random coordinates within the map
def get_random_coords() -> tuple[int, int]:
	return (random.randint(minPos[0], maxPos[0]), random.randint(minPos[1], maxPos[1]))

# Entity 
class Entity():	
	def __init__(self, images:list, x:int, y:int, size:tuple=(100, 100), step=1.5, hitboxes:tuple=(0,0,0,0)):
		# Image
		self._images = list()
		for image in images:
			if isinstance(image, pygame.Surface):
				self._images.append(image)
			else:
				self._images.append(pygame.transform.scale(pygame.image.load(image), size))
		self._image = self._images[0]

		# Size of Entity
		self._size = size
		self._width, self._height = self._image.get_size()
		self._custom_hitbox = hitboxes
		self._step = step
		self.setPos(x, y)

	# Set position of entity
	def setPos(self, x:int, y:int) -> None:
		self._x = x
		self._y = y
		self.refreshHitbox()

	# Refresh hitbox
	def refreshHitbox(self, offset=5, screen=None, color:tuple=(0,255,0)) -> None:
		self._hitboxOffset = offset
		if self._custom_hitbox != (0,0,0,0):
			self._hitbox = (self._x+offset, self._y+offset, self._custom_hitbox[2]-2*offset, self._custom_hitbox[3]-2*offset)
		self.map_field = pygame.Rect(minPos[0], minPos[1], maxPos[0]-minPos[0]-self._hitboxOffset*4, maxPos[1]-minPos[1])
		#				x, y, width, height
		self._hitbox = (self._x+offset, self._y+offset, self._width-2*offset, self._height-2*offset)
		if screen and SHOW_HITBOXES:
			pygame.draw.rect(screen, color, self._hitbox, HITBOX_WIDTH)

	# Check if the player is within the boundaries of the map
	def boundariesCheck(self, x:int, y:int):
		inBounds = self.map_field.collidepoint(self._hitbox[0]+x, self._hitbox[1]+y)
		if inBounds:
			return True
		return False
	
	image = property(lambda self: self._image)
	x = property(lambda self: self._x)
	y = property(lambda self: self._y)
	step = property(lambda self: self._step)
	hitbox = property(lambda self: self._hitbox)

class Ball(Entity):
	def __init__(self, x:int=0, y:int=0, direction=(1,1)):
		super().__init__(images=["./assets/pellet.png"], x=x, y=y, step=3)
		(self._vel_x, self._vel_y) = direction
	def move(self, screen=None) -> None:
		# Enemy bounces off walls like a dvd logo
		if self._hitbox[0] <= minPos[0]:
			self._vel_x = 1
		if self._hitbox[0] >= maxPos[0]-self._hitbox[2]:
			self._vel_x = -1
		self._x += self._step * self._vel_x
		if self._hitbox[1] <= minPos[1]:
			self._vel_y = 1
		if self._hitbox[1] > maxPos[1]-self._hitbox[3]:
			self._vel_y = -1
		self._y += self._step * self._vel_y
		self.refreshHitbox(offset=20, screen=screen, color=(255, 0, 0))

# A wall that the player can't pass through and moves from right to left
class Alien(Entity):
	def __init__(self, images=["./assets/alien.png"], hitbox_offset:int=25, size=(100, 100)):
		# x = maxPos[0]
		# y = minPos[1]+random.randint(1, 4)*self._spawn_area
		super().__init__(images=images, x=maxPos[0], y=0, step=3, size=size)
		self._spawn_area = ((FIELDSIZE[1]-self._height)//4)
		self._y = minPos[1]+random.randint(1, 4)*self._spawn_area
		self._x = WIDTH
		self._hitboxOffset = hitbox_offset

	def move(self, screen=None):
		self._x -= 1*self._step
		if self._x <= -self._width:
			self._x = WIDTH
			self._y = minPos[1]+random.randint(1, 4)*self._spawn_area
		self.refreshHitbox(offset=self._hitboxOffset, screen=screen, color=(255, 0, 0))

class Cactus(Alien):
	def __init__(self, images=["./assets/cactus.png"],size:tuple=(25, 200)):
		super().__init__(images=images, hitbox_offset=10, size=(25, 200))

class Player(Entity):
	def __init__(self):
		# Player states
		self.isJumping, self.isFlying = False, False

		# Flight variables
		self.flight_stamina = 0
		self.max_flight_time = 5
		self.lastFlightToggle = pygame.time.get_ticks()
		self.lastStaminaRegen = pygame.time.get_ticks()

		# Sound effects
		self.jump_sound = pygame.mixer.Sound("./assets/sfx/jump.ogg")
		self.hit_sound = pygame.mixer.Sound("./assets/sfx/hit.ogg")
		pygame.mixer.Sound.set_volume(self.hit_sound, 0.5)
		pygame.mixer.Sound.set_volume(self.jump_sound, 0.5)

		# Player movement variables
		self.gravity = 0.2
		self.jump_height = 7.5
		self.vel_jump = self.jump_height
		(self.vel_x, self.vel_y) = 0, 0

		# Health
		self.max_hp = 100
		self.hp = self.max_hp
		self.last_damaged = pygame.time.get_ticks()

		# Initialize entity properties
		super().__init__(images=["./assets/player_00.png", "./assets/player_01.png"], x=0, y=0, size=(PLAYER_SIZE,PLAYER_SIZE), step=PLAYER_SPEED)
		self.update_darkness(255)

	def update_darkness(self, val:int=0):
		self._dark_overlay = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA)
		self._dark_overlay.fill((val, val, val))

	def move(self, screen=None) -> None:
		if self.isJumping:
			self.vel_jump -= self.gravity
			self._y -= self.vel_jump
			# force non-flight mode (dirty fix)
			self.map_field = pygame.Rect(minPos[0], minPos[1], maxPos[0]-minPos[0]-self._hitboxOffset*4, maxPos[1]-minPos[1])

			# if player hits the ceiling
			if self._y < self.map_field[1]:
				self._y = self.map_field[1]
				self.vel_jump = -0.2

			# if player is on the floor
			if self.map_field[1]+self.map_field[3] <= (self._y+self._height-self._hitboxOffset):
				self.isJumping = False
				self.vel_jump = self.jump_height
				self._y = self.map_field[1]+self.map_field[3]-self._height+self._hitboxOffset

		# if player is flying
		elif self.isFlying:
			if self.boundariesCheck(0, self.vel_y):
				self._y += self.vel_y

		if self.boundariesCheck(self.vel_x, 0):
			self._x += self.vel_x

		self.draw_healthbar(screen)
		self.refreshHitbox(screen=screen, offset=20)

	def update_image(self, id:int=0) -> None:
		self._image = self._images[id]

	# Toggle flight mode
	def toggleFlight(self, force:bool=None) -> None:
		# prevent spamming (500ms cooldown)
		if pygame.time.get_ticks() - self.lastFlightToggle < 500:
			return
		self.lastFlightToggle = pygame.time.get_ticks()
		if force != None:
			self.isFlying = force
		else:
			self.isFlying = not self.isFlying

		if self.isFlying:
			self.update_image(1)
			self.vel_jump = 0
			self.vel_x = 0
		else:
			self.update_image(0)
			self.vel_jump = self.jump_height
			self.vel_x = 0
			self.jump()

	# Trigger jump event
	def jump(self) -> None:
		pygame.mixer.Sound.play(self.jump_sound)
		self.isJumping = True
	
	# Trigger hit event
	def hit(self) -> None:
		if pygame.time.get_ticks() - self.last_damaged < 1000:
			return
		pygame.mixer.Sound.play(self.hit_sound)
		self.last_damaged = pygame.time.get_ticks()
		self.update_darkness(120)
		self.hp -= 34
		if self.hp <= 0:
			self.hp = 0
			global GAME_END
			GAME_END = True

	def draw_healthbar(self, screen) -> None:
		# Set the position and size of the health bar
		position = (self._x, self._y - 20)  # 20 pixels above the player
		size = (self._width, 10)  # 10 pixels high

		# Calculate the length of the health bar
		hp_length = int(size[0] * (self.hp / self.max_hp))

		# Draw the health bar
		pygame.draw.rect(screen, (255, 0, 0), (*position, hp_length, size[1]))
		pygame.draw.rect(screen, (255, 128, 0), (*position, *size), 2)  # outline

		# Draw flight stamina bar
		position = (self._x, self._y - 5)  # 20 pixels above the player
		size = (self._width, 10)  # 10 pixels high
	
		stamina_length = int(size[0] * (self.flight_stamina / self.max_flight_time))
		pygame.draw.rect(screen, (0, 0, 255), (*position, stamina_length, size[1]))
		pygame.draw.rect(screen, (0, 128, 255), (*position, *size), 2)  # outline


	# Player-specific hitbox
	def refreshHitbox(self, offset=5, screen=None, color:tuple=(0,255,0)) -> None:
		self._hitboxOffset = offset
		if self.isFlying:
			self.map_field = pygame.Rect(minPos[0], minPos[1], maxPos[0]-minPos[0]-self._hitboxOffset*4, maxPos[1]-minPos[1]-self._hitboxOffset*4)
		else:
			self.map_field = pygame.Rect(minPos[0], minPos[1], maxPos[0]-minPos[0]-self._hitboxOffset*4, maxPos[1]-minPos[1])
		#				x, y, width, height
		self._hitbox = (self._x+offset, self._y+offset, self._width-2*offset, self._height-2*offset)
		if screen and SHOW_HITBOXES:
			pygame.draw.rect(screen, color, self._hitbox, HITBOX_WIDTH)

def main():
	global TPSCLOCK
	TPSCLOCK = pygame.time.Clock()
	pygame.init()
	logo = pygame.image.load("./assets/logo.png")
	pygame.display.set_icon(logo)
	pygame.display.set_caption("murimuri adventures")
	title_screen()
	# runGame()

def title_screen():
	screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.WINDOWMAXIMIZED)

	# Load song
	pygame.mixer.music.load("./assets/sfx/titlescreen.ogg")
	pygame.mixer.music.set_volume(MUSIC_VOLUME)
	pygame.mixer.music.play(loops=-1)

	# Preload asset
	logo = pygame.image.load("./assets/logo.png")
	logo = pygame.transform.scale(logo, (500, 500))

	waiting = True
	while waiting:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if pygame.key.get_pressed()[pygame.K_w]:
					waiting = False
			if event.type == pygame.QUIT:
				pygame.quit()
				return
		### Main Menu
		screen.fill(PRIMARY_COLOR)
		screen.blit(logo, (WIDTH//2-logo.get_width()//2, HEIGHT//2-logo.get_height()//2-200))

		# Draw Textbox
		font = pygame.font.Font(None, 45)
		string = '''
Controls:
- Use WASD controls to move
- Press [F] to toggle Flightmode\n
Gameplay:
Survive for as long as you can!
You can only fly for a limited time\n
* Press the W key to start! *'''
		rect = pygame.Rect((0, 0, 500, 400))
		text = Textrect.render_textrect(string, font, rect, (0,0,0), (255,255,255), 1)
		screen.blit(text, (WIDTH//2-text.get_width()//2, HEIGHT//2-text.get_height()//2+200))
		pygame.draw.rect(screen, (235,106,234), (WIDTH//2-text.get_width()//2, HEIGHT//2-text.get_height()//2+200, 500, 400), 2)

		pygame.display.update()
		TPSCLOCK.tick(TPS)
	pygame.mixer.music.stop()
	pygame.mixer.music.unload()
	runGame()

def runGame():
	screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.WINDOWMAXIMIZED)

	pygame.mixer.music.load("./assets/sfx/music.ogg")
	pygame.mixer.music.set_volume(MUSIC_VOLUME*0.5)
	pygame.mixer.music.play(loops=-1)

	### Game start
	# Load player image
	player = Player()
	# set player to middle of map
	player.setPos(FIELDSIZE[0]//2, player.map_field[1]+player.map_field[3]-player._height+player._hitboxOffset)
	player.isJumping = True # Jumps at the beginning
	time = pygame.time.get_ticks() # time since game started
	last_spawned = pygame.time.get_ticks() # last time an entity spawned
	spawn_cycles = 1 # how many times a mob has spawned
	entities = list()

	def spawn(entity_dict:dict):
		for entity, count in entity_dict.items():
			if entity == "ball":
				entity = Ball(*get_random_coords(), direction=(-1**random.randint(1, 2), -1))
			elif entity == "alien":
				entity = Alien()
			elif entity == "cactus":
				entity = Cactus()
			else:
				continue
			for _ in range(count):
				entities.append(entity)

	spawn({"ball":1})
	background_img = pygame.image.load("assets/background.jpg")
	# main loop
	running = True
	while running:
		if GAME_END:
			running = False
			continue
		# event handling, gets all event from the event queue
		for event in pygame.event.get():
			# only do something if the event is of type QUIT
			if event.type == pygame.QUIT:
				# change the value to False, to exit the main loop
				running = False
		# renderings
		screen.fill((0, 0, 0))
		screen.blit(background_img, (0,0))
		# fill the min and max positions
		rect_surface = pygame.Surface((maxPos[0]-minPos[0], maxPos[1]-minPos[1]))
		rect_surface.fill((255,235,254, 128))
		# draw outline
		pygame.draw.rect(rect_surface, (0, 0, 0), rect_surface.get_rect(), 2)
		screen.blit(rect_surface, minPos)
		input = pygame.key.get_pressed()
		player.vel_x = 0
		player.vel_y = 0
		if pygame.time.get_ticks() - player.last_damaged >= 1000:
			player.update_darkness(255)
		if input[pygame.K_f]:
			if player.flight_stamina != 0:
				player.toggleFlight()
		if input[pygame.K_w]:
			if not player.isFlying and not player.isJumping:
				player.jump()
			else:
				player.vel_y = -player.step
		if input[pygame.K_a]:
			player.vel_x = -player.step
		if input[pygame.K_d]:
			player.vel_x = player.step
		if input[pygame.K_s]:
			if player.isFlying:
				player.vel_y = player.step

		if input[pygame.K_ESCAPE]:
			quit()

		for entity in entities:
			entity.move(screen=screen)
			screen.blit(entity.image, (entity.x, entity.y))
			if pygame.Rect.colliderect(pygame.Rect(*player.hitbox), pygame.Rect(*entity.hitbox)):
				player.hit()
			entity.refreshHitbox(screen=screen, color=(255, 0, 255), offset=entity._hitboxOffset)
		##Player movement
		player.move(screen=screen)
		image_copy = player.image.copy()

		# Darken the copy
		image_copy.blit(player._dark_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

		# Draw the darkened image
		screen.blit(image_copy, (player.x, player.y))

		# Track player's flight time
		if player.isFlying:
			# Check if 1 second has passed
			if pygame.time.get_ticks() - player.lastStaminaRegen >= 1000:
				if player.flight_stamina >= 1:
					player.flight_stamina-=1
				else:
					player.toggleFlight()
				player.lastStaminaRegen = pygame.time.get_ticks()
		else:
			# Check if 2 seconds have passed
			if pygame.time.get_ticks() - player.lastStaminaRegen >= 2000:  
				if player.flight_stamina < player.max_flight_time:  # Don't exceed max flight time
					player.flight_stamina += 1  # Regenerate stamina
				player.lastStaminaRegen = pygame.time.get_ticks()  # Update last stamina regeneration time
		# rect_surface as a rect
		if SHOW_HITBOXES:
			drawCorners(screen)
			# pygame.draw.rect(screen, (255, 0, 0), player.map_field, 2)
		
		# display time
		font = pygame.font.Font(None, 36)
		text = font.render(f"{float(pygame.time.get_ticks() - time)/1000}s", True, (0,0,0))
		screen.blit(text, (WIDTH//2-text.get_width()//2, 20))

		# Entity spawning
		if pygame.time.get_ticks() - last_spawned >= 5000*(spawn_cycles):
			last_spawned = pygame.time.get_ticks()
			if spawn_cycles%2==0:
				spawn({"cactus":1})
			elif spawn_cycles%5==0:
				spawn({"ball":1})
			else:
				spawn({"alien":1})
			spawn_cycles+=1
		pygame.display.update()
		TPSCLOCK.tick(TPS)
	# game over screen
	# play gameover sfx
	pygame.mixer.music.stop()
	pygame.mixer.music.unload()
	pygame.mixer.music.load("./assets/sfx/gameover.ogg")
	pygame.mixer.music.set_volume(MUSIC_VOLUME)
	pygame.mixer.music.play()
	screen.fill((0, 0, 0))
	# game over text
	font = pygame.font.Font(None, 74)
	text = font.render("Game Over", True, (255, 255, 255))
	textRect = text.get_rect()
	textRect.center = (WIDTH // 2, HEIGHT // 2)
	screen.blit(text, textRect)
	# time the player survived
	time_survived = pygame.time.get_ticks() - time
	# time survived text
	font = pygame.font.Font(None, 48)
	text = font.render(f"You survived for {time_survived//1000} seconds", True, (255, 255, 255))
	textRect = text.get_rect()
	textRect.center = (WIDTH // 2, HEIGHT // 2 + 50)
	screen.blit(text, textRect)
	# player is below the text
	white_overlay = pygame.Surface((player.image.get_width(), player.image.get_height()), pygame.SRCALPHA)
	white_overlay.fill((255, 255, 255, 128))
	# draw white player
	player_img = player.image.copy()
	player_img.blit(white_overlay, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
	screen.blit(player_img, (WIDTH//2-PLAYER_SIZE//2, HEIGHT//2+100))
	# make copy of player that is completely white
	pygame.display.update()
	pygame.time.wait(5000)

if __name__=="__main__":
	main()

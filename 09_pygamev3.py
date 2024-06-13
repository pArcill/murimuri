# import the pygame module, so you can use it
import pygame
import random

WIDTH, HEIGHT = 1920, 1080
TPS = 120
FIELDSIZE = (1024,512)

DEFAULT_SPEED = 4
HITBOX_WIDTH = 4

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

def get_random_coords() -> tuple[int, int]:
	return (random.randint(minPos[0], maxPos[0]), random.randint(minPos[1], maxPos[1]))

class Entity(pygame.sprite.Sprite):	
	def __init__(self, image, x:int, y:int, size:int=100, step=1.5):
		pygame.sprite.Sprite.__init__(self)
		self._image = pygame.transform.scale(pygame.image.load(image), (size, size))
		self._width, self._height = self._image.get_size()
		self._step = step
		self.setPos(x, y)
		self._hitboxOffset = 5
	def setPos(self, x:int, y:int) -> None:
		self._x = x
		self._y = y
		self.refreshHitbox()
	def refreshHitbox(self, offset=5, screen=None, color:tuple=(0,255,0)) -> None:
		self._hitboxOffset = offset
		self.map_field = pygame.Rect(minPos[0], minPos[1], maxPos[0]-minPos[0]-self._hitboxOffset*4, maxPos[1]-minPos[1])
		#				x, y, width, height
		self._hitbox = (self._x+offset, self._y+offset, self._width-2*offset, self._height-2*offset)
		if screen:
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
        super().__init__(image="./assets/pellet.png", x=x, y=y, size=100, step=3)
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
	
class Player(Entity):
	def __init__(self):
		super().__init__(image="./assets/player_00.png", x=0, y=0, size=PLAYER_SIZE, step=PLAYER_SPEED)
		self.isJumping = False
		self.gravity = 0.2
		self.jump_height = 7.5
		self.vel_y = self.jump_height
		self.vel_x = 0
	def move(self, screen=None) -> None:
		if self.isJumping:
			self.vel_y -= self.gravity
			self._y -= self.vel_y
			#draw a dot
			# pygame.draw.circle(screen, (255, 0, 0), (self._x, self._y), 5)
			# if player is on the floor
			if self.map_field[1]+self.map_field[3] <= (self._y+self._height-self._hitboxOffset):
				self.isJumping = False
				self.vel_y = self.jump_height
				self._y = self.map_field[1]+self.map_field[3]-self._height+self._hitboxOffset
		if self.boundariesCheck(self.vel_x, 0):
			self._x += self.vel_x

		self.refreshHitbox(screen=screen, offset=20)
	def jump(self) -> None:
		self.isJumping = True
	def hit(self) -> None:
		
		exit()
		pass

def main():
	global TPSCLOCK
	TPSCLOCK = pygame.time.Clock()
	pygame.init()
	logo = pygame.image.load("./assets/player_00.png")
	pygame.display.set_icon(logo)
	pygame.display.set_caption("murimuri adventures")
	runGame()

def runGame():
	screen = pygame.display.set_mode((WIDTH, HEIGHT))

	# Load player image
	player = Player()
	# set player to middle of map
	player.setPos(FIELDSIZE[0]//2, player.map_field[1]+player.map_field[3]-player._height+player._hitboxOffset)
	player.jump()

	# define a variable to control the main loop
	running = True
	entities = list()
	# Load enemy image
	for i in range(1):
		ball = Ball(*get_random_coords(), direction=(-1**i, -1))
		entities.append(ball)
	entities.append(player)
	# main loop
	while running:
		# event handling, gets all event from the event queue
		for event in pygame.event.get():
			# only do something if the event is of type QUIT
			if event.type == pygame.QUIT:
				# change the value to False, to exit the main loop
				running = False
		# renderings
		screen.fill((0, 0, 0))
		# fill the min and max positions
		rect_surface = pygame.Surface((maxPos[0]-minPos[0], maxPos[1]-minPos[1]))
		rect_surface.fill((255, 255, 255))
		screen.blit(rect_surface, minPos)
		input = pygame.key.get_pressed()
		player.vel_x = 0
		if input[pygame.K_w]:
			player.jump()
		if input[pygame.K_a]:
			player.vel_x = -player.step
		if input[pygame.K_d]:
			player.vel_x = player.step
		for entity in entities:
			entity.move(screen=screen)
			#entity.move(screen=screen)
			screen.blit(entity.image, (entity.x, entity.y))
			if not isinstance(entity, Player):
				if pygame.Rect.colliderect(pygame.Rect(*player.hitbox), pygame.Rect(*entity.hitbox)):
					player.hit()
		# drawCorners(screen)
		#draw mapfield
		# rect_surface as a rect
		# pygame.draw.rect(screen, (255, 0, 0), player.map_field, 2)
		pygame.display.update()
		TPSCLOCK.tick(TPS)
		
if __name__=="__main__":
	main()
# import the pygame module, so you can use it
import pygame
import random
import PIL

WIDTH, HEIGHT = 1920, 1080
TPS = 120
PLAYER_SIZE = 125
PLAYER_SPEED = 4
FIELDSIZE = (1024,512)

minPos = (WIDTH//2-FIELDSIZE[0]//2, HEIGHT//2-FIELDSIZE[1]//2)
maxPos = (WIDTH//2+FIELDSIZE[0]//2, HEIGHT//2+FIELDSIZE[1]//2)

def get_random_coords() -> tuple[int, int]:
	return (random.randint(minPos[0], maxPos[0]), random.randint(minPos[1], maxPos[1]))

class Entity(pygame.sprite.Sprite):	
	def __init__(self, image, x:int, y:int, size:int=100, step=1.5):
		pygame.sprite.Sprite.__init__(self)
		self._image = pygame.transform.scale(pygame.image.load(image), (size, size))
		self._width, self._height = self._image.get_size()
		self._step = step

		self.setPos(x, y)
	def setPos(self, x:int, y:int) -> None:
		self._x = x
		self._y = y
		self.refreshHitbox()
	def refreshHitbox(self, offset=5, screen=None) -> None:
		self._hitboxOffset = offset
		self._hitbox = (self._x+offset, self._y+offset, self._width-2*offset, self._height-2*offset)
		if screen:
			pygame.draw.rect(screen, (0,255,0), self._hitbox, 2)
			pass
			
	# Check if the player is within the boundaries of the map
	def boundariesCheck(self, x:int, y:int):
		map_field = pygame.Rect(minPos[0],minPos[1], FIELDSIZE[0]-self._hitbox[3], FIELDSIZE[1]-self._hitbox[2])
		inBounds = map_field.collidepoint(self._hitbox[0]+x, self._hitbox[1]+y)
		if inBounds:
			return True
		return False
	


	image = property(lambda self: self._image)
	x = property(lambda self: self._x)
	y = property(lambda self: self._y)
	step = property(lambda self: self._step)
	hitbox = property(lambda self: self._hitbox)

class Player(Entity):
	def __init__(self):
		super().__init__(image="./assets/player_00.png", x=0, y=0, size=PLAYER_SIZE, step=PLAYER_SPEED)
		self.isJumping = False
		self.vel_y = 0
		self.vel_x = 0
	def move(self, x:int, y:int, screen=None) -> None:
		if self.boundariesCheck(x, y):
			self._x += x
			self._y += y
		self.refreshHitbox(screen=screen, offset=20)
	def jump(self) -> None:
		self.isJumping = True
		self.move(0, -self.step)
		self.isJumping = False
	def hit(self) -> None:
		# exit()
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
	player.setPos(FIELDSIZE[0]//2, FIELDSIZE[1])

	# define a variable to control the main loop
	running = True
	 
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
		if input[pygame.K_a]:
			player.move(-player.step, 0, screen=screen)
		if input[pygame.K_d]:
			player.move(player.step, 0, screen=screen)
		if input[pygame.K_w]:
			player.move(0, -player.step, screen=screen)
		if input[pygame.K_s]:
			player.move(0, player.step, screen=screen)
		screen.blit(player.image, (player.x, player.y))
		pygame.display.flip()
		TPSCLOCK.tick(TPS)
		
if __name__=="__main__":
	main()
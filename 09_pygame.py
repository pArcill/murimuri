# import the pygame module, so you can use it
import pygame
import random

WIDTH, HEIGHT = 1920, 1080
TPS = 60

MAPSIZE = (512, 512)

minPos = (WIDTH//2-MAPSIZE[0]//2, HEIGHT//2-MAPSIZE[1]//2)
maxPos = (WIDTH//2+MAPSIZE[0]//2, HEIGHT//2+MAPSIZE[1]//2)

def get_random_coords() -> tuple[int, int]:
    return (random.randint(minPos[0], maxPos[0]), random.randint(minPos[1], maxPos[1]))

class Entity:
    def __init__(self, image, x:int, y:int, size:int=100, step=1.5):
        self._image = pygame.transform.scale(pygame.image.load(image), (size, size))
        self._width, self._height = self._image.get_size()
        self._step = step
        self.setPos(x, y)
    def setPos(self, x:int, y:int) -> None:
        self._x = x
        self._y = y
        self.refreshHitbox()
    def refreshHitbox(self, offset:int=int(5), screen=None) -> None:
        self._hitboxOffset = offset
        self._hitbox = (self._x+offset, self._y+offset, self._width-2*offset, self._height-2*offset)
        if screen:
            pygame.draw.rect(screen, (0,255,0), self._hitbox, 2)

    # Correct 
    def boundsCheck(self):
        if self._hitbox[0] < minPos[0]:
            self._x = minPos[0]-self._hitboxOffset
        elif self._x+self._hitbox[2] > maxPos[0]:
            self._x = maxPos[0]-self._hitbox[2]
        if self._hitbox[1] < minPos[1]:
            self._y = minPos[1]-self._hitboxOffset
        elif self._y+self._hitbox[3] > maxPos[1]:
            self._y = maxPos[1]-self._hitbox[3]

    image = property(lambda self: self._image)
    x = property(lambda self: self._x)
    y = property(lambda self: self._y)
    step = property(lambda self: self._step)
    hitbox = property(lambda self: self._hitbox)

class Player(Entity):
    def __init__(self):
        super().__init__(image="./assets/player_00.png", x=0, y=0, size=100, step=5)
    def move(self, x:int, y:int, screen=None) -> None:
        self._x += x
        self._y += y
        self.boundsCheck()
        self.refreshHitbox(screen=screen, offset=10)
    def hit(self) -> None:
        #exit()
        pass

# Pellet moves in a straight line to a random destination
class Pellet(Entity):
    def __init__(self, x:int=0, y:int=0, direction=(1,1)):
        super().__init__(image="./assets/pellet.png", x=x, y=y, size=50, step=2)
        self._newDest()
    def _newDest(self) -> None:
        self.boundsCheck()
        # get a random destination
        self._dest = (random.randint(minPos[0], maxPos[0]),
                      random.randint(minPos[1], maxPos[1]))
        # calculate the slope and direction
        self._slope = (self._dest[1]-self._y)/(self._dest[0]-self._x)
        self._directionX = 1 if self._dest[0] > self._x else -1

    def move(self, screen=None) -> None:
        if not (minPos[0] < self._x < maxPos[0]-self._width) or not (minPos[1] < self._y <= maxPos[1]-self._height):
            self._newDest()
        self._x += self._directionX*self._step
        self._y += self._slope*self._step

class Ball(Entity):
    def __init__(self, x:int=0, y:int=0, direction=(1,1)):
        super().__init__(image="./assets/enemy.png", x=x, y=y, size=100, step=3)
        (self._directionX, self._directionY) = direction
    def move(self, screen=None) -> None:
        # Enemy bounces off walls like a dvd logo
        if self._x < minPos[0]:
            self._x = minPos[0]
            self._directionX = 1
        if self._x > maxPos[0]-self._width:
            self._x = maxPos[0]-self._width
            self._directionX = -1
        self._x += self._step * self._directionX
        if self._y < minPos[1]:
            self._y = minPos[1]
            self._directionY = 1
        if self._y > maxPos[1]-self._height:
            self._y = maxPos[1]-self._height
            self._directionY = -1
        self._y += self._step * self._directionY
        self.refreshHitbox(screen=screen)

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
    player.setPos(WIDTH//2, HEIGHT//2)

    enemies:list = list()
    # Load enemy image
    for i in range(1):
        ball = Ball(*get_random_coords(), direction=(-1**i, -1))
        enemies.append(ball)
    for i in range(0):
        pellet = Pellet(*get_random_coords())
        enemies.append(pellet)
    print(enemies)
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
        rect_surface.set_alpha(128)
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

        # 
        for enemy in enemies:
            enemy.move(screen=screen)
            screen.blit(enemy.image, (enemy.x, enemy.y))
            if pygame.Rect.colliderect(pygame.Rect(*player.hitbox), pygame.Rect(*enemy.hitbox)):
                player.hit()
        # update the screen display
        pygame.display.flip()
        TPSCLOCK.tick(TPS)
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
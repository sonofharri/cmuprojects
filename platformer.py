import math
import time

app.currentTick = 0
app.stepsPerSecond = 60
app.constGravity = 9.8/30 # 9.8/60 felt too floaty
app.hasTouchedGrass = False
app.transitioning = False

sky = Rect(0, 0, 400, 400, fill=gradient(rgb(180, 180, 255), rgb(235, 235, 255), start="top"))
ground = Rect(0, 300, 400, 100, fill=gradient(rgb(128, 90, 34), rgb(105, 76, 36), start="top"))
ground2 = Polygon(0, 300, 400, 300, 400, 350, 350, 340, 200, 370, 100, 345, 0, 350, fill=gradient(rgb(0, 120, 0), rgb(25, 80, 25), start="top"), opacity=10)
grassyTop = Polygon(0, 300, 200, 298, 400, 300, 400, 310, 200, 305, 0, 310, fill=gradient(rgb(120, 169, 71), rgb(141, 179, 71)), opacity=100 )
app.overlay = Rect(-100, -100, 600, 600, fill="white", opacity=0)

pebbles = []
def createPebble(x, y):
    pebbles.append(Oval(x, y, randomInt(5, 10), randomInt(5, 10), rotateAngle=randomInt(-10, 50), fill=gradient(rgb(100, 100, 120), rgb(120, 120, 140), start="top"), opacity=80))


class Player:
    def __init__(self, x, y):
        self.respawnX = x
        self.respawnY = y
        self.x = x
        self.y = y
        self.vX = 0
        self.vY = 0
        self.canJump = False
        self.shape = Rect(x - 10, y - 10, 20, 20, fill=gradient(rgb(255, 40, 40), rgb(255, 90, 90), start="top"), border=gradient(rgb(5,5,30), rgb(5,5,5), rgb(50, 50, 60), start="top") )
    def update(self):
        if not app.hasTouchedGrass:
            for grass in grassPatches:
                if (min(grass.x, grass.x2) < self.x and max(grass.x, grass.x2) > self.x) and (min(grass.y, grass.y2) < self.y and max(grass.y, grass.y2) > self.y):
                    app.hasTouchedGrass = True
                    self.explode()
                    break
        self.vY -= app.constGravity
        self.x += self.vX
        self.y -= self.vY
        
        self.x = min(390, max(10, self.x))
        
        self.vX *= .8
        
        couldJump = False
        if (self.y > 290):
            self.y = 290
            self.canJump = True
            couldJump = True
            self.vY = max(self.vY, 0)
        for platform in platforms:
            if (min(platform.x, platform.x2) < self.x + 10 and max(platform.x, platform.x2) > self.x - 10):
                if (self.y + 10 > platform.y) and (self.y < platform.y):
                    self.y = platform.y - 10
                    self.vY = max(self.vY, 0)
                    self.canJump = True
                    couldJump = True
                    platform.shapes.centerY = platform.y + 2
                else:
                    platform.shapes.centerY = platform.y
            else:
                platform.shapes.centerY = platform.y
        if not app.hasTouchedGrass:
            self.shape.centerX = self.x
            self.shape.centerY = self.y
        if (distance(self.x, self.y, app.endPoint.x, app.endPoint.y) < 40) and not app.transitioning:
            levelTransition(app.endPoint.level)
            print(distance(self.x, self.y, app.endPoint.x, app.endPoint.y))
    def explode(self):
        self.shape.fill = "black"
        r = randomInt(0, 180)
        app.explosion = Group(
            Star(self.x, self.y, 140, 8, roundness=60, rotateAngle=r, fill=rgb(255, 40, 21)),
            Star(self.x, self.y, 120, 8, roundness=60, rotateAngle=r, fill=rgb(240, 146, 31)),
            Star(self.x, self.y, 100, 8, roundness=60, rotateAngle=r, fill=rgb(255, 222, 36)),
            Star(self.x, self.y,  80, 8, roundness=60, rotateAngle=r, fill=rgb(255, 242, 56)),
            Star(self.x, self.y,  60, 8, roundness=60, rotateAngle=r, fill="white")
        )
        screenShake(5, 10)
        for i in range(10):
            schedule("app.explosion.rotateAngle += randomInt(-25,25);r=randomInt(-10,10);for c in app.explosion.children:\n  c.radius += r", i)
        schedule("app.group.remove(app.explosion)\napp.player.shape.fill=gradient(rgb(255, 40, 40), rgb(255, 90, 90), start='top')\napp.player.respawn()\napp.hasTouchedGrass = False\napp.player.update()", 10)
        self.shape.toFront()
    def teleport(self, x, y):
        self.x = x
        self.y = y
        self.vY = 0
    def respawn(self):
        self.teleport(self.respawnX, self.respawnY)

hints = []
class Hint:
    def __init__(self, t, x, y):
        self.x = x
        self.y = y
        self.shapes = Group(
            Label(t, x + 2, y + 2, fill="black", opacity=10, font="cinzel", bold=True),
            Label(t, x, y, fill=gradient(rgb(245, 250, 255), "white", "white"), font="cinzel", bold=True, opacity=80)
        )
        hints.append(self)
    def update(self):
        self.shapes.centerY = self.y + math.sin(app.currentTick/20) * 3
        self.shapes.rotateAngle = math.sin(app.currentTick/50)
        for shape in self.shapes.children:
            shape.opacity = min(100, max(0, shape.opacity + math.sin(app.currentTick/50)/5))

grassPatches = []
class GrassPatch:
    def __init__(self, x, x2, y):
        self.x = x
        self.x2 = x2
        self.y = y
        self.y2 = y - 20
        grassPatches.append(self)

grasses = []
class Grass:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x2 = x + randomInt(-15, 15)
        self.y2 = y - randomInt(20, 40)
        self.offset = randomInt(-10, 10)
        self.div = randomInt(20, 40)
        self.shadow = Line(x + 2, y, self.x2 + 2, self.y2 + 2, fill=rgb(0,0,0), opacity=5 )
        self.shape = Line(x, y, self.x2, self.y2, fill=gradient(rgb(141 + randomInt(-25, 25),179,71), rgb(120 + randomInt(-25, 25),179,71) ))
        grasses.append(self)
    def update(self):
        self.shape.x2 = self.x2 + math.sin((self.offset + app.currentTick)/self.div) * 10
        self.shadow.x2 = self.shape.x2 + 2
    def remove(self):
        app.group.remove(self.shape)
        app.group.remove(self.shadow)
        
platforms = []
class Platform:
    def __init__(self, x, y, wx, wy):
        self.x = x
        self.y = y
        self.x2 = x + wx
        self.y2 = y + wy
        self.shapes = Group(
            Rect(x, y, wx, wy, fill=rgb(30, 30, 40), border="white"),
            Rect(x, y, wx, wy/4, fill=rgb(50, 50, 60))
        )
        platforms.append(self)
        
class EndPoint:
    def __init__(self, x, y, levelToLoad):
        self.x = x
        self.y = y
        self.level = levelToLoad
        self.shapes = [
            Rect(x - 10, y - 10, 50, 50, fill=None, borderWidth=3, border=rgb(180, 255, 200), rotateAngle=0),
            Rect(x, y, 30, 30, fill=None, borderWidth=3, border=rgb(180, 255, 200), rotateAngle=45),
            Rect(x, y, 30, 30, fill=None, borderWidth=3, border=rgb(180, 255, 200), rotateAngle=20)
        ]
        self.effects = [
            Circle(x, y, 2, fill=rgb(180, 255, 200), rotateAngle=randomInt(-60, 60)),
            Circle(x, y, 2, fill=rgb(180, 255, 200), rotateAngle=randomInt(-60, 60)),
            Circle(x, y, 2, fill=rgb(180, 255, 200), rotateAngle=randomInt(-60, 60)),
            Circle(x, y, 2, fill=rgb(180, 255, 200), rotateAngle=randomInt(-60, 60))
        ]
    def update(self):
        s = math.sin(app.currentTick/30) * 20 + 20
        for c in self.shapes:
            c.centerX = self.x
            c.centerY = self.y
            c.width = abs(math.sin(app.currentTick/10) * 50)
            c.rotateAngle += randomInt(10, 90)/20
            c.border = rgb(180 + s, 255, 200 + s)
        for e in self.effects:
            e.centerX = self.x + math.sin((app.currentTick + e.rotateAngle)/30) * 5
            e.centerY = self.y + math.sin((app.currentTick + e.rotateAngle)/30) * 2
            e.fill = rgb(180 + s, 255, 200 + s)
        
def generateGrass(y, x1, x2):
    for i in range(rounded(abs(x2 - x1)/4)):
        Grass(x1 + i * 4 + randomInt(-3, 3), y + randomInt(0, 2))
    GrassPatch(x1, x2, y)
        
def randomInt(range1, range2):
    return rounded(random() * (range2 - range1) + range1)
    
scheduledTasks = []
def schedule(runnable, ticks):
    scheduledTasks.append([runnable, ticks])

def checkScheduledTasks():
    for task in scheduledTasks:
        if task[1] <= 0:
            exec(task[0])
            scheduledTasks.remove(task)
        else:
            task[1]-=1
            
def screenShake(intensity, length=5):
    for i in range(length):
        x = intensity * randomInt(-1, 1)
        y = intensity * randomInt(-1, 1)
        schedule(f"shake({x}, {y})", i * 2)
        schedule(f"shake({-x}, {-y})", i * 2 + 1)

def shake(x, y):
    for shape in app.group:
        shape.centerX+=x
        shape.centerY+=y

app.player = None
def loadLevel(level):
    if app.player != None:
        app.group.remove(app.player.shape)
    app.player = None
    if (level == 0):
        generateGrass(300, 200, 400)
        for i in range(20):
            createPebble(randomInt(20, 380), randomInt(310, 390))
        Platform(250, 230, 50, 10)
        Platform(350, 150, 50, 10)
        Hint("Don't touch the grass!", 150, 200)
        app.endPoint = EndPoint(370, 115, 1)
        app.player = Player(100, -100)
    if (level == 1):
        app.endPoint = EndPoint(30, 250, 2)
        generateGrass(300, 100, 200)
        Hint("Jump over it!", 200, 200)
        app.player = Player(300, -100)
    if (level == 2):
        app.endPoint = EndPoint(350, 250, 3)
        generateGrass(300, 100, 400)
        Platform(0, 210, 50, 10)
        Platform(100, 110, 50, 10)
        Hint("Jump through the bottoms of platforms!", 200, 150)
        app.player = Player(50, 250)
    if (level == 3):
        Hint("You win!", 200, 150)
        app.player = Player(50, 250)
        app.endPoint = EndPoint(2000, 250, 3)
    app.overlay.toFront()
    
loadLevel(0)
        
def unloadLevel():
    for platform in platforms:
        app.group.remove(platform.shapes)
    for hint in hints:
        app.group.remove(hint.shapes)
    for grass in grasses:
        grass.remove()
    for peb in pebbles:
        app.group.remove(peb)
        
    for shape in app.endPoint.shapes:
        app.group.remove(shape)
    for shape in app.endPoint.effects:
        app.group.remove(shape)
        
    platforms.clear()
    hints.clear()
    grasses.clear()
    grassPatches.clear()
    eff.clear()



def levelTransition(level):
    app.overlay.toFront()
    app.transitioning = True
    print("Transitioning to level " + str(level))
    screenShake(2, 20)
    for i in range(100):
        schedule(f"app.overlay.opacity = {(i/100)**3 * 100}", i)
    schedule(f"unloadLevel()\nloadLevel({level})\napp.transitioning = False", 100)
    schedule("levelTransitionEffects()", 150)
    for i in range(100):
        schedule(f"app.overlay.opacity = {100 - ((i/100)**3) * 100}", i + 100)
        
eff = []
def levelTransitionEffects():
    for i in range(50):
        c = eff.append(TransitionEffect())
            
class TransitionEffect():
    def __init__(self):
        self.x = randomInt(0, 400)
        self.y = randomInt(380, 400)
        self.v = randomInt(2, 50)/10
        self.t = 0
        self.shapes = Group(
            Circle(self.x, 400, 6, fill=rgb(254, 255, 230), opacity=10),
            Circle(self.x, 400, 4, fill=rgb(254, 255, 230), opacity=10),
            Circle(self.x, 400, 3, fill=rgb(254, 255, 230), opacity=10),
            Circle(self.x, 400, 2, fill=rgb(254, 255, 230), opacity=10),
            Circle(self.x, 400, 1, fill=rgb(254, 255, 230), opacity=10)
        )
    def update(self):
        self.t += 1
        self.v *= 0.985
        self.shapes.opacity = max(0, 10 * (1 - self.t/180))
        self.y -= self.v
        self.shapes.centerY = self.y
        if (self.t > 180):
            app.group.remove(self.shapes)
        
    
app.buffer = 0
def onKeyHold(keys):
    if ('left' in keys):
        app.player.vX -= 0.75
    if ('right' in keys):
        app.player.vX += 0.75
def onKeyPress(key):
    if 'up' == key and app.player.canJump:
        app.player.vY = 8
        app.player.canJump = False
    elif not app.player.canJump:
        app.buffer = 4
        
app.enablePerformanceTools = True
app.lastSecond = time.perf_counter()
app.fpsLabel = Label(f"{app.stepsPerSecond} fps", 21, 390, fill='white')
app.frames = 0
def onStep():
    app.currentTick += 1
    app.frames += 1
    if app.enablePerformanceTools and app.frames > 59:
        app.fpsLabel.value = f"{(int) (app.stepsPerSecond - ((time.perf_counter() - app.lastSecond)//app.stepsPerSecond) ) } fps"
        app.fpsLabel.left = 5
        app.lastSecond = time.perf_counter()
    if not app.transitioning:
        update()
    if app.buffer > 0 and app.player.canJump:
        onKeyPress('up')
        app.buffer = 0
    app.buffer = max(0, app.buffer - 1)
    checkScheduledTasks()
    
def update():
    if app.transitioning:
        return
    if app.player == None:
        return
    for grass in grasses:
        grass.update()
    for hint in hints:
        hint.update()
    for e in eff:
        e.update()
    app.endPoint.update()
    app.player.update()




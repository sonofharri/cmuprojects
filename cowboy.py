import math
import time

app.stepsPerSecond = 30

app.background = rgb(242, 210, 141)
app.mousePosX = 0
app.mousePosY = 0
app.globalOffsetX = 0
app.globalOffsetY = 0
app.collisionObjects = []
app.objects = []

app.halfPi = math.pi/2

app.setMaxShapeCount(10000)

app.reloadTime = 90 # Reload time in frames (30fps)

Sound("cmu://765177/30872820/revolver_shoot.mp3")
Sound("cmu://765177/30872837/revolver_reload.mp3")
Sound("cmu://765177/30887004/hit.mp3")
Sound("cmu://765177/30887007/death.mp3")

class V:
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z # Z actually controls scale, or how far up the object is, because it's top-down.
    def __add__(self, other):
        if type(other) is V: return V(self.x + other.x, self.y + other.y)
        elif type(other) is float or type(other) is int: return V(self.x + other, self.y + other)
    def __sub__(self, other):
        if type(other) is V: return V(self.x - other.x, self.y - other.y)
        elif type(other) is float or type(other) is int: return V(self.x - other, self.y - other)
    def __mul__(self, other):
        if type(other) is V: return V(self.x * other.x, self.y * other.y)
        elif type(other) is float or type(other) is int: return V(self.x * other, self.y * other)
    def __str__(self):
        return f"{self.x}, {self.y}, {self.z}"
    def normalized(self):
        magnitude = (self.x*self.x + self.y*self.y)**0.5
        return V(self.x / magnitude, self.y / magnitude) if (magnitude > 0) else V(0, 0)
    def distance(self, target):
        return distance(self.x, self.y, target.x, target.y)
    def clone(self):
        return V(self.x, self.y, self.z)
    def dot(self, vec):
        return (self.x*vec.x + self.y*vec.y)

# Shape Part (shape with an offset and z value)
class SP:
    def __init__(self, shape, z=0, xOffset=0, yOffset=0):
        self.shape = shape
        self.z = z + 10
        self.xOffset = xOffset
        self.yOffset = yOffset
    # Sets the SCREEN position of the part
    def setPos(self, x, y, isPlayer=False):
        zShiftX = self.z/10 if isPlayer else (x - app.player.pos.x) * self.z/10
        zShiftY = self.z/10 if isPlayer else (y - app.player.pos.y) * self.z/-10
        self.shape.centerX = x + zShiftX + self.xOffset
        self.shape.centerY = y - zShiftY - self.yOffset
        # print(f'{self.shape.centerX} | {self.shape.centerY}')
    def rotate(self, theta):
        self.shape.rotateAngle = theta
        # TODO: Calculate how to rotate around the center
    def rotateTowards(self, theta):
        self.rotate((theta-self.shape.rotateAngle)/10)
        
def randomInt(range1, range2):
    return rounded(random() * (range2 - range1) + range1)

class Object:
    def __init__(self, pos, parts, collision=False, hideWhenBehind=False):
        self.pos = pos
        self.parts = parts
        self.hide = hideWhenBehind
        if collision:
            app.collisionObjects.append(self)
        app.objects.append(self)
    def update(self):
        if self.hide:
            for part in self.parts:
                if app.player.parts[0].shape.hitsShape(part.shape):
                    if part.shape.opacity > 10:
                        part.shape.opacity = max(10, part.shape.opacity - (part.shape.opacity/5))
                elif part.shape.opacity < 100:
                    part.shape.opacity = min(100, part.shape.opacity + (100 - part.shape.opacity)/5)
        for part in self.parts:
            part.setPos(self.pos.x - app.player.pos.x + 200 + app.globalOffsetX, self.pos.y - app.player.pos.y + 200 + app.globalOffsetY)
    def remove(self):
        for part in self.parts:
            app.group.remove(part.shape)


class Player:
    def __init__(self, pos):
        self.pos = pos
        self.speed = 2
        self.rot = 0
        self.velocity = V(0, 0)
        self.forceVelocity = V(0, 0)
        self.parts = [
            # Body
            SP( Oval(0,0, 20, 40, fill=rgb(81, 123, 172)), 0, 0, 0 ),
            # Head
            SP( Circle(0,0, 15, fill=rgb(240, 188, 151)), .1, 0, 0 ),
            
            # Gun
            SP( Rect(0,0, 35,8, fill=rgb(180, 180, 185)), .1, 0, 5 ),
            
            # Hat
            SP( Circle(0,0, 15, fill=rgb(97, 72, 51)), .2, 0, 0),
            SP( Circle(0,0, 6, fill=rgb(107, 78, 55)), .3, 0, 0)
            
        ]
        self.shots = 0
        self.ammo = 6
        self.reloading = False
    def update(self):
        self.pos += self.velocity
        self.pos += self.forceVelocity
        self.pos.x = max(-200, min(self.pos.x, 160))
        self.pos.y = max(-250, min(self.pos.y, 55))
        self.velocity*=0.6
        self.forceVelocity*=0.6
        self.rot = angleTo(200, 200, app.mousePosX, app.mousePosY) + 90
        for part in self.parts:
            part.setPos(200 + app.globalOffsetX, 200 + app.globalOffsetY, True)
            part.rotate(self.rot)
    def push(self, vec):
        self.forceVelocity += vec
        
def blur(shape, glowSize):
    glowShapes = []
    if type(shape) is Circle:
        shape.radius -= glowSize
        for i in range(glowSize):
            glowShapes.append(Circle(shape.centerX, shape.centerY, shape.radius + i, fill=None, border=shape.fill, borderWidth=i, opacity=(100 - i*(100/glowSize) ) ))
    if type(shape) is Line:
        for i in range(glowSize):
            glowShapes.append(Line(shape.x1, shape.y1, shape.x2, shape.y2, lineWidth=shape.lineWidth + i, fill=shape.fill, opacity=(100 - i*(100/glowSize) ) ))
    elif type(shape) is Rect:
        cX = shape.centerX
        cY = shape.centerY
        shape.height -= glowSize
        shape.width -= glowSize
        shape.centerX = cX
        shape.centerY = cY
        for i in range(glowSize):
            r = Rect(0,0, shape.width+i, shape.height+i, fill=None, border=shape.fill, borderWidth=i, opacity=(100 - i*(100/glowSize) )  )
            glowShapes.append(r)
            r.centerX = cX
            r.centerY = cY
    return glowShapes
        
app.player = Player(V(0, 0))

app.bullets = []
class Bullet():
    def __init__(self):
        self.inaccuracy = app.player.shots*app.player.shots * 10
        self.angle = angleTo(200, 200, app.mousePosX, app.mousePosY) + randomInt(-self.inaccuracy, self.inaccuracy)/10
        self.dir = getPointInDir(0, 0, self.angle, 1)
        line = Line(200, 200, 200 + self.dir[0] * 300, 200 + self.dir[1] * 300, lineWidth=2, fill=rgb(255, 242, 199))
        self.shapes = [
            line,
            Line(200, 200, 200 + self.dir[0] * 300, 200 + self.dir[1] * 300, lineWidth=5, opacity=20, fill=rgb(255, 255, 255))
        ]
        # print(f'Dir: {self.dir[0]}, {self.dir[1]}')
        self.state = 0
        # States: 0 = newly spawned, 1-5 = Moving, 6 = Marked for deletion
        app.bullets.append(self)
        app.player.shots += 1
        schedule("app.player.shots -= 1", 15)
        self.checkEnemies()
    def update(self):
        for shape in self.shapes:
            shape.x1 += self.dir[0] * 50
            shape.x2 += self.dir[0] * 50
            shape.y1 += self.dir[1] * 50
            shape.y2 += self.dir[1] * 50
        self.state += 1
        if (self.state == 3):
            self.remove()
    def remove(self):
        for shape in self.shapes:
            app.group.remove(shape)
    def checkEnemies(self):
        for enemy in enemies:
            if self.check(enemy.object.parts[1].shape):
                enemy.hit()
                break
    def check(self, shape):
        
        checkLine = Line(200, 200, 200 + self.dir[0] * 500, 200 + self.dir[1] * 500, lineWidth=2, visible=False)
        return checkLine.hitsShape(shape)

    

enemies = []
class Enemy:
    def __init__(self, x, y):
        self.state = 0 # 0 = Still, 1 = Moving, 2 = Still and Shooting
        self.pathFindingTarget = app.player.pos.clone()
        self.health = 1
        self.object = Object(V(x, y), [
            # Body
            SP( Oval(0,0, 20, 40, fill=rgb(172, 81, 82)), 0, 0, 0 ),
            # Head
            SP( Circle(0,0, 15, fill=rgb(240, 188, 151)), .1, 0, 0 ),
            
            # Hat
            SP( Circle(0,0, 15, fill=rgb(97, 72, 51)), .2, 0, 0),
            SP( Circle(0,0, 6, fill=rgb(107, 78, 55)), .3, 0, 0)
        ], True, False)
        enemies.append(self)
        self.aliveTicks = randomInt(0, 30)
    def update(self):
        self.aliveTicks += 1
        self.object.pos.x += math.sin(self.aliveTicks/randomInt(8,12)) * randomInt(10, 20)/10
    def hit(self):
        self.health -=1
        if (self.health == 0):
            self.die()
    def die(self):
        self.object.remove()
        enemies.remove(self)
        Sound("cmu://765177/30887007/death.mp3").play(restart=True)
        
Enemy(-100, -150)
Enemy(-160, -180)
Enemy(-250, -50)

Enemy(30, -210)
Enemy(70, -320)
Enemy(10, -270)
Enemy(-240, -240)
Enemy(-380, -170)

Enemy(-260, -320)

tumbleweeds = []    
class Tumbleweed:
    def __init__(self):
        self.shapes = []
        for i in range(25):
            r = randomInt(180, 215)
            shape = Oval(0,0, randomInt(5, 40), randomInt(5, 40), dashes=(8, 3), fill=None, border=rgb(r, r - 35, r - 60))
            self.shapes.append(SP(shape, randomInt(0, 3)/10, randomInt(-5, 5), randomInt(-5, 5) ) )
        self.object = Object(V(0, 0), self.shapes)
        self.pos = V(randomInt(-200, -50), randomInt(0, 100))
        self.speed = randomInt(-30, 30)/3
        if (self.speed) == 0:
            self.speed = 1
        self.dir = V(randomInt(-20, 20)/10, randomInt(-40, -20)/10)
        # print(f'{self.dir}')
        self.aliveTime = 0
        tumbleweeds.append(self)
        # print(f"size of tumbleweeds: {len(tumbleweeds)}")
    def update(self):
        # print(f"pos: {self.pos}")
        self.aliveTime += 1
        self.pos += self.dir
        finPosX = self.pos.x - app.player.pos.x + 200 + app.globalOffsetX
        finPosY = self.pos.y - app.player.pos.y + 200 + app.globalOffsetY + math.sin(self.aliveTime/self.speed)*5
        if (finPosX < 400 and finPosX > 0) and (finPosY < 400 and finPosY > 0):
            for s in self.shapes:
                s.setPos(finPosX, finPosY)
                s.shape.rotateAngle += self.speed
                s.shape.visible = True
        else:
            self.aliveTime = 600
            self.remove()
        if (self.aliveTime >= 599):
            self.remove()
    def remove(self):
        # print("removed!")
        for s in self.shapes:
            app.group.remove(s.shape)


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

def update():
    app.globalOffsetX = (app.mousePosX - 200)/-10
    app.globalOffsetY = (app.mousePosY - 200)/-10
    app.player.update()
    for obj in app.objects:
        obj.update()
    for bullet in app.bullets:
        bullet.update()
    for enemy in enemies:
        enemy.update()
    for t in tumbleweeds:
        t.update()
    # Tumbleweeds cause too much lag to be an important feature. Oh well!
    # if len(tumbleweeds) < 10 and randomInt(0, 60) == 1:
    #     Tumbleweed()
    app.bullets[:] = [bullet for bullet in app.bullets if bullet.state < 5]
    tumbleweeds[:] = [t for t in tumbleweeds if t.aliveTime <= 600]
    
app.fps = 30
app.enablePerformanceTools = True
app.lastFrame = time.perf_counter()
app.fpsLabel = Label(f"{app.stepsPerSecond} fps", 21, 375, fill='white')
def onStep():
        
    update()
    checkScheduledTasks()
    if app.player.shots > 0:
        ammoIndicator.opacity = min(100, ammoIndicator.opacity + 20)
    else:
        ammoIndicator.opacity = max(20, ammoIndicator.opacity - 5)
    
    app.fps = (int) (app.stepsPerSecond//(time.perf_counter() - app.lastFrame)//app.stepsPerSecond)
    app.fpsLabel.value = f"{app.fps} fps"
    app.fpsLabel.left = 5
    app.lastFrame = time.perf_counter()
    
    app.fpsLabel.toFront()
    
    
    
crosshair = Group(
    Line(-10, 0, 10, 0, fill='white', lineWidth=1),
    Line(0, -10, 0, 10, fill='white', lineWidth=1)
)

ammoIndicator = Label("6/6", -100, 0, size=20, bold=True, fill="white", border=rgb(100, 50, 50), borderWidth=1, font="grenze", opacity=20)
reloadIndicator = Arc(-100, 0, 20, 20, 0, 1, fill="white", border="white", borderWidth=3, opacity=30, visible=False)

def updateCrosshair(x, y):
    angle = angleTo(200, 200, x, y)
    point = getPointInDir(0, 0, angle, 100)
    crosshair.centerX = min(max(0, point[0] + 200), 400)
    crosshair.centerY = min(max(0, point[1] + 200), 400)
    crosshair.toFront()
    
    if app.player.reloading:
        reloadIndicator.visible = True
        reloadIndicator.centerX = crosshair.centerX
        reloadIndicator.centerY = crosshair.centerY
        ammoIndicator.value = "reloading..."
    else:
        reloadIndicator.visible = False
        ammoIndicator.value = f"{app.player.ammo}/6"
    
    
    ammoIndicator.centerX = crosshair.centerX
    ammoIndicator.centerY = crosshair.centerY + 25
    ammoIndicator.toFront()
    # print(f"x: {crosshair.centerX}, y: {crosshair.centerY}")
    
def onMouseMove(x,y):
    app.mousePosX = x
    app.mousePosY = y
    updateCrosshair(x, y)
def onMouseDrag(x,y):
    app.mousePosX = x
    app.mousePosY = y
    updateCrosshair(x, y)
def onMousePress(x,y):
    if app.player.ammo > 0 and not app.player.reloading:
        Bullet()
        pushDir = getPointInDir(0, 0, app.player.rot, -5)
        app.player.push(V(pushDir[1], -pushDir[0]))
        app.player.ammo -= 1
        updateCrosshair(app.mousePosX, app.mousePosY)
        Sound("cmu://765177/30872820/revolver_shoot.mp3").play(restart=True)

def onKeyHold(keys):
    if ('s' in keys):
        app.player.velocity.y = app.player.speed
    if ('a' in keys):
        app.player.velocity.x = -app.player.speed
    if ('w' in keys):
        app.player.velocity.y = -app.player.speed
    if ('d' in keys):
        app.player.velocity.x = app.player.speed
        
def onKeyPress(key):
    if key == "r" and not app.player.reloading and not app.player.ammo == 6:
        # print("reloading")
        Sound("cmu://765177/30872837/revolver_reload.mp3").play(restart=True)
        app.player.reloading = True
        updateCrosshair(app.mousePosX, app.mousePosY)
        schedule("app.player.reloading = False;app.player.ammo = 6;updateCrosshair(app.mousePosX, app.mousePosY)", app.reloadTime)
        reloadIndicator.sweepAngle = 1
        schedule("ammoIndicator.opacity = 100;app.player.shots = 1", app.reloadTime + 1)
        schedule("app.player.shots -= 1", app.reloadTime + 21)
        for i in range(app.reloadTime):
            schedule("reloadIndicator.sweepAngle = min(360, reloadIndicator.sweepAngle + 360/app.reloadTime)", i)
        for i in range(20):
            schedule(f"ammoIndicator.fill = rgb(55 + {i} * 10, 255, 55 + {i} * 10)", i + app.reloadTime + 1)


music = Sound("cmu://765177/30434660/Wild+Arms+-+Town+Theme.mp3")
music.play(loop=True)




#           * * * * * * * * * * *

#                 OBJECTS

#           * * * * * * * * * * *

# Saloon
def createLeftBuilding(x, y, text):
    Object(V(x, y), [
        
        # Bottom Pillar
        SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.0, 180, -200),
        SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.5, 180, -200),
        SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.0, 180, -200),
        SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.5, 180, -200),
        SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 2.0, 180, -200),
        
        # Top Pillar
        SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.0, 200, 200),
        SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.5, 200, 200),
        SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.0, 200, 200),
        SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.5, 200, 200),
        SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 2.0, 200, 200),
        
        # Ceiling
        SP(Rect(0,0, 400, 400, fill=rgb(138, 82, 43)), 2.5),
        SP(Rect(0,0, 100, 200, fill=rgb(166, 99, 53)), 4, 100, 0),
        SP(Label(text,0,0, size=32, font="grenze", bold=True, fill='black', rotateAngle=-90), 4, 100, 0)
    ], False, True)
    
    ln = Line(0,0,400,0, dashes=(2, 30), lineWidth=400, fill=rgb(112, 65, 31))
    ln.toBack()
    floor = Rect(0,0, 400, 400, fill=rgb(116, 69, 35))
    floor.toBack()
    # Saloon Interior
    Object(V(x, y), [
        # Floor
        SP(floor, 0),
        SP(ln, 0)
    ], False, False)

createLeftBuilding(-300, -100, "Ye Olde Saloon")
createLeftBuilding(-300, -350, "Apothecary")





ln2 = Line(0,0,400,0, dashes=(2, 30), lineWidth=400, fill=rgb(112, 65, 31))
ln2.toBack()
floor2 = Rect(0,0, 400, 400, fill=rgb(116, 69, 35))
floor2.toBack()
# Firearms Interior
Object(V(50, -100), [
    # Floor
    SP(floor2, 0),
    SP(ln2, 0),
], False, False)


# Firearms building
Object(V(50, -100), [
    
    # Bottom Pillar
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.0, -180, -200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.5, -180, -200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.0, -180, -200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.5, -180, -200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 2.0, -180, -200),
    
    # Top Pillar
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.0, -200, 200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.5, -200, 200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.0, -200, 200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.5, -200, 200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 2.0, -200, 200),
    
    # Ceiling
    SP(Rect(0,0, 400, 400, fill=rgb(138, 82, 43)), 2.5),
    SP(Rect(0,0, 100, 200, fill=rgb(166, 99, 53)), 4, -100, 0),
    SP(Label("Blacksmith",0,0, size=32, font="grenze", bold=True, fill='black', rotateAngle=90), 4, -100, 0)
], False, True)



ln3 = Line(0,0,400,0, dashes=(2, 30), lineWidth=400, fill=rgb(112, 65, 31))
ln3.toBack()
floor3 = Rect(0,0, 400, 400, fill=rgb(116, 69, 35))
floor3.toBack()
# Hotel Interior
Object(V(50, -350), [
    # Floor
    SP(floor3, 0),
    SP(ln3, 0),
], False, False)


# hotel
Object(V(50, -350), [
    
    # Bottom Pillar
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.0, -180, -200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.5, -180, -200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.0, -180, -200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.5, -180, -200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 2.0, -180, -200),
    
    # Top Pillar
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.0, -200, 200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 0.5, -200, 200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.0, -200, 200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 1.5, -200, 200),
    SP(Rect(0,0, 20, 20, fill=rgb(122, 72, 37)), 2.0, -200, 200),
    
    # Ceiling
    SP(Rect(0,0, 400, 400, fill=rgb(138, 82, 43)), 2.5),
    SP(Rect(0,0, 100, 200, fill=rgb(166, 99, 53)), 4, -100, 0),
    SP(Label("Hotel",0,0, size=32, font="grenze", bold=True, fill='black', rotateAngle=90), 4, -100, 0)
], False, True)



# Dirt road
road = Rect(0,0, 200, 1600, fill=rgb(77, 53, 27), border=rgb(54,38,20), borderWidth=10)
road.toBack()
Object(V(-125, -200), [SP(road,0.5,0,0)], False, False)


sandLines = []
off = 5
for i in range(-5, 5):
    for j in range(-5, 5):
        o2 = Oval(0,0, 200, 40, fill=rgb(242, 210, 141))
        o2.toBack()
        o1 = Oval(0,0, 200, 40, fill=rgb(209, 180, 117))
        o1.toBack()
        
        sandLines.append(SP(o1, 0, j * 200, i * 200))
        sandLines.append(SP(o2, 0, j * 200, i * 200 + off))
        off *= -1

# Sand
Object(V(0, 0), sandLines, False, False)
update()


# Crate
Object(V(-125, 20), [
    SP(Rect(0,0,100,100, fill=rgb(92, 71, 50)), 0, 0, 0),
    SP(Rect(0,0,100,100, fill=rgb(125, 92, 59)), 0.5, 0, 0)
    
], True, False)


















































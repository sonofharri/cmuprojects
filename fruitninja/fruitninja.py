import math
import time

app.stepsPerSecond = 60

app.started = False
app.frozen = False
app.timeLeft = 60
app.score = 0

fruits = []
slicedFruits = []
splatters = []

fruitTypes = ["watermelon", "apple", "mango", "orange", "coconut", "bomb"]
class Fruit:
    def __init__(self, type="random"):
        self.x = randomInt(100, 300)
        self.y = 400
        self.z = 1
        self.rotation = randomInt(-90, 90)
        self.hasGravity = True
        self.velocity = [randomInt(-30, 30)/10, 10]
        self.shapes = []
        self.cshapes = []
        
        if type == "random":
            type = (fruitTypes[randomInt(0, len(fruitTypes) - 1)])
        
        self.setType(type)
        
        self.shadow = Oval(self.x + 10, self.y + 10, self.width, 60, fill='black', opacity=30)
        self.shapes.append(Oval(self.x, self.y, self.width, 60, fill=self.fillColor, border=self.borderColor, borderWidth=3 ))
        if type == "watermelon":
            self.cshapes.append(Oval(self.x, self.y, self.width, 40, fill=None, border=self.borderColor, borderWidth=3 ))
            self.cshapes.append(Oval(self.x, self.y, self.width, 15, fill=None, border=self.borderColor, borderWidth=3 ))
        if type == "bomb":
            self.cshapes.append(Line(self.x - 20, self.y, self.x + 10, self.y, fill=self.borderColor, lineWidth=5))
            self.cshapes.append(Line(self.x, self.y - 20, self.x, self.y + 10, fill=self.borderColor, lineWidth=5))
        
        #self.shapes.append(Polygon(-40, 0, 40, 0, 40, 5, -40, 5, 30, 5, 5, 20, fill=rgb(17, 55, 22)))
        self.update()
    def setType(self, type):
        self.width = 60
        self.fillColor = None # This should never happen!
        self.borderColor = None
        self.type = type
        if type == "watermelon":
            self.fillColor = gradient(rgb(17, 55, 22), rgb(81, 157, 71), start='bottom-right')
            self.borderColor = rgb(27, 67, 33)
            self.splatterColor = 'red'
            self.width = 80
        if type == "apple":
            self.fillColor = gradient(rgb(55, 17, 17), rgb(175, 71, 71), start='bottom-right')
            self.borderColor = rgb(67, 27, 27)
            self.splatterColor = rgb(237, 230, 230)
        if type == "mango":
            self.fillColor = gradient(rgb(205, 75, 24), rgb(188, 194, 83), start='bottom-right')
            self.borderColor = rgb(125, 47, 0)
            self.splatterColor = rgb(205, 75, 24)
            self.width = 70
        if type == "orange":
            self.fillColor = gradient(rgb(240, 169, 26), rgb(235, 168, 59), start='bottom-right')
            self.borderColor = rgb(255, 157, 0)
            self.splatterColor = rgb(205, 75, 24)
        if type == "coconut":
            self.fillColor = gradient(rgb(55, 32, 17), rgb(158, 104, 71), start='bottom-right')
            self.borderColor = rgb(66, 25, 0)
            self.splatterColor = rgb(240, 229, 201)
        if type == "bomb":
            self.fillColor = gradient(rgb(20, 0, 0), rgb(0, 0, 0), start='bottom-right')
            self.borderColor = rgb(140, 0, 0)
            self.splatterColor = rgb(0, 0, 0)
    def update(self):
        if (self.y > 470):
            self.__del__()
        if (self.y < 0):
            self.y = 0
        if (self.x > 400 and self.velocity[0] > 0) or (self.x < 0 and self.velocity[0] < 0):
            self.velocity[0] *= -0.5
        self.velocity[1]-=(9.8/app.stepsPerSecond)
        if self.hasGravity and not app.frozen:
            self.x += self.velocity[0]
            self.y -= self.velocity[1]
        self.rotation += self.velocity[0] * 1.5
        for shape in self.cshapes:
            shape.centerX = self.x
            shape.centerY = self.y
            shape.rotateAngle = self.rotation
        for shape in self.shapes:
            if (app.swipePoly != None and app.holding and app.swipePoly.hitsShape(shape) and distance(app.lmx, app.lmy, app.mx, app.my) > 10):
                self.slice()
                pass
            shape.centerX = self.x
            shape.centerY = self.y
            shape.rotateAngle = self.rotation
        
        self.shadow.centerX = self.x + 10
        self.shadow.centerY = self.y + 10
        self.shadow.rotateAngle = self.rotation
        
    def slice(self):
        if self.type == "bomb":
            stopGame(self.x, self.y)
            fruits.remove(self)
            self.__del__()
            return
        if not self.hasGravity:
            startGame()
        if not self in fruits:
            return
        app.score += 1
        updateScore()
        screenShake(randomInt(1, 3))
        splatters.append(Splatter(self.x, self.y, self.splatterColor)) # needs to be drawn first
        angle = angleTo(app.lmx, app.lmy, app.mx, app.my) - 90
        v = self.velocity if self.hasGravity else [0, 1]
        v[0] += randomInt(-10, 10)/10
        v[0] += (app.mx - app.lmx)/20
        v[1] += (app.my - app.lmy)/-20
        slicedFruits.append(SlicedFruit(self.x, self.y, angle, v, self.type))
        point = getPointInDir(self.x, self.y, angle, -50)
        slicedFruits.append(SlicedFruit(point[0], point[1], angle + 180, v, self.type))
        fruits.remove(self)
        self.__del__()
    def __del__(self):
        for shape in self.shapes:
            app.group.remove(shape)
        for shape in self.cshapes:
            app.group.remove(shape)
        app.group.remove(self.shadow)
        
class Splatter:
    def __init__(self, x, y, color='red'):
        self.x = x
        self.y = y
        self.shapes = []
        self.aliveTime = 0
        for i in range(5):
            self.shapes.append(Star(self.x + randomInt(-15, 15), self.y + randomInt(-15, 5), randomInt(35, 40), randomInt(7, 11), roundness=randomInt(75, 90), fill=color, opacity=10))
        for i in range(15):
            self.shapes.append(Star(self.x + randomInt(-50, 50), self.y + randomInt(-50, 30), randomInt(3, 6), randomInt(7, 11), roundness=randomInt(75, 90), fill=color, opacity=20))
    def update(self):
        self.aliveTime+=1
        if (self.aliveTime > 120):
            times = 0
            for shape in self.shapes:
                if shape.opacity > 0.2:
                    shape.opacity -= 0.2
                    times += 1
                else:
                    continue
            if times == 0:
                self.__del__()
                splatters.remove(self)
    def __del__(self):
        for shape in self.shapes:
            app.group.remove(shape)
        
class SlicedFruit:
    def __init__(self, x, y, rot, velocity, type):
        self.x = x
        self.y = y
        self.rotation = rot
        self.velocity = velocity
        self.setType(type)
        self.shapes = []
        self.shapes.append(Polygon(
            -35, 0, 
            -30, -30, 
            -20, -40, 
            0, -50,
            20, -40, 
            30, -30, 
            35, 0,
            fill=self.fillColor, border=self.borderColor, borderWidth=3 )) if type == "watermelon" else self.shapes.append(Polygon(
            -35, 0, 
            -30, -20, 
            -20, -30, 
            0, -33,
            20, -30, 
            30, -20, 
            35, 0,
            fill=self.fillColor, border=self.borderColor, borderWidth=3 ))
        self.update()
    def setType(self, type):
        self.width = 60
        self.fillColor = None # This should never happen!
        self.borderColor = None
        if type == "watermelon":
            self.fillColor = gradient(rgb(17, 55, 22), rgb(81, 157, 71), start='bottom-right')
            self.borderColor = rgb(27, 67, 33)
            self.splatterColor = 'red'
        if type == "apple":
            self.fillColor = gradient(rgb(55, 17, 17), rgb(175, 71, 71), start='bottom-right')
            self.borderColor = rgb(67, 27, 27)
            self.splatterColor = rgb(237, 230, 230)
        if type == "mango":
            self.fillColor = gradient(rgb(205, 75, 24), rgb(188, 194, 83), start='bottom-right')
            self.borderColor = rgb(125, 47, 0)
            self.splatterColor = rgb(205, 75, 24)
        if type == "orange":
            self.fillColor = gradient(rgb(240, 169, 26), rgb(235, 199, 59), start='bottom-right')
            self.borderColor = rgb(255, 157, 0)
            self.splatterColor = rgb(205, 75, 24)
        if type == "coconut":
            self.fillColor = gradient(rgb(55, 32, 17), rgb(158, 104, 71), start='bottom-right')
            self.borderColor = rgb(66, 25, 0)
            self.splatterColor = rgb(240, 229, 201)
    def update(self):
        if (self.y > 470):
            self.__del__()
            slicedFruits.remove(self)
        if (self.y < 0):
            self.y = 0
        self.velocity[1]-=.163
        self.x += self.velocity[0]
        self.y -= self.velocity[1]
        self.rotation += self.velocity[0] * 1.5
        for shape in self.shapes:
            shape.centerX = self.x
            shape.centerY = self.y
            shape.rotateAngle = self.rotation
            pass
    def __del__(self):
        for shape in self.shapes:
            app.group.remove(shape)
        
def createBand(size, offset):
    ret = [-size, offset, size, offset]
    for i in range(2):
        for j in range(rounded(size/2)):
            ret.append(-size + j*size/10)
            ret.append(randomInt(-size/3, size/3) + offset)
    #debugList(ret)
    return ret

def calcEaseOut(x):
    if (x < 0.5):
        return (1 - math.sqrt(1 - ((2 * x)**2)))/2
    else:
        return (math.sqrt(1 - (-2*x + 2)**2) + 1)/2
        
    
def calcEaseOutCubic(x):
    return 4 * x * x * x if x < 0.5 else 1 - (-2*x**3)/2
        
app.sliceToStartText = None
app.sliceToStartShadow = None
app.menuFruitCircle = None
app.menuFruit = None
def createMenuFruit():
    app.menuFruit = createFruit("watermelon")
    app.menuFruit.x = 200
    app.menuFruit.y = 400
    app.menuFruit.velocity = [5, 0]
    app.menuFruit.hasGravity = False
    
    app.menuFruitCircle = Circle(200, 300, 60, fill=None, border=rgb(29, 90, 171), borderWidth=10, opacity=0)
    app.sliceToStartShadow = Image("cmu://765177/27110022/slicetostartoutline.png", 600, 200)
    app.sliceToStartText = Image("cmu://765177/27112387/slicetostart.png", 600, 200)
    
    for i in range(100):
        a = calcEaseOut(i/100)
        schedule(f"app.menuFruit.y={450 - a * 150}\napp.sliceToStartText.centerX={600 - a * 400}\napp.sliceToStartShadow.centerX={600 - a * 400}\napp.menuFruitCircle.opacity={a*80}", i)
    
        
def createFruit(type="random"):
    f = Fruit(type)
    fruits.append(f)
    return f
    
flashes = []
app.stopBomb = None
def stopGame(x, y):
    screenShake(2, 60)
    app.frozen = True
    schedule("screenShake(10, 60)", 60)
    app.started = False
    for i in range(15):
        flashes.append(Star(x, y, randomInt(400, 600), randomInt(8, 12), roundness=0, fill=rgb(255, 255, 255), opacity=30, rotateAngle=(i * 40)))
    app.stopBomb = Circle(x, y, 30, fill=gradient(rgb(20, 0, 0), rgb(0, 0, 0), start='bottom-right'), border=rgb(140, 0, 0))
    for i in range(240):
        schedule(f"for flash in flashes:\n    flash.rotateAngle+=randomInt(-20, 20)", i)
    for i in range(9):
        schedule(f"for flash in flashes:\n    if flash.opacity > 3:\n        flash.opacity-=3", i + 110)
    schedule("gameOver()", 120)
    
def gameOver():
    for flash in flashes:
        app.group.remove(flash)
    app.group.remove(app.stopBomb)
    flashes.clear()
    app.gameOverImage = Image("cmu://765177/27296832/gameOver.png", 25, 150)
    app.frozen = False
    screenShake(2, 30)
            
    
def startGame():
    #
    #
    # TODO: Add a countdown
    #
    #
    screenShake(5)
    app.started = True
    for i in range(40):
        a = calcEaseOut(i/40)
        schedule(f"app.menuFruitCircle.opacity={80 - a * 80}\napp.sliceToStartText.opacity={100 - a * 100}\napp.sliceToStartShadow.opacity-=2.49\nlogo.opacity={100 - a * 100}", i)
        
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
    
    
app.fruitCooldown = 60
def updateFruits():
    if app.started:
        app.fruitCooldown-=1
        if (randomInt(0, 50) == 1 and app.fruitCooldown <= 0):
            createFruit()
            app.fruitCooldown = 15
    for fruit in fruits:
        fruit.update()
    for sf in slicedFruits:
        sf.update()
    for splatter in splatters:
        splatter.update()


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

def randomInt(range1, range2):
    return rounded(random() * (range2 - range1) + range1)
    
def clamp(number, number1, number2):
    if (number < number1):
        return number1
    if (number > number2):
        return number2
    return number
    
def setTuple(tup, index, value):
    ret = list(tup)
    ret[index] = value
    return tuple(ret)
    
def sortTuplesBySecond(tup):
    s = len(tup)
    for i in range(0, s):
        for j in range(0, s-i-1):
            if (tup[j][1] > tup[j + 1][1]):
                temp = tup[j]
                tup[j]= tup[j + 1]
                tup[j + 1] = temp
    return tup
    
def setLists(listToSet, listToSetTo):
    for i in range(len(listToSet)):
        listToSet[i] = listToSetTo[i] if len(listToSetTo) > i else listToSet.pop(i)
        
def playSound(assetName):
    asset = "https://github.com/sonofharri/cmuprojects/raw/fa8501bf7cb60a2828a457bda93b7b64afa322cc/fruitninja/sounds/" + assetName + ".mp3"
    Sound(asset)

def debugList(*values):
    ret = ""
    for s in values:
        ret += str(s) + ","
    print("[Debug] " + ret)

def midPoint(x1, y1, x2, y2):
    return ((x1 + x2)/2, (y1 + y2)/2)

def p(r, g, b, *points):
    return Polygon(*points, fill=rgb(r, g, b))
    
def r(rd,g,b,x,y,x2,y2):
    Rect(x,y,x2,y2,fill=rgb(rd,g,b))
    
def rr(rd,g,b,x,y,x2,y2,rot):
    Rect(x,y,x2,y2,fill=rgb(rd,g,b),rotateAngle=rot)
    

    
scratches = []
def scratch(x1, y1, x2, y2):
    scratches.append(Line(x1, y1, x2, y2, lineWidth=4, fill=gradient(rgb(40, 25, 12), rgb(81, 45, 22))) )
    pt = midPoint(x1, y1, x2, y2)
    scratches.append(p(81, 45, 22, x1, y1, pt[0], pt[1]+5, x2, y2))
    #debugList(x1, y1, x2, y2)
    
bg = Rect(0, 0, 800, 800, fill=gradient(rgb(108, 62, 33),rgb(81, 45, 22)))
fg = Line(40, 200, 400, 200, fill=gradient(rgb(56, 31, 14), rgb(43,23,8)), lineWidth=400, dashes=(8, 62), opacity=30)

scratch(100, 100, 200, 200)
scratch(50, 300, 150, 250)
scratch(300, 150, 250, 300)
for i in range(3):
    scratch(randomInt(0, 400), randomInt(0, 400), randomInt(0, 400), randomInt(0, 400))
    
Line(40, 200, 400, 200, fill=gradient(rgb(56, 31, 14), rgb(43,23,8)), lineWidth=400, dashes=(10, 60), opacity=30)

logo = Image("cmu://765177/27101810/fnlogo.png", 50, -100)
for i in range(60):
    a = calcEaseOut(i/60) * 100
    schedule(f"logo.centerY={a}\nlogo.opacity={a}\nlogo.rotateAngle={a/4 - 25}", i)

schedule("createMenuFruit()", 60)
playSound("music")
    
app.lmx = 0
app.lmy = 0
app.mx = 0
app.my = 0

app.holding = False

def onMousePress(x, y):
    app.holding = True
def onMouseRelease(x, y):
    app.holding = False
    
def onMouseDrag(x, y):
    app.lmx = app.mx
    app.lmy = app.my
    app.mx = x
    app.my = y
def onMouseMove(x, y):
    app.lmx = app.mx
    app.lmy = app.my
    app.mx = x
    app.my = y
    
def updateBackground(x, y):
    bg.centerX = 400 - x
    bg.centerY = 400 - y

swipe = []
swipeTimes = []
app.swipePoly = None
app.swipePolyBg = None
app.offTick = False

#app.lastReset = time.time()
#app.frameCount = 0


def onStep():
    # app.frameCount += 1
    # if app.frameCount >= 60:
    #     app.frameCount = 0
    #     frameTime = time.time() - app.lastReset
    #     if (frameTime > 1.05):
    #         print("Frame dropped! " + str(frameTime - 1))
    #     app.lastReset = time.time()
    updateBlade()
    updateBackground(app.mx, app.my)
    checkScheduledTasks()
    updateFruits()

scoreNumbers = []
def updateScore():
    n = 0
    for i in scoreNumbers:
        app.group.remove(i)
    scoreNumbers.clear()
    for digit in str(app.score):
        n += 1
        scoreNumbers.append(Image(getFontNumber(digit), n * 40, 40))
        
    
def getFontNumber(number):
    return "https://raw.githubusercontent.com/sonofharri/cmuprojects/fa8501bf7cb60a2828a457bda93b7b64afa322cc/fruitninja/font/" + str(number) + ".png"
    
# Initiate assets
for i in range(10):
    Image(getFontNumber(i), -1000, 50)
    
def updateBlade():
    
    mx = app.mx
    my = app.my
    
    if (len(swipe) > 0 and app.swipePoly != None):
        app.group.remove(app.swipePoly)
    if (len(swipe) > 0 and app.swipePolyBg != None):
        app.group.remove(app.swipePolyBg)
        
    if app.holding and app.lmx != mx and app.lmy != my:
        swipe.append((mx, my))
        swipeTimes.append(0)
        
    if (len(swipe) > 0):
        angle = angleTo(app.lmx, app.lmy, mx, my)
        #setLists(swipe, swap(swipe))
        #swipe = sortTuplesBySecond(swipe)
        points = []
        swipe.reverse()
        if len(swipe) > 1:
            
            # for s in range(len(swipe)):
            #     rot = 360 - angleTo(swipe[s + 1][0], swipe[s + 1][1], swipe[s][0], swipe[s][1]) if s == 0 else angleTo(swipe[s - 1][0], swipe[s -1][1], swipe[s][0], swipe[s][1])
            #     size = clamp(s * 5, 0, 15)
            #     x, y = getPointInDir( swipe[s][0], swipe[s][1], rot + 90, size)
            #     points.append(y)
            #     points.append(x)
            # swipe.reverse()
            # for s in range(len(swipe)):
            #     rot = 360 - angleTo(swipe[s + 1][0], swipe[s + 1][1], swipe[s][0], swipe[s][1]) if s == 0 else angleTo(swipe[s - 1][0], swipe[s -1][1], swipe[s][0], swipe[s][1])
            #     size = clamp(s * 5, 0, 15)
            #     x, y = getPointInDir( swipe[s][0], swipe[s][1], rot - 90, size)
            #     points.append(y)
            #     points.append(x)
            for s in range(len(swipe)):
                points.append(swipe[s][1])
                points.append(swipe[s][0])
        points.reverse()
        lastPoint = getPointInDir( mx, my, angleTo(app.lmx, app.lmy, mx, my), 20 )
        
        points.append(lastPoint[0])
        points.append(lastPoint[1] )
        
        if (app.swipePoly != None) :
            app.group.remove(app.swipePoly)
        if (app.swipePoly != None) :
            app.group.remove(app.swipePolyBg)
        
        app.swipePolyBg = Polygon(*points, fill=None, border=rgb(117, 130, 130), borderWidth=16 - len(swipe), opacity=100)
        app.swipePoly = Polygon(*points, fill=rgb(236, 250, 250), border=rgb(236, 250, 250), borderWidth=6 - len(swipe), opacity=80)
        
    if app.offTick and len(swipe) > 0:
        swipe.pop(0)
        swipeTimes.pop(0)
        if (len(swipe) > 2):
            swipe.pop(0)
            swipeTimes.pop(0)
    app.offTick = not app.offTick














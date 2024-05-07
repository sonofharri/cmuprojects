
app.stepsPerSecond = 60

app.background = gradient(rgb(245, 137, 37), rgb(255, 123, 0), rgb(201, 138, 54), start='top')

app.objects = []
app.constGravity = 9.8/60
app.bounciness = 0.8 # How much energy is absorbed on impact; 1 = 0%, 0 = 100%

app.m = False # Mouse Pressed
app.mx = 0
app.my = 0

class Object:
    def __init__(self, x, y, size, *c):
        self.x = x
        self.y = y
        self.size = size
        self.rotation = 0
        self.vX = 0
        self.vY = 0
        self.shape = Rect(x - size/2, y - size/2, size, size, fill=gradient(rgb(c[0], c[1], c[2]), rgb(c[3], c[4], c[5])), border=gradient(rgb(255, 255, 255), rgb(200, 200, 200), start='top'))
        self.line = None
        app.objects.append(self)
    def update(self):
        if app.m:
            if self.y > 399:
                self.y = 395
            self.vX += (self.x - app.mx)/400
            self.vY += (self.y - app.my)/400
            if self.line == None:
                self.line = Line(self.x, self.y, app.mx, app.my, lineWidth=2, fill=rgb(255, 255, 255 ))
            else:
                self.line.x1 = self.x
                self.line.y1 = self.y
                self.line.x2 = app.mx
                self.line.y2 = app.my
                self.line.fill = rgb(0, randomInt(100, 255), randomInt(100, 255))
        else:
            self.vY-=app.constGravity
            if self.line != None:
                app.group.remove(self.line)
                self.line = None
                
                
        self.x-=self.vX
        self.y-=self.vY
        self.rotation += self.vX
        
        if (abs(self.vY) < 0.1 and abs(self.rotation) % 90 > 1):
            self.vX += ((self.rotation % 90) - 45)/360
        
        self.vX *= 0.99
        self.vY *= 0.99
        #print(f"vx{self.vX} : vy{self.vY}")
        self.shape.centerX = self.x
        self.shape.centerY = self.y
        self.shape.rotateAngle = self.rotation
        if (self.shape.bottom >= 400):
            self.vY *= -app.bounciness
            self.shape.bottom = 398
            if (self.vY == 0):
                self.vY = 20
        if (self.shape.left <= 0):
            self.vX *= -app.bounciness
            self.shape.left = 1
            if (self.vX == 0):
                self.vX = -20
        if (self.shape.right >= 400):
            self.vX *= -1
            self.shape.right = 399
            if (self.vX == 0):
                self.vX = 20

def onStep():
    checkScheduledTasks()
    for obj in app.objects:
        obj.update()
        
def createSnake():
    rand = randomInt(0, 400)
    r1 = randomInt(0, 245)
    g1 = randomInt(0, 245)
    b1 = randomInt(0, 245)
    r2 = r1 + randomInt(0, 10)
    b2 = b1 + randomInt(0, 10)
    g2 = g1 + randomInt(0, 10)
    #schedule(f'Object({rand}, -20, 30, {r1}, {b1}, {g1}, {r2}, {b2}, {g2})', 5)
    Object(rand, -20, 30, r1, b1, g1, r2, b2, g2)
    schedule(f'Object({rand}, -20, 20, {r1}, {b1}, {g1}, {r2}, {b2}, {g2})', 10) 
    schedule(f'Object({rand}, -20, 15, {r1}, {b1}, {g1}, {r2}, {b2}, {g2})', 20)
    schedule(f'Object({rand}, -20, 10, {r1}, {b1}, {g1}, {r2}, {b2}, {g2})', 30)
        
def onMouseDrag(x, y):
    app.m = True
    app.mx = x
    app.my = y

def onMouseMove(x, y):
    app.m = False
    app.mx = x
    app.my = y
    
def onMousePress(x, y):
    app.m = True
    app.mx = x
    app.my = y
    
def onMouseRelease(x, y):
    app.m = False
    app.mx = x
    app.my = y
        
def randomInt(range1, range2):
    return rounded(random() * (range2 - range1) + range1)
    
def clamp(number, number1, number2):
    if (number < number1):
        return number1
    if (number > number2):
        return number2
    return number
    
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
    

for i in range(15):
    schedule('createSnake()', randomInt(20, 120))
    

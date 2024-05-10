import math
import time

app.stepsPerSecond = 60
# The frame rate does not matter because the notes depend on the current millisecond rather than frame count.

app.audio = None

app.started = False
app.botted = False
app.background = gradient(rgb(30, 30, 60), rgb(60, 30, 30), start='left')
app.tempo = 177
app.msPerBeat = 1
app.beatsElapsed = 0
app.noteSpeed = 0.75 # How many cmu units the notes travel per millisecond
app.startMillisecond = 0
app.endMillisecond = 0

app.score = 0
app.hits = 0.0
app.totalHits = 0
app.combo = 0

app.notes = []
app.spawnedNotes = []
app.notesSpawned = 0

app.offset = 100

app.overlay = Rect(0, 0, 400, 400, fill=gradient('black', 'white', start='top'), opacity=0)

class Note:
    def __init__(self, pos, timestamp, type, holdTime=0):
        self.pos = math.floor(pos * 4 / 512) # ranges from 0-3
        self.ms = timestamp # The exact millisecond the note should be clicked at
        self.appearTime = (timestamp - (300/app.noteSpeed)) # The exact millisecond the note should appear at
        self.holdTime = holdTime
        self.type = type
        self.spawned = False
        app.notes.append(self)
    def check(self):
        if (not self.spawned) and (getTime() > app.startMillisecond + self.appearTime):
            self.spawn()
            #print(self.appearTime)
    def spawn(self):
        self.spawned = True
        SNote(self, self.holdTime)
        
class SNote: # Spawned Notes
    def __init__(self, note, holdTime=0):
        
        app.notesSpawned += 1
        
        self.hold = (holdTime != 0)
        self.holdTime = holdTime
        self.pressed = False
        
        self.pos = note.pos
        x = 100 + (self.pos * 50)
        if (self.hold):
            self.finalHoldTime = (note.ms - self.holdTime) * -app.noteSpeed
            self.holdShape = Rect(x, -15 - self.holdTime, 50, self.finalHoldTime, fill='white', opacity=20)
            #print(self.finalHoldTime)
        self.shape = Rect(x, 0, 50, 15, fill=gradient(rgb(200, 255, 255), 'white', rgb(255, 200, 200), start='left'), border=rgb(255, 255, 255))
        
        self.spawnTime = getTime()
        self.clickTime = note.ms
        
        
        
        self.y = 0
        app.spawnedNotes.append(self)
    def update(self):
        self.y = (getTime() - self.spawnTime)*app.noteSpeed
        
        if not self.pressed or (app.botted and not self.y > 365):
            self.shape.bottom = self.y
        elif self.shape.opacity > 0:
            self.shape.opacity -= 5
        elif not self.hold:
            self.press()
        elif self.hold and self.holdTime + app.startMillisecond + 100 < getTime():
            self.press()
        
        if self.hold:
            self.holdShape.bottom = self.y - 15
                
        if not self.pressed and app.botted and abs(app.startMillisecond + self.clickTime - getTime()) < app.offset:
            if self.pos == 0:
                checkPress('a', False)
            elif self.pos == 1:
                checkPress('s', False)
            elif self.pos == 2:
                checkPress(';', False)
            elif self.pos == 3:
                checkPress("'", False)
        if (self.y - self.holdTime/app.noteSpeed >= 400) or ((self.clickTime + self.holdTime)/app.noteSpeed > getTime() + 100):
            app.group.remove(self.shape)
            if self.hold:
                app.group.remove(self.holdShape)
            app.spawnedNotes.remove(self)
            if not self.pressed:
                breakCombo()
                displayHitLabel(0, self.pos)
                app.totalHits += 1
            updateScoreLabels()
    def press(self):
        app.spawnedNotes.remove(self)
        app.group.remove(self.shape)
        if self.hold:
            app.group.remove(self.holdShape)
    
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
    
startLabel1 = Label("No map loaded. Go to https://sonofharri.github.io/rhythmgame,", 200, 180, fill='white')
startLabel2 = Label("Find a map, and paste into console!", 200, 200, fill='white')
startLabel3 = Label("Website doesn't work on Chrome for some reason, use Safari/Firefox", 200, 230, fill="pink", bold=True, size=12)
print("https://sonofharri.github.io/rhythmgame")

pauseLabel = Label("Unpause to play!", 100, 20, visible=False, fill="white", size=20)
app.song = None
app.map = None
def read(song, omap):
    app.notes = []
    pauseLabel.visible = True
    startLabel1.visible = False
    startLabel2.visible = False
    startLabel3.visible = False
    app.song = song
    app.map = omap
    schedule("read2()", 1)
    
app.readTimestamp = 0
def read2():
    app.readTimestamp = getTime()
    print("Reading map...")
    readTimingPoints()
    pauseLabel.visible = False
    map = app.map.split("[HitObjects]|")[1]
    for note in map.split("|"):
        noteData = note.split(",")
        if len(noteData) > 2:
            if len(noteData) > 5:
                Note(int(noteData[0]), int(noteData[2]), int(noteData[3]), abs(int(noteData[5].split(":")[0])) )
            else:
                Note(int(noteData[0]), int(noteData[2]), int(noteData[3]))
    startMap(app.song)
    
    
    
def readTimingPoints():
    print("Reading Timing Points...")
    point = app.map.split("[TimingPoints]|")[1].split("[HitObjects]")[0].split(",")[1]
    app.tempo = rounded(1/float(point) * 60000)
    app.msPerBeat = rounded(float(point))
    print("Tempo: " + str(app.tempo))
    
        
def loadAudio(audio):
    app.audio = Sound(audio)
    
def getTime():
    return time.time() * 1000
    
def calcEaseOut(x):
    if (x < 0.5):
        return (1 - math.sqrt(1 - ((2 * x)**2)))/2
    else:
        return (math.sqrt(1 - (-2*x + 2)**2) + 1)/2

scoreLabel = Label("", 40, 20, fill='white', size=20, bold=True, font='orbitron')
percentageLabel = Label("", 40, 40, fill='white', size=20, bold=True, font='orbitron')
comboLabel = Label("", 200, 100, fill='white', size=40, bold=True, font='orbitron', opacity=50)

scoreLabel.left = 10
percentageLabel.left = 10

fpsLabel = Label("60 fps", 20, 390, fill='white', bold=True, font='orbitron')
fpsLabel.left =10
app.lastSecond = time.time()
app.frames = 0
app.fps = 1
def onStep():
    update()
    if app.started:
        updateEffects()
    checkScheduledTasks()
    
    app.frames += 1
    if app.frames >= 59:
        app.fps = min(60, math.floor(60/(time.time() - app.lastSecond)) )
        fpsLabel.value = str(app.fps) + " fps"
        app.lastSecond = time.time()
        app.frames = 0
        

def onKeyPress(key):
    if not app.botted:
        checkPress(key, False)
    if key == "b":
        app.botted = not app.botted
def onKeyRelease(key):
    if not app.botted:
        checkPress(key, True)

lastNoteTypes = [False, False, False, False] # Whether the last note hit in each lane was a hold
app.keyLabels = []
def checkPress(key, release):
    pos = -1
    if (key == "a"):
        pos = 0
    elif key == "s":
        pos = 1
    elif key == ";":
        pos = 2
    elif key == "'":
        pos = 3
    if (pos == -1):
        return
    noteToHit = None
    noteToHitMs = 10000
    for snote in app.spawnedNotes:
        if snote.pos == pos:
            if snote.pressed:
                continue
            if snote.y < 200:
                continue
            ms = (abs(getTime() - (app.startMillisecond + snote.clickTime)) - app.offset) if not release else (abs(getTime() - (app.startMillisecond + snote.holdTime)) - app.offset)
            if (ms < 300 and ms < noteToHitMs):
                noteToHit = snote
                noteToHitMs = ms
    #print(noteToHitMs)
    if (not lastNoteTypes[pos] and release):
        return
    if (not noteToHit == None):
        noteToHit.pressed = True
    lastNoteTypes[pos] = (noteToHit != None and noteToHit.hold)
    noteToHitMs = abs(noteToHitMs)
    #print(noteToHitMs)
    app.totalHits += 1
    if not release:
        app.combo += 1
        
    if (noteToHitMs < 15):
        app.hits += 1
        app.score += 300
        displayHitLabel(300, pos)
    elif (noteToHitMs < 40):
        app.hits += 0.75
        app.score += 200
        displayHitLabel(200, pos)
    elif (noteToHitMs < 75):
        app.hits += 0.5
        app.score += 100
        displayHitLabel(100, pos)
    elif (noteToHitMs < 200):
        app.hits += 0.25
        app.score += 50
        displayHitLabel(50, pos)
    elif not release:
        displayHitLabel(0, pos)
        breakCombo()
    updateScoreLabels()
    
def updateScoreLabels():
    percentageLabel.value = str(pythonRound(app.hits/app.totalHits * 100, 1)) + "%"
    scoreLabel.value = str(app.score)
    comboLabel.value = str(app.combo) + "X"
    scoreLabel.left = 10
    percentageLabel.left = 10
    
def breakCombo():
    app.combo = 0

def displayHitLabel(score, pos):
    if score != 0:
        comboLabel.opacity = 80
    if score == 300:
        app.keyLabels.append(Label("Perfect!", 125 + pos*50, 250, size=20, fill=rgb(170, 255, 255), font='montserrat'))
        StarEffect()
        StarEffect()
    if score == 200:
        app.keyLabels.append(Label("Great", 125 + pos*50, 250, size=20, fill=rgb(0, 255, 80), font='montserrat'))
        StarEffect()
    if score == 100:
        app.keyLabels.append(Label("Good", 125 + pos*50, 250, size=20, fill=rgb(180, 255, 70), font='montserrat'))
    if score == 50:
        app.keyLabels.append(Label("OK", 125 + pos*50, 250, size=20, fill=rgb(255, 255, 0), font='montserrat'))
    if score == 0:
        app.keyLabels.append(Label("X", 125 + pos*50, 250, size=20, fill=rgb(255, 0, 0), font='montserrat'))
    

mapElements = []
def startMap(audio):
    print("Finished reading. Loading audio...")
    loadAudio(audio)
    #app.maxHits = len(app.notes)
    schedule("""app.startMillisecond = getTime()
app.audio.play(restart=True)""", 60)
    mapElements.append(Rect(100, 0, 200, 400, fill='black', opacity=50))
    mapElements.append(Rect(100, 350, 200, 15, fill=None, border='white', opacity=50))
    mapElements.append(Label(" A            S            ;            ' ", 200, 375, fill='white'))
    print(f"Finished reading map in {getTime() - app.readTimestamp} ms.")
    app.started = True
    
def debug():
    for shape in app.group.children:
        print(f"{shape.centerX}, {shape.centerY}")
    

app.ended = False
def update():
    if (app.startMillisecond != 0):
        for note in app.notes:
            note.check()
        for spawnedNote in app.spawnedNotes:
            spawnedNote.update()
            
            
        toRemove = []
        for label in app.keyLabels:
            if (label.opacity > 30):
                label.opacity -= label.opacity/20
                label.centerY -= label.opacity/20
            else:
                app.group.remove(label)
                toRemove.append(label)
        for label in toRemove:
            app.keyLabels.remove(label)
    if app.started and len(app.notes) == app.notesSpawned and len(app.spawnedNotes) == 0 and app.endMillisecond == 0:
        app.endMillisecond = getTime() + 3000
    if app.endMillisecond != 0 and app.endMillisecond < getTime() and not app.ended:
        app.ended = True
        for element in mapElements:
            app.group.remove(element)
            comboLabel.visible = False
            Label("Map ended. Restart to play again!", 200, 200, size=20, fill='white', font='orbitron')
    
        

def updateEffects():
    if (getTime() % app.msPerBeat < 20):
        app.beatsElapsed += 1
        app.overlay.opacity = 10
    if (app.overlay.opacity > 0.2):
        app.overlay.opacity -= 0.20
    
    for star in app.starEffects:
        star.update()
        
    if comboLabel.opacity > 50:
        comboLabel.opacity -= 0.50


app.starEffects = []
class StarEffect:
    def __init__(self):
        negative = random() >= 0.5
        self.x = 400 if negative else 0
        self.y = 400
        self.vX = (random() * 5) * -1 if negative else 1
        self.vY = (random() * 7)
        self.shape = Star(self.x, self.y, 10, 5, fill='white', opacity=20)
        app.starEffects.append(self)
    def update(self):
        
        self.vX *= 0.99
        self.vY -= 9.8/app.fps
        
        self.x += self.vX
        self.y -= self.vY
        
        self.shape.centerX = self.x
        self.shape.centerY = self.y
        self.shape.rotateAngle += self.vX
        
        if self.y > 420 or self.x < -10 or self.x > 410:
            app.group.remove(self.shape)
            app.starEffects.remove(self)




















    




































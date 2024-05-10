"""

      Hi! Sorry for submitting a rat.
      I wanted to do something cooler,
      but I didn't have time.


"""

import math 
import time

app.stepsPerSecond = 30
app.setMaxShapeCount(10000) # 10000 shapes will run slowly anyway, but at least it won't just give up and die.

# basic config
app.fov = 60.0

# end of config, start of constants/positions
app.elapsedTicks = 0
app.a = 1 #(w/h, which is always 400/400)
app.f = 1/math.tan(app.fov/2)
app.halfPi = math.pi/2
app.fNear = 0.01
app.fFar = 0.02 # Decreasing this number helps with performance, but also decreases render distance.

app.objects = []
app.polygons = []

# Stands for vector. Represents a point in 3d space.
class V:
    def __init__(self, x, y, z, w=1):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w) # Apparently, we need a fourth term for matrix vector multiplication.
    def __add__(self, vec):
        if type(vec) is V:
            return V(self.x + vec.x, self.y + vec.y, self.z + vec.z)
        elif type(vec) is float or type(vec) is int:
            return V(self.x + vec, self.y + vec, self.z + vec)
        else:
            raise TypeError(f"Tried to add unsupported type '{type(vec)}' to vector.")
    def __sub__(self, vec):
        if type(vec) is V:
            return V(self.x - vec.x, self.y - vec.y, self.z - vec.z)
        elif type(vec) is float or type(vec) is int:
            return V(self.x - vec, self.y - vec, self.z - vec)
        else:
            raise TypeError(f"Tried to subtract unsupported type '{type(vec)}' to vector.")
    def __mul__(self, vec):
        if type(vec) is V:
            return V(self.x * vec.x, self.y * vec.y, self.z * vec.z)
        elif type(vec) is float or type(vec) is int:
            return V(self.x * vec, self.y * vec, self.z * vec)
        else:
            raise TypeError(f"Tried to multiply unsupported type '{type(vec)}' to vector.")
    def __truediv__(self, num):
        if type(vec) is V:
            return V(self.x / vec.x, self.y / vec.y, self.z / vec.z)
        elif type(vec) is float or type(vec) is int:
            return V(self.x / vec, self.y / vec, self.z / vec)
        else:
            raise TypeError(f"Tried to divide unsupported type '{type(vec)}' to vector.")
    def cross(self, vec):
        return V(self.y * vec.z - self.z * vec.y,
                 self.z * vec.x - self.x * vec.z,
                 self.x * vec.y - self.y * vec.x)
    def dot(self, vec):
        return (self.x*vec.x + self.y*vec.y + self.z*vec.z)
    def clone(self):
        return V(self.x, self.y, self.z)
    def normalize(self):
        l = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if (l != 0):
            self.x /= l
            self.y /= l
            self.z /= l
        
        
def sin(x):
    # t = x * 0.15915
    # t = t - int(t)
    
    # return 20.785 * t * (t - 0.5) * (t - 1.0)
    return math.sin(x)
def cos(x):
    # return sin(x + 1.571)
    return math.cos(x)
app.degRadConversionConstant = math.pi/180
def toDegrees(x):
    return app.degRadConversionConstant*x
       
# Represents a 4x4 matrix.
class M4:
    def __init__(self, points=None):
        self.p = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] if points == None else points
    def __str__(self):
        return f"{self.p[1]}, {self.p[2]}, {self.p[3]}\n{self.p[4]}, {self.p[5]}, {self.p[6]}, {self.p[7]}\n{self.p[8]},{self.p[9]}, {self.p[10]}, {self.p[11]}\n{self.p[12]},{self.p[13]}, {self.p[14]}, {self.p[15]}"
    def s(self, x, y, value): # Stands for set.
        self.p[y * 4 + x] = value
    def g(self, x, y): # Stands for get.
        return self.p[y * 4 + x]
    def clone(self):
        return M4([self.p[0], self.p[1], self.p[2], self.p[3], self.p[4], self.p[5], self.p[6], self.p[7], self.p[8], self.p[9], self.p[10], self.p[11], self.p[12], self.p[13], self.p[14], self.p[15]])
    def __add__(self, v):
        if type(v) is M4:
            m = self.clone()
            for i in range(len(v.p)):
                m.p[i] += v.p[i]
            return m
    def __mul__(self, v):
        if type(v) is V:
            r = V(
                v.x * self.g(0,0) + v.y * self.g(1,0)  + v.z * self.g(2,0) + v.w * self.g(3,0),
                v.x * self.g(0,1) + v.y * self.g(1,1)  + v.z * self.g(2,1) + v.w * self.g(3,1),
                v.x * self.g(0,2) + v.y * self.g(1,2)  + v.z * self.g(2,2) + v.w * self.g(3,2)
            )
            w = v.x * self.g(0,3) + v.y * self.g(1,3)  + v.z * self.g(2,3) + self.g(3,3)
            if (w != 0):
                r.x/=w
                r.y/=w
                r.z/=w
            return r
        if type(v) is M4:
            m = M4()
            for c in range(4):
                for r in range(4):
                    m.s(r,c,self.g(r,0)*v.g(0,c) + self.g(r,1)*v.g(1,c) + self.g(r,1)*v.g(2,c) + self.g(r,3)*v.g(3,c))
            return m
        
def createProjectionMatrix():
    ffr = (1 / math.tan(app.fov * 0.5 / 180 * math.pi)) # Stands for fFovRad in the video
    r = M4()
    r.s(0, 0, app.a * ffr)
    r.s(1, 1, ffr)
    r.s(2, 2, app.fFar / (app.fFar - app.fNear))
    r.s(3, 2, (-app.fFar * app.fNear) / (app.fFar - app.fNear))
    r.s(2, 3, 1)
    r.s(3, 3, 0)
    return r
        
def createIdentityMatrixPoints():
    return [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
    
def createTranslationMatrix(x, y, z):
    m = M4()
    m.s(0,0,1)
    m.s(1,1,1)
    m.s(2,2,1)
    m.s(3,3,1)
    m.s(3,0,x)
    m.s(3,1,y)
    m.s(3,2,z)
    return m
    
# ft = fTheta (radians around axis)
def createRotationMatrixX(ft):
    r = M4()
    r.s(0, 0, 1)
    r.s(1, 1, cos(ft * 0.5))
    r.s(1, 2, sin(ft * 0.5))
    r.s(2, 1, -sin(ft * 0.5))
    r.s(2, 2, cos(ft * 0.5))
    r.s(3, 3, 1)
    return r
    
def createRotationMatrixY(ft):
    r = M4()
    r.s(0,0,cos(ft))
    r.s(0,2,sin(ft))
    r.s(2,0,-sin(ft))
    r.s(1,1,1)
    r.s(2,2,cos(ft))
    r.s(3,3,1)
    return r
    
def createRotationMatrixZ(ft):
    r = M4()
    r.s(0, 0, cos(ft))
    r.s(0, 1, sin(ft))
    r.s(1, 0, -sin(ft))
    r.s(1, 1, cos(ft))
    r.s(2, 2, 1)
    r.s(3, 3, 1)
    return r

# Stands for triangle. Represents a triangle with three points in 3d space.
class T:
    def __init__(self, v1, v2, v3):
        self.p = [v1, v2, v3]
    def getProjected(self):
        # [x, y, z] = [(w/h = 1) fx/z, fy/z, z((zfar/zfar-znear) - (zfar*znear)/(zfar-znear)]
        # q = zfar/(zfar-znear)
        # SIMPLIFIED: [x, y, z] = [afx/z, fy/z, zq - znearq]
        return T2(v1, v2, v3)
    def clone(self):
        return T(
            V(self.p[0].x, self.p[0].y, self.p[0].z),
            V(self.p[1].x, self.p[1].y, self.p[1].z),
            V(self.p[2].x, self.p[2].y, self.p[2].z)
        )
    def midpointZ(self):
        # return (self.p[0].z + self.p[1].z + self.p[2].z)/3
        return min( (self.p[0].z, self.p[1].z, self.p[2].z) )
    def draw(self, color):
        app.polygons.append(Polygon(
                self.p[0].x, self.p[0].y,
                self.p[1].x, self.p[1].y,
                self.p[2].x, self.p[2].y, fill=color, border=color))
        pass
    # Triangle operator overloaders
    # Make things faster and uses fewer lines
    def __add__(self, val):
        self.p[0] += val
        self.p[1] += val
        self.p[2] += val
        return self
    def __sub__(self, val):
        self.p[0] -= val
        self.p[1] -= val
        self.p[2] -= val
        return self
    def __mul__(self, val):
        self.p[0] *= val
        self.p[1] *= val
        self.p[2] *= val
        return self
    def multiplyMatrix(self, mat):
        return T(   mat * self.p[0],
                    mat * self.p[1],
                    mat * self.p[2] )
                
# Structure for a triangle with extra fields (normal and color)
class StoredTriangle():
    def __init__(self, tri, normal, color):
        self.tri = tri
        self.normal = normal
        self.color = color
    
class Mesh:
    def __init__(self, tris):
        self.tris = tris
        app.objects.append(self)
        
class Camera:
    def __init__(self, pos):
        self.pos = pos
        pass
        
app.camera = Camera(V(0, 0, 0))
        
        
app.background = gradient(rgb(50, 50, 50), rgb(10, 10, 10))
    
def readObj(obj):
    obj = obj.replace("s off", "") # Why does this exist??
    readFaces = obj.split("f ")
    readVerts = readFaces[0].split("v ")
    readVerts.pop(0) # This gets rid of the beginning comment
    readFaces.pop(0) # This gets rid of the vertices
    
    verts = []
    tris = []
    
    for vertex in readVerts:
        v = vertex.split(" ")
        verts.append(V( float(v[0]), float(v[1]), float(v[2]) ))
    for face in readFaces:
        f = face.split(" ")
        tris.append(T(
            verts[int(f[0]) - 1],
            verts[int(f[1]) - 1],
            verts[int(f[2]) - 1] ));
            
    Mesh(tris)
    

    

# def init():
#     app.f = 1/tan(app.fov/2)

app.enablePerformanceTools = True
app.lastFrame = time.perf_counter()
app.fpsLabel = Label(f"{app.stepsPerSecond} fps", 21, 375, fill='white')
app.polygonCount = Label(f"0 polygons", 21, 390, fill='white')
def onStep():
    
    app.elapsedTicks += 1
    render()
    
    if app.enablePerformanceTools:
        app.fpsLabel.value = f"{(int) (app.stepsPerSecond//(time.perf_counter() - app.lastFrame)//app.stepsPerSecond) } fps"
        app.fpsLabel.left = 5
        app.lastFrame = time.perf_counter()
        
        app.polygonCount.value = f"{len(app.polygons)} triangles"
        app.polygonCount.left = 5
    

    
app.mat = createProjectionMatrix()
# Projection Matrix

def onKeyHold(keys):
    if ('a' in keys):
        app.camera.pos.x -= 0.5
    if ('d' in keys):
        app.camera.pos.x += 0.5
        
    if ('w' in keys):
        app.camera.pos.z += 0.5
    if ('s' in keys):
        app.camera.pos.z -= 0.5
    # print(f"x: {app.camera.pos.x}, y: {app.camera.pos.y}, z: {app.camera.pos.z}")
        
def hsvToRgb(h, s, v):
    h = h % 360
    hi = math.floor(h/60.0) % 6
    f = h/60.0 - math.floor(h/60.0)
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    
    r = 0
    g = 0
    b = 0
    if hi==0: r=v;g=t;b=p
    elif hi==1:r=q;g=v;b=p;
    elif hi==2:r=p;g=v;b=t;
    elif hi==3:r=p;g=q;b=v;
    elif hi==4:r=t;g=p;b=v;
    elif hi==5:r=v;g=p;b=q;
    else:r=v;b=v;g=v;
    return (r, g, b)

def render():
    
    #print(len(app.group))
    for c in app.polygons:
        app.group.remove(c)
    app.polygons = []
    
    # Rotation Matrix
    ft = 0.05 * app.elapsedTicks # stands for fTheta
    rotation = V(ft/10 + 4.5, ft + 0.8, 0)
    if rotation.x != 0:
        rotX = createRotationMatrixX(rotation.x)
    if rotation.y != 0:
        rotY = createRotationMatrixY(rotation.y)
    if rotation.z != 0:
        rotZ = createRotationMatrixZ(rotation.z)
    
    
    # Illumination
    hsvColor = hsvToRgb(app.elapsedTicks % 255, 0.6, 1)
            
    lightDirection = V(0, 0, -1)
    lightDirection.normalize()

    storedTriangles = []
    for obj in app.objects:
        for t in obj.tris:
            
            # Transformation
            tt = t.clone()
            if rotation.x != 0:
                tt = tt.multiplyMatrix(rotX)
            if rotation.y != 0:
                tt = tt.multiplyMatrix(rotY)
            if rotation.z != 0:
                tt = tt.multiplyMatrix(rotZ)
            tt += V(0, 0, 10)
            tt -= app.camera.pos
            
            # Normals
            # line1 and line2 from the video got simplified into this.
            normal = (tt.p[1] - tt.p[0]).cross(tt.p[2] - tt.p[0])
            normal.normalize()
            if (normal.dot(tt.p[0] - app.camera.pos) > 0):
                continue
            
            # Illumination
            
            dp = normal.dot(lightDirection)
            
            c = (dp+1)/2
            # print(f"{c}, {hsvColor[0]}")
            color = rgb( 
                math.floor(c * hsvColor[0] * 255),
                math.floor(c * hsvColor[1] * 255),
                math.floor(c * hsvColor[2] * 255) 
            )
            
            # Projection
            p = tt.p
            tp = tt.multiplyMatrix(app.mat)
            
            # Offset into a visible, normalised space
            tp += 1
            tp *= 200
            
            storedTriangles.append(StoredTriangle(tp, normal, color))
            # tp.draw(color)
            
    storedTriangles.sort(key=lambda stri: stri.tri.midpointZ(), reverse=True)
    for st in storedTriangles:
        st.tri.draw(st.color)
    
    
    
    
    
    
    

    
song = Sound("cmu://765177/29548231/freebird_lq_trimmed.ogg")
song.play(loop=True)

# Ship
# readObj("# Blender v2.79 (sub 0) OBJ File: '' # www.blender.org v 1.000000 -1.000000 -1.000000 v 1.000000 1.000000 -1.000000 v 1.000000 -1.000000 1.000000 v 1.000000 1.000000 1.000000 v -1.000000 -1.000000 -1.000000 v -1.000000 1.000000 -1.000000 v -1.000000 -1.000000 1.000000 v -1.000000 1.000000 1.000000 v -0.720000 0.120000 -1.400000 v 0.300000 0.000000 5.000000 v -0.600000 -0.600000 -1.400000 v -0.300000 0.000000 5.000000 v -1.200000 0.200000 1.000000 v -0.600000 0.600000 -1.400000 v -1.200000 -0.200000 -1.000000 v -1.200000 0.200000 -1.000000 v 1.200000 -0.200000 1.000000 v 1.200000 -0.200000 -1.000000 v 1.200000 0.200000 -1.000000 v 1.200000 0.200000 1.000000 v -1.200000 -0.200000 1.000000 v 0.600000 0.600000 -1.400000 v 0.600000 -0.600000 -1.400000 v -4.200000 0.060000 1.000000 v -4.200000 -0.060000 1.000000 v -4.200000 -0.060000 -1.000000 v -4.200000 0.060000 -1.000000 v 4.200000 -0.060000 1.000000 v 4.200000 -0.060000 -1.000000 v 4.200000 0.060000 -1.000000 v 4.200000 0.060000 1.000000 v 4.200000 -0.180000 1.000000 v 4.200000 -0.180000 -1.000000 v 4.200000 0.180000 -1.000000 v 4.200000 0.180000 1.000000 v 4.500000 -0.180000 1.000000 v 4.500000 -0.180000 -1.000000 v 4.500000 0.180000 -1.000000 v 4.500000 0.180000 1.000000 v -4.200000 0.180000 1.000000 v -4.200000 -0.180000 1.000000 v -4.200000 -0.180000 -1.000000 v -4.200000 0.180000 -1.000000 v -4.500000 0.180000 1.000000 v -4.500000 -0.180000 1.000000 v -4.500000 -0.180000 -1.000000 v -4.500000 0.180000 -1.000000 v 4.350000 -0.180000 3.000000 v 4.350000 0.180000 3.000000 v -4.350000 0.180000 3.000000 v -4.350000 -0.180000 3.000000 v 0.000000 -0.700000 3.000000 v -0.720000 -0.120000 -1.400000 v 0.720000 -0.120000 -1.400000 v 0.720000 0.120000 -1.400000 s off f 21 52 12 f 6 13 8 f 5 23 1 f 7 1 3 f 4 6 8 f 4 12 10 f 17 20 10 f 20 4 10 f 17 52 3 f 7 3 52 f 16 14 9 f 7 15 5 f 20 30 19 f 18 23 54 f 4 19 2 f 1 17 3 f 13 25 21 f 13 21 12 f 12 52 10 f 8 13 12 f 27 42 43 f 15 27 16 f 21 26 15 f 16 24 13 f 31 34 30 f 18 28 17 f 17 31 20 f 19 29 18 f 32 49 35 f 29 32 28 f 31 32 35 f 29 34 33 f 38 36 37 f 34 37 33 f 35 38 34 f 33 36 32 f 43 44 40 f 25 42 26 f 27 40 24 f 25 40 41 f 44 46 45 f 40 44 50 f 42 47 43 f 41 46 42 f 44 47 46 f 32 36 48 f 39 35 49 f 39 48 36 f 45 51 50 f 40 51 41 f 45 41 51 f 45 50 44 f 18 29 28 f 17 28 31 f 4 2 6 f 18 55 19 f 15 11 5 f 19 22 2 f 2 14 6 f 16 53 15 f 53 9 54 f 19 30 29 f 15 26 27 f 16 27 24 f 13 24 25 f 21 25 26 f 7 21 15 f 7 5 1 f 21 7 52 f 1 18 17 f 17 10 52 f 4 20 19 f 20 31 30 f 4 8 12 f 43 47 44 f 6 16 13 f 40 50 51 f 41 45 46 f 42 46 47 f 2 22 14 f 19 55 22 f 18 54 55 f 18 1 23 f 5 11 23 f 15 53 11 f 16 9 53 f 16 6 14 f 9 14 22 f 22 55 9 f 55 54 9 f 54 23 11 f 11 53 54 f 34 38 37 f 38 39 36 f 39 49 48 f 35 39 38 f 33 37 36 f 25 41 42 f 27 43 40 f 31 35 34 f 29 33 32 f 32 48 49 f 27 26 42 f 31 28 32 f 29 30 34 f 25 24 40")

# Rat (v2)
readObj("# Blender 4.0.2 # www.blender.org o rat v 0.234375 1.734318 -6.092284 v 0.468750 1.734319 -7.597814 v 0.703125 1.734318 -6.092284 v 0.000000 1.734318 -4.214801 v 0.937500 1.734318 -4.214801 v 0.000000 1.734318 -2.812500 v 0.937500 1.734318 -2.812500 v 0.937500 0.328068 -2.812500 v 0.000000 0.328068 -2.812500 v -0.937500 0.328068 -0.937500 v -0.937500 2.671818 -0.937500 v 1.875000 2.671818 -0.937500 v 1.875000 0.328068 -0.937500 v 1.406250 0.328068 3.281250 v -0.468750 0.328068 3.281250 v -0.468750 1.734318 3.281250 v 1.406250 1.734318 3.281250 v 0.468750 0.796818 5.156250 v 0.937500 1.584318 -4.214801 v 0.703125 1.584319 -6.092284 v 0.468750 1.584319 -7.597814 v 0.234375 1.584319 -6.092284 v 0.000000 1.584318 -4.214801 v 0.000000 1.584318 -2.812500 v 0.937500 1.584318 -2.812500 v 1.263187 2.396531 3.281250 v 0.643301 1.735583 3.296633 v 1.276814 1.780728 2.918109 v 0.337326 1.734318 3.281250 v -0.109037 1.774127 2.910088 v -0.314257 2.342216 3.228561 s 0 f 1 3 2 f 6 5 4 f 6 7 5 f 6 7 8 f 6 8 9 f 10 6 9 f 11 6 10 f 11 7 6 f 12 7 11 f 12 8 7 f 13 8 12 f 13 9 8 f 13 10 9 f 14 10 13 f 15 10 14 f 15 11 10 f 16 11 15 f 16 12 11 f 17 12 16 f 17 13 12 f 17 14 13 f 18 14 17 f 18 15 14 f 18 16 15 f 18 17 16 f 2 3 21 f 21 3 20 f 1 2 22 f 22 2 21 f 25 24 23 19 f 6 4 24 f 24 4 23 f 7 6 25 f 25 6 24 f 20 3 5 19 f 22 23 4 1 f 3 1 4 5 f 22 20 19 23 f 20 22 21 f 8 9 24 25 f 5 7 25 19 f 27 17 26 f 17 28 26 f 26 28 27 f 29 31 16 f 16 31 30 f 29 30 31")


for i in range(10):
    for j in range(10):
        Circle(i * 40 + 20, j * 40 + 20, 4, fill=rgb(100, 100, 100), opacity=20)



Label("3D Render of a Rat", 200, 20, fill='white', bold=True)
Label("400+ lines of code", 200, 35, fill='white')















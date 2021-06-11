import pygame
import math

CIRCLE=0
RECTANGLE = 1
POLYGON = 2
TAU = 2*math.pi
def rotate(a,r): 
    b = [math.cos(r/360 * TAU) * a[0] - math.sin(r/360 * TAU) *a[1] , math.sin(r/360 * TAU) * a[0] + math.cos(r/360 * TAU) *a[1] ] 
    return b


class Shape(object):
    def __init__(self,surface,shapetype,color):
        self.surface = surface
        self.type = shapetype
        self.color = color

    def collidepoint(self,point):
        pass

class Circle(Shape):
    def __init__(self,surface,color,center,radius,width=1):
        Shape.__init__(self,surface,CIRCLE,color)
        self.center = center
        self.radius = radius

    def draw(self):
        return pygame.draw.circle(self.surface,self.color,self.center,self.radius)

    def collidepoint(self,point):
        dist = (self.center[0]-point[0])**2+(self.center[1]-point[1])**2
        if dist < self.radius**2:
            return True
        else:
            return False

class Rectangle(Shape):
    def __init__(self,surface,color,start,end,width=1):
        Shape.__init__(self,surface,RECTANGLE,color)
        self.start = start
        self.end = end

    def draw(self):
        coords = (self.start[0],self.start[1],self.end[0]-self.start[0],self.end[1]-self.start[1])
        return pygame.draw.rect(self.surface,self.color,coords)

    def collidepoint(self,point):
        if self.start[0]<=point[0] and self.end[0]>=point[0] and self.start[1]<=point[1] and self.end[1]>=point[1]:
            return True
        else:
            return False

class nPolygon(Shape):
    def __init__(self,surface,color,N,center,radius,rotation,width=1):
        Shape.__init__(self,surface,POLYGON,color)
        self.center = center
        self.radius = radius
        self.N = N
        self.points = []
        for i in range(N):
            x = int(math.sin(TAU/N*i+(rotation+180)/360*TAU) * radius + center[0])
            y = int(math.cos(TAU/N*i+(rotation+180)/360*TAU) * radius + center[1])
            self.points.append((x,y))

    def draw(self):
        return pygame.draw.polygon(self.surface,self.color,self.points)

    def collidepoint(self,point):
        points = self.points + self.points[0:1]
        for i in range(self.N):
            z = points[i]
            nv = [ points[i+1][0] - z[0], points[i+1][1] -z[1] ]
            p = [ point[0] - z[0] , point[1] - z[1] ]
            angnv = math.atan2(nv[1],nv[0])*360/TAU
            np = rotate(p,-angnv+90)
            if np[0]<0:
                return False
        return True


class Draw(object):
    def __init__(self,surface):
        self.surface = surface

    def circle(self,color,center,radius):
        self.shape = Circle(self.surface,color,center,radius)
        self.shape.draw()
        return self.shape

    def polygon(self,color,N,center,radius,rotation=0):
        self.shape = nPolygon(self.surface,color,N,center,radius,rotation)
        self.shape.draw()
        return self.shape

    def rect(self,color,start=None,center=None,size=None,end=None):
        if start and end:
            pass
        elif start and size:
            end = (start[0]+size[0],start[1]+size[1])
        elif center and size:
            start = (center[0]-size[0]/2,center[1]-size[1]/2)
            end = (start[0]+size[0],start[1]+size[1])
        else:
            raise ValueError('Missing values')
        self.shape = Rectangle(self.surface,color,start,end)
        self.shape.draw()
        return self.shape

    def collidepoint(self,point):
        return self.shape.collidepoint(point)

import pygame, math


class Player():
    def __init__(self,x,y,angle,velocity,ptype):
        self.hp = 100
        self.x = x
        self.y = y
        self.angle = angle
        self.velocity = velocity
        self.ptype = ptype
        if ptype == 1:
            self.max_speed = 30*0.04
        else:
            self.max_speed = 32*0.04

    def turn(self,dir,mag):
        self.angle += mag * dir
        self.angle = self.angle % 360

    def change_velocity(self,dir,mag):
        if dir == 1:
            if self.velocity + 0.05 <= self.max_speed:
                self.velocity += dir * mag
        else:
            if self.velocity - 0.05 >= self.max_speed*dir:
                self.velocity += dir*mag

    def change_coords(self):
        self.x += self.velocity * math.cos(math.radians(self.angle))
        self.y -= self.velocity * math.sin(math.radians(self.angle))

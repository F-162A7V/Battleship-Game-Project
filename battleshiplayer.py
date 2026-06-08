__author__ = "F-162A7V"


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
            self.max_speed = 30*0.02
        else:
            self.max_speed = 32*0.02

    def turn(self,dir,mag):
        if self.ptype == 1:
            mag2 = self.velocity/(30*0.02) + 0.4
        else:
            mag2 = self.velocity/(32 * 0.02) + 0.4
        if mag2 > 1:
            mag2 = 1
        self.angle += mag * dir * mag2
        self.angle = self.angle % 360

    def change_velocity(self,dir,mag):
        if dir == 1:
            if self.velocity + 0.025 <= self.max_speed:
                self.velocity += dir * mag
        else:
            if self.velocity - 0.025 >= self.max_speed*dir:
                self.velocity += dir*mag

    def set_velocity(self,num):
        self.velocity = num

    def set_coords(self,x,y):
        self.x = x
        self.y = y

    def change_coords(self):
        self.x += self.velocity * math.cos(math.radians(self.angle))
        self.y -= self.velocity * math.sin(math.radians(self.angle))

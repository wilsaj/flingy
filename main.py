#!/usr/bin/env python
from functools import partial
import itertools
import math
from random import random

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import ListProperty, NumericProperty
from kivy.vector import Vector
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button


kivy.require('1.0.9')


class AimLine(Widget):
    start_pt = ListProperty([0, 0])
    end_pt = ListProperty([0, 0])

    def __init__(self, start_pt, **kwargs):
        super(AimLine, self).__init__(**kwargs)
        self.start_pt = start_pt
        self.end_pt = start_pt


class BlackHole(Widget):
    d = NumericProperty(50.)
    mass = NumericProperty(50.)

    def __init__(self, **kwargs):
        super(BlackHole, self).__init__(**kwargs)


class Shot(Widget):
    d = NumericProperty(10.)
    mass = NumericProperty(1.)
    motion_v = ListProperty([0, 0])

    def __init__(self, motion_v, **kwargs):
        super(Shot, self).__init__(**kwargs)
        self.motion_v = motion_v

    def move(self):
        self.x += self.motion_v[0]
        self.y += self.motion_v[1]

    def gravitate_towards(self, body):
        m_v = Vector(self.motion_v)
        g_v = Vector(body.pos) - Vector(self.pos)
        self.motion_v = m_v + (g_v * 1. / g_v.length2()) * body.mass


class Stars(Widget):
    points = ListProperty([(0,0), (0, 0), (0, 0)])

    def __init__(self, number_of_stars, **kwargs):
        super(Stars, self).__init__(**kwargs)
        Clock.schedule_once(partial(self.add_stars, number_of_stars), -1)

    def add_stars(self, number_of_stars, dt):
        width = self.parent.width
        height = self.parent.height
        self.points[0] = list(itertools.chain(*[(random() * width, random() * height)
                                                for i in xrange(number_of_stars)]))
        self.points[1] = list(itertools.chain(*[(random() * width, random() * height)
                                                for i in xrange(number_of_stars/3)]))
        self.points[2] = list(itertools.chain(*[(random() * width, random() * height)
                                                for i in xrange(number_of_stars/50)]))

class FlingBoard(FloatLayout):
    """
    Main application widget, takes all the touches.
    """
    def __init__(self, *args, **kwargs):
        super(FlingBoard, self).__init__()
        self.aim_line = None
        self.black_hole = None
        self.shots = []
        Window.clearcolor = (0.1, 0.1, 0.1, 1.)
        Clock.schedule_once(self.add_stars, -1)
        Clock.schedule_interval(self.tick, 1 / 60.)

    def add_stars(self, dt):
        self.stars = Stars(2000)
        self.add_widget(self.stars)

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            if self.black_hole:
                self.remove_widget(self.black_hole)
            self.black_hole = BlackHole(pos=touch.pos)
            self.add_widget(self.black_hole)
        self.aim_line = AimLine(touch.pos)
        self.add_widget(self.aim_line)
        return True

    def on_touch_move(self, touch):
        try:
            self.aim_line.end_pt = touch.pos
            return True
        except (KeyError), e:
            pass

    def on_touch_up(self, touch):
        start_v = Vector(self.aim_line.start_pt)
        end_v = Vector(self.aim_line.end_pt)

        motion_v = start_v - end_v
        l = motion_v.length()
        if l == 0.:
            return
        motion_v /= math.sqrt(l)

        shot = Shot(motion_v=motion_v, pos=(touch.x, touch.y))
        self.add_widget(shot)
        self.remove_widget(self.aim_line)
        self.shots.append(shot)

    def tick(self, dt):
        for shot1, shot2 in itertools.combinations(self.shots, 2):
            if circles_collide(shot1, shot2):
                shots_collide(shot1, shot2)

        for shot in self.shots:
            if self.black_hole:
                shot.gravitate_towards(self.black_hole)
                if circles_collide(shot, self.black_hole):
                    self.remove_widget(shot)
                    self.shots.remove(shot)
            shot.move()


class FlingyApp(App):
    def build(self):
        return FlingBoard()


def circles_collide(widget_1, widget_2):
    widget_distance = Vector(widget_1.pos).distance(Vector(widget_2.pos))
    radial_distance = (widget_1.d + widget_2.d) / 2.
    return widget_distance < radial_distance


def shots_collide(shot1, shot2):
    p1_v = Vector(shot1.pos)
    p2_v = Vector(shot2.pos)
    shot1.motion_v = (p1_v - p2_v).normalize() / Vector(shot1.motion_v).length()
    shot2.motion_v = (p2_v - p1_v).normalize() / Vector(shot2.motion_v).length()


if __name__ == '__main__':
    FlingyApp().run()

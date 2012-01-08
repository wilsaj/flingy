#!/usr/bin/env python
import math

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import ListProperty, NumericProperty
from kivy.vector import Vector
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button


kivy.require('1.0.9') # replace with your current kivy version !


class AimLine(Widget):
    start_pt = ListProperty([0, 0])
    end_pt = ListProperty([0, 0])

    def __init__(self, start_pt, **kwargs):
        super(AimLine, self).__init__(**kwargs)
        self.start_pt = start_pt
        self.end_pt = start_pt


class Shot(Widget):
    d = NumericProperty(10.)
    motion_x = NumericProperty(0.)
    motion_y = NumericProperty(0.)

    def __init__(self, motion_x, motion_y, **kwargs):
        super(Shot, self).__init__(**kwargs)
        self.motion_x = motion_x
        self.motion_y = motion_y
        Clock.schedule_interval(self.move, 1 / 60.)

    def move(self, dt):
        self.x += self.motion_x
        self.y += self.motion_y


class FlingBoard(FloatLayout):
    """
    Main application widget, takes all the touches.
    """
    def __init__(self, *args, **kwargs):
        super(FlingBoard, self).__init__()
        self.aim_line = None
        self.black_hole = None
        self.shots = []

    def on_touch_down(self, touch):
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

        shot = Shot(motion_x=motion_v.x, motion_y=motion_v.y, pos=(touch.x, touch.y))
        self.add_widget(shot)
        self.remove_widget(self.aim_line)
        self.shots.append(shot)


class FlingyApp(App):
    def build(self):
        return FlingBoard()

if __name__ == '__main__':
    FlingyApp().run()

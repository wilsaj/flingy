#!/usr/bin/env python
import itertools
import math

import kivy
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.vector import Vector
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

import levels
from widgets import AimLine, BlackHole, GoalPoint, MainMenu, Rocket, Shot, Stars

kivy.require('1.0.9')


class FlingBoard(Widget):
    """
    Main application widget, takes all the touches and turns them into
    fun.
    """
    def __init__(self, *args, **kwargs):
        super(FlingBoard, self).__init__()
        Window.clearcolor = (0.1, 0.1, 0.1, 1.)
        Clock.schedule_once(self.add_stars, -1)
        Clock.schedule_interval(self.tick, 1 / 60.)
        self._keyboard = Window.request_keyboard(
            None, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.aim_line = None
        self.black_holes = []
        self.current_level = 0
        self.level_label = None
        self.goal_points = []
        self.rockets = []
        self.shots = []
        self.walls = []

        # schedule rather than call directly init, so that width and
        # height are finished initializing
        Clock.schedule_once(self.display_main_menu)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        try:
            level_index = int(text)
            print "loading level %s..." % (level_index)
            self.load_level(level_index)
            return True
        except ValueError:
            pass

    def add_black_hole(self, black_hole):
        self.black_holes.append(black_hole)
        self.add_widget(black_hole)

    def add_goal_point(self, goal_point):
        self.goal_points.append(goal_point)
        self.add_widget(goal_point)

    def add_shot(self, shot):
        self.shots.append(shot)
        self.add_widget(shot)

    def add_stars(self, dt):
        self.stars = Stars(2000)
        self.add_widget(self.stars)

    def add_wall(self, wall):
        self.walls.append(wall)
        self.add_widget(wall)

    def clear_level(self):
        if self.aim_line:
            self.remove_widget(self.aim_line)

        for black_hole in self.black_holes:
            self.remove_widget(black_hole)
        self.black_holes = []

        for shot in self.shots:
            self.remove_widget(shot)
        self.shots = []

        for goal_point in self.goal_points:
            self.remove_widget(goal_point)
        self.goal_points = []

        for wall in self.walls:
            self.remove_widget(wall)
        self.walls = []

        if self.level_label:
            self.remove_widget(self.level_label)

    def load_level(self, level_index):
        self.clear_level()
        level = levels.levels[level_index]()
        level.load(self)
        level_text = "level %s: %s" % (level_index + 1, level.name)
        self.current_level = level_index
        self.display_level_text(level_text)

    def restart_level(self, *args):
        self.load_level(self.current_level)

    def display_level_text(self, level_text):
        self.level_label = Label(
            text=level_text, font_size=20, width=self.width, halign='center',
            y=self.height - 200, color=(1., 1., 1., 0.))
        self.add_widget(self.level_label)
        anim = Animation(color=(1, 1, 1, 1), duration=2.) + \
            Animation(color=(1, 1, 1, 1), duration=.5) + \
            Animation(color=(1, 1, 1, 0), duration=2.)
        anim.start(self.level_label)

    def display_instructions(self, button):
        instructions_text = """ 
you can shoot things by dragging your finger
or mouse across the screen
 
for each level, collect all the goal points
 
double tap to screen at any time to bring up the menu"""
        instructions_label = Label(
            text=instructions_text, font_size=20, width=self.width * .8,
            x=self.width * .1, y=self.height - 200, color=(1., 1., 1., 0.))
        self.add_widget(instructions_label)
        anim = Animation(color=(1, 1, 1, 1), duration=2.)
        anim.start(instructions_label)

    def display_main_menu(self, *args):
        self.clear_level()

        layout_width = self.width * .2
        layout_x = self.width * .4
        layout_y = self.height * .2

        self.menu = MainMenu(self, x=layout_x, y=layout_y, width=layout_width,
                             current_level=self.current_level)
        self.add_widget(self.menu)
    def on_touch_down(self, touch):
        if hasattr(self, 'menu') and self.menu.collide_point(*touch.pos):
            for child in self.menu.children:
                if child.collide_point(*touch.pos):
                    child.dispatch('on_touch_down', touch)

        if touch.is_double_tap:
            # for black_hole in self.black_holes:
            #     if black_hole.collide_point(*touch.pos):
            #         self.remove_widget(black_hole)
            #         self.black_holes.remove(black_hole)
            #         return True
            # black_hole = BlackHole(pos=touch.pos)
            # self.add_widget(black_hole)
            # self.black_holes.append(black_hole)
            for goal_point in self.goal_points:
                if goal_point.collide_point(*touch.pos):
                    self.remove_widget(goal_point)
                    self.goal_points.remove(goal_point)
                    return True
            goal_point = GoalPoint(pos=touch.pos)
            self.add_widget(goal_point)
            self.goal_points.append(goal_point)
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
        self.shots.append(shot)

        # rocket = Rocket(motion_v=motion_v, pos=(touch.x, touch.y))
        # self.add_widget(rocket)
        # self.rockets.append(rocket)

        self.remove_widget(self.aim_line)

    def remove_black_hole(self, black_hole):
        self.black_holes.remove(black_hole)
        self.remove_widget(black_hole)

    def remove_goal_point(self, goal_point):
        self.goal_points.remove(goal_point)
        self.remove_widget(goal_point)

    def remove_shot(self, shot):
        self.remove_widget(shot)
        self.shots.remove(shot)

    def start_game(self, button):
        self.load_level(0)

    def tick(self, dt):
        for shot1, shot2 in itertools.combinations(self.shots, 2):
            if circles_collide(shot1, shot2):
                shots_collide(shot1, shot2)
                shot1.last_bounced = None
                shot2.last_bounced = None

        for shot in self.shots:
            for black_hole in self.black_holes:
                shot.gravitate_towards(black_hole)
                if circles_collide(shot, black_hole):
                    self.remove_widget(shot)
                    self.shots.remove(shot)
            for wall in self.walls:
                if shot.collide_wall(wall):
                    print "collide"
            shot.move()

        for goal_point in self.goal_points:
            goal_point.move()

            for shot in self.shots:
                if circles_collide(goal_point, shot):
                    self.remove_widget(goal_point)
                    self.goal_points.remove(goal_point)

                    if len(self.goal_points) == 0:
                        print "DONE"
                    continue

        for rocket in self.rockets:
            for black_hole in self.black_holes:
                rocket.gravitate_towards(black_hole)
                if black_hole.collide_point(*rocket.pos):
                    self.remove_widget(rocket)
                    self.rockets.remove(rocket)
            rocket.move()


class FlingyApp(App):
    def build(self):
        return FlingBoard()


def circles_collide(widget_1, widget_2):
    widget_distance = Vector(widget_1.pos).distance(Vector(widget_2.pos))
    radial_distance = widget_1.r + widget_2.r
    return widget_distance < radial_distance


def shots_collide(shot1, shot2):
    p1_v = Vector(shot1.pos)
    p2_v = Vector(shot2.pos)
    shot1.motion_v = (p1_v - p2_v).normalize() / Vector(shot1.motion_v).length()
    shot2.motion_v = (p2_v - p1_v).normalize() / Vector(shot2.motion_v).length()


if __name__ == '__main__':
    FlingyApp().run()

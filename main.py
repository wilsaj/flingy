#!/usr/bin/env python
import itertools
import math

import kivy
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang import Builder
from kivy.vector import Vector
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from widgets import (AimLine, BlackHole, GoalPoint, MainMenu, Shot,
                     ShotCounter, Stars)
from levels import levels

kivy.require('1.0.9')

# set a limit on the number of shots allowed on screen at once
MAX_SHOTS = 20


class FlingBoard(Widget):
    """
    Main application widget, takes all the touches and turns them into
    fun.
    """
    def __init__(self, *args, **kwargs):
        super(FlingBoard, self).__init__()
        Window.clearcolor = (0.1, 0.1, 0.1, 1.)
        Clock.schedule_interval(self.tick, 1 / 60.)
        self._keyboard = Window.request_keyboard(
            None, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.aim_line = None
        self.black_holes = []
        self.buttons = []
        self.current_level = None
        self.level_label = None
        self.goal_points = []
        self.shot_counter = None
        self.shots = []
        self.stars = None
        self.walls = []

        self.new_background()

        # schedule rather than call directly init, so that width and
        # height are finished initializing
        Clock.schedule_once(self.display_main_menu)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        try:
            level_index = int(text)
            print "loading level %s..." % (level_index)
            self.load_level(levels[level_index])
        except ValueError:
            pass

    def add_aim_line(self, aim_line):
        self.aim_line = (aim_line)
        self.add_widget(aim_line)

    def add_black_hole(self, black_hole):
        self.black_holes.append(black_hole)
        self.add_widget(black_hole)

    def add_goal_point(self, goal_point):
        self.goal_points.append(goal_point)
        self.add_widget(goal_point)

    def add_shot(self, shot):
        self.shots.append(shot)
        self.add_widget(shot)
        self.shot_counter.increment()

    def add_shot_counter(self, shot_counter):
        self.shot_counter = shot_counter
        self.add_widget(shot_counter)

    def add_wall(self, wall):
        self.walls.append(wall)
        self.add_widget(wall)

    def clear_level(self):
        if hasattr(self, 'menu') and self.menu:
            self.menu.clear_widgets()

        self.black_holes = []
        self.goal_points = []
        self.shots = []
        self.walls = []
        self.clear_widgets()
        if self.stars:
            self.add_widget(self.stars)

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
for each level, the goal is to shoot an asteroid that
touches all the blue dots
 
touch and drag to aim an asteroid, release to shoot it
 
you have a limited number of shots per level, you'll
need to restart the level if you run out
 
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
        layout_y = self.height * .1

        self.menu = MainMenu(self, x=layout_x, y=layout_y, width=layout_width,
                             current_level=self.current_level)
        self.add_widget(self.menu)

    def end_game(self, *args):
        end_game_text = """ 
thanks for playing
 
you've mastered all the levels we've got for now, but
check back soon for more levels and updates"""
        end_game_label = Label(
            text=end_game_text, font_size=20, width=self.width * .8,
            x=self.width * .1, y=self.height - 200, color=(1., 1., 1., 0.))
        self.add_widget(end_game_label)
        anim = Animation(color=(1, 1, 1, 1), duration=2.)
        anim.start(end_game_label)

    def load_level(self, level):
        self.clear_level()
        self.new_background()
        level.load(self)
        level_index = levels.index(level)
        level_text = "level %s: %s" % (level_index + 1, level.name)
        self.current_level = level
        self.display_level_text(level_text)
        self.add_shot_counter(ShotCounter(
            max_shots=level.max_shots, x=30, y=15))

    def new_background(self):
        if self.stars:
            self.remove_widget(self.stars)

        self.stars = Stars(2000)
        self.add_widget(self.stars)

    def next_level(self, *args):
        next_level_index = levels.index(self.current_level) + 1
        if next_level_index < len(levels):
            self.load_level(levels[next_level_index])
        else:
            Clock.schedule_once(self.end_game, 2.)

    def on_touch_down(self, touch):
        if hasattr(self, 'menu') and self.menu.collide_point(*touch.pos):
            for child in self.menu.children:
                if child.collide_point(*touch.pos):
                    child.dispatch('on_touch_down', touch)

        if touch.is_double_tap:
            self.display_main_menu()

        if self.current_level and \
           len(self.shots) < self.current_level.max_shots:
            self.add_aim_line(AimLine(start_pt=touch.pos))

    def on_touch_move(self, touch):
        if not self.aim_line:
            return

        try:
            self.aim_line.end_pt = touch.pos
        except (KeyError), e:
            pass

    def on_touch_up(self, touch):
        if not self.aim_line:
            return

        start_v = Vector(self.aim_line.start_pt)
        end_v = Vector(self.aim_line.end_pt)

        velocity_v = start_v - end_v
        l = velocity_v.length()
        if l == 0.:
            return
        velocity_v /= math.sqrt(l)

        if len(self.shots) > MAX_SHOTS:
            self.remove_shot(self.shots[0])

        if self.current_level and \
           len(self.shots) < self.current_level.max_shots:
            self.add_shot(Shot(velocity=velocity_v, pos=(touch.x, touch.y)))

        self.remove_aim_line(self.aim_line)

    def remove_aim_line(self, aim_line):
        self.remove_widget(aim_line)
        self.aim_line = None

    def remove_black_hole(self, black_hole):
        self.black_holes.remove(black_hole)
        self.remove_widget(black_hole)

    def remove_goal_point(self, goal_point):
        self.goal_points.remove(goal_point)
        self.remove_widget(goal_point)

    def remove_shot(self, shot):
        self.remove_widget(shot)
        self.shots.remove(shot)

    def restart_level(self, *args):
        self.load_level(self.current_level)

    def start_game(self, button):
        self.load_level(levels[0])

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
                        Clock.schedule_once(self.next_level, 1)
                    continue


class FlingyApp(App):
    def build(self):
        return FlingBoard()

    def build_config(self, config):
        config.setdefaults('graphics', {
            'width': '800',
            'height': '600'
        })


def circles_collide(widget_1, widget_2):
    widget_distance = Vector(widget_1.pos).distance(Vector(widget_2.pos))
    radial_distance = widget_1.r + widget_2.r
    return widget_distance < radial_distance


def shots_collide(shot1, shot2):
    p1_v = Vector(shot1.pos)
    p2_v = Vector(shot2.pos)
    shot1.velocity = (p1_v - p2_v).normalize() / Vector(shot1.velocity).length()
    shot2.velocity = (p2_v - p1_v).normalize() / Vector(shot2.velocity).length()


if __name__ == '__main__':
    FlingyApp().run()

"""module that holds all the levels"""

from widgets import AimLine, BlackHole, GoalPoint, Rocket, Shot, Stars

class First(object):
    def load(self, fling_board):
        goal_point = GoalPoint(pos=(250, 250))
        fling_board.add_widget(goal_point)
        fling_board.goal_points.append(goal_point)


levels = [First]

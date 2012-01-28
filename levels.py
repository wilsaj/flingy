"""module that holds all the levels"""


import main


class First(object):
    def load(self, fling_board):
        goal_point = main.GoalPoint(pos=(50, 50))
        fling_board.add_widget(goal_point)
        fling_board.goal_points.append(goal_point)


levels = [First]

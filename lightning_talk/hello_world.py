from kivy.app import App
from kivy.uix.widget import Widget

class HelloWidget(Widget):
    pass

class WorldApp(App):
    def build(self):
        return HelloWidget()

if __name__ == '__main__':
    WorldApp().run()

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label


class HelloWidget(Widget):
    def __init__(self, **kwargs):
        super(HelloWidget, self).__init__(**kwargs)
        with self.canvas:
            Label(text='hello world!')


class WorldApp(App):
    def build(self):
        return HelloWidget()

if __name__ == '__main__':
    WorldApp().run()

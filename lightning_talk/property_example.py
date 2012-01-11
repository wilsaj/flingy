from kivy.properties import StringProperty
from kivy.uix.widget import Widget

def some_callback(instance, value):
    print "callback fired: property changed to " + value

class Foo(Widget):
    bar = StringProperty('starting value')

    def __init__(self, **kwargs):
        super(Foo, self).__init__(**kwargs)
        self.bind(bar=some_callback)

if __name__ == '__main__':
    f = Foo()
    f.bar = 'changeit'
    # callback fired: property changed to changeit

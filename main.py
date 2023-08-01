from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window

# Debug
from kivy.config import Config

from catchme import CatchMe
from automaton import Automaton

#### TO USE ####
# size_hint=(None, None),
# size = self.parent.size
# with self.canvas:
#     Color(1,0,0,1)
#     Rectangle(
#             pos = self.parent.pos,
#             size_hint = (None, None),
#             size = self.parent.size
#         )
#### TO USE ####

class MainWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        grid_size = int(min(Window.size)*2/3)
        
        catch_me = CatchMe(
            size = (grid_size, grid_size),
            x = (Window.size[0]-grid_size)/2,
            y = (Window.size[1]-grid_size)/2)
        # self.add_widget(catch_me)
        
        autom = Automaton()
        self.add_widget(autom)
        autom.reset()


class FreeAdsApp(App):
    def build(self):
        self.width = Window.width
        self.height = Window.height
        return MainWidget()
        
    

if __name__ == "__main__":
    
    app = FreeAdsApp()
    app.run()
    
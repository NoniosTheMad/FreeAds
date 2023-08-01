# Style
from kivy.graphics import *
# Layouts
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
# Other
from kivy.core.window import Window
from kivy.clock import Clock

import math
import random


from templates import *

class Automaton(FloatLayout):
    
    # Initializes the class, without creating the grid
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        ############# self variables #############
        self.pause = None
        self.turn = None
        
        self.auto_resume = True # future configuration
        self.action_consumes_turn = False # future configuration
        
        # Widgets
        self.grid = None
        self.menu = None
    
    
    # Resets the entire grid
    def reset(self):
        
        ############# Initialize widgets #############
        # Must be done outside __init__, to ensure the self.parent is defined
        
        self.size_hint=(None, None)
        self.size = self.parent.size
        
        # Clear priority canvas
        #self.canvas.after.clear()
        
        self.grid = BackgroundCanvas(
                pos = self.pos,
                size_hint = (None, None),
                size = self.size
            )
        self.grid.action_consumes_turn = self.action_consumes_turn
        self.grid.auto_resume = self.auto_resume
        
        self.add_widget(self.grid)
        
        # Create the menu instance
        self.menu = AutomatonMenu(
                # Whole screen (parent) width, 20% height, alligned on top (80%)
                pos = (self.pos[0], self.pos[1] + self.size[1] * 0.8),
                size_hint = (None, None),
                size = (self.size[0], self.size[1] * 0.2)
            )
        self.add_widget(self.menu)
        # Setup main menu functionality
        self.menu.setup()
        
        # Priorize self.menu canvas
        #self.canvas.after.add(self.menu.canvas)
        
        
                    
class Cell():
    def __init__(self, x=0, y=0, state=(1,1,1,1)) -> None:
        self.x = x
        self.y = y
        self.state = state
        self.fut_state = state
        
        self.neighbours = []



class BackgroundCanvas(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.margin = 2
        self.cells = []
        self.pause = True
        self.turn = 0
        
        self.density_factor = 60 # pixels per cell
        self.rows = int(self.size[1]/self.density_factor) + 2*self.margin
        self.cols = int(self.size[0]/self.density_factor) + 2*self.margin
        self.offsets = (self.size[0]%self.density_factor,
                        self.size[1]%self.density_factor)
        
        self.cell_position = lambda x, y: (
                (x-self.margin) * self.density_factor + self.offsets[0]/2+1,
                (y-self.margin) * self.density_factor + self.offsets[1]/2+1
            )
        
        # cell generation
        for x in range(self.cols):
            self.cells.append([])
            for y in range(self.rows):
                cell = Cell(
                        x=x,
                        y=y,
                        state=self.get_state(x, y)
                    )
                
                with self.canvas:
                    Color(*cell.state)
                    Rectangle(
                            pos= self.cell_position(x, y),
                            size=(self.density_factor-2,
                                  self.density_factor-2)
                        )
                
                self.cells[x].append(cell)
                
        self.get_neighbours()
        self.start()
    
    # Enable auto-run
    def start(self, frequency=10):
        Clock.schedule_interval(
            lambda dt: self.update(),
            1.0 / frequency)  # 4 frames per second
    
    # trigger update functions
    def update(self, force=False):
        if force or self.parent.menu.game_controls.pause_button.text == "On":
            self.update_states(interact=not force)
            self.update_grid()
    
    # update cell values
    def update_states(self, interact):
        if interact:
            self.turn += 1
            self.parent.menu.turn_counter.text = str(self.turn)
        
        self.canvas.clear()
        
        for col in self.cells:
            for cell in col:
                with self.canvas:
                    Color(*cell.state)
                    Rectangle(
                            pos=self.cell_position(cell.x, cell.y),
                            size=(self.density_factor-2,
                                  self.density_factor-2)
                        )
                if interact: self.interact(cell)
                else: cell.fut_state = cell.state
        return True
    
    # initial state of cells, based on their x, y position
    def get_state(self, x, y):
        return (1,1,1,1) # TODO: Randomize initial
    
    # touch effect on cell state
    def update_state(self, cell, mode="black", value=None):
        
        if mode == "black":
            cell.state = (0, 0, 0, 1)
        if mode == "white":
            cell.state = (1, 1, 1, 1)
        if mode == "invert":
            cell.state = tuple([1-x for x in cell.state])
            
        if mode == "red":
            cell.state = (1, 0, 0, 1)
        if mode == "green":
            cell.state = (0, 1, 0, 1)
        if mode == "blue":
            cell.state = (0, 0, 1, 1)

        if mode == "custom":
            cell.state = value
            
            
    # interaction between a cell and its neighbours.
    # this includes all the logic for future state values
    def interact(self, cell, template=storm_template):
        template(cell)
    
    # visual update after simulating the interacitons
    def update_grid(self):
        for col in self.cells:
            for cell in col:
                cell.state = cell.fut_state
    
    
    # touch trigger
    def on_touch_down(self, touch):
        
        # find touched cell
        obj_pos = (math.floor((touch.pos[0]-self.offsets[0]/2)/self.density_factor)+self.margin,
                   math.floor((touch.pos[1]-self.offsets[1]/2)/self.density_factor)+self.margin)
        
        # check if cell is outside of bounds
        if 0 > obj_pos[0] or len(self.cells) <= obj_pos[0] or \
                0 > obj_pos[1] or len(self.cells[obj_pos[0]]) <= obj_pos[1] or \
                touch.pos[1] < self.offsets[1]/2 - self.margin*self.density_factor or \
                touch.pos[0] < self.offsets[0]/2 - self.margin*self.density_factor:
            print("Out of bounds:", len(self.cells[obj_pos[1]]), len(self.cells), obj_pos)
            return None
        
        # trigger updates
        self.update_state(self.cells[obj_pos[0]][obj_pos[1]])
            
        self.update(force=self.auto_resume)
        if self.auto_resume:
            self.parent.menu.game_controls.pause_button.state = "down"
        
        
    def get_neighbours(self):
        limits = (len(self.cells), len(self.cells[0]))
        
        for col in range(len(self.cells)):
            for row in range(len(self.cells[col])):
                for i in range(2):
                    i = i*2 - 1
                    if col+i < 0 or col+i > limits[0]-1:
                        self.cells[col][row].neighbours.append(Cell())
                        continue
                    self.cells[col][row].neighbours.append(
                        self.cells[col+i][row])
                for i in range(2):
                    i = i*2 - 1
                    if row+i < 0 or row+i > limits[1]-1:
                        self.cells[col][row].neighbours.append(Cell())
                        continue
                    self.cells[col][row].neighbours.append(
                        self.cells[col][row+i])



class AutomatonMenu(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.game_controls = None
        self.turn_text = None
        self.turn_counter = None
        
    def setup(self):
        
        self.game_controls = GameControls(
                pos = (self.pos[0], self.pos[1] + self.size[1]/2),
                size_hint = (None, None),
                size = (self.size[0], self.size[1]/2)
            )
        self.add_widget(self.game_controls)
        self.game_controls.setup()
        
        self.turn_text = Label(
                text="Turn",
                size_hint=(None, None),
                size = (self.size[0], self.size[1]/4),
                pos = (self.pos[0], self.pos[1] + self.size[1]/3),
                color = (0, 0.8, 1, 0.6),
                font_size = 80
            )
        self.add_widget(self.turn_text)
        
        # Turn display layout
        self.turn_counter = Label(
                text="0",
                size_hint=(None, None),
                size = (self.size[0], self.size[1]/4),
                pos = (self.pos[0], self.pos[1]),
                color = (0, 0.8, 1, 0.6),
                font_size = 100,
                markup = True
            )
        self.add_widget(self.turn_counter)
        
        
class GameControls(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.pause_button = None
        self.menu_extension_button = None
        self.menu = None
        
        
    def setup(self):
        
        self.pause_button = PauseButton(
                text = "Off",
                pos = (self.pos[0] + self.size[0]*9/20, self.pos[1] + self.size[1]/4),
                size_hint = (None, None),
                size = (self.size[0]/10, self.size[1]/2)
            )
        self.add_widget(self.pause_button)
        
        
        self.show_menu = MenuButton(
                text = "Menu",
                pos = (self.pos[0] + self.size[0]*35/40, self.pos[1] + self.size[1]/4),
                size_hint = (None, None),
                size = (self.size[0]/10, self.size[1]/2)
            )
        self.add_widget(self.show_menu)
        
        self.menu = AdsMenu(
                orientation = "vertical",
                pos = (self.size[0]*9/10-10, 10),
                size_hint = (None, None),
                size = self.show_menu.size
            )
        

class PauseButton(ToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_state(self, _, value):
        if value == "down":
            self.text = "On"
        else:
            self.text = "Off"
            
            
class MenuButton(ToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_state(self, widget, value):
        
        if value == "down":
            self.text = "Hide"
            self.parent.add_widget(self.parent.menu)
        else:
            self.text = "Menu"
            self.parent.remove_widget(self.parent.menu)
            
class AdsMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.banner_counter = self.BannerCounter(
            orientation = "horizontal"
        )
        self.banner_counter.setup()
        
        self.banner_add2 = Button(text = "2"
        )
        
        self.add_widget(self.banner_counter)
        self.add_widget(self.banner_add2)
        
    class BannerCounter(BoxLayout):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            
            self.counter = None
            self.counter_change = None
            
            
        def setup(self):
            
            self.counter = Button(
                    text = '0',
                    disabled = True,
                    background_disabled_normal = '',
                    disabled_color = (1, 1, 1, 1),
                    background_normal = '',
                    background_color =(0.207, 0.423, 0.635, 0.9)
                )
            #self.counter.background_color = (1,1,1,1)
                
            self.counter_change = self.CounterChange(
                    orientation = "vertical"
                )
            self.counter_change.setup()
            
            self.add_widget(self.counter)
            self.add_widget(self.counter_change)

            
        class CounterChange(BoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                
                self.count = 0
                self.adder = None
                self.reducer = None
                self.MAX_BANNERS = 3# TODO
                
            def setup(self):
                self.adder = Button(text = "+1", on_press = self.add)
                self.reducer = Button(text = "-1", on_press = self.subtract)
                
                self.add_widget(self.adder)
                self.add_widget(self.reducer)
            
            def add(self, button):
                self.count = min(self.count + 1, self.MAX_BANNERS)
                self.parent.counter.text = str(self.count)
            
            def subtract(self, button):
                self.count = max(self.count - 1, 0)
                self.parent.counter.text = str(self.count)
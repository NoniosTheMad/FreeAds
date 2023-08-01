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
        self.fut_state = None
        
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
    
    # Enable auto-run
    def start(self, frequency=10):
        Clock.schedule_interval(
            lambda dt: self.update(),
            1.0 / frequency)  # 4 frames per second
    
    # trigger update functions
    def update(self):
        self.update_states()
        self.update_grid()
    
    # update cell values
    def update_states(self):
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
                self.interact(cell)
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
        
        if self.collide_point(*touch.pos):
            pass
        
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
        
        if self.action_consumes_turn:
            self.update()
        
        # begin automatic simulation
        if self.pause and self.auto_resume:
            self.start()
            self.pause=False
        
        
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
        
    def setup(self):
        
        self.pause_button = ToggleButton(
                text = "Pause",
                pos = (self.pos[0] + self.size[0]*9/20, self.pos[1] + self.size[1]/4),
                size_hint = (None, None),
                size = (self.size[0]/10, self.size[1]/2),
                on_state = self.pause_press
            )
        self.add_widget(self.pause_button)
        
        
        self.auto_start_button = ToggleButton(
                text = "Extend Menu",
                pos = (self.pos[0] + self.size[0]*35/40, self.pos[1] + self.size[1]/4),
                size_hint = (None, None),
                size = (self.size[0]/10, self.size[1]/2),
                on_state = self.extend_menu
            )
        self.add_widget(self.auto_start_button)
        
    
    # TODO: Fix click detection
    def pause_press(self, state):
        #TODO
        print("paused!")
        
    def extend_menu(self, state):
        #TODO
        pass
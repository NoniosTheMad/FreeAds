from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
import random

class CatchMe(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.rows = 16
        self.cols = 16
        
        self.buttons = []
        
        runner_pos = self.spawner("runner")
        hunter_pos = self.spawner("hunter")
        
        for x in range(self.cols):
            self.buttons.append([])
            for y in range(self.rows):
                cell = Button(
                        on_press = self.button_pressed,
                        on_release = self.button_released,
                        always_release = True
                    )
                cell.x_coord = x
                cell.y_coord = y
                cell.coords = (x, y)
                
                cell.safe_zone = self.check_safe_zone(cell)
                
                if cell.coords == runner_pos:
                    cell.cargo = "runner" #TODO
                elif cell.coords == hunter_pos:
                    cell.cargo = "hunter" #TODO
                else:
                    cell.cargo = None
                
                self.adjust_cell(cell)
                
                self.buttons[x].append(cell)
                self.add_widget(cell)
        
    def adjust_cell(self, button):
        
        # Color center cells (spawn)
        lim = self.find_center_cells(radius=1)
        
        if lim["x"][0] < button.x_coord < lim["x"][1] and \
            lim["y"][0] < button.y_coord < lim["y"][1]:
                    button.background_color = (.8, .8, .8, 1)
        
        button.background_color = (1, 1, 1, 1)
        if button.safe_zone == True:
            button.background_color = (.8, .8, .8, 1)
        if button.cargo == "runner":
            button.background_color = (.5, .8, 1, 1)
        if button.cargo == "hunter":
            button.background_color = (1, 0, 0, 1)
        if button.cargo == "wall":
            button.background_color = (.4, .4, .4, 1)
            
        
        
    def spawner(self, entity_type):
        
        if entity_type == "runner":
            
            x_rnd = random.randint(0, self.cols)
            y_rnd = random.randint(0, self.rows)
            
            lim = self.find_center_cells(radius = 2)
            
            # Ensure it is outside center radius
            while lim["x"][0] < x_rnd < lim["x"][1] and \
                lim["y"][0] < y_rnd < lim["y"][1]:
                x_rnd = random.randint(0, self.cols)
                y_rnd = random.randint(0, self.rows)
                
            return (x_rnd, y_rnd)
        
        if entity_type == "hunter":
            
            # Generate number within radius
            lim = self.find_center_cells(radius = 0)
            x_rnd = random.randint(lim["x"][0], lim["x"][1])
            y_rnd = random.randint(lim["y"][0], lim["y"][1])
            
            return (x_rnd, y_rnd)
    
    
    def check_safe_zone(self, button):
        lim = self.find_center_cells(radius = 1)
        if lim["x"][0] < button.x_coord < lim["x"][1] and \
                lim["y"][0] < button.y_coord < lim["y"][1]:
            return True
        return False
       
       
    def find_center_cells(self, radius):
        center_x = self.cols/2
        center_y = self.rows/2
        
        x_offset, y_offset = 0, 0
        
        if center_x == int(center_x):
            center_x = center_x
            x_offset = 1
        if center_y == int(center_y):
            center_y = center_y
            y_offset = 1
            
            return {"x": (center_x - x_offset - radius, center_x + radius),
                    "y": (center_y - y_offset - radius, center_y + radius)}
        
        
    def button_pressed(self, button):
        if button.cargo == None and not button.safe_zone:
            button.cargo = "wall"
        elif button.cargo == "wall":
            button.cargo = None
            
        self.adjust_cell(button)
    
    
    def button_released(self, button):
        self.adjust_cell(button)
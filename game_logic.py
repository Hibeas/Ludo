import pygame
import random
import time
import constants


class Pawn:
    def __init__(self, color, pawn_id, start_pos_xy):
        self.color = color      
        self.pawn_id = pawn_id  
        self.position = 0       # 0 = Yard, 1-57 = Board, 99 = Home
        self.is_home = False
        self.board_index = 0
        self.move_timer = 0
        self.move_speed = 30
        
        self.screen_pos = start_pos_xy
        
        self.image = pygame.image.load(f"assets/pawn_{color}.png").convert_alpha()
        self.rect = self.image.get_rect(center=self.screen_pos)

    def to_dict(self):
        """Prepares the pawn data to be sent over JSON"""
        return {
            "pawn_id": self.pawn_id,
            "color": self.color,
            "new_pos": self.position
        }
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        
    
    
    def reset_to_start(self, start_pos):
        self.position = 0
        self.board_index = 0
        self.is_home = False
        self.screen_pos = start_pos
        self.rect.center = self.screen_pos
        
        
        
        
    def update_screen_pos(self, board_index):
        if self.position < 52:
            self.screen_pos = constants.BOARD[board_index]
            self.rect.center = self.screen_pos
        else:
            home_step = self.position - 52
            if self.color == "blue":
                self.screen_pos = constants.BLUE_HOME[home_step]
            elif self.color == "green":
                self.screen_pos = constants.GREEN_HOME[home_step]
            
            self.rect.center = self.screen_pos
            self.is_home = True
                
    def move(self, dice, other_pawns):
        moved = False       
        if self.position == 0 and dice == 6:
            self.position = 1
            self.board_index = 0 if self.color == "blue" else 26
            self.update_screen_pos(self.board_index)
            moved = True
        elif self.position > 0 and not self.is_home:
            if self.position + dice > 51:
                self.position += dice
                self.board_index = 52 + (self.position - 52) 
            else:
                self.position += dice
                self.board_index = (self.board_index + dice) % 52 
            self.update_screen_pos(self.board_index)
            moved = True
        elif self.position > 0 and not self.is_home:
            self.board_index = self.board_index + dice
            self.position = self.position + dice
            self.update_screen_pos(self.board_index)
            moved = True
        elif self.is_home:
            current_home_idx = self.board_index - 52
            
            if current_home_idx + dice < 6:
                self.board_index += dice
                self.position += dice
                self.update_screen_pos(self.board_index)
                moved = True
                if self.board_index - 52 == 5:
                    print(f"{self.color} pawn {self.pawn_id} has FINISHED!")
            else:
                print("Roll too high to move further in home lane!")
        if moved and not self.is_home:
            self.check_capture(other_pawns)
        return moved
    
    def check_capture(self, other_pawns):
        for other in other_pawns:
            if other.color != self.color and other.position > 0 and not other.is_home:
                if other.board_index == self.board_index:
                    print(f"ZBICIE! {self.color} zbija {other.color}")
                    start_list = constants.BLUE_START if other.color == "blue" else constants.GREEN_START
                    other.reset_to_start(start_list[other.pawn_id - 1])




class Dice:
    def __init__(self, position):
        self.position = position
        self.images = [pygame.image.load(f"assets/dice_{i}.png").convert_alpha() for i in range(1, 7)]
        self.current_value = 0
        self.is_rolling = False
        self.roll_start_time = 0
        self.roll_duration = 1.0  
        self.last_frame_time = 0
        self.frame_delay = 0.1
        self.new_value = False

    def start_roll(self):
        if not self.is_rolling:
            self.is_rolling = True
            self.roll_start_time = time.time()
            self.last_frame_time = time.time()

    def update(self):
        if self.is_rolling:
            now = time.time()
            elapsed = now - self.roll_start_time
            
            if elapsed < self.roll_duration:
                if now - self.last_frame_time > self.frame_delay:
                    self.current_value = random.randint(1, 6)
                    self.last_frame_time = now 
            else:
                self.is_rolling = False
                self.new_value = True
                self.current_value = random.randint(1, 6)
                print("Dice rolled:", self.current_value)
                return self.current_value

    def draw(self, surface):
        img = self.images[self.current_value - 1]
        rect = img.get_rect(center=self.position)
        surface.blit(img, rect)

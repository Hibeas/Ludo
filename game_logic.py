import pygame
import random
import time


class Pawn:
    def __init__(self, color, pawn_id, start_pos_xy):
        self.color = color      
        self.pawn_id = pawn_id  
        self.position = 0       # 0 = Yard, 1-40 = Board, 99 = Home
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
        
    def auto_walk(self, board_list):
        if self.board_index < len(board_list):
            self.move_timer += 1
            if self.move_timer >= self.move_speed:
                self.rect.center = board_list[self.board_index]
                self.board_index += 1
                self.move_timer = 0 # Reset timer




class Dice:
    def __init__(self, position):
        self.position = position
        self.images = [pygame.image.load(f"assets/dice_{i}.png").convert_alpha() for i in range(1, 7)]
        self.current_value = 1
        self.is_rolling = False
        self.roll_start_time = 0
        self.roll_duration = 1.0  
        self.last_frame_time = 0
        self.frame_delay = 0.1

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
                self.current_value = random.randint(1, 6)
                print("Dice rolled:", self.current_value)

    def draw(self, surface):
        img = self.images[self.current_value - 1]
        rect = img.get_rect(center=self.position)
        surface.blit(img, rect)

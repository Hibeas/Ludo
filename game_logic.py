import pygame
import random
import time
import constants


class Pawn:
    #pawn initialization
    def __init__(self, color, pawn_id, start_pos_xy, load_image):
        self.color = color      
        self.pawn_id = pawn_id  
        self.position = 0       # 0 = Yard, 1-57 = Board, 99 = Home
        self.is_home = False
        self.board_index = 0
        self.move_timer = 0
        self.move_speed = 30
        
        self.screen_pos = start_pos_xy

        if load_image:
            #images for 1,2,3 and 4 pawns
            self.images = {
                1: pygame.image.load(f"assets/pawn_{color}.png").convert_alpha(),
                2: pygame.image.load(f"assets/pawn_{color}_2.png").convert_alpha(),
                3: pygame.image.load(f"assets/pawn_{color}_3.png").convert_alpha(),
                4: pygame.image.load(f"assets/pawn_{color}_4.png").convert_alpha()
            }
            self.image = self.images[1]
            self.rect = self.image.get_rect(center=self.screen_pos)
        else:
            self.images = {}
            self.image =None
            self.rect = pygame.Rect(0, 0, 30, 30)
            self.rect.center = self.screen_pos

    #updating an image of single pawn
    def update_image(self, count):
        if self.image is not None:
            self.stack_count = count
            self.image = self.images.get(count, self.images[1])
            self.rect = self.image.get_rect(center=self.screen_pos)
            
    def to_dict(self):
        """Prepares the pawn data to be sent over JSON"""
        return {
            "pawn_id": self.pawn_id,
            "color": self.color,
            "new_pos": self.position,
            "board_index": self.board_index
        }
    
    #
    def draw(self, surface):
        surface.blit(self.image, self.rect)
    
    #reseting the pawn to starting position
    def reset_to_start(self, start_pos):
        self.position = 0
        self.board_index = 0
        self.is_home = False
        self.screen_pos = start_pos
        self.rect.center = self.screen_pos

    #   
    def update_screen_pos(self, board_index):
        #in starting home (not picked up yet)
        if self.position==0:
            start_list=constants.BLUE_START if self.color=="blue" else constants.GREEN_START
            self.screen_pos=start_list[self.pawn_id-1]
        #on the board
        elif 1 <= self.position <= 51:
            self.screen_pos = constants.BOARD[board_index]
            self.rect.center = self.screen_pos
        #in home
        else:
            home_step = self.position - 52
            if home_step>5: 
                home_step=5
            if self.color == "blue":
                self.screen_pos = constants.BLUE_HOME[home_step]
            elif self.color == "green":
                self.screen_pos = constants.GREEN_HOME[home_step]
            
            self.rect.center = self.screen_pos
            self.is_home = True
        #so the captured pawn dissappears 
        self.rect.center=self.screen_pos

    #moving a pawn            
    def move(self, dice, other_pawns):
        moved = False   
        #getting the pawn out of starting home    
        if self.position == 0 and dice == 6:
            self.position = 1
            self.board_index = 0 if self.color == "blue" else 26
            self.update_screen_pos(self.board_index)
            moved = True
        #moving on board
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
        #moving in home
        elif self.is_home:
            current_home_idx = self.board_index - 52
            #you can move
            if current_home_idx + dice < 6:
                self.board_index += dice
                self.position += dice
                self.update_screen_pos(self.board_index)
                moved = True
                if self.board_index - 52 == 5:
                    print(f"{self.color} pawn {self.pawn_id} has FINISHED!")
            #you rolled too high
            else:
                print("Roll too high to move further in home lane!")
        if moved and not self.is_home:
            self.check_capture(other_pawns)
        return moved
    
    #checking captures
    def check_capture(self, other_pawns):
        for other in other_pawns:
            if other.color != self.color and other.position > 0 and not other.is_home:
                if other.board_index == self.board_index:
                    print(f"ZBICIE! {self.color} zbija {other.color}")
                    start_list = constants.BLUE_START if other.color == "blue" else constants.GREEN_START
                    other.reset_to_start(start_list[other.pawn_id - 1])




class Dice:
    #initialization
    def __init__(self, position):
        self.position = position
        self.images = [pygame.image.load(f"assets/dice_{i}.png").convert_alpha() for i in range(1, 7)]
        self.current_value = 1
        self.is_rolling = False
        self.roll_start_time = 0
        self.roll_duration = 1.0  
        self.last_frame_time = 0
        self.frame_delay = 0.1
        self.new_value = False
        self.final_server_value=0

    #setting final value after a roll
    def set_final_value(self, val):
        self.final_server_value=val
        if not self.is_rolling:
            self.current_value=val

    #rolling animation
    def start_roll(self):
        if not self.is_rolling:
            self.is_rolling = True
            self.roll_start_time = time.time()
            self.last_frame_time = time.time()

    #updating dice
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
                self.current_value = self.final_server_value
                print("Dice rolled:", self.current_value)
                return self.current_value

    #drawing a dice
    def draw(self, surface):
        img = self.images[self.current_value - 1]
        rect = img.get_rect(center=self.position)
        surface.blit(img, rect)

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
        self.stack_count = 1

        if load_image:
            # Lazy-load and cache pawn images per color to avoid duplicate disk I/O
            try:
                images = _PAWN_IMAGE_CACHE.get(color)
            except NameError:
                _PAWN_IMAGE_CACHE = {}
                images = None

            if images is None:
                images = {
                    1: pygame.image.load(f"assets/pawn_{color}.png").convert_alpha(),
                    2: pygame.image.load(f"assets/pawn_{color}_2.png").convert_alpha(),
                    3: pygame.image.load(f"assets/pawn_{color}_3.png").convert_alpha(),
                    4: pygame.image.load(f"assets/pawn_{color}_4.png").convert_alpha()
                }
                try:
                    _PAWN_IMAGE_CACHE[color] = images
                except NameError:
                    # create cache in module scope
                    globals()['_PAWN_IMAGE_CACHE'] = {color: images}
            self.images = images
            self.image = self.images[1]
            self.rect = self.image.get_rect(center=self.screen_pos)
        else:
            self.images = {}
            self.image =None
            self.rect = pygame.Rect(0, 0, 30, 30)
            self.rect.center = self.screen_pos

    # updating the image of a single pawn
    def updateImage(self, count):
        if self.image is not None:
            self.stack_count = count
            self.image = self.images.get(count, self.images[1])
            self.rect = self.image.get_rect(center=self.screen_pos)
            
    def toDict(self):
        """Prepares the pawn data to be sent over JSON"""
        return {
            "pawn_id": self.pawn_id,
            "color": self.color,
            "new_pos": self.position,
            "board_index": self.board_index
        }
    
    #
    def draw(self, surface):
        if self.image is not None:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, (255,0,0), self.rect)
        
    def getOpponentCountAt(self, index, other_pawns):
        """Helper to count how many opponent pawns are at a specific board index."""
        return sum(1 for other in other_pawns 
                    if other.color != self.color 
                    and other.position > 0 
                    and not other.is_home 
                    and other.board_index == index)
        
    # resetting the pawn to starting position
    def resetToStart(self, start_pos):
        self.position = 0
        self.board_index = 0
        self.is_home = False
        self.screen_pos = start_pos
        self.rect.center = self.screen_pos

    #   
    def updateScreenPos(self, board_index):
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
        if self.position == 0 and dice == 6:
            target_index = 0 if self.color == "blue" else 26

            if self.getOpponentCountAt(target_index, other_pawns) >= 2:
                print(f"Cannot move out! Opponent block at index {target_index}!")
                return False
                
            self.position = 1
            self.board_index = target_index
            self.updateScreenPos(self.board_index)
            moved = True
            
        #move main board
        elif self.position > 0 and not self.is_home:
            current_pos = self.position
            current_idx = self.board_index
            path_blocked = False

            for step in range(1, dice + 1):
                check_pos = current_pos + step
                
                if check_pos > 51:
                    break 
                else:
                    check_idx = (current_idx + step) % 52
                
                if self.getOpponentCountAt(check_idx, other_pawns) >= 2:
                    path_blocked = True
                    break
            
            if path_blocked:
                print("Move invalid! Path or landing tile is blocked by an opponent stack!")
                return False
                
            if self.position + dice > 51:
                self.position += dice
                self.board_index = 52 + (self.position - 52) 
            else:
                self.position += dice
                self.board_index = (self.board_index + dice) % 52 
                
            self.updateScreenPos(self.board_index)
            moved = True
            
        # In home
        elif self.is_home:
            current_home_idx = self.board_index - 52
            if current_home_idx + dice < 6:
                self.board_index += dice
                self.position += dice
                self.updateScreenPos(self.board_index)
                moved = True
                if self.board_index - 52 == 5:
                    print(f"{self.color} pawn {self.pawn_id} has FINISHED!")
            else:
                print("Roll too high to move further in home lane!")
                
        if moved and not self.is_home:
            self.checkCapture(other_pawns)
        return moved
    
    #checking captures
    def checkCapture(self, other_pawns):
        for other in other_pawns:
            if other.color != self.color and other.position > 0 and not other.is_home:
                if other.board_index == self.board_index:
                    # Capture: send opponent pawn back to its starting yard
                    print(f"CAPTURE! {self.color} captures {other.color}")
                    start_list = constants.BLUE_START if other.color == "blue" else constants.GREEN_START
                    other.resetToStart(start_list[other.pawn_id - 1])




class Dice:
    #initialization
    def __init__(self, position):
        self.position = position
        # cache dice images at class level to avoid reloading
        try:
            images = Dice._images
        except AttributeError:
            images = None

        if images is None:
            Dice._images = [pygame.image.load(f"assets/dice_{i}.png").convert_alpha() for i in range(1, 7)]
        self.images = Dice._images
        self.current_value = 1
        self.is_rolling = False
        self.roll_start_time = 0
        self.roll_duration = 1.0  
        self.last_frame_time = 0
        self.frame_delay = 0.1
        self.new_value = False
        self.final_server_value=0

    #setting final value after a roll
    def setFinalValue(self, val):
        self.final_server_value=val
        if not self.is_rolling:
            self.current_value=val

    #rolling animation
    def startRoll(self):
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

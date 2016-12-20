# Mixxhead
# By Mixone Computing
# Mixhead - a copy of the original Boxhead game made in Python with Tkinter
 
from Tkinter import *
import random
import time
import math
 
Window_Height = 550 # set the window height and width
Window_Width = 800
 
X_Window_Buffer = 40
Y_Window_Buffer = 40
 
canvas = Canvas(highlightthickness=0, height=Window_Height, width=Window_Width)
canvas.master.title("Mixhead")
canvas.pack()
Main = canvas.create_rectangle(0,0,Window_Width,Window_Height,fill="#EBDCC7", belowThis = None) # create the base color similar to that of the Boxhead game
pic = PhotoImage(width=Window_Width, height=Window_Height)
canvas.create_image(0,0,image=pic,anchor=NW)
 
Zombie_Dict_Made = False # have the Zombies and Boxhead been created?
boxhead_made = False
Run_Game = True
New_Level = False
 
B_move_length = 2 # Some the game attributes that change and are used for the initial setup. Most would be better in a central Game Class
Zombie_per_move = .5
Devil_move = 1
direction = 1
shot_duration = .01
Zombie_Buffer = 30
kill_zone = 15
Number_of_Zombies = 5
total_devil_attacks = 0
blood_marks = 0
number_of_mines = 0
 
global pause_game # pause the game if 'P' is pressed or start it up if 'O' is pressed
pause_game = False
 
Mines_Dict = {} # holds all of the mines
Zombie_Dict = {} # Where the Zombies are kept - elements are deleted as Boxhead shoots them
Devil_Dict = {} # same as Zombie_Dict but for Devils
Dead_Zombie_List = []
Devil_Attack_Dict = {} # The spheres that the Devils can attack with
 
class Edge_limits(object):
    """Tells limits in x any y direction to objects so that they don't run off of the game screen"""
    def __init__(self):
        self.x_start = 2*X_Window_Buffer - 20
        self.y_start = 3*Y_Window_Buffer -35
        self.x_end = Window_Width - X_Window_Buffer - 20
        self.y_end = Window_Height - Y_Window_Buffer - 20
 
class Buffer(object):
    """The edge buffers for the game"""
    def __init__ (self,x_start,y_start,x_end,y_end,fill):
        canvas.create_rectangle(x_start,y_start,x_end,y_end,fill = fill)
 
left_buffer = Buffer(0,0,(X_Window_Buffer),(Y_Window_Buffer+Window_Height), "Black") # create all of the buffer images
right_buffer = Buffer((X_Window_Buffer+Window_Width),0,(Window_Width-(X_Window_Buffer)),((2*Y_Window_Buffer)+Window_Height), "Black")
top_buffer = Buffer(0,0,(Window_Width-X_Window_Buffer),Y_Window_Buffer,"Black")
bottom_buffer = Buffer(0,(Window_Height-Y_Window_Buffer),Window_Width,Window_Height,"Black")
 
class Blood(object):
    """What happens when you kill something. It create a blood spot on the coordinates of the killed Zombie(s) / Devil(s)
    They are deleted at the beginning of each new level"""
    def __init__(self,x,y):
        global base_for_blood
        self.image = PhotoImage(file = "images/game_elements/blood.gif")
        self.blood_spot = canvas.create_image(x,y,image = self.image)
        canvas.tag_lower(self.blood_spot)
        canvas.tag_lower(Main)
 
class MINE(object):
    """ The mines class. Watch where you step"""
    def __init__(self,x,y):
        self.photo = PhotoImage(file = "images/game_elements/mine.gif")
        self.image = canvas.create_image(x,y,image = self.photo) # Create a black rectangle for the mine image
        canvas.tag_lower(self.image)
        canvas.tag_lower(Main)
        self.destroy = False
        self.x = x
        self.y = y
    def explode(self):
        """Determine if a Zombie or Devil is close enought to set of the mine. If that is True then it tests
        to see whether any Zombie or Devil in the greater surrounding area should be killed"""
        destroy_zombie = []
        destroy_devil = []
        self.exploded = False
        for the_zombie in Zombie_Dict:
            Zombie = Zombie_Dict[the_zombie]
            if abs(self.x - Zombie.x) < 20 and abs(self.y - Zombie.y) < 20: # Test to see if an Zombie/Devil is within the box that is +/- 40 pixels of the mine's x and y
                self.exploded = True
                self.destroy = True
        for the_devil in Devil_Dict:
            Devil = Devil_Dict[the_devil]
            if abs(self.x - Devil.x) < 20 and abs(self.y - Devil.y) < 20:
                self.exploded = True
                self.destroy = True
        if self.exploded == True:
            explode = canvas.create_oval((self.x - 80),(self.y - 80),(self.x + 80),(self.y + 80),fill='Orange') # the Radius of the explosion is 80
            canvas.update()
        if self.exploded == True:
 
            for devil in Devil_Dict:
                Devil = Devil_Dict[devil]# Add the Zombie to a list to be deleted, since you cannot modify Dictionaries while traversing them
                if abs(self.x - Devil.x) < 80 and abs(self.y - Devil.y) < 80:
                    destroy_devil.append(devil)
 
            for zombie in Zombie_Dict:
                Zombie = Zombie_Dict[zombie]
                if abs(self.x - Zombie.x) < 80 and abs(self.y - Zombie.y) < 80:
                    destroy_zombie.append(zombie)
 
        for item in destroy_zombie: # Delete the Zombie/Devils caught up in the explosion
            canvas.delete(Zombie_Dict[item].zombie)
            del Zombie_Dict[item]
        for item in destroy_devil:
            canvas.delete(Devil_Dict[item].devil)
            del Devil_Dict[item]
        if self.exploded == True:
            canvas.delete(explode)
 
class Zombie_Attack(object):
    """The yellow circle that the zombies uses to attack Boxhead. It has a life span of 125 instances in the while loop before it disappears.
    Unless of course it strikes boxhead and lowers boxhead's health by a lot"""
    def __init__(self,x,y,x_vel,y_vel):
        self.x = x
        self.y = y
        self.image = PhotoImage(file = "images/game_elements/devil_a.gif")
        self.attack = canvas.create_image(self.x,self.y,image = self.image)
        self.x_vel = x_vel
        if self.x_vel > 0: # If the velocity in that direction is not 0 it adds 1 to the speed so that it is faster than the Devil who shot it.
            self.x_vel += .75
        if self.x_vel < 0:
            self.x_vel -= .75
        self.y_vel = y_vel
        if self.y_vel > 0:
            self.y_vel += .75
        if self.y_vel < 0:
            self.y_vel -= .75
        self.life_span = 125
    def move(self):
        global boxhead1
        self.x += self.x_vel
        self.y += self.y_vel
        canvas.coords(self.attack,self.x,self.y)
        self.life_span -=1
        if abs(self.x - boxhead1.x) < 30 and abs(self.y - boxhead1.y) < 30: #Strike Boxhead if within 30 pixels
            boxhead1.health -= 10
            self.life_span = 0
 
class Shot(object):
    """Correct where gun shoots from depending on which direction boxhead is. Because of the Boxhead image the coordinates from where the gun is if Boxhead is shooting up
    is different that if he were shooting to the left in regards to the original x,y position in the top left of the image"""
 
class Stats(object):
    """Creates the score label/info. This updates once per loop based on all of Boxhead's attributes ex. health and score"""
    def __init__(self):
        global boxhead1
        self.board = self.board = canvas.create_text(200,65)
        canvas.create_rectangle(X_Window_Buffer,Y_Window_Buffer,Window_Width-X_Window_Buffer,Y_Window_Buffer+20,fill="Red")
    def update(self):
        health_string = str(boxhead1.health)
        score_string = str(boxhead1.score)
        level_string = str(boxhead1.level)
        gun_string = str(boxhead1.gun)
        ammo_string = str(boxhead1.ammo)
        score_board = "Health: " + health_string + "  " + "Score: " + score_string + "  " + "Level: " + level_string + "  " + "Gun: " + gun_string + "  " + "Ammo: " + ammo_string
        canvas.delete(self.board)
        self.board = canvas.create_text(230,52,text=score_board)
 
class Boxhead(object):
    """The Boxhead charecter. Shoot, move, lay mines etc. are all contianed within the Boxhead class. Eventually all of the gun details need to be moved to thier own class so that Pistol = Gun(range,damage) and Mine = Gun(radius, damage)
    eventually even Shotgun = Gun(range,damange,arc_width) and so on"""
    def __init__(self):
        self.image_up = PhotoImage(file = "images/boxhead/bhup.gif") # The image changes if Boxhead is facing up down left right
        self.image_down = PhotoImage(file = "images/boxhead/bhdown.gif")
        self.image_left = PhotoImage(file = "images/boxhead/bhleft.gif")
        self.image_right = PhotoImage(file = "images/boxhead/bhright.gif")
        self.x = random.randrange(((game_limit.x_start/2)+15),game_limit.x_end) # pick a random starting point on the right side of the field. Zombies start on the left half.
        self.y = random.randrange(game_limit.y_start,game_limit.y_end)
        self.image = canvas.create_image(self.x,self.y,image = self.image_up)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = 1
        self.health = 100 # +5 health is added at the beginning of every level
        self.gun = "Pistol"
        self.level = 1
        self.score = 0
        self.ammo = "Infinite"
        self.pause = False
        self.bonus_score = 0
        self.pistol_range = 150 # the range of the pistol in pixels
        self.mine_count = 0 # how many mines are left
 
    def move(self):
        global move
        if (self.x >= game_limit.x_end) and self.x_vel > 0: # Can boxhead move in that direction or will he strike the edge of the game
            self.x_vel = 0
        if self.x <= game_limit.x_start and self.x_vel < 0:
            self.x_vel = 0
        else:
            pass
 
        if (self.y >= game_limit.y_end) and self.y_vel > 0:
            self.y_vel = 0
        elif self.y <= game_limit.y_start and self.y_vel < 0:
            self.y_vel = 0
        else:
            pass
 
        self.x += self.x_vel
        self.y += self.y_vel
        canvas.coords(self.image,(self.x),(self.y))
 
    def shot_coords_update(self):
        """update the coordinates of where the gun should be fired from"""
        if self.gun == "Pistol" or self.gun == 'Mines':
            gun_range = self.pistol_range
        global up
        global down
        global left
        global right
 
        up.x_start = 10 + boxhead1.x
        up.y_start = -5 + boxhead1.y
        up.x_end = 11 + boxhead1.x
        up.y_end = boxhead1.y - (gun_range + 5)
 
        down.x_start = boxhead1.x - 10
        down.y_start = 5 + boxhead1.y
        down.x_end = boxhead1.x - 9
        down.y_end = gun_range+5 + boxhead1.y
 
        left.x_start = 15 + boxhead1.x
        left.y_start = boxhead1.y - 15
        left.x_end = boxhead1.x - gun_range - 15
        left.y_end = boxhead1.y -15
 
        right.x_start = 5 + boxhead1.x
        right.y_start = 0 + boxhead1.y
        right.x_end = gun_range + 5 + boxhead1.x
        right.y_end = 1 + boxhead1.y
 
        if self.direction == 1: # what direction boxhead is fact 1=up 2=down etc.
            boxhead1.shoot_coords(up.x_start,up.y_start,up.x_end,up.y_end)
        if self.direction == 2:
            boxhead1.shoot_coords(down.x_start,down.y_start,down.x_end,down.y_end)
        if self.direction == 3:
            boxhead1.shoot_coords(left.x_start,left.y_start,left.x_end,left.y_end)
        if self.direction == 4:
            boxhead1.shoot_coords(right.x_start,right.y_start,right.x_end,right.y_end)
 
    def pic(self):
        """Change Boxhead's image based on the direction he is moving"""
        if self.direction == 1:
            canvas.itemconfigure(self.image, image = self.image_up)
        if self.direction == 2:
            canvas.itemconfigure(self.image, image = self.image_down)
        if self.direction == 3:
            canvas.itemconfigure(self.image, image = self.image_left)
        if self.direction == 4:
            canvas.itemconfigure(self.image, image = self.image_right)
 
    def fire_gun(self):
        """Fires whichever weapon that boxhead is using at the moment"""
        global blood_marks,Blood_Dict
        self.bonus_score = 0
        Dead_Zombie_List = []
        which_zombie = 0
        global Zombie_Dict
        kill_list = [] # the librarys that hold which Zombie needs to be deleted from Zombie_Dict
        kill_devil = []
 
        if self.gun == "Pistol":
            self.bullet_image = canvas.create_rectangle(self.shoot_x_start,self.shoot_y_start,self.shoot_x_end+1,self.shoot_y_end+1,fill="Black") # create the bullet
            canvas.update()
            for Each_Zombie in Zombie_Dict:
                    Zombie = Zombie_Dict[Each_Zombie] # test whether every Zombie is within the path of the bullet
                    if self.direction == 1:
                        if Zombie.y < self.shoot_y_start and Zombie.y > self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                            kill_list.append(Each_Zombie)
                    elif self.direction == 2:
                        if Zombie.y > self.shoot_y_start and Zombie.y < self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                            kill_list.append(Each_Zombie)
                    elif self.direction == 3:
                        if Zombie.x < self.shoot_x_start and Zombie.x > self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                            kill_list.append(Each_Zombie)
                    elif self.direction == 4:
                        if Zombie.x > self.shoot_x_start and Zombie.x < self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                            kill_list.append(Each_Zombie)
 
            for each_devil in Devil_Dict:
                    Zombie = Devil_Dict[each_devil]
                    if self.direction == 1:
                        if Zombie.y < self.shoot_y_start and Zombie.y > self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                            Zombie.health -= 26 # Lower the Devil's health by 26 so that it takes 4 shots to kill a Devil while 1 for a Zombie
                            kill_devil.append(each_devil)
                    elif self.direction == 2:
                        if Zombie.y > self.shoot_y_start and Zombie.y < self.shoot_y_end and abs(Zombie.x - self.shoot_x_start) < 25:
                            Zombie.health -= 26
                            kill_devil.append(each_devil)
                    elif self.direction == 3:
                        if Zombie.x < self.shoot_x_start and Zombie.x > self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                            Zombie.health -= 26
                            kill_devil.append(each_devil)
                    elif self.direction == 4:
                        if Zombie.x > self.shoot_x_start and Zombie.x < self.shoot_x_end and abs(Zombie.y - self.shoot_y_start) < 25:
                            Zombie.health -= 26
                            kill_devil.append(each_devil)
 
            for Each_Zombie in kill_list: # Destroy the Zombie to be killed from the Zombie_Dict and canvas
                mark = Blood(Zombie_Dict[Each_Zombie].x,Zombie_Dict[Each_Zombie].y)
                Blood_Dict[blood_marks] = mark
                blood_marks +=1
                canvas.delete(Zombie_Dict[Each_Zombie])
                del Zombie_Dict[Each_Zombie]
                boxhead1.score+=1
                self.bonus_score +=1
 
            for the_devil in kill_devil:
                mark = Blood(Devil_Dict[the_devil].x,Devil_Dict[the_devil].y)
                Blood_Dict[blood_marks] = mark
                blood_marks +=1
                if Devil_Dict[the_devil].health <= 0:
                    canvas.delete(Devil_Dict[the_devil])
                    del Devil_Dict[the_devil]
                    boxhead1.score+=1
                    self.bonus_score +=1
            canvas.delete(self.bullet_image)
            self.score += (self.bonus_score / 3)
 
        if self.gun == 'Mines': # lay a mine and give it mine.x = boxhead1.x and mine.y = boxhead1.y
            global number_of_mines
            if self.mine_count > 0:
                mine = MINE(self.x,self.y)
                Mines_Dict[number_of_mines] = mine
                number_of_mines +=1
                self.mine_count -=1
            else:
                pass
 
        canvas.update()
 
    def key(self,key):
        """Look at the input from the keyboard and adjust Boxhead accordingly. Movement = WASD Fire = Space Pistol = I Mines = U Pause = P Unpause = O"""
        global press,pause_game
        press = key
        if press == 'z':
            self.x_vel = 0
            self.y_vel = -B_move_length
            self.direction = 1
        if press == 's':
            self.x_vel = 0
            self.y_vel = B_move_length
            self.direction = 2
        if press == 'q':
            self.x_vel = -B_move_length
            self.y_vel = 0
            self.direction = 3
        if press == 'd':
            self.x_vel = B_move_length
            self.y_vel = 0
            self.direction = 4
        if press == 'space':
            self.fire_gun()
        if press == 'p':
            pause_game = True
        if press == 'o':
            pause_game = False
        if press == 'i':
            self.gun = "Pistol"
            self.ammo = 'Infinte'
        if press == 'u':
            self.gun = 'Mines'
            self.ammo = self.mine_count
 
    def shoot_coords(self,x_start,y_start,x_end,y_end):
        """Help to adjust the coordinates based on where to shoot from each direction"""
        self.shoot_x_start = x_start
        self.shoot_y_start = y_start
        self.shoot_x_end = x_end
        self.shoot_y_end = y_end
 
class Zombie(object):
    """ZOMBIES. Nothing like a bunch of Zombies that chase you around. Boxhead is faster then Zombies, but Zombies can move diagonally"""
    def __init__(self):
        self.zup = PhotoImage(file = "images/zombies/zup.gif") # there are 8 directions that Zombies can move in
        self.zdown = PhotoImage(file = "images/zombies/zdown.gif")
        self.zleft = PhotoImage(file = "images/zombies/zleft.gif")
        self.zright = PhotoImage(file = "images/zombies/zright.gif")
        self.zrightup = PhotoImage(file = "images/zombies/zrightup.gif")
        self.zrightdown = PhotoImage(file = "images/zombies/zrightdown.gif")
        self.zleftup = PhotoImage(file = "images/zombies/zleftup.gif")
        self.zleftdown = PhotoImage(file = "images/zombies/zleftdown.gif")
        self.x = random.randrange(game_limit.x_start,(game_limit.x_end-(game_limit.x_end / 2))) # create Zombies in the left half of the arena
        self.y = random.randrange(game_limit.y_start,game_limit.y_end)
        self.direction = 1
        self.zombie = canvas.create_image(self.x,self.y, image = self.zup)
        self.alive = True
        self.distance_to_b = 0
        self.attacked = False
    def move(self,target):
        """
            This function like Boxhead1.move tests to see whether the Zombie will hit the edge of the game, but also tests to see whether the Zombie will collide with another
        Zombie in front of it. This helps avoid having all of the Zombies stack up on top of each other and froming one really dense Zombie. That is what the really long line of code
        below is testing"""
        global boxhead1
        which_zombie = 0
        collision = False
        self.x_vel = 0
        self.y_vel = 0
        for which_zombie in Zombie_Dict:
            test_self = Zombie_Dict[which_zombie]
            if abs(self.x - boxhead1.x) - abs(boxhead1.x - test_self.x) > 0 and abs(self.x - boxhead1.x) - abs(boxhead1.x - test_self.x) < Zombie_Buffer and abs(self.y - boxhead1.y) - abs(boxhead1.y - test_self.y) > 0 and abs(self.y - boxhead1.y) - abs(boxhead1.y - test_self.y) < Zombie_Buffer:
                collision = True
            else:
                pass
        if collision == True:
           pass
        elif collision == False:
            if self.x < target.x:
                self.x_vel = Zombie_per_move
            if self.x > target.x:
                self.x_vel= -Zombie_per_move
            elif self.x == target.x:
                self.x_vel = 0
            if self.x >= Window_Width - 25: # x coords
                self.x_vel = -Zombie_per_move
            if self.x <= 0 + 5:
                self.x_vel = Zombie_per_move
            if self.y < target.y:
                self.y_vel = Zombie_per_move
            if self.y > target.y:
                self.y_vel = -Zombie_per_move
            elif self.y == target.y:
                self.y_vel = 0
            if self.y >= Window_Height - 25:# y coords
                self.y_vel = -Zombie_per_move
            if self.y <= 0 + 5:
                self.y_vel = Zombie_per_move
            self.y += self.y_vel
            self.x += self.x_vel
            canvas.coords(self.zombie,(self.x),(self.y)) # move the Zombie accordingly based on if it should move or another Zombie is in its path
        else:
            pass
    def pic(self):
        """Update the Zombie image based on which of the 8 directions that it is traveling in"""
        if self.y_vel < 0 and self.x_vel == 0:
            canvas.itemconfigure(self.zombie, image = self.zup)
        if self.y_vel > 0 and self.x_vel == 0:
            canvas.itemconfigure(self.zombie, image = self.zdown)
        if self.x_vel < 0 and self.y_vel == 0:
            canvas.itemconfigure(self.zombie, image = self.zleft)
        if self.x_vel > 0 and self.y_vel == 0:
            canvas.itemconfigure(self.zombie, image = self.zright)
        if self.y_vel > 0 and self.x_vel > 0:
            canvas.itemconfigure(self.zombie, image = self.zrightdown)
        if self.y_vel < 0 and self.x_vel > 0:
            canvas.itemconfigure(self.zombie, image = self.zrightup)
        if self.y_vel > 0 and self.x_vel < 0:
            canvas.itemconfigure(self.zombie, image = self.zleftdown)
        if self.y_vel < 0 and self.x_vel < 0:
            canvas.itemconfigure(self.zombie, image = self.zleftup)
 
    def contact(self):
        """This is how the Zombies do damage to Boxhead. If they com in contact with Boxhead it deducts health from boxhead"""
        if abs(boxhead1.x - self.x) < 10 and abs(boxhead1.y - self.y) < 10 and self.attacked == False:
            boxhead1.health -= 1
            self.attacked = True
        else:
            self.attacked = False
 
class Devil(object):
    """The Devil Class. They move faster than Zombies have more health and can attack Boxhead by colliding with him or by shooting him"""
    def __init__(self):
        self.x = random.randrange(game_limit.x_start,(game_limit.x_end-(game_limit.x_end / 2)))
        self.y = random.randrange(game_limit.y_start,game_limit.y_end)
        self.direction = 1
        self.alive = True
        self.distance_to_b = 0
        self.attacked = False
        self.attack_fire = 0
        self.health = 100
        self.dup = PhotoImage(file = "images/devils/du.gif") # the 8 Devil images
        self.ddown = PhotoImage(file = "images/devils/db.gif")
        self.dleft = PhotoImage(file = "images/devils/dl.gif")
        self.dright = PhotoImage(file = "images/devils/dr.gif")
        self.drightup = PhotoImage(file = "images/devils/dtr.gif")
        self.drightdown = PhotoImage(file = "images/devils/dbr.gif")
        self.dleftup = PhotoImage(file = "images/devils/dtl.gif")
        self.dleftdown = PhotoImage(file = "images/devils/dbl.gif")
 
        self.devil = canvas.create_image(self.x,self.y, image = self.dup)
 
    def move(self,target):
        """The Devil's movement is the same as the Zombies except that Devils move faster"""
        which_zombie = 0
        collision = False
        self.x_vel = 0
        self.y_vel = 0
        for the_devil in Devil_Dict:
            test_self = Devil_Dict[the_devil]
            if abs(self.x - boxhead1.x) - abs(boxhead1.x - test_self.x) > 0 and abs(self.x - boxhead1.x) - abs(boxhead1.x - test_self.x) < Zombie_Buffer and abs(self.y - boxhead1.y) - abs(boxhead1.y - test_self.y) > 0 and abs(self.y - boxhead1.y) - abs(boxhead1.y - test_self.y) < Zombie_Buffer:
                collision = True
            else:
                pass
        if collision == True:
           pass
        elif collision == False:
            if self.x < target.x:
                self.x_vel = Devil_move
            if self.x > target.x:
                self.x_vel= -Devil_move
            elif self.x == target.x:
                self.x_vel = 0
            if self.x >= Window_Width - 25: # x coords
                self.x_vel = -Devil_move
            if self.x <= 0 + 5:
                self.x_vel = Devil_move
            if self.y < target.y:
                self.y_vel = Devil_move
            if self.y > target.y:
                self.y_vel = -Devil_move
            elif self.y == target.y:
                self.y_vel = 0
            if self.y >= Window_Height - 25:# y coords
                self.y_vel = -Devil_move
            if self.y <= 0 + 5:
                self.y_vel = Devil_move
            self.y += self.y_vel
            self.x += self.x_vel
            canvas.coords(self.devil,(self.x),(self.y))
        else:
            pass
 
    def pic(self):
        """update the image"""
        if self.y_vel < 0 and self.x_vel == 0:
            canvas.itemconfigure(self.devil, image = self.dup)
        if self.y_vel > 0 and self.x_vel == 0:
            canvas.itemconfigure(self.devil, image = self.ddown)
        if self.x_vel < 0 and self.y_vel == 0:
            canvas.itemconfigure(self.devil, image = self.dleft)
        if self.x_vel > 0 and self.y_vel == 0:
            canvas.itemconfigure(self.devil, image = self.dright)
        if self.y_vel > 0 and self.x_vel > 0:
            canvas.itemconfigure(self.devil, image = self.drightdown)
        if self.y_vel < 0 and self.x_vel > 0:
            canvas.itemconfigure(self.devil, image = self.drightup)
        if self.y_vel > 0 and self.x_vel < 0:
            canvas.itemconfigure(self.devil, image = self.dleftdown)
        if self.y_vel < 0 and self.x_vel < 0:
            canvas.itemconfigure(self.devil, image = self.dleftup)
 
    def contact(self):
        """If a Devil comes in contact with boxhead it deducts more health than a Zombie would"""
        if abs(boxhead1.x - self.x) < 10 and abs(boxhead1.y - self.y) < 10 and self.attacked == False:
            boxhead1.health -= 2
            self.attacked = True
        else:
            self.attacked = False
 
    def attack(self,boxhead1):
        """If the Devil is within +/- 200 pixels in the X and Y directions then it shoots a fireball at boxhead 1 time and then waits 45 loops to shoot agian"""
        global total_devil_attacks
        if abs(boxhead1.x - self.x) < 200 and abs(boxhead1.y - self.y) < 200 and self.attack_fire > 45:
            d_attack = Zombie_Attack(self.x,self.y,self.x_vel,self.y_vel)
            Devil_Attack_Dict[total_devil_attacks] = d_attack
            total_devil_attacks +=1
            self.attack_fire = 0
        else:
            self.attack_fire +=1
 
def key_press(event):
    """This function passes all of the key presses to the Boxhead1.key function for further analysis"""
    global pause_game
    press = event.keysym
    boxhead1.key(press)
    if press == 'o':
        pause_game = False
 
def init_game_parts():
    """ This builds all of the inital game elements that are only created once regardless of the number of levels. For example it creates the score board"""
    global up, down, right, left
    global down
    global right
    global left
    global current_shot
    global game_limit
    global score_board
    global boxhead1
    global Zombie_Dict
    global game_limit
    up = Shot()
    down = Shot()
    left = Shot()
    right = Shot()
    current_shot = Shot()
    game_limit = Edge_limits()
    boxhead1 = Boxhead()
    score_board = Stats()
 
def new_level():
    """For every new level all of the Devils and Zombies have been killed so new ones need to be created. Each time 70% more Zombies are added"""
    build_zombie = 0
    build_devil = 0
    for i in range(Number_of_Zombies):
            z = Zombie()
            Zombie_Dict[build_zombie] = z
            build_zombie+=1
    for i in range(int(Number_of_Zombies / 5)):
        D = Devil()
        Devil_Dict[build_devil] = D
        build_devil +=1
 
def main_loop():
    """The central function for the game. There are 2 while loops. The inner one is only broken for a new level and the outer while loop is only broken
    if boxhead dies and the game is over"""
    global New_Level,Run_Game,Zombie_Dict,Dead_Zombie_List,Number_of_Zombies,boxhead1
    init_game_parts() # create all of the game images like the edge buffers
    while Run_Game == True:
        global Blood_Dict
        Blood_Dict = {} # create a new empty blood dictionary
        if boxhead1.health <= 0: # boxhead died - game over
            return 'Game Over! Final Score: '+str(boxhead1.score)+' Final Level: '+str((boxhead1.level - 1))
        else:
            new_level()
            boxhead1.health += 5 # add +5 to Boxheads health each new level
            boxhead1.mine_count += int(Number_of_Zombies / 5) # Boxhead gets 1/5 of the # of Zombies of Mines. If there are 5 Zombies Boxhead gets 1 mine
            while New_Level == False: # the Level loop that runs until Boxhead dies or all of the Zombie/Devils have been killed
                New_Level = False
                """Moves the Devils and Zombies"""
                for the_zombie in Zombie_Dict:
                    if pause_game != True:
                        Zombie_Dict[the_zombie].move(boxhead1)
                    Zombie_Dict[the_zombie].pic()
                    Zombie_Dict[the_zombie].contact()
                for the_devil in Devil_Dict:
                    if pause_game != True:
                        Devil_Dict[the_devil].move(boxhead1)
                        Devil_Dict[the_devil].attack(boxhead1)
                    Devil_Dict[the_devil].pic()
                    Devil_Dict[the_devil].contact()
 
                destroy = []
                """ The attack sphere that the Devils shoot"""
                if pause_game != True:
                    for d_attack in Devil_Attack_Dict:
                        Devil_Attack_Dict[d_attack].move()
                        if Devil_Attack_Dict[d_attack].life_span <= 0:
                            destroy.append(d_attack)
                    for item in destroy:
                        canvas.delete(Devil_Attack_Dict[item].attack)
                        del Devil_Attack_Dict[item]
 
                """Explode the mines"""
                mine_destroy = []
                for mine in Mines_Dict:
                    Mines_Dict[mine].explode()
                    if Mines_Dict[mine].destroy == True:
                        mine_destroy.append(mine)
                for mine in mine_destroy:
                    canvas.delete(Mines_Dict[mine].image)
                    del Mines_Dict[mine]
 
                """Boxhead moves"""
                if pause_game != True:
                    boxhead1.move()
                boxhead1.pic()
                boxhead1.shot_coords_update()
                score_board.update()
                time.sleep(.02) # sleep for 1/100 of a second between loops
                canvas.update()
                if len(Zombie_Dict) == 0 and len(Devil_Dict) == 0: # if they both = 0 then a new level is created
                    New_Level = True
                if boxhead1.health <= 0:
                    New_Level = True
                    Run_Game = False
 
            boxhead1.level +=1
            Number_of_Zombies = int(float(Number_of_Zombies) * 1.7) # Increase the number of Zombies each round
            for blood in Blood_Dict: # Delete all of the blood for the new round
                canvas.delete(Blood_Dict[blood])
 
            New_Level = False
 
    print 'Game Over! Final Score: '+str(boxhead1.score)+' Final Level: '+str(boxhead1.level - 1) # print the final score
 
canvas.after(30, main_loop)
canvas.master.bind("<Key>", key_press)
canvas.pack()
canvas.mainloop()

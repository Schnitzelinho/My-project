import arcade
import random
import pprint

# Konstanty
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Labyrinth"
MOVEMENT_SPEED = 100    #Pohyb o jeden díl
TILE_SIZE = 100         #Velikost dílu
GRID_SIZE = 7           #Počet sloupců a řádků
BACKGROUND_WIDTH = GRID_SIZE * TILE_SIZE
BACKGROUND_HEIGHT = GRID_SIZE * TILE_SIZE
DISTANCE_BORDER = 150   #Vzdálenost středu karty od hranice pole
STARTING_POSITIONS = [
    (DISTANCE_BORDER, DISTANCE_BORDER),
    (DISTANCE_BORDER, SCREEN_HEIGHT - DISTANCE_BORDER),
    (SCREEN_WIDTH - DISTANCE_BORDER - 400, SCREEN_HEIGHT - DISTANCE_BORDER), 
    (SCREEN_WIDTH - DISTANCE_BORDER - 400, DISTANCE_BORDER)  
]
EXTRA_TILE_POSITION = (10, 10)
LAST_COLUMN_INDEX = GRID_SIZE - 1

TREASURE_COUNT = 24
STATIC_CORDS = [(0, 0),(0, 6), (6, 0), (6, 6)]
TILE_TEXTURES = ["kartalabvzor1.png", "kartalabvzor2.png", "kartalabvzor3.png"]
PLAYER_IMAGES = ["player_red.png","player_blue.png","player_green.png","player_yellow.png"]
 
class TextButton():
    def __init__(self, center_x, center_y, width, height, text, action_function):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.action_function = action_function

    def draw(self):
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, arcade.color.LIGHT_GRAY)
        arcade.draw_text(self.text, self.center_x, self.center_y, arcade.color.BLACK, font_size=20, anchor_x="center", anchor_y="center")

    def check_mouse_press(self, x, y):
        if (self.center_x - self.width / 2 < x < self.center_x + self.width / 2 and
                self.center_y - self.height / 2 < y < self.center_y + self.height / 2):
            self.action_function()


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate = 1/30)

        # Nastavení barvy pozadí
        arcade.set_background_color(arcade.color.GRAY)
 
        #Držení spritů
        self.tile_list = arcade.SpriteList()
        self.players = []
        self.active_player_index = 0
        self.tile_positions = {}
        self.button_list = []

        # Načtení hráče
        for i in range(4):
            player_sprite = arcade.Sprite(PLAYER_IMAGES[i],0.8)
            player_sprite.center_x, player_sprite.center_y = STARTING_POSITIONS[i] 
            self.players.append(player_sprite)
        
        # Herní deska
        self.first_shift = True
        corner_angles = [90,180,0,270]

        for row in range(GRID_SIZE):    # Pro každý díl z plánu
            for col in range(GRID_SIZE):    
                center_x = DISTANCE_BORDER + col * TILE_SIZE        #střed dílu = vzdálenost od hrany + číslo sloupce * velikost dílu (150+1*100 = 250)
                center_y = DISTANCE_BORDER + row * TILE_SIZE
                texture = random.choice(TILE_TEXTURES)              #random volba z textur - rovna, zatacka,...
                tile = arcade.Sprite(texture, 1)
                tile.center_x = center_x
                tile.center_y = center_y
                
                if (row, col) in STATIC_CORDS:                      
                    # Pokud je statická, přiřaď následující vlastnosti
                    texture = "kartalabvzor1.png"
                    tile.texture = arcade.load_texture(texture)
                    angle = corner_angles[STATIC_CORDS.index((row, col))]
                    tile.angle = angle
                else:
                    tile.angle = random.randint(0, 3) * 90
                

                # Determine movement options based on texture and angle
                move_right = move_left = move_down = move_up = False            #základní pohybové vlastnosti karet

                if texture == "kartalabvzor1.png":      # Zatáčka
                    name = "curve"
                    tile.texture.name = "kartalabvzor1.png"
                    if tile.angle == 0:
                        move_right = True
                        move_down = True
                    elif tile.angle == 90:
                        move_up = True
                        move_right = True
                    elif tile.angle == 180:
                        move_left = True
                        move_up = True
                    elif tile.angle == 270:
                        move_down = True
                        move_left = True
                
                elif texture == "kartalabvzor2.png":    # Rovná
                    name = "straight"
                    tile.texture.name = "kartalabvzor2.png"
                    if tile.angle in [0, 180]:
                        move_right = True
                        move_left = True
                    elif tile.angle in [90, 270]:
                        move_down = True
                        move_up = True
                elif texture == "kartalabvzor3.png":    # Křižovatka
                    name = "t-junction"
                    tile.texture.name = "kartalabvzor3.png"
                    if tile.angle == 0:
                        move_left = True
                        move_right = True
                        move_up = True
                    elif tile.angle == 90:
                        move_left = True
                        move_down = True
                        move_up = True
                    elif tile.angle == 180:
                        move_left = True
                        move_right = True
                        move_down = True
                    elif tile.angle == 270:
                        move_right = True
                        move_up = True
                        move_down = True

                #Přiřazení vlastností ke každému dílu do slovníku
                self.tile_positions[(col, row)] = {
                    'name': name,
                    'angle': tile.angle,
                    'move_right': move_right,
                    'move_down': move_down,
                    'move_up': move_up,
                    'move_left': move_left
                }
                self.tile_list.append(tile)

        # Initialize extra tile
        self.extra_tile = None

        # Create the extra tile and assign it
        self.extra_tile = self.create_extra_tile()
        self.tile_positions[(10, 10)] = self.extra_tile
        
        pprint.pprint(self.tile_positions)  # Vytisknutí slovníku se všemi informacemi o všech dílech

    def create_extra_tile(self):
        texture = random.choice(["kartalabvzor1.png", "kartalabvzor2.png"])
        angle = random.choice([0, 90, 180, 270])

        # Create the sprite for the extra tile
        extra_tile = arcade.Sprite(texture, 1)
        extra_tile.angle = angle
        extra_tile.center_x = SCREEN_WIDTH - DISTANCE_BORDER
        extra_tile.center_y = SCREEN_HEIGHT - DISTANCE_BORDER

        # Set movement properties based on the chosen texture and angle
        move_right = move_left = move_down = move_up = False

        if texture == "kartalabvzor1.png":  # Curve
            name = "curve"
            if angle == 0:
                move_right = True
                move_down = True
            elif angle == 90:
                move_up = True
                move_right = True
            elif angle == 180:
                move_left = True
                move_up = True
            elif angle == 270:
                move_down = True
                move_left = True
        elif texture == "kartalabvzor2.png":  # Straight
            name = "straight"
            if angle in [0, 180]:
                move_right = True
                move_left = True
            elif angle in [90, 270]:
                move_down = True
                move_up = True

        # Add the sprite to the tile_list
        self.tile_list.append(extra_tile)

        return {
            'name': name,
            'angle': angle,
            'move_right': move_right,
            'move_down': move_down,
            'move_up': move_up,
            'move_left': move_left
        }

    def setup(self):
        self.button = TextButton(DISTANCE_BORDER // 3, 250 , 25, 25, "→", self.on_button_click)
        self.button_list.append(self.button)
    
    def shift_grid(self, entity, index, direction):
        # entity = row/column; index is the row/column number
        if entity == 'row':
            row = index - 1  # Adjust for zero-based indexing
            if direction == 'right':
                self.shift_row(row, 'right')
            elif direction == 'left':
                self.shift_row(row, 'left')
        elif entity == 'column':
            col = index - 1
            if direction == 'down':
                self.shift_column_down(col)
            elif direction == 'up':
                self.shift_column_up(col)

    def shift_row(self, row_index, direction):
        """Shifts a row left or right based on the direction provided."""
        extra_tile_properties = self.tile_positions[EXTRA_TILE_POSITION].copy()  # Copy extra tile properties

        if direction == 'right':
            pushed_out_tile_properties = self.tile_positions[(0, row_index)].copy()  # Pushed out tile from the left
            range_func = range(GRID_SIZE)
            step = 1
        else:  # direction == 'left'
            pushed_out_tile_properties = self.tile_positions[(LAST_COLUMN_INDEX, row_index)].copy()  # Pushed out tile from the right
            range_func = range(LAST_COLUMN_INDEX, -1, -1)
            step = -1

        pushed_out_texture = self.tile_list[row_index * GRID_SIZE + (0 if direction == 'right' else LAST_COLUMN_INDEX)].texture
        pushed_out_angle = self.tile_list[row_index * GRID_SIZE + (0 if direction == 'right' else LAST_COLUMN_INDEX)].angle

        for col in range_func:
            current_position = (col, row_index)
            neighbor_position = (col + step, row_index) if direction == 'right' else (col - step, row_index)

            if neighbor_position in self.tile_positions:
                # Copy properties from neighbor position to current position
                self.tile_positions[current_position] = self.tile_positions[neighbor_position]
                self.tile_list[col + row_index * GRID_SIZE].texture = self.tile_list[neighbor_position[0] + row_index * GRID_SIZE].texture
                self.tile_list[col + row_index * GRID_SIZE].angle = self.tile_list[neighbor_position[0] + row_index * GRID_SIZE].angle
            else:
                # Assign extra tile properties if out of bounds
                self.tile_positions[current_position] = extra_tile_properties
                self.tile_list[col + row_index * GRID_SIZE].texture = self.tile_list[-1].texture
                self.tile_list[col + row_index * GRID_SIZE].angle = extra_tile_properties["angle"]

        # Set values for the pushed out tile
        self.tile_positions[EXTRA_TILE_POSITION] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle

    def shift_column_up(self, col_index):
        """Shifts a column up, pushing out the top tile."""
        extra_tile_properties = self.tile_positions[EXTRA_TILE_POSITION].copy()  # Copy extra tile properties

        pushed_out_tile_properties = self.tile_positions[(col_index, 0)].copy()  # Pushed out tile from the bottom
        pushed_out_texture = self.tile_list[col_index].texture
        pushed_out_angle = self.tile_list[col_index].angle

        for row in range(GRID_SIZE):
            current_position = (col_index, row)
            above_position = (col_index, row + 1)

            if above_position in self.tile_positions:
                # Copy properties from the above tile to the current tile
                self.tile_positions[current_position] = self.tile_positions[above_position]
                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[(row + 1) * GRID_SIZE + col_index].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = self.tile_list[(row + 1) * GRID_SIZE + col_index].angle
            else:
                # Assign extra tile properties if out of bounds
                self.tile_positions[current_position] = extra_tile_properties
                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[-1].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = extra_tile_properties["angle"]

        # Set values for the pushed out tile
        self.tile_positions[EXTRA_TILE_POSITION] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle

    def shift_column_down(self, col_index):
        """Shifts a column down, pushing out the bottom tile."""
        extra_tile_properties = self.tile_positions[EXTRA_TILE_POSITION].copy()  # Copy extra tile properties

        pushed_out_tile_properties = self.tile_positions[(col_index, LAST_COLUMN_INDEX)].copy()  # Pushed out tile from the top
        pushed_out_texture = self.tile_list[col_index + LAST_COLUMN_INDEX * GRID_SIZE].texture
        pushed_out_angle = self.tile_list[col_index + LAST_COLUMN_INDEX * GRID_SIZE].angle

        for row in range(LAST_COLUMN_INDEX, -1, -1):  # Start from the bottom and go up
            current_position = (col_index, row)
            below_position = (col_index, row - 1)

            if below_position in self.tile_positions:
                # Copy properties from the below tile to the current tile
                self.tile_positions[current_position] = self.tile_positions[below_position]
                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[(row - 1) * GRID_SIZE + col_index].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = self.tile_list[(row - 1) * GRID_SIZE + col_index].angle
            else:
                # Assign extra tile properties if out of bounds
                self.tile_positions[current_position] = extra_tile_properties
                self.tile_list[col_index].texture = self.tile_list[-1].texture
                self.tile_list[col_index].angle = extra_tile_properties["angle"]

        # Set values for the pushed out tile
        self.tile_positions[EXTRA_TILE_POSITION] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle

    def on_draw(self):
        arcade.start_render()
        self.tile_list.draw()
        for button in self.button_list:
            button.draw()

        # Vykreslení hráčů na obrazovku
        self.players[self.active_player_index].draw()
        #for player in self.players:
            #player.draw()
    def update(self, delta_time):
        self.tile_list.update()
        active_player = self.players[self.active_player_index]
        
        # Border check
        if active_player.center_x < DISTANCE_BORDER:
            active_player.center_x = DISTANCE_BORDER
        if active_player.center_x > SCREEN_WIDTH - DISTANCE_BORDER - 400:
            active_player.center_x = SCREEN_WIDTH - DISTANCE_BORDER - 400
        if active_player.center_y < DISTANCE_BORDER:
            active_player.center_y = DISTANCE_BORDER
        if active_player.center_y > SCREEN_HEIGHT - DISTANCE_BORDER:
            active_player.center_y = SCREEN_HEIGHT - DISTANCE_BORDER
    

    def get_tile_under_player(self, player):
        """Returns the position and properties of the tile under the given player."""
        # Calculate grid position based on player's center position
        grid_x = int(player.center_x - DISTANCE_BORDER) // TILE_SIZE
        grid_y = int(player.center_y - DISTANCE_BORDER) // TILE_SIZE

        tile_position = (int(grid_x), int(grid_y))
        return self.tile_positions.get(tile_position, None)
    
    
    def get_adjacent_tile(self,current_tile_position, direction):
        if direction == 'up':
            adjacent_position = (current_tile_position[0], current_tile_position[1] + 1)
        elif direction == 'down':
            adjacent_position = (current_tile_position[0], current_tile_position[1] - 1)
        elif direction == 'left':
            adjacent_position = (current_tile_position[0] - 1, current_tile_position[1])
        elif direction == 'right':
            adjacent_position = (current_tile_position[0] + 1, current_tile_position[1])
        return self.tile_positions.get(adjacent_position,None)


    def on_key_press(self, key, modifiers):
        active_player = self.players[self.active_player_index]
        tile_under_player = self.get_tile_under_player(active_player)

        if key == arcade.key.UP:
            if tile_under_player and tile_under_player["move_up"]:
                grid_x = int((active_player.center_x - DISTANCE_BORDER) // TILE_SIZE)
                grid_y = int((active_player.center_y - DISTANCE_BORDER) // TILE_SIZE)
                adjacent_tile = self.get_adjacent_tile((grid_x, grid_y), 'up')
                if adjacent_tile and adjacent_tile["move_down"]:
                    active_player.center_y += MOVEMENT_SPEED
            else:
                print("Cannot move up")
            
        elif key == arcade.key.DOWN:
            if tile_under_player and tile_under_player["move_down"]:
                grid_x = int((active_player.center_x - DISTANCE_BORDER) // TILE_SIZE)
                grid_y = int((active_player.center_y - DISTANCE_BORDER) // TILE_SIZE)
                adjacent_tile = self.get_adjacent_tile((grid_x, grid_y), 'down')
                if adjacent_tile and adjacent_tile["move_up"]:
                    active_player.center_y -= MOVEMENT_SPEED
            else:
                print("Cannot move down")
        elif key == arcade.key.LEFT:
            if tile_under_player and tile_under_player["move_left"]:
                grid_x = int((active_player.center_x - DISTANCE_BORDER) // TILE_SIZE)
                grid_y = int((active_player.center_y - DISTANCE_BORDER) // TILE_SIZE)
                adjacent_tile = self.get_adjacent_tile((grid_x, grid_y), 'left')
                if adjacent_tile and adjacent_tile["move_right"]:
                    active_player.center_x -= MOVEMENT_SPEED
            else:
                print("Cannot move left")

        elif key == arcade.key.RIGHT:
            if tile_under_player and tile_under_player["move_right"]:
                grid_x = int((active_player.center_x - DISTANCE_BORDER) // TILE_SIZE)
                grid_y = int((active_player.center_y - DISTANCE_BORDER) // TILE_SIZE)
                adjacent_tile = self.get_adjacent_tile((grid_x, grid_y), 'right')
                if adjacent_tile and adjacent_tile["move_left"]:
                    active_player.center_x += MOVEMENT_SPEED
            else:
                print("Cannot move right")  

        elif key == arcade.key.D:
            # Šoupnutí zprava
            self.shift_grid('row', 4, 'right')

        elif key == arcade.key.A:
            # Šoupnutí zleva
            self.shift_grid('row', 4, 'left')

        elif key == arcade.key.W:
            # Šoupnutí zhora
            self.shift_grid('column', 4, 'up')

        elif key == arcade.key.S:
            # Šoupnutí zdola
            self.shift_grid('column', 4, 'down')

        elif key == arcade.key.P:
            tile_info = self.tile_positions.get((6, 1), None)
            tile_info1 = self.tile_positions.get((0, 1), None)
            tile_info2 = self.tile_positions.get((10, 10), None)
            if tile_info:
                print(f"2. ŘADA POSLEDNÍ: ", end="")
                pprint.pprint(tile_info)
                print(f"2. ŘADA PRVNÍ: ", end="")
                pprint.pprint(tile_info1)                           
                print(f"EXTRA: ", end="")
                pprint.pprint(tile_info2)

        elif key == arcade.key.ENTER:
            # Switch to the next player
            self.active_player_index = (self.active_player_index + 1) % len(self.players) 
        print(tile_under_player)


    def on_key_release(self, key, modifiers):
        """ Called whenever the user releases a key. """
        pass

    def on_button_click(self):
        print("Button clicked!")

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for button in self.button_list:
                button.check_mouse_press(x, y)

if __name__ == "__main__":
    window = MyGame()
    window.setup()
    arcade.run()

"""DODĚLAT ŠOUPÁNÍ, STATICKÁ POLE, ODMĚNY NEJSPÍŠ UDĚLAT VE STYLU 1-24 A SBÍRAT"""

import arcade, random, pprint

import arcade.color

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
TREASURE_COUNT = 24
STATIC_CORDS = [(0, 0), (0, 2), (0, 4), (0, 6),
                (2, 0), (2, 2), (2, 4), (2, 6),
                (4, 0), (4, 2), (4, 4), (4, 6),
                (6, 0), (6, 2), (6, 4), (6, 6)
                ]                               # SOUŘADNICE NEPOHYBLIVÝCH DÍLŮ
STATIC_ANGLES = [90,0,0,180,
                270,0,90,90,
                270,270,180,90,
                0,180,180,270
                ]
STATIC_TEXTURES = ["labkarta_0red.png", "labkarta_s2.png", "labkarta_s3.png", "labkarta_0yellow.png",
                "labkarta_s5.png", "labkarta_s6.png", "labkarta_s7.png", "labkarta_s8.png",
                "labkarta_s9.png", "labkarta_s10.png", "labkarta_s11.png", "labkarta_s12.png",
                "labkarta_0blue.png", "labkarta_s14.png", "labkarta_s15.png", "labkarta_0green.png"
                ]
TEXTURES_CURVE = ["kartalabvzor1.png", "labkarta_0red.png", "labkarta_0blue.png", "labkarta_0yellow.png", "labkarta_0green.png", "labkarta7.png", "labkarta8.png", "labkarta9.png", "labkarta10.png", "labkarta11.png", "labkarta12.png" ]
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
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, arcade.color.YELLOW_ORANGE)
        arcade.draw_text(self.text, self.center_x, self.center_y, arcade.color.BLACK, font_size=20, anchor_x="center", anchor_y="center")

    def check_mouse_press(self, x, y):
        if (self.center_x - self.width / 2 < x < self.center_x + self.width / 2 and
                self.center_y - self.height / 2 < y < self.center_y + self.height / 2):
            self.action_function(self.text, x, y)


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate = 1/30)

        # Nastavení barvy pozadí
        arcade.set_background_color(arcade.color.NAVY_BLUE)
 
        #Držení spritů
        self.tile_list = arcade.SpriteList()
        self.players = []
        self.active_player_index = 0
        self.tile_positions = {}
        self.button_list = []

        # Generate the tile textures with desired frequencies
        self.tile_textures = (
            ["kartalabvzor1.png"] * 10 +
            ["kartalabvzor2.png"] * 12 +
            ["labkarta1.png","labkarta2.png","labkarta3.png","labkarta4.png","labkarta5.png","labkarta6.png","labkarta7.png","labkarta8.png","labkarta9.png","labkarta10.png","labkarta11.png","labkarta12.png"]  # Add more if needed
        )

        # Shuffle the list to randomize texture selection order
        random.shuffle(self.tile_textures)

        # Načtení hráče
        self.player_colors = [arcade.color.RED, arcade.color.BLUE, arcade.color.GREEN, arcade.color.YELLOW]
        self.player_color_names = {
            arcade.color.RED: "Red",
            arcade.color.GREEN: "Green",
            arcade.color.BLUE: "Blue",
            arcade.color.YELLOW: "Yellow"
        }
        for i in range(4):
            player_sprite = arcade.Sprite(PLAYER_IMAGES[i],0.8)
            player_sprite.center_x, player_sprite.center_y = STARTING_POSITIONS[i] 
            self.players.append(player_sprite)
        
        # Herní deska
        self.first_shift = True

        for row in range(GRID_SIZE):    # Pro každý díl z plánu
            for col in range(GRID_SIZE):    
                center_x = DISTANCE_BORDER + col * TILE_SIZE        #střed dílu = vzdálenost od hrany + číslo sloupce * velikost dílu (150+1*100 = 250)
                center_y = DISTANCE_BORDER + row * TILE_SIZE

                tile = arcade.Sprite(None, 1)
                tile.center_x = center_x
                tile.center_y = center_y
            
                if (row, col) in STATIC_CORDS:
                    index = STATIC_CORDS.index((row, col))
                    print(index)
                    texture = STATIC_TEXTURES[index]
                    angle = STATIC_ANGLES[index]

                    # Load texture and set angle
                    tile.texture = arcade.load_texture(texture)
                    tile.angle = angle
                    
                else:
                    texture = self.tile_textures.pop()  # Get and remove the last element from the list
                    tile.texture = arcade.load_texture(texture)
                    tile.angle = random.randint(0, 3) * 90
                
                tile.my_texture_name = texture

                # Stanovení vlastností podle textury a úhlu
                move_right = move_left = move_down = move_up = False            #základní pohybové vlastnosti karet

                if texture in TEXTURES_CURVE:      # Zatáčka
                    name = "curve"
                    tile.my_texture_name = "kartalabvzor1.png"
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
                    tile.my_texture_name = "kartalabvzor2.png"
                    if tile.angle in [0, 180]:
                        move_right = True
                        move_left = True
                    elif tile.angle in [90, 270]:
                        move_down = True
                        move_up = True
                else:#elif texture == "kartalabvzor3.png":    # Křižovatka
                    name = "t-junction"
                    tile.my_texture_name = "kartalabvzor3.png"
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

    def transform_tile(self, tile):
        tile.angle += 90
        if tile.angle > 270:
            tile.angle = 0
        
        texture = tile.my_texture_name
        print(texture)
        move_right = move_left = move_down = move_up = False

        # Determine movement options based on texture and angle
        if texture in TEXTURES_CURVE:  # Curve
            name = "curve"
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

        elif texture == "kartalabvzor2.png":  # Straight
            name = "straight"
            if tile.angle in [0, 180]:
                move_right = True
                move_left = True
            elif tile.angle in [90, 270]:
                move_down = True
                move_up = True

        else: #elif texture == "kartalabvzor3.png":  # T-junction
            name = "t-junction"
            if tile.angle == 0:
                move_left = move_right = move_up = True
            elif tile.angle == 90:
                move_left = move_down = move_up = True
            elif tile.angle == 180:
                move_left = move_right = move_down = True
            elif tile.angle == 270:
                move_right = move_up = move_down = True

        # Assign properties to the tile's position
        self.tile_positions[(10,10)] = {
            'name': name,
            'angle': tile.angle,
            'move_right': move_right,
            'move_down': move_down,
            'move_up': move_up,
            'move_left': move_left
        }
        
        return tile

    def create_extra_tile(self):
        texture = self.tile_textures.pop()
        angle = random.choice([0, 90, 180, 270])

        # Create the sprite for the extra tile
        extra_tile = arcade.Sprite(texture, 1)
        extra_tile.angle = angle
        extra_tile.center_x = SCREEN_WIDTH - DISTANCE_BORDER
        extra_tile.center_y = SCREEN_HEIGHT - DISTANCE_BORDER
        
        # Přiřazení vlastností
        move_right = move_left = move_down = move_up = False

        if texture in TEXTURES_CURVE:  # Curve
            name = "curve"
            extra_tile.my_texture_name = "kartalabvzor1.png"
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
            extra_tile.my_texture_name = "kartalabvzor2.png"
            if angle in [0, 180]:
                move_right = True
                move_left = True
            elif angle in [90, 270]:
                move_down = True
                move_up = True

        else:#elif texture == "kartalabvzor3.png":    # Křižovatka
            name = "t-junction"
            extra_tile.my_texture_name = "kartalabvzor3.png"
            if angle == 0:
                move_left = True
                move_right = True
                move_up = True
            elif angle == 90:
                move_left = True
                move_down = True
                move_up = True
            elif angle == 180:
                move_left = True
                move_right = True
                move_down = True
            elif angle == 270:
                move_right = True
                move_up = True
                move_down = True
        
        
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
        # Tlačítko na otočení extra karty
        button = TextButton(SCREEN_WIDTH - DISTANCE_BORDER, SCREEN_HEIGHT - 1.5*DISTANCE_BORDER, 100,25,"Rotate", self.on_button_click)
        self.button_list.append(button)
        # Přidání tlačítek na levou stranu
        for i in range(3):
            button = TextButton(DISTANCE_BORDER // 3, DISTANCE_BORDER + (i * 2 + 1) * 100, 50, 50, "→", self.on_button_click)
            self.button_list.append(button)

        # Přidání tlačítek na pravou stranu
        for i in range(3):
            button = TextButton(SCREEN_WIDTH - DISTANCE_BORDER - 300, DISTANCE_BORDER + (i * 2 + 1) * 100, 50, 50, "←", self.on_button_click)
            self.button_list.append(button)

        # Přidání tlačítek na horní stranu
        for i in range(3):
            button = TextButton(DISTANCE_BORDER + (i * 2 + 1) * 100, SCREEN_HEIGHT - DISTANCE_BORDER // 3, 50, 50, "↓", self.on_button_click)
            self.button_list.append(button)

        # Přidání tlačítek na dolní stranu
        for i in range(3):
            button = TextButton(DISTANCE_BORDER + (i * 2 + 1) * 100, DISTANCE_BORDER // 3, 50, 50, "↑", self.on_button_click)
            self.button_list.append(button)
    
    def shift_grid(self, entity, index, direction): #entity = row/column; index číslo řádku/sloupce, direction up/down
        if entity == 'row':
            row = index - 1 #Odečtení kvůli indexování (souřadnice (2,2) v py == (1,1)...)
            if direction == 'right':
                self.shift_row_right(row)
            elif direction == 'left':
                self.shift_row_left(row)
        elif entity == 'column':
            col = index - 1
            if direction == 'down':
                self.shift_column_down(col)
            elif direction == 'up':
                self.shift_column_up(col)
            
    def shift_row_right(self, row_index):           
        """Šoupání zprava, mění se pouze sloupec, [T1, T2, T3, T4, T5, T6, T7] → [T2, T3, T4, T5, T6, T7, extra_tile]"""
        extra_tile_properties = self.tile_positions[(10, 10)].copy()  # Copy extra tile properties

        # Copy properties of the pushed out tile (leftmost tile)
        pushed_out_tile_properties = self.tile_positions[(0, row_index)].copy()
        pushed_out_texture = self.tile_list[row_index * GRID_SIZE].texture
        pushed_out_angle = self.tile_list[row_index * GRID_SIZE].angle
        pushed_out_texture_name = self.tile_list[row_index * GRID_SIZE].my_texture_name

        # Shift all tiles to the right
        for col in range(GRID_SIZE):
            current_position = (col, row_index)
            right_position = (col + 1, row_index)

            if right_position in self.tile_positions:  # If right position is within grid bounds
                # Copy the properties from the right to the current position
                self.tile_positions[current_position] = self.tile_positions[right_position]

                self.tile_list[col + row_index * GRID_SIZE].texture = self.tile_list[col + 1 + row_index * GRID_SIZE].texture
                self.tile_list[col + row_index * GRID_SIZE].angle = self.tile_list[col + 1 + row_index * GRID_SIZE].angle
                self.tile_list[col + row_index * GRID_SIZE].my_texture_name = self.tile_list[col + 1 + row_index * GRID_SIZE].my_texture_name
            else:
                # Otherwise assign extra tile properties to the current position
                self.tile_positions[current_position] = extra_tile_properties

                self.tile_list[col + row_index * GRID_SIZE].texture = self.tile_list[-1].texture
                self.tile_list[col + row_index * GRID_SIZE].angle = extra_tile_properties["angle"]
                self.tile_list[col + row_index * GRID_SIZE].my_texture_name = self.tile_list[-1].my_texture_name

        # Assign pushed out tile properties to the extra tile
        self.tile_positions[(10, 10)] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle
        self.tile_list[-1].my_texture_name = pushed_out_texture_name


    def shift_row_left(self, row_index):
        """Šoupání zleva, mění se pouze sloupec, [T1, T2, T3, T4, T5, T6, T7] → [extra_tile, T1, T2, T3, T4, T5, T6] """
        extra_tile_properties = self.tile_positions[(10, 10)].copy()

        # Copy properties of the pushed out tile (rightmost tile)
        pushed_out_tile_properties = self.tile_positions[(6, row_index)].copy()
        pushed_out_texture = self.tile_list[6 + row_index * GRID_SIZE].texture
        pushed_out_angle = self.tile_list[6 + row_index * GRID_SIZE].angle
        pushed_out_texture_name = self.tile_list[6 + row_index * GRID_SIZE].my_texture_name

        # Shift all tiles to the left
        for col in range(6, -1, -1):  # Start from rightmost column
            current_position = (col, row_index)
            left_position = (col - 1, row_index)

            if left_position in self.tile_positions:
                # Copy the properties from the left to the current position
                self.tile_positions[current_position] = self.tile_positions[left_position]

                self.tile_list[col + row_index * GRID_SIZE].texture = self.tile_list[col - 1 + row_index * GRID_SIZE].texture
                self.tile_list[col + row_index * GRID_SIZE].angle = self.tile_list[col - 1 + row_index * GRID_SIZE].angle
                self.tile_list[col + row_index * GRID_SIZE].my_texture_name = self.tile_list[col - 1 + row_index * GRID_SIZE].my_texture_name
            else:
                # Assign extra tile properties to the current position
                self.tile_positions[current_position] = extra_tile_properties

                self.tile_list[col + row_index * GRID_SIZE].texture = self.tile_list[-1].texture
                self.tile_list[col + row_index * GRID_SIZE].angle = extra_tile_properties["angle"]
                self.tile_list[col + row_index * GRID_SIZE].my_texture_name = self.tile_list[-1].my_texture_name

        # Assign pushed out tile properties to the extra tile
        self.tile_positions[(10, 10)] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle
        self.tile_list[-1].my_texture_name = pushed_out_texture_name


    def shift_column_up(self, col_index):           
        """Šoupání zhora, mění se pouze řádek, [T1, T2, T3, T4, T5, T6, T7] → [extra_tile, T1, T2, T3, T4, T5, T6]  """
        extra_tile_properties = self.tile_positions[(10, 10)].copy()

        # Copy properties of the pushed out tile (bottommost tile)
        pushed_out_tile_properties = self.tile_positions[(col_index, 0)].copy()
        pushed_out_texture = self.tile_list[col_index].texture
        pushed_out_angle = self.tile_list[col_index].angle
        pushed_out_texture_name = self.tile_list[col_index].my_texture_name

        # Shift all tiles upwards
        for row in range(GRID_SIZE):
            current_position = (col_index, row)
            above_position = (col_index, row + 1)

            if above_position in self.tile_positions:
                # Copy the properties from the above tile
                self.tile_positions[current_position] = self.tile_positions[above_position]

                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[(row + 1) * GRID_SIZE + col_index].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = self.tile_list[(row + 1) * GRID_SIZE + col_index].angle
                self.tile_list[row * GRID_SIZE + col_index].my_texture_name = self.tile_list[(row + 1) * GRID_SIZE + col_index].my_texture_name
            else:
                # Assign extra tile properties
                self.tile_positions[current_position] = extra_tile_properties

                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[-1].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = extra_tile_properties["angle"]
                self.tile_list[row * GRID_SIZE + col_index].my_texture_name = self.tile_list[-1].my_texture_name

        # Assign pushed out tile properties to the extra tile
        self.tile_positions[(10, 10)] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle
        self.tile_list[-1].my_texture_name = pushed_out_texture_name
     

    def shift_column_down(self, col_index):           
        """Šoupání zespoda, mění se pouze řádek, [T1, T2, T3, T4, T5, T6, T7] → [T2, T3, T4, T5, T6, T7, extra_tile]  """
        extra_tile_properties = self.tile_positions[(10, 10)].copy()

        # Copy properties of the pushed out tile (topmost tile)
        pushed_out_tile_properties = self.tile_positions[(col_index, 6)].copy()
        pushed_out_texture = self.tile_list[col_index + (GRID_SIZE - 1) * GRID_SIZE].texture
        pushed_out_angle = self.tile_list[col_index + (GRID_SIZE - 1) * GRID_SIZE].angle
        pushed_out_texture_name = self.tile_list[col_index + (GRID_SIZE - 1) * GRID_SIZE].my_texture_name

        # Shift all tiles downwards
        for row in range(6, -1, -1):
            current_position = (col_index, row)
            below_position = (col_index, row - 1)

            if below_position in self.tile_positions:
                # Copy the properties from the below tile
                self.tile_positions[current_position] = self.tile_positions[below_position]

                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[(row - 1) * GRID_SIZE + col_index].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = self.tile_list[(row - 1) * GRID_SIZE + col_index].angle
                self.tile_list[row * GRID_SIZE + col_index].my_texture_name = self.tile_list[(row - 1) * GRID_SIZE + col_index].my_texture_name
            else:
                # Assign extra tile properties
                self.tile_positions[current_position] = extra_tile_properties

                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[-1].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = extra_tile_properties["angle"]
                self.tile_list[row * GRID_SIZE + col_index].my_texture_name = self.tile_list[-1].my_texture_name

        # Assign pushed out tile properties to the extra tile
        self.tile_positions[(10, 10)] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle
        self.tile_list[-1].my_texture_name = pushed_out_texture_name


    def on_draw(self):
        arcade.start_render()
        self.tile_list.draw()
        for button in self.button_list:
            button.draw()

        # Vykreslení hráčů na obrazovku
        #self.players[self.active_player_index].draw()
        for player in self.players:
            player.draw()
        
        # Text
        current_player_color = self.player_colors[self.active_player_index]
        current_color_name = self.player_color_names[current_player_color]
        arcade.draw_text(f"Now plays {current_color_name} player", SCREEN_WIDTH - 2* DISTANCE_BORDER,SCREEN_HEIGHT - 2* DISTANCE_BORDER, arcade.color.WHITE , 20, font_name="Arial")

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

    def on_button_click(self, button_label, x, y):
        if button_label == "Rotate":
            self.transform_tile(self.tile_list[-1])

        if button_label == "←":
            if y in range (225,275):
                self.shift_grid("row", 2, "right")
            elif y in range (425,475):
                self.shift_grid("row", 4, "right")
            elif y in range (625,675):
                self.shift_grid("row", 6, "right")
        elif button_label == "→":
            if y in range (225,275):
                self.shift_grid("row", 2, "left")
            elif y in range (425,475):
                self.shift_grid("row", 4, "left")
            elif y in range (625,675):
                self.shift_grid("row", 6, "left")
        elif button_label == "↑":
            if x in range (225,275):
                self.shift_grid("column", 2, "down")
            elif x in range (425,475):
                self.shift_grid("column", 4, "down")
            elif x in range (625,675):
                self.shift_grid("column", 6, "down")
        elif button_label == "↓":
            if x in range (225,275):
                self.shift_grid("column", 2, "up")
            elif x in range (425,475):
                self.shift_grid("column", 4, "up")
            elif x in range (625,675):
                self.shift_grid("column", 6, "up")
            
    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.button_list:
            btn.check_mouse_press(x, y)

if __name__ == "__main__":
    window = MyGame()
    window.setup()
    arcade.run()

"""DODĚLAT PŘI ŠOUPÁNÍ POHYB HRÁČŮ S KARTOU, STATICKÁ POLE, ODMĚNY NEJSPÍŠ UDĚLAT VE STYLU 1-24 A SBÍRAT, CELKOVÉ GUI
    ODMĚNY NEJSPÍŠ ZPŮSOBEM NAHRÁT DALŠÍ DÍLY, PAK UDĚLAT NĚJAKOU LOGIKU, JAKOŽE DÍL 1-10 JSOU ZATÁČKY, PODLE TOHO ATRIBUTY,...
    GENERACE POKLADŮ """
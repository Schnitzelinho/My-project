import tkinter as tk
from tkinter import messagebox
import arcade, random

import arcade.color

"""KONSTANTY"""
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Labyrinth"
MOVEMENT_SPEED = 100    #Pohyb o jeden díl
TILE_SIZE = 100         #Velikost dílu
GRID_SIZE = 7           #Počet sloupců a řádků
DISTANCE_BORDER = 150   #Vzdálenost středu karty od hranice pole
STARTING_POSITIONS = [
    (DISTANCE_BORDER, DISTANCE_BORDER),
    (DISTANCE_BORDER, SCREEN_HEIGHT - DISTANCE_BORDER),
    (SCREEN_WIDTH - DISTANCE_BORDER - 400, SCREEN_HEIGHT - DISTANCE_BORDER), 
    (SCREEN_WIDTH - DISTANCE_BORDER - 400, DISTANCE_BORDER)  
]   # RED, BLUE, GREEN, YELLOW
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
                ]                               # Jejich souřadnice
STATIC_TEXTURES = ["labkarta_0red.png", "labkarta_s2.png", "labkarta_s3.png", "labkarta_0yellow.png",
                "labkarta_s5.png", "labkarta_s6.png", "labkarta_s7.png", "labkarta_s8.png",
                "labkarta_s9.png", "labkarta_s10.png", "labkarta_s11.png", "labkarta_s12.png",
                "labkarta_0blue.png", "labkarta_s14.png", "labkarta_s15.png", "labkarta_0green.png"
                ]                               # Jejich vzhledy
TEXTURES_CURVE = ["kartalabvzor1.png", "labkarta_0red.png", "labkarta_0blue.png", "labkarta_0yellow.png", "labkarta_0green.png", "labkarta7.png", "labkarta8.png", "labkarta9.png", "labkarta10.png", "labkarta11.png", "labkarta12.png" ]  # Všechny zatáčky
NO_TREASURE_TEXTURES = ["kartalabvzor1.png","kartalabvzor2.png", "labkarta_0red.png", "labkarta_0yellow.png", "labkarta_0blue.png", "labkarta_0green.png"]  # Všechny bez pokladu
PLAYER_IMAGES = ["player_red.png","player_blue.png","player_green.png","player_yellow.png"]
 
class TextButton():         # Třída tlačítka s textem
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
        arcade.set_background_color(arcade.color.COBALT)    #nebo NAVY_BLUE?
 
        #Držení spritů (zákl. grafické jednotky), atd.
        self.tile_list = arcade.SpriteList()
        self.players = []       
        self.active_player_index = 0
        self.has_shifted = False
        self.game_over = False
        self.last_shift = None
        self.tile_positions = {}
        self.button_list = []
        self.treasures = {} #dictionary s poklady
        self.current_treasure_positions = {}
        
        tile_id_counter = 0 #pro přiřazení ID všem pokladům

        # Co aktuální hráč hledá
        self.target_treasure_sprite = arcade.Sprite(scale=1.0)
        self.target_treasure_sprite.center_x = 1150
        self.target_treasure_sprite.center_y = 750

        # Vložení všech možných textur s četností
        self.tile_textures = (
            ["kartalabvzor1.png"] * 10 +
            ["kartalabvzor2.png"] * 12 +
            ["labkarta1.png","labkarta2.png","labkarta3.png","labkarta4.png","labkarta5.png","labkarta6.png","labkarta7.png","labkarta8.png","labkarta9.png","labkarta10.png","labkarta11.png","labkarta12.png"]  # Add more if needed
        )
        random.shuffle(self.tile_textures) # Zamíchání pořadí, aby to nebylo postupné

        """Hráč"""
        # v případě přepsání do češtiny zkontrolovat všude, kde se pracuje s player_color!!!!
        self.player_colors = [arcade.color.RED, arcade.color.BLUE, arcade.color.GREEN, arcade.color.YELLOW]
        self.player_color_names = {
            arcade.color.RED: "Red",
            arcade.color.GREEN: "Green",
            arcade.color.BLUE: "Blue",
            arcade.color.YELLOW: "Yellow"
        }
        for i in range(4):
            player_sprite = arcade.Sprite(PLAYER_IMAGES[i],0.95)
            player_sprite.center_x, player_sprite.center_y = STARTING_POSITIONS[i] 
            player_sprite.alpha = 255 # Průhlednost (100% neprůhledné)
            self.players.append(player_sprite)
        
        """Herní deska"""
        for row in range(GRID_SIZE):    # Pro každý díl z plánu
            for col in range(GRID_SIZE):    
                center_x = DISTANCE_BORDER + col * TILE_SIZE        #střed dílu = vzdálenost od hrany + číslo sloupce * velikost dílu (150+1*100 = 250)
                center_y = DISTANCE_BORDER + row * TILE_SIZE

                tile = arcade.Sprite(None, 1)
                tile.center_x = center_x
                tile.center_y = center_y
            
                if (row, col) in STATIC_CORDS:  # Neměnné díly
                    index = STATIC_CORDS.index((row, col))
                    texture = STATIC_TEXTURES[index]
                    angle = STATIC_ANGLES[index]

                    # Načti náležitou texturu a úhel
                    tile.texture = arcade.load_texture(texture)
                    tile.angle = angle
                    
                else:   # Je pohyblivá
                    texture = self.tile_textures.pop()  # Získá a odstraní vybranou texturu
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
                
                if texture not in NO_TREASURE_TEXTURES: # Pokud má texturu
                    tile_id_counter += 1
                    if tile_id_counter > 9: #jen aby to bylo seřazené (11 vnímáno před 9 ale irelevantní pro fčnost)
                        tile.id = f"treasure_{tile_id_counter}"
                    else:
                        tile.id = f"treasure_0{tile_id_counter}"
                    self.treasures[tile.id] = texture
                else:
                    tile.id = None
                
                #Přiřazení vlastností ke každému dílu do slovníku
                self.tile_positions[(col, row)] = {
                    "name": name,
                    "angle": tile.angle,
                    "move_right": move_right,
                    "move_down": move_down,
                    "move_up": move_up,
                    "move_left": move_left,
                }
            
                self.tile_list.append(tile)

        # Vytvoření extra_tile
        self.extra_tile = None
        self.extra_tile = self.create_extra_tile()
        self.tile_positions[(10, 2)] = self.extra_tile

        # Prvotní spuštění fcí (získání souřadnic všech pokladů, přiřazení hráčům)
        self.get_treasure_coords()
        self.treasure_goal()    

        # tkinter na messagebox
        self.root = tk.Tk()
        self.root.withdraw()  # Skryje hlavní okno tkinter

    def transform_tile(self, tile):     # K otočení extra_tile pomocí tlačítka
        tile.angle -= 90
        if tile.angle < 0:
            tile.angle = 270
        
        texture = tile.my_texture_name
        move_right = move_left = move_down = move_up = False

        # Přiřazení pohybových vlastností na základě textury, upraveno protože změněn úhel
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

        # Upravení (jen změněných) vlastností na extra tile
        self.tile_positions[(10, 2)] = {
            "name": name,
            "angle": tile.angle,
            "move_right": move_right,
            "move_down": move_down,
            "move_up": move_up,
            "move_left": move_left
        }
        
        return tile

    def create_extra_tile(self):   # Inicializace extra dílu, prakticky stejné jako ostatní díly
        texture = self.tile_textures.pop()
        angle = random.choice([0, 90, 180, 270])

        # Vytvoření spritu
        extra_tile = arcade.Sprite(texture, 1)
        extra_tile.angle = angle
        extra_tile.center_x = SCREEN_WIDTH - DISTANCE_BORDER
        extra_tile.center_y = SCREEN_HEIGHT //2 - 10
        
        # Přiřazení vlastností
        move_right = move_left = move_down = move_up = False

        if texture not in NO_TREASURE_TEXTURES:
            tile_id = 24 # Musí být 24, protože chybí poslední
            extra_tile.id = f"treasure_{tile_id}"
            self.treasures[extra_tile.id] = texture
            print(extra_tile.id)
        else:
            extra_tile.id = None

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
        
        
        # Přidání k ostatním dílům
        self.tile_list.append(extra_tile)

        return {
            "name": name,
            "angle": angle,
            "move_right": move_right,
            "move_down": move_down,
            "move_up": move_up,
            "move_left": move_left,
            }
    
    def get_treasure_coords(self):      # Získávání souřadnic texturám s pokladem
        for tile in self.tile_list:
            if tile.id is not None:         # Pokud je tile.id nějaký z pokladů
                texture = self.treasures[tile.id]
                treasure_coords = ((tile.center_x - DISTANCE_BORDER)//TILE_SIZE,(tile.center_y - DISTANCE_BORDER)//TILE_SIZE)
                self.current_treasure_positions[tile.id] ={
                    "texture": texture,
                    "position": treasure_coords
                }

    def treasure_goal(self):
        """Vygenerování seznamu pokladů pro každého hráče, jen při spuštění"""
        self.player_treasures_dict = {}
        first_current_treasure_positions = self.current_treasure_positions  # prvotní stav pokladů, pro kontrolu
        for player in range(len(self.players)):
            current_player_color = self.player_colors[player]
            current_color_name = self.player_color_names[current_player_color]
            player_name = f"Player {current_color_name}"
            self.player_treasures_dict[player_name] = []
            counter = 0
            while counter < 1:  # přiřazení 6 pokladů každému hráči
                counter += 1
                treasure_name = random.choice(list(first_current_treasure_positions))
                treasure = first_current_treasure_positions.pop(treasure_name)
                print(treasure)
                self.player_treasures_dict[player_name].append(treasure)
    
    def update_treasure_position(self):
        # Updatování vlastností pokladů při posunu deskou
        if self.player_treasures_dict:  # teoreticky by neměla nastat situace, kdy neexistuje
            # Každý hráč
            for player in range(len(self.players)):
                current_player_color = self.player_colors[player]
                current_color_name = self.player_color_names[current_player_color]
                player_name = f"Player {current_color_name}"
                treasures = self.player_treasures_dict[player_name]
                for index, treasure in enumerate(treasures):    # index = pozice v listu, treasure = jednotlivý poklad
                    texture = treasure["texture"]
                    for treasure_id, treasure_info in self.current_treasure_positions.items():  # treasure_id = index pokladu (treasure_24...), treasure_info = položka v seznamu
                        if treasure_info["texture"] == texture: # Pokud jsou shodné
                            new_position = treasure_info["position"]    # přendání na nové souřadnice
                            self.player_treasures_dict[player_name][index]["position"] = new_position
                            print(f"Updated {treasure_id} for {player_name} to new position: {new_position}")   # pro kontrolu
                            break  # Nemusím dál hledat

    def update_target_treasure(self):
        """Změnění textury, aby bylo vidět v programu, co se hledá"""
        # Jméno aktuálního hráče
        current_player_color = self.player_colors[self.active_player_index]
        current_color_name = self.player_color_names[current_player_color]
        player_name = f"Player {current_color_name}"

        # Jeho seznam pokladů
        player_treasures = self.player_treasures_dict[player_name]

        # Kontrola, jestli má ještě co sbírat
        if player_treasures:
            treasure_texture = player_treasures[0]["texture"]   # hledaná textura
            self.target_treasure_sprite.texture = arcade.load_texture(treasure_texture) # náležité updatování spritu
            self.target_treasure_sprite.angle = 0 # úhel není důležitý
        else:   # má sebráno vše, musí dojít domů
            if current_color_name == "Red":
                self.target_treasure_sprite.texture = arcade.load_texture("labkarta_0red.png")
                self.target_treasure_sprite.angle = 90
            elif current_color_name == "Blue":
                self.target_treasure_sprite.texture = arcade.load_texture("labkarta_0blue.png")
                self.target_treasure_sprite.angle = 0
            elif current_color_name == "Green":
                self.target_treasure_sprite.texture = arcade.load_texture("labkarta_0green.png")
                self.target_treasure_sprite.angle = 270              
            elif current_color_name == "Yellow":
                self.target_treasure_sprite.texture = arcade.load_texture("labkarta_0yellow.png")
                self.target_treasure_sprite.angle = 180
    
    def setup(self):
        """Tvoření tlačítek,..."""
        # Tlačítko na otočení extra karty
        button_rotate = TextButton(1150,SCREEN_HEIGHT // 2 - 85 , 100,25," ", self.on_button_click)
        self.button_list.append(button_rotate)
        button_nextplayer = TextButton(1150, 650, 130 , 40, "  ", self.on_button_click)
        self.button_list.append(button_nextplayer)
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


        self.update_target_treasure()   # aby již při prvním kole hráč věděl, co sbírat

    def get_player_grid_position(self, player): 
        """Získání souřadnic hráče"""
        grid_x = int((player.center_x - DISTANCE_BORDER) // TILE_SIZE)
        grid_y = int((player.center_y - DISTANCE_BORDER) // TILE_SIZE)
        return grid_x, grid_y

    def check_for_treasure(self):
        """Jestli hráč stojí na hledaném pokladu"""
        # Aktuální hráč
        active_player = self.players[self.active_player_index]
        grid_x, grid_y = self.get_player_grid_position(active_player)   # jeho souřadnice
        current_player_color = self.player_colors[self.active_player_index]
        current_color_name = self.player_color_names[current_player_color]
        player_name = f"Player {current_color_name}"
        if current_color_name == "Red":
            barva_hrace = "červený"
        elif current_color_name == "Blue":
            barva_hrace = "modrý"
        elif current_color_name == "Green":
            barva_hrace = "zelený"
        else:
            barva_hrace = "žlutý"

        # Jeho seznam pokladů
        player_treasures = self.player_treasures_dict[player_name]

        # Kontrola, jestli stojí na pokladu
        if player_treasures:    # Pokud seznam není prázdný
            searched_treasure = player_treasures[0]  # Hledaný poklad je na nulté pozici v seznamu
            treasure_position = searched_treasure["position"]

            # Jestli jsou souřadnice stejné
            if (grid_x, grid_y) == treasure_position:
                print("Treasure Collected!")
                # Odeber poklad se seznamu
                self.player_treasures_dict[player_name].pop(0)
            else:
                print("No treasure at the current position.")
        
        else: # Má sebrány všechny poklady
            starting_position = STARTING_POSITIONS[self.active_player_index]
            if (active_player.center_x, active_player.center_y) == starting_position:
                print(f"{player_name} won!")

                # Vytvoření a zobrazení vyskakovacího okna s "Konec hry"
                root = tk.Tk()
                root.withdraw()  # Skryje hlavní okno tkinter
                messagebox.showinfo("Konec hry", f"{barva_hrace} hráč vyhrál!")
                root.destroy()  # Ukončí tkinter po zavření okna
                self.game_over = True
            else:
                print("Player must return to starting position")

    def update_player_opacity(self):
        """Zprůhlednění neaktivních hráčů, aby bylo vidět, na čem stojí"""
        for i, player in enumerate(self.players):
            if i == self.active_player_index:
                player.alpha = 255  # Neprůhledné
            else:
                player.alpha = 170  # Cca napůl průhledné

    def show_invalid_shift_message(self, entity, index, attempted_direction, last_direction):
        """Zobrazení upozornění na neplatný tah s detaily tahu"""
        message = (
            f"Nemůžete posunout {entity} {index} směrem {attempted_direction}, protože byl právě posunut směrem {last_direction}."
        )
        messagebox.showwarning("Neplatný tah", message)

    def shift_grid(self, entity, index, direction): #entity = row/column; index číslo řádku/sloupce, direction up/down/left/right
        """Posun hrací deskou"""
        if self.game_over:  # Zkontrolujte, zda je hra ukončena
            print("Game over. No more playing.")
            return
        
        if self.last_shift:     # Pokud to není první, jinak neexistuje žádná podmínka
            last_entity, last_index, last_direction = self.last_shift

            # Zabránění hráči aby táhl proti předchozímu tahu
            if entity == last_entity and index == last_index: #pokud je to row a row, 2 a 2
                if (last_direction == "right" and direction == "left") or (last_direction == "left" and direction == "right"): # pokud je směr doprava a doleva nebo obráceně
                    print(f"Cannot shift {entity} {index} to the {direction}, it was just shifted to the {last_direction}.")
                    if last_direction == "right":
                        self.show_invalid_shift_message(entity="řádek", index=index,attempted_direction= "doprava", last_direction= "doleva" )
                    else:
                        self.show_invalid_shift_message(entity="řádek", index=index,attempted_direction= "doleva", last_direction= "doprava" )
                    return # pokud ano, okamžitě ukonči shift_grid
                if (last_direction == "up" and direction == "down") or (last_direction == "down" and direction == "up"):        # pokud je směr nahoru a dolů nebo obráceně
                    print(f"Cannot shift {entity} {index} to the {direction}, it was just shifted to the {last_direction}.")
                    if last_direction == "up":
                        self.show_invalid_shift_message(entity = "sloupec", index = index,attempted_direction= "nahoru", last_direction= "dolů" )
                    else:
                        self.show_invalid_shift_message(entity = "sloupec", index = index,attempted_direction= "dolů", last_direction= "nahoru" )
                    return

        if entity == "row":
            """Aktualizace při pohybu s řadou"""
            row = index - 1 #Odečtení kvůli indexování (souřadnice (2,2) v py == (1,1)...)
            if direction == "right": #Zprava
                self.shift_row_from_right(row)
            elif direction == "left": #Zleva
                self.shift_row_from_left(row)

            # Kontrola pohybu hráče s dílem
            for player in self.players:
                player_grid_x, player_grid_y = self.get_player_grid_position(player)
                if player_grid_y == row: # Pokud je hráč v řadě
                    if direction == "right":
                        # Jestliže se hýbalo zprava
                        if player.center_x == DISTANCE_BORDER:  # Je na levém kraji → přesun na pravý kraj
                            player.center_x = DISTANCE_BORDER + (GRID_SIZE -1) * TILE_SIZE
                            print(player.center_x)
                        else:
                            player.center_x -= TILE_SIZE  # Jinak jen posun o díl doleva
                    elif direction == "left":
                        # Jestliže se hýbalo zleva
                        if player.center_x == DISTANCE_BORDER + (GRID_SIZE -1) * TILE_SIZE :  # Na pravém kraji
                            player.center_x = DISTANCE_BORDER  # Dej ho na druhou stranu
                        else:
                            player.center_x += TILE_SIZE  # Move left
                else:
                    pass

        elif entity == "column":
            """Aktualizace při pohybu se sloupcem"""
            col = index - 1
            if direction == "down":
                self.shift_column_from_down(col)
            elif direction == "up":
                self.shift_column_from_up(col)
            
            # Kontrola pohybu hráče s dílem
            for player in self.players:
                player_grid_x, player_grid_y = self.get_player_grid_position(player)
                if player_grid_x == col:  # Hráč je v šoupnutém sloupci
                    if direction == "down":
                        # Zdola
                        if player.center_y == DISTANCE_BORDER  + (GRID_SIZE - 1) * TILE_SIZE:  # Pokud je na horním, dej ho dolů
                            player.center_y = DISTANCE_BORDER
                        else:
                            player.center_y += TILE_SIZE  # Jinak popojde nahoru
                    elif direction == "up":
                        # Shora
                        if player.center_y == DISTANCE_BORDER:  # Je na dolním, dej ho nahoru
                            player.center_y = DISTANCE_BORDER + (GRID_SIZE - 1) * TILE_SIZE 
                        else:
                            player.center_y -= TILE_SIZE  # Jinak jdi dolů
        
        self.last_shift = (entity, index, direction) # Uložení čím se hýbalo pro dalšího hráče (sloupec,5,dolů)
        self.has_shifted = True     # Posunul → může jít
        self.get_treasure_coords()  # Aktualizace pozic pokladů
        self.update_treasure_position()
            
    def shift_row_from_right(self, row_index):   # Pro shift z nějakého důvodu nefunguje třeba extra_tile_sprite.texture,...        
        """Šoupání zprava, mění se pouze sloupec, [T1, T2, T3, T4, T5, T6, T7] → [T2, T3, T4, T5, T6, T7, extra_tile]"""
        extra_tile_properties = self.tile_positions[(10, 2)].copy()  # Kopírování extra tile properties
        extra_tile_sprite = self.tile_list[-1]

        # Kopírování vlastností levého dílu
        pushed_out_tile_properties = self.tile_positions[(0, row_index)].copy()
        pushed_out_tile_sprite = self.tile_list[row_index * GRID_SIZE]
        pushed_out_texture = self.tile_list[row_index * GRID_SIZE].texture
        pushed_out_angle = self.tile_list[row_index * GRID_SIZE].angle
        pushed_out_texture_name = self.tile_list[row_index * GRID_SIZE].my_texture_name
        pushed_out_id = getattr(pushed_out_tile_sprite, "id", None)

        
        # Posun všech doprava
        for col in range(GRID_SIZE):
            current_position = (col, row_index)
            right_position = (col + 1, row_index)

            current_tile_sprite = self.tile_list[col + row_index * GRID_SIZE]

            if right_position in self.tile_positions:  # Pokud je pravá pozice v poli
                # Kopírování vlastností z pravé na aktuální
                self.tile_positions[current_position] = self.tile_positions[right_position]

                right_tile_sprite = self.tile_list[col + 1 + row_index * GRID_SIZE]
                self.tile_list[col + row_index * GRID_SIZE].texture = self.tile_list[col + 1 + row_index * GRID_SIZE].texture
                self.tile_list[col + row_index * GRID_SIZE].angle = self.tile_list[col + 1 + row_index * GRID_SIZE].angle
                self.tile_list[col + row_index * GRID_SIZE].my_texture_name = self.tile_list[col + 1 + row_index * GRID_SIZE].my_texture_name
                
                if right_tile_sprite.id is not None:
                    current_tile_sprite.id = right_tile_sprite.id
                    print(f"V řádku: {right_tile_sprite.id}")
                    right_tile_sprite.id = None
                
                else:
                    current_tile_sprite.id = None
                    
            else:
                # Jinak přiřaď extra tile
                self.tile_positions[current_position] = extra_tile_properties

                self.tile_list[col + row_index * GRID_SIZE].texture = self.tile_list[-1].texture
                self.tile_list[col + row_index * GRID_SIZE].angle = extra_tile_properties["angle"]
                self.tile_list[col + row_index * GRID_SIZE].my_texture_name = self.tile_list[-1].my_texture_name

                if extra_tile_sprite.id is not None:
                    current_tile_sprite.id = extra_tile_sprite.id
                    print(f"Extra:{extra_tile_sprite.id}")     # v terminálu bude odpovídat předchozímu, jelikož to je před celou aktualizací pozic
                    extra_tile_sprite.id = None
                else:
                    current_tile_sprite.id = None
                    


        # Vezme vlastnosti první a dá je do extra tile (ještě nepřepsané)
        self.tile_positions[(10, 2)] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle
        self.tile_list[-1].my_texture_name = pushed_out_texture_name

        extra_tile_sprite.id = pushed_out_id

    def shift_row_from_left(self, row_index):
        """Šoupání zleva, mění se pouze sloupec, [T1, T2, T3, T4, T5, T6, T7] → [extra_tile, T1, T2, T3, T4, T5, T6] """
        extra_tile_properties = self.tile_positions[(10, 2)].copy()
        extra_tile_sprite = self.tile_list[-1]

        # Kopíruj vlastnosti krajní pravé karty
        pushed_out_tile_properties = self.tile_positions[(6, row_index)].copy()
        pushed_out_tile_sprite = self.tile_list[6 + row_index*GRID_SIZE]
        pushed_out_texture = self.tile_list[6 + row_index * GRID_SIZE].texture
        pushed_out_angle = self.tile_list[6 + row_index * GRID_SIZE].angle
        pushed_out_texture_name = self.tile_list[6 + row_index * GRID_SIZE].my_texture_name
        pushed_out_id = getattr(pushed_out_tile_sprite, "id", None)

        # Posune všechny vpravo
        for col in range(6, -1, -1):  # Začni kopírovat zprava
            current_position = (col, row_index)
            left_position = (col - 1, row_index)

            current_tile_sprite = self.tile_list[col + row_index * GRID_SIZE]
            
            if left_position in self.tile_positions:
                # Kopíruj z levé na aktuální
                self.tile_positions[current_position] = self.tile_positions[left_position]

                left_tile_sprite = self.tile_list[col - 1 + row_index * GRID_SIZE]
                self.tile_list[col + row_index * GRID_SIZE].texture = self.tile_list[col - 1 + row_index * GRID_SIZE].texture
                self.tile_list[col + row_index * GRID_SIZE].angle = self.tile_list[col - 1 + row_index * GRID_SIZE].angle
                self.tile_list[col + row_index * GRID_SIZE].my_texture_name = self.tile_list[col - 1 + row_index * GRID_SIZE].my_texture_name

                if left_tile_sprite.id is not None:
                    current_tile_sprite.id = left_tile_sprite.id
                    print(f"V řádku: {left_tile_sprite.id}")
                    left_tile_sprite.id = None
                else:
                    current_tile_sprite.id = None
            else:
                # Dej vlastnosti extra_tile té nejvíce vlevo
                self.tile_positions[current_position] = extra_tile_properties

                self.tile_list[col + row_index * GRID_SIZE].texture = self.tile_list[-1].texture
                self.tile_list[col + row_index * GRID_SIZE].angle = extra_tile_properties["angle"]
                self.tile_list[col + row_index * GRID_SIZE].my_texture_name = self.tile_list[-1].my_texture_name

                if extra_tile_sprite.id is not None:
                    current_tile_sprite.id = extra_tile_sprite.id
                    print(f"Extra:{extra_tile_sprite.id}")
                    extra_tile_sprite.id = None
                else:
                    current_tile_sprite.id = None

        # Dej vlasnosti extra_tile vysunuté kartě
        self.tile_positions[(10, 2)] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle
        self.tile_list[-1].my_texture_name = pushed_out_texture_name
        
        extra_tile_sprite.id = pushed_out_id

    def shift_column_from_up(self, col_index):           
        """Šoupání zhora, mění se pouze řádek, [T1, T2, T3, T4, T5, T6, T7] → [extra_tile, T1, T2, T3, T4, T5, T6]  """
        extra_tile_properties = self.tile_positions[(10, 2)].copy()
        extra_tile_sprite = self.tile_list[-1]

        # Vem vlastnosti nejspodnější karty
        pushed_out_tile_properties = self.tile_positions[(col_index, 0)].copy()
        pushed_out_tile_sprite = self.tile_list[col_index]
        pushed_out_texture = self.tile_list[col_index].texture
        pushed_out_angle = self.tile_list[col_index].angle
        pushed_out_texture_name = self.tile_list[col_index].my_texture_name
        pushed_out_id = getattr(pushed_out_tile_sprite, "id", None)


        # Posuň všechny nahoru
        for row in range(GRID_SIZE):
            current_position = (col_index, row)
            above_position = (col_index, row + 1)

            current_tile_sprite = self.tile_list[col_index + row * GRID_SIZE]
            if above_position in self.tile_positions:
                # Přidej vlastnosti z karty nad
                self.tile_positions[current_position] = self.tile_positions[above_position]
                
                above_tile_sprite = self.tile_list[col_index + (row + 1) * GRID_SIZE]
                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[(row + 1) * GRID_SIZE + col_index].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = self.tile_list[(row + 1) * GRID_SIZE + col_index].angle
                self.tile_list[row * GRID_SIZE + col_index].my_texture_name = self.tile_list[(row + 1) * GRID_SIZE + col_index].my_texture_name

                if above_tile_sprite.id is not None:
                    current_tile_sprite.id = above_tile_sprite.id
                    #print(f"Ve sloupci: {above_tile_sprite.id}")     # v terminálu bude odpovídat předchozímu, jelikož to je před celou aktualizací pozic
                    above_tile_sprite.id = None
                else:
                    current_tile_sprite.id = None                    
            else:
                # Přidej vlastnosti extra_tile
                self.tile_positions[current_position] = extra_tile_properties

                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[-1].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = extra_tile_properties["angle"]
                self.tile_list[row * GRID_SIZE + col_index].my_texture_name = self.tile_list[-1].my_texture_name

                if extra_tile_sprite.id is not None:
                    current_tile_sprite.id = extra_tile_sprite.id
                    #print(f"Extra:{extra_tile_sprite.id}")     # v terminálu bude odpovídat předchozímu, jelikož to je před celou aktualizací pozic
                    extra_tile_sprite.id = None
                else:
                    current_tile_sprite.id = None

        # Přidej vlastnosti extra_tile vysunuté
        self.tile_positions[(10, 2)] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle
        self.tile_list[-1].my_texture_name = pushed_out_texture_name


        extra_tile_sprite.id = pushed_out_id
     
    def shift_column_from_down(self, col_index):           
        """Šoupání zespoda, mění se pouze řádek, [T1, T2, T3, T4, T5, T6, T7] → [T2, T3, T4, T5, T6, T7, extra_tile]  """
        extra_tile_properties = self.tile_positions[(10, 2)].copy()
        extra_tile_sprite = self.tile_list[-1]

        # Kopíruj vlastnosti nejhornější karty
        pushed_out_tile_properties = self.tile_positions[(col_index, 6)].copy()
        pushed_out_tile_sprite = self.tile_list[col_index + (GRID_SIZE - 1)*GRID_SIZE]
        pushed_out_texture = self.tile_list[col_index + (GRID_SIZE - 1) * GRID_SIZE].texture
        pushed_out_angle = self.tile_list[col_index + (GRID_SIZE - 1) * GRID_SIZE].angle
        pushed_out_texture_name = self.tile_list[col_index + (GRID_SIZE - 1) * GRID_SIZE].my_texture_name
        pushed_out_id = getattr(pushed_out_tile_sprite, "id", None)

        # Šoupni všechny dolů
        for row in range(6, -1, -1):
            current_position = (col_index, row)
            below_position = (col_index, row - 1)

            current_tile_sprite = self.tile_list[row * GRID_SIZE + col_index]
            if below_position in self.tile_positions:
                # Kopíruj vlastnosti spodní
                self.tile_positions[current_position] = self.tile_positions[below_position]

                below_tile_sprite = self.tile_list[(row - 1) * GRID_SIZE + col_index]
                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[(row - 1) * GRID_SIZE + col_index].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = self.tile_list[(row - 1) * GRID_SIZE + col_index].angle
                self.tile_list[row * GRID_SIZE + col_index].my_texture_name = self.tile_list[(row - 1) * GRID_SIZE + col_index].my_texture_name

                if below_tile_sprite.id is not None:
                    current_tile_sprite.id = below_tile_sprite.id
                    #print(f"Ve sloupci: {below_tile_sprite.id}")     # v terminálu bude odpovídat předchozímu, jelikož to je před celou aktualizací pozic
                    below_tile_sprite.id = None
                else:
                    current_tile_sprite.id = None
            else:
                # Předej vlastnosti extra_tile
                self.tile_positions[current_position] = extra_tile_properties

                self.tile_list[row * GRID_SIZE + col_index].texture = self.tile_list[-1].texture
                self.tile_list[row * GRID_SIZE + col_index].angle = extra_tile_properties["angle"]
                self.tile_list[row * GRID_SIZE + col_index].my_texture_name = self.tile_list[-1].my_texture_name

                if extra_tile_sprite.id is not None:
                    current_tile_sprite.id = extra_tile_sprite.id
                    print(f"Extra:{extra_tile_sprite.id}")     # v terminálu bude odpovídat předchozímu, jelikož to je před celou aktualizací pozic
                    extra_tile_sprite.id = None
                else:
                    current_tile_sprite.id = None

        # Vlastnosti vysunuté předej extra_tile
        self.tile_positions[(10, 2)] = pushed_out_tile_properties
        self.tile_list[-1].texture = pushed_out_texture
        self.tile_list[-1].angle = pushed_out_angle
        self.tile_list[-1].my_texture_name = pushed_out_texture_name
        
        extra_tile_sprite.id = pushed_out_id


    def on_draw(self):
        arcade.start_render()
        arcade.draw_rectangle_filled(1100, 450, 350, 850, arcade.color.GRAY)
        self.tile_list.draw()
        
        for button in self.button_list:
            button.draw()

        # Vykreslení všech hráčů a aktivního hráče na závěr, takže se zobrazí nad ostatními
        active_player = self.players[self.active_player_index]
        other_players = [player for i, player in enumerate(self.players) if i != self.active_player_index]  # všichni kdo nejsou na indexu active_player_index
        for player in other_players:
            player.draw()
        active_player.draw()
    
        # Hledaná karta
        self.target_treasure_sprite.draw()

        # Text, kdo hraje
        current_player_color = self.player_colors[self.active_player_index]
        current_color_name = self.player_color_names[current_player_color]
        if current_color_name == "Red":
            barva_hrace = "červený"
        elif current_color_name == "Blue":
            barva_hrace = "modrý"
        elif current_color_name == "Green":
            barva_hrace = "zelený"
        else:
            barva_hrace = "žlutý"

        arcade.draw_text(f"Na řadě je {barva_hrace} hráč",950,825, current_player_color , 20, font_name="Impact")
        arcade.draw_text("Hledaný cíl:",950,775, arcade.color.BLACK, 14, font_name="Arial")
        arcade.draw_text("Sebráno:",950,730, arcade.color.BLACK, 14, font_name="Arial")
       
        #zbývá pokladů
        player_name = f"Player {current_color_name}"
        player_treasures_left = 6 - len(self.player_treasures_dict[player_name])
        arcade.draw_text(f"{player_treasures_left} / 6",960,705, arcade.color.BLACK, 14, font_name="Arial")
        
        # Další hráč text
        arcade.draw_text("DALŠÍ HRÁČ", 1088,639, arcade.color.BLACK,20, font_name="Impact")
        # Herní statistiky
        arcade.draw_text("Herní statistiky",950,570, arcade.color.BLACK, 20, font_name="Impact")
        ## Červený
        red_player_color = self.player_colors[0]
        red_player_color_name = self.player_color_names[red_player_color]
        arcade.draw_text("Hráč 1",950,540,red_player_color, 14, font_name="Arial")
        red_player_name = f"Player {red_player_color_name}"
        red_treasures_left = 6 - len(self.player_treasures_dict[red_player_name])
        arcade.draw_text(f"{red_treasures_left} / 6",960,515, arcade.color.BLACK, 14, font_name="Arial")
        ## Modrý
        blue_player_color = self.player_colors[1]
        blue_player_color_name = self.player_color_names[blue_player_color]
        arcade.draw_text("Hráč 2",1025,540,blue_player_color, 14, font_name="Arial")
        blue_player_name = f"Player {blue_player_color_name}"
        blue_treasures_left = 6 - len(self.player_treasures_dict[blue_player_name])
        arcade.draw_text(f"{blue_treasures_left} / 6",1035,515, arcade.color.BLACK, 14, font_name="Arial")
        ## Zelený
        green_player_color = self.player_colors[2]
        green_player_color_name = self.player_color_names[green_player_color]
        arcade.draw_text("Hráč 3",1100,540,green_player_color, 14, font_name="Arial")
        green_player_name = f"Player {green_player_color_name}"
        green_treasures_left = 6 - len(self.player_treasures_dict[green_player_name])
        arcade.draw_text(f"{green_treasures_left} / 6",1110,515, arcade.color.BLACK, 14, font_name="Arial")
        ## Žlutý
        yellow_player_color = self.player_colors[3]
        yellow_player_color_name = self.player_color_names[yellow_player_color]
        arcade.draw_text("Hráč 4",1175,540,yellow_player_color, 14, font_name="Arial")
        yellow_player_name = f"Player {yellow_player_color_name}"
        yellow_treasures_left = 6 - len(self.player_treasures_dict[yellow_player_name])
        arcade.draw_text(f"{yellow_treasures_left} / 6",1185,515, arcade.color.BLACK, 14, font_name="Arial")
        
        # Extra díl
        arcade.draw_text("Vysunutá karta:",950,465, arcade.color.BLACK, 14, font_name="Arial")
        arcade.draw_text("ROTUJ",1116,355, arcade.color.BLACK, 20, font_name="Impact")

        # Pravidla
        arcade.draw_text("Pravidla", 950, 305, arcade.color.BLACK, 20, font_name="Impact" )
        arcade.draw_text("CÍL HRY: ",950,275, arcade.color.BLACK, 14, font_name="Arial")
        arcade.draw_text("Posbírej všechny své poklady",960,250, arcade.color.BLACK, 14, font_name="Arial")
        arcade.draw_text("a dostaň se zpět na svůj start.",960,225, arcade.color.BLACK, 14, font_name="Arial")
        arcade.draw_text("OVLÁDÁNÍ: ",950,190, arcade.color.BLACK, 14, font_name="Arial")
        arcade.draw_text("1. Vlož vysunutou kartu šipkami",960,165, arcade.color.BLACK, 14, font_name="Arial")
        arcade.draw_text("2. Jdi pomocí WSAD nebo šipek",960,140, arcade.color.BLACK, 14, font_name="Arial")
        arcade.draw_text("3. Ukonči tah na svém pokladu",960,115, arcade.color.BLACK, 14, font_name="Arial")
        arcade.draw_text("Nelze táhnout proti minulému tahu.",950,70, arcade.color.BLACK, 14, font_name="Arial")
        arcade.draw_text("Poklad sebereš přepnutím hráče.",950,45, arcade.color.BLACK, 14, font_name="Arial")

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
        """Vrací pozici a vlastnosti dílu pod hráčem"""
        active_player = self.players[self.active_player_index]
        grid_x, grid_y = self.get_player_grid_position(active_player)

        tile_position = (grid_x, grid_y)
        return self.tile_positions.get(tile_position)       # z dict s pozicemi vrací konkrétní souřadnice
    
    def get_adjacent_tile(self,current_tile_position, direction):
        if direction == "up":
            adjacent_position = (current_tile_position[0], current_tile_position[1] + 1)
        elif direction == "down":
            adjacent_position = (current_tile_position[0], current_tile_position[1] - 1)
        elif direction == "left":
            adjacent_position = (current_tile_position[0] - 1, current_tile_position[1])
        elif direction == "right":
            adjacent_position = (current_tile_position[0] + 1, current_tile_position[1])
        return self.tile_positions.get(adjacent_position,None)  # none pokud jinde nic není


    def on_key_press(self, key, modifiers):
        active_player = self.players[self.active_player_index]
        tile_under_player = self.get_tile_under_player(active_player)

        if key == arcade.key.P:
            self.get_treasure_coords()

        if self.has_shifted:
            if key == arcade.key.W or key == arcade.key.UP:
                if tile_under_player["move_up"]:      #pokud je move up true (nahoru vede cesta)
                    grid_x = int((active_player.center_x - DISTANCE_BORDER) // TILE_SIZE)
                    grid_y = int((active_player.center_y - DISTANCE_BORDER) // TILE_SIZE)
                    adjacent_tile = self.get_adjacent_tile((grid_x, grid_y), "up")      #získá info o dílu nad
                    if adjacent_tile and adjacent_tile["move_down"]:           # pokud nad ním existuje a vede z ní cesta dolů
                        active_player.center_y += MOVEMENT_SPEED
                    else:
                        print("Cannot move up")
                else:
                    print("Cannot move up")
                
            elif key == arcade.key.S or key == arcade.key.DOWN:
                if tile_under_player["move_down"]:
                    grid_x = int((active_player.center_x - DISTANCE_BORDER) // TILE_SIZE)
                    grid_y = int((active_player.center_y - DISTANCE_BORDER) // TILE_SIZE)
                    adjacent_tile = self.get_adjacent_tile((grid_x, grid_y), "down")
                    if adjacent_tile and adjacent_tile["move_up"]:
                        active_player.center_y -= MOVEMENT_SPEED
                    else:
                        print("Cannot move down")                        
                else:
                    print("Cannot move down")
            elif key == arcade.key.A or key == arcade.key.LEFT:
                if tile_under_player["move_left"]:
                    grid_x = int((active_player.center_x - DISTANCE_BORDER) // TILE_SIZE)
                    grid_y = int((active_player.center_y - DISTANCE_BORDER) // TILE_SIZE)
                    adjacent_tile = self.get_adjacent_tile((grid_x, grid_y), "left")
                    if adjacent_tile and adjacent_tile["move_right"]:
                        active_player.center_x -= MOVEMENT_SPEED
                    else:
                        print("Cannot move left")
                else:
                    print("Cannot move left")

            elif key == arcade.key.D or key == arcade.key.RIGHT:
                if tile_under_player["move_right"]:
                    grid_x = int((active_player.center_x - DISTANCE_BORDER) // TILE_SIZE)
                    grid_y = int((active_player.center_y - DISTANCE_BORDER) // TILE_SIZE)
                    adjacent_tile = self.get_adjacent_tile((grid_x, grid_y), "right")
                    if adjacent_tile and adjacent_tile["move_left"]:
                        active_player.center_x += MOVEMENT_SPEED
                    else:
                        print("Cannot move right")
                else:
                    print("Cannot move right")  
            elif key == arcade.key.ENTER:
                # Konec kola
                self.has_shifted = False
                
                # Kontrola, jestli stojí na hledaném pokladu
                self.check_for_treasure()
                
                # Přepnutí na dalšího hráče
                self.active_player_index = (self.active_player_index + 1) % len(self.players) 
                self.update_target_treasure()
                # Změnění průhlednosti pro lepší viditelnost
                self.update_player_opacity()
                
        else:
            print("Player must shift first")
        
    def on_key_release(self, key, modifiers):
        """ Called whenever the user releases a key. """
        pass

    def on_button_click(self, button_label, x, y):
        if self.game_over:
            print("Game over. No more playing.")
            return
        if button_label == " ":
            self.transform_tile(self.tile_list[-1])
            return  # prevence aby program nepokračoval ve fci (nenastavil has_shifted na true)
        
        if button_label == "  ":
            if self.has_shifted:
                # Konec kola
                self.has_shifted = False
                    
                # Kontrola, jestli stojí na hledaném pokladu
                self.check_for_treasure()
                    
                # Přepnutí na dalšího hráče
                self.active_player_index = (self.active_player_index + 1) % len(self.players) 
                self.update_target_treasure()
                # Změnění průhlednosti pro lepší viditelnost
                self.update_player_opacity()

        if not self.has_shifted:        # pokud hráč ještě nepohnul
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
        else:
            print("Player has already shifted this turn. Move or end turn.")
            
    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.button_list:
            btn.check_mouse_press(x, y)

if __name__ == "__main__":
    window = MyGame()
    window.setup()
    arcade.run()

"""Vytvořit aplikaci"""
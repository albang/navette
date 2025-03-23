import json
import time

import pygame
import random
from pathlib import Path
import logging
logger = logging.getLogger(__name__)
def custom_slice(lst, start, end):
    """
    Fonction qui effectue un slicing intelligent même si start > end.

    :param lst: La liste à slicer
    :param start: Indice de début (peut être négatif)
    :param end: Indice de fin (peut être négatif)
    :return: La sous-liste extraite
    """
    if start < 0:
        return lst[start:]+lst[:end]

    elif end < start:
        return lst[start:]+lst[:end]
    else:
        return lst[start:end]

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')  # Supprime le #
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
buttons_map={
    0:"green",
    1:"green",
    2:"red",
    3:"red",
    4:"yellow",
    5:"yellow",
    6:"blue",
    7:"blue",
    9:"settings",
    10:"settings2",
}

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
speed=25
WIDTH, HEIGHT = 1920, 1080
class Scene:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def render(self, screen):
        pass

#def check_color(btn_id):

# ========================= MENU PRINCIPAL =========================
class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title = game.default_font.render("Départ", True, WHITE)
        self.instructions = game.default_font.render("Appuyez sur ESPACE pour jouer", True, WHITE)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.JOYBUTTONDOWN and (event.button == 0 or event.button == 1):
                self.game.change_scene(PlayerSelectionScene(self.game))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game.change_scene(ChoisisVaisseauScene(self.game))  # Passage à la scène de jeu

    def render(self, screen):
        background = pygame.image.load("imgs/back/back_start.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        green_button = pygame.image.load("imgs/logos/green_button.png")
        green_button = pygame.transform.scale(green_button, (100, 100))
        instructions = self.game.default_font.render("Appuyez sur                pour jouer", True, WHITE)
        screen.blit(background, (0, 0))
        screen.blit(green_button, (935, 835))
        screen.blit(instructions, (int(WIDTH // 2 - instructions.get_width() // 2),int( 900 - instructions.get_height() // 2)))


class GameScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        # Charger l'image de fond
        self.background = pygame.image.load(self.game.current_scene["planet"])
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        # Chargement du hublot
        self.hublot_image = pygame.image.load("./imgs/hublottranparent.png")
        self.hublot_image = pygame.transform.scale(self.hublot_image, (self.game.vaisseau['rayon']*3, self.game.vaisseau['rayon']*3))

        # Création du brou
        # illard
        self.fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.fog.fill((0, 0, 0, 255))

        # Position initiale du faisceau
        self.beam_x, self.beam_y = int(WIDTH // 2), int(HEIGHT // 2)
        self.beam_radius = self.game.vaisseau['rayon']
        self.found = False
        self.first_move=False
        # Position aléatoire de l'objet caché
        self.hidden_x, self.hidden_y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
        self.speed=self.game.vaisseau['vitesse']

        self.sound_to_play = [pygame.mixer.Sound(f'./audio/common/atterrir.ogg')]

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.change_scene(MenuScene(self.game))  # Retour au menu
            elif self.found and  event.type == pygame.JOYBUTTONDOWN and (event.button == 0 or event.button == 1):
                self.game.change_scene(DialogueScene(self.game))
            elif self.found and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game.change_scene(DialogueScene(self.game))
                #  # Retour au menu
    def update(self):
        keys = pygame.key.get_pressed()

        # Déplacement avec les touches fléchées
        if keys[pygame.K_LEFT]:
            self.beam_x -= speed
            self.first_move = True
        if keys[pygame.K_RIGHT]:
            self.beam_x += speed
            self.first_move = True
        if keys[pygame.K_UP]:
            self.beam_y -= speed
            self.first_move = True
        if keys[pygame.K_DOWN]:
            self.beam_y += speed
            self.first_move = True
        if self.game.joystick:
            x_axis = self.game.joystick.get_axis(0)  # Axe X
            y_axis = self.game.joystick.get_axis(1)  # Axe Y

            # Déplacement du faisceau
            if x_axis > 0.008 or x_axis<-0.008:
                self.beam_x += int(x_axis * self.speed)
                self.first_move = True
            if y_axis > 0.008 or y_axis <-0.008:
                self.beam_y += int(y_axis * self.speed)
                self.first_move=True
        # Empêcher le faisceau de sortir de l'écran
        self.beam_x = max(self.beam_radius, min(WIDTH - self.beam_radius, self.beam_x))
        self.beam_y = max(self.beam_radius, min(HEIGHT - self.beam_radius, self.beam_y))

        # Vérification si l'objet est trouvé
        distance = ((self.beam_x - self.hidden_x) ** 2 + (self.beam_y - self.hidden_y) ** 2) ** 0.5
        if distance < self.beam_radius:
            self.found = True


    def render(self, screen):
        if not pygame.mixer.music.get_busy() and len(self.sound_to_play) > 0:
            son = self.sound_to_play.pop()
            son.play()
        screen.blit(self.background, (0, 0))
        stich = pygame.image.load(self.game.current_scene["personage"]["img"])
        stich = pygame.transform.scale(stich, (100, 100))
        screen.blit(stich, (self.hidden_x, self.hidden_y))
        if not self.found:
            pygame.draw.circle(self.fog, (0, 0, 0, 0), (self.beam_x, self.beam_y), self.beam_radius)
            screen.blit(self.fog, (0, 0))

        screen.blit(self.hublot_image, (self.beam_x - (self.game.vaisseau['rayon']*1.5), (self.beam_y - self.game.vaisseau['rayon']*1.5)))
        if not self.first_move:
            back_conv = pygame.image.load("imgs/menu/back_conversation.png")
            screen.blit(back_conv, (int(WIDTH // 2 - back_conv.get_width() // 2), 500))

            for j, ligne in enumerate("Tu viens d'attérrir sur une planète inconnue.|Utilise le hublot de ta fusée pour trouver un extraterrestre".split("|")):
                line_text = self.game.default_font.render(f"{ligne}", True, hex_to_rgb("#9499C3"))

                screen.blit(line_text, (350, 520 + j  * 30))
        if self.found:
            message = self.game.default_font.render("Extraterrestre trouvé !", True, WHITE)
            screen.blit(message, (int(WIDTH // 2 - message.get_width() // 2),int( HEIGHT // 2 - message.get_height() // 2)))

# ========================= SCÈNE DE VICTOIRE =========================
class VictoryScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.message = game.default_font.render("Bravo, tu as trouvé l'objet !", True, hex_to_rgb("#9499C3"))
        self.instructions = game.default_font.render("Appuie sur ENTER pour retourner au menu", True, WHITE)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game.change_scene(DialogueScene(self.game))  # Retour au menu

    def render(self, screen):
        screen.fill(GREEN)
        screen.blit(self.message, (int(WIDTH // 2 - self.message.get_width() // 2),int( HEIGHT // 3)))
        screen.blit(self.instructions, int((WIDTH // 2 - self.instructions.get_width() // 2),int( HEIGHT // 2)))


class PlayerSelectionScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title = game.default_font.render("Départ", True, hex_to_rgb("#9499C3"))
        self.current_player=0

    def handle_events(self, events):
        for event in events:
            #print(event)
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.JOYBUTTONDOWN and (event.button == 0 or event.button == 1):
                print("OK")
                self.game.player_name = self.game.players[self.current_player]
                self.game.change_scene(ValideScene(self.game))
                #self.game.change_scene(DialogueScene(self.game))
            elif event.type == pygame.JOYBUTTONDOWN and (event.button == 2 or event.button == 3):
                self.current_player = (self.current_player - 1) % len(self.game.players)
            elif event.type == pygame.JOYBUTTONDOWN and (event.button == 4 or event.button == 5):
                self.current_player = (self.current_player - 1) % len(self.game.players)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game.change_scene(GameScene(self.game))  # Passage à la scène de jeu

            if event.type == pygame.JOYAXISMOTION:
                y_axis = self.game.joystick.get_axis(1)  # Axe Y (haut/bas)

                if y_axis < -0.5:  # Vers le haut
                    self.current_player = (self.current_player - 1) % len(self.game.players)
                elif y_axis > 0.5:  # Vers le bas
                    self.current_player= (self.current_player+1)%len(self.game.players)
    def render(self, screen):
        background = pygame.image.load("imgs/back/back clean.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))

        start_point=500
        for i, player in enumerate(self.game.players):
            if i == self.current_player:
                player_name = self.game.default_font.render(f"         {player}", True, GREEN)
            else:
                player_name = self.game.default_font.render(f"{player}", True, WHITE)
            screen.blit(player_name, (500,50*i+400))


class ValideScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title = game.default_font.render("êtes vous sur ?", True, hex_to_rgb("#9499C3"))


    def handle_events(self, events):
        for event in events:
            #print(event)
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.JOYBUTTONDOWN and (event.button == 0 or event.button == 1):
                print("OK")
                self.game.change_scene(ChoisisVaisseauScene(self.game))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game.change_scene(GameScene(self.game))  # Passage à la scène de jeu

            if event.type == pygame.JOYAXISMOTION:
                y_axis = self.game.joystick.get_axis(1)  # Axe Y (haut/bas)

                if y_axis < -0.5:  # Vers le haut
                    self.game.current_player = (self.game.current_player - 1) % len(self.game.players)
                elif y_axis > 0.5:  # Vers le bas
                    self.game.current_player= (self.game.current_player+1)%len(self.game.players)
    def render(self, screen):
        background = pygame.image.load("imgs/back/back clean.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        back_conv = pygame.image.load("imgs/menu/back_conversation.png")
        #back_conv = pygame.transform.scale(back_conv, (500, 500))
        screen.blit(back_conv, (int(WIDTH // 2 - back_conv.get_width() // 2), 500))
        player_name = self.game.default_font.render(f"{self.game.player_name}, Choisissez votre fusée et préparez vous !", True, BLACK)
        screen.blit(player_name, (350, 520))

class ChoisisVaisseauScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title = game.default_font.render("êtes vous sur ?", True, hex_to_rgb("#9499C3"))
        self.current_vaisseau = 1
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.JOYBUTTONDOWN and (event.button == 0 or event.button == 1):
                self.game.vaisseau=self.game.vaisseaux[self.current_vaisseau]
                self.game.change_scene(Decollage(self.game))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game.vaisseau=self.game.vaisseaux[self.current_vaisseau]
                self.game.change_scene(Decollage(self.game))
            if event.type == pygame.JOYAXISMOTION:
                y_axis = self.game.joystick.get_axis(1)  # Axe Y (haut/bas)

                if y_axis < -0.5:  # Vers le haut
                    self.current_vaisseau = (self.current_vaisseau - 1) % len(self.game.vaisseaux)
                elif y_axis > 0.5:  # Vers le bas
                    self.current_vaisseau= (self.current_vaisseau+1)%len(self.game.vaisseaux)
    def render(self, screen):
        background = pygame.image.load("imgs/back/back clean.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        for i, vaisseau in enumerate(custom_slice(self.game.vaisseaux,self.current_vaisseau-1,(self.current_vaisseau+2)%len(self.game.vaisseaux))):
            vaisseau_img=pygame.image.load(vaisseau["skin"])
            if i == 1:
                vaisseau_min = pygame.transform.scale(vaisseau_img, (225, 225))
            else:
                vaisseau_min = pygame.transform.scale(vaisseau_img, (150, 150))
            screen.blit(vaisseau_min, (100,100 +(200*i)))
        #player_name = self.game.default_font.render(f"{self.game.player_name}, Choisissez votre fusée et préparez vous !", True, BLACK)
        #screen.blit(player_name, (350, 520))


class DialogueScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title = game.default_font.render("êtes vous sur ?", True, hex_to_rgb("#9499C3"))
        self.already_sayed=1
        self.scene_name="scene_1"
        self.audios = [pygame.mixer.Sound(f'{replique["audio_path"]}') or None for replique in self.game.current_scene["scenes"]]
        logging.debug(self.audios)
        self.sound_to_play = [self.audios[0]]
        self.no_more_audio = False
    def handle_events(self, events):
        for event in events:
            #print(event)
            if event.type == pygame.QUIT:
                self.game.running = False
            elif (event.type == pygame.JOYBUTTONDOWN and (event.button == 0 or event.button == 1)) or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                print("OK")
                logger.debug(f"déja _dis{self.already_sayed} longueur audio {len(self.audios)}")
                if len(self.audios)>self.already_sayed:
                    self.sound_to_play.append(self.audios[self.already_sayed])
                else:
                    self.no_more_audio=True
                    self.game.change_scene(redecollage_planete(self.game))
                self.already_sayed += 1

            #elif event.type == pygame.JOYBUTTONDOWN and (event.button == 2 or event.button == 3):
            #    self.game.change_mission()
    def render(self, screen):
        background = pygame.image.load("imgs/back/back clean.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        back_conv = pygame.image.load("imgs/menu/back_conversation.png")

        moreline=0
        #If personnage
        if self.game.current_scene.get("personage"):
            perso = pygame.image.load(self.game.current_scene["personage"]["img"])
            perso=pygame.transform.scale(perso, (self.game.current_scene["personage"]["size"]["x"], self.game.current_scene["personage"]["size"]["y"]))
            screen.blit(perso, (self.game.current_scene["personage"]["position"]["x"], self.game.current_scene["personage"]["position"]["y"]))

            perso = pygame.image.load("./imgs/persos/astro_back.png")
            #perso=pygame.transform.scale(perso, (150,300))
            screen.blit(perso, (300,5))

        screen.blit(back_conv,(int(WIDTH // 2 - back_conv.get_width() // 2), 500))
        #logger.critical(int( (WIDTH // 2 - back_conv.get_width() // 2))
        for i,line in enumerate(self.game.current_scene["scenes"][:self.already_sayed]):
            for j,souligne in enumerate(line['text'].split("|")):
                line_text = self.game.default_font.render(f"{souligne}", True, hex_to_rgb("#9499C3"))

                screen.blit(line_text, (350, 520+((moreline+j+i)*30)))
            moreline += j+1
        if  not pygame.mixer.music.get_busy() and len(self.sound_to_play)>0:
            son=self.sound_to_play.pop()
            son.play()



class Decollage(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title = game.default_font.render("êtes vous sur ?", True, WHITE)
        self.current_vaisseau = 1
        self.button_list = random.choices(["yellow","red","green","blue"],k=4)
        self.player_input = []
        self.phrase=["Préparation du pique nique","Un DERNIER BISOUS aux parents","Vérification du DOUDOU","Décollage"]
        self.sound_to_play = []
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if buttons_map.get(event.button) == self.button_list[len(self.player_input)]:
                    #self.game.vaisseau=self.game.vaisseaux[self.current_vaisseau]
                    logger.info(f"bouton valide {buttons_map.get(event.button)}")
                    self.player_input.append(event.button)
                    if len(self.player_input) == len(self.button_list):
                        self.sound_to_play.append(pygame.mixer.Sound("./audio/common/decolage.ogg"))


                else:
                    logger.info(f"bouton {event.button} pas valide {buttons_map.get(event.button)}")

                #self.game.change_scene(GameScene(self.game))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game.change_scene(decollage_planete(self.game))  # Passage à la scène de jeu


    def render(self, screen):
        background = pygame.image.load("imgs/back/back clean.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))

        btn_uncheck = pygame.transform.scale(self.game.assets["check"]["uncheck"], (40, 40))
        for i, bouton in enumerate(self.button_list):
            line_text = self.game.default_font.render(f"{self.phrase[i]}", True, hex_to_rgb("#9499C3"))
            screen.blit(line_text, (100, 300 + (i) * 100))
            if i >= len(self.player_input):
                screen.blit(btn_uncheck, (55, 300 + (i) * 100))
            btn = pygame.transform.scale(self.game.assets["boutons"][bouton], (150, 150))
            screen.blit(btn, (1310 +(150*i),540-75))
        btn = pygame.transform.scale(self.game.assets["check"]["check"], (40, 40))
        for i, bouton in enumerate(self.player_input):
            screen.blit(btn, (1365 +(150*i),670))
            screen.blit(btn, (55, 300 + (i) * 100))
        if  not pygame.mixer.music.get_busy() and len(self.sound_to_play)>0:
            son=self.sound_to_play.pop()
            son.play()
            self.game.change_scene(decollage_planete(self.game))
        skin = pygame.image.load(self.game.vaisseau["skin"])
        skin = pygame.transform.scale(skin, (510, 510))
        screen.blit(skin, (int(1920/2-510/2), int(1080/2-510/2)))

class decollage_planete(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title = game.default_font.render("êtes vous sur ?", True, hex_to_rgb("#9499C3"))
        self.topy=0
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
        if 1080-500+self.topy < -100 :
            self.game.change_scene(GameScene(self.game))

    def render(self, screen):
        background = pygame.image.load("imgs/back/back clean.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))

        earth_cut = pygame.image.load("imgs/logos/terre_coupe.png")
        screen.blit(earth_cut, (100, 1080-600))
        reactor = pygame.image.load("imgs/fusee/reacteur.png")

        reactor = pygame.transform.scale(reactor, (200,200))
        screen.blit(reactor, (440, 810+self.topy))

        skin = pygame.image.load(self.game.vaisseau["skin"])
        skin = pygame.transform.scale(skin, (int(510/2), int(510/2)))
        screen.blit(skin, (100+300, 1080-500+self.topy))
        self.topy-=30


def load_and_rotate(image_path, size, angle, pivot):
    """Charge, redimensionne, fait pivoter et aligne une image sur un pivot."""
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, size)
    image_rotated = pygame.transform.rotate(image, angle)

    # Repositionner l’image pour qu’elle tourne autour du pivot
    rect = image_rotated.get_rect(center=pivot)

    return image_rotated, rect.topleft


class redecollage_planete(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title = game.default_font.render("êtes vous sur ?", True, WHITE)
        self.current_vaisseau = 1
        self.button_list = random.choices(["yellow","red","green","blue"],k=4)
        self.player_input = []
        self.phrase=["Préparation du pique nique","Un DERNIER BISOUS aux parents","Vérification du DOUDOU","Décollage"]
        self.sound_to_play = []

        self.beam_radius=1
        self.beam_x=0
        self.beam_y=0
        self.speed=30

        self.position_init_vaiseau_x=400+self.beam_x
        self.position_init_vaiseau_y=580+self.beam_y
        self.earth_center_x=1420+250
        self.earth_center_y=300
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if buttons_map.get(event.button) == self.button_list[len(self.player_input)]:
                    #self.game.vaisseau=self.game.vaisseaux[self.current_vaisseau]
                    logger.info(f"bouton valide {buttons_map.get(event.button)}")
                    self.player_input.append(event.button)
                    if len(self.player_input) == len(self.button_list):
                        self.sound_to_play.append(pygame.mixer.Sound("./audio/common/decolage.ogg"))
                else:
                    logger.info(f"bouton {event.button} pas valide {buttons_map.get(event.button)}")
                #self.game.change_scene(GameScene(self.game))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game.change_mission()
                self.game.change_scene(PlayerSelectionScene(self.game))

        if self.game.joystick:
            x_axis = self.game.joystick.get_axis(0)  # Axe X
            y_axis = self.game.joystick.get_axis(1)  # Axe Y

            # Déplacement du faisceau
            if x_axis > 0.008 or x_axis < -0.008:
                self.beam_x += int(x_axis * self.speed)
            if y_axis > 0.008 or y_axis < -0.008:
                self.beam_y += int(y_axis * self.speed)

            distance = ((self.position_init_vaiseau_x+self.beam_x+255 - self.earth_center_x) ** 2 + (self.position_init_vaiseau_y+self.beam_y - self.earth_center_y) ** 2) ** 0.5
            print(distance)
            if distance<90:
                self.game.change_mission()
                self.game.change_scene(PlayerSelectionScene(self.game))  # Passage à la scène de jeu

        # Empêcher le faisceau de sortir de l'écran
        #self.beam_x = max(self.beam_radius, min(WIDTH - self.beam_radius, self.beam_x))
        #self.beam_y = max(self.beam_radius, min(HEIGHT - self.beam_radius, self.beam_y))

    def render(self, screen):
        background = pygame.image.load("imgs/back/back clean.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        logger.debug(f"{self.beam_x},{self.beam_y}")
        earth = pygame.image.load("imgs/logos/terre.png")
        earth = pygame.transform.scale(earth, (500, 500))
        screen.blit(earth, (1420, 50))
        reactor = pygame.image.load("imgs/fusee/reacteur.png")

        reactor = pygame.transform.scale(reactor, (200, 200))
        reactor = pygame.transform.rotate(reactor, -45)
        screen.blit(reactor, (300+self.beam_x, 783+self.beam_y))

        skin = pygame.image.load(self.game.vaisseau["skin"])
        skin = pygame.transform.scale(skin, (255, 255))
        skin = pygame.transform.rotate(skin, -45)
        screen.blit(skin, (self.position_init_vaiseau_x+self.beam_x, self.position_init_vaiseau_y+self.beam_y))



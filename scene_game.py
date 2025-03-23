import json
import os
import pygame
import random
from src.scene import MenuScene, GameScene, VictoryScene,DialogueScene
import logging

# Initialisation de Pygame
pygame.mixer.init()
pygame.init()
logger = logging.getLogger(__name__)
# Dimensions de l'écran
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
#screen =pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

pygame.display.set_caption("Cherche et Trouve")
pygame.joystick.init()

#
colors = ["blue", "yellow", "red", "green"]
buttons_map={
    "0":"green",
    "1":"green",
    "2":"red",
    "3":"red",
    "4":"yellow",
    "5":"yellow",
    "6":"blue",
    "7":"blue",
    "9":"settings",
    "10":"settings2",
}

##
# ========================= CLASSE PRINCIPALE DU JEU =========================
class Game:
    def __init__(self):
        self.running = True


        self.scene_list = ["./texts/mission_fusee.json","./texts/mission_boite.json","./texts/mission_potager.json","./texts/mission_devin.json","./texts/mission_books.json","./texts/mission_desarts.json"]
        self.scene_data = []

        for scene in self.scene_list:
            with open(scene,"r",encoding="utf-8") as scene_json:
                self.scene_data.append(json.load(scene_json))



        if len(self.scene_data) >0:
            self.current_scene=self.scene_data.pop()
        self.default_font = pygame.font.Font(None, 50)
        self.scene = MenuScene(self)  # Commence avec le menu
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None
        with open("config.json", "r") as config_file:
            self.config = json.load(config_file)
        self.players = self.config["participants"]
        self.vaisseaux = self.config["vaisseaux"]
        self.vaisseau=self.config["vaisseaux"][1]
        self.current_player = 0
        self.user_inputs=[]
        self.assets = {"boutons": {
            "blue": pygame.image.load("imgs/logos/blue_button.png"),
            "yellow": pygame.image.load("imgs/logos/yellow_button.png"),
            "red": pygame.image.load("imgs/logos/red_button.png"),
            "green": pygame.image.load("imgs/logos/green_button.png"),

        },
        "check":{
            "uncheck":pygame.image.load("imgs/logos/Check_Icon.png"),
            "check":pygame.image.load("imgs/logos/Check_Icon_green.png")
                 }
        }

    def change_scene(self, new_scene):
        self.scene = new_scene
    def change_mission(self):
        if len(self.scene_data) > 0:
            self.current_scene = self.scene_data.pop()


    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            events = pygame.event.get()
            self.scene.handle_events(events)  # Gérer les événements
            self.scene.update()  # Mettre à jour la scène
            self.scene.render(screen)  # Dessiner la scène
            pygame.display.flip()
            clock.tick(30)


# Lancer le jeu
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s',
                        handlers=[logging.FileHandler("my_log.log", mode='w'),
                                  logging.StreamHandler()])
    stream_handler = [h for h in logging.root.handlers if isinstance(h, logging.StreamHandler)][0]
    stream_handler.setLevel(logging.INFO)
    game = Game()
    game.run()
    pygame.quit()

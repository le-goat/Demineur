# _______________Importation des modules_______________ #
import arcade
from arcade import color
import random
import time

# ________________CONSTANTES________________ #

nb_case_w = 10  # le nombre de cases de largeur qui formeront la fenetre
nb_case_h = 10  # le nombre de cases de hauteur qui formeront la fenetre
TAILLE_CASE = 30  # la taille (en pixels) d'une case
NB_BOMBE = int((13 / 100) * (nb_case_w * nb_case_h))  # le nombre ou le pourcentage de bombes dans le tableau
print("Il y a " + str(NB_BOMBE) + " bombes!")
liste_voisin = [  # les coordonnées des voisins par rapport à une case (0, 0)
    [0, 1],
    [1, 1],
    [1, 0],
    [1, -1],
    [0, -1],
    [-1, -1],
    [-1, 0],
    [-1, 1],
]


def generateur_grille(valeur):  # génère un tableau remplit par la valeur
    return [[valeur for i in range(nb_case_w)] for i in range(nb_case_h)]


def position_Sprite_grille(x, y, largeur_grille):  # permet de centrer les sprites sur le "tableau"
    return (x + 0.5) * largeur_grille, (y + 0.5) * largeur_grille


def calculateur_bombe(grille):  # retourne le nombre de bombes dans la grille
    compteur = 0
    for y in range(len(grille)):
        for x in range(len(grille[y])):
            if grille[y][x] == 1:
                compteur += 1
    return compteur


def placement_bombe(grille, nb_bombe):  # place de manière "aléatoire" le nombre exact de bombes demandées
    while calculateur_bombe(grille) < nb_bombe:
        grille[random.randint(0, nb_case_h - 1)][random.randint(0, nb_case_w - 1)] = 1


def compteur_de_voisin(grille):  # retourne pour chaque case de la grille le nombre de ses voisins qui sont des bombes
    compteur = 0
    nombre_voisin = generateur_grille(0)
    for y in range(len(grille)):
        for x in range(len(grille[y])):
            if grille[y][x] == 1:
                compteur = 'X'
            else:
                for z in range(len(liste_voisin)):
                    xx = x + liste_voisin[z][1]
                    yy = y + liste_voisin[z][0]
                    if xx < 0 or yy < 0:
                        pass
                    else:
                        try:
                            if grille[yy][xx] == 1:
                                compteur += 1
                        except IndexError:
                            pass
            nombre_voisin[y][x] = compteur
            compteur = 0
    return nombre_voisin


# # # # # # # # # # # # # # # # # #_________________ARCADE___________________# # # # # # # # # # # # # # # # # # # # # #


class MaFenetre(arcade.Window):  # contient toute la partie graphique du jeu
    def __init__(self, width: int = (TAILLE_CASE * nb_case_w), height: int = (TAILLE_CASE * nb_case_h)):
        super().__init__(width, height, "Démineur")
        self.ma_grille = generateur_grille(0)  # on crée une grille de jeu vide
        placement_bombe(self.ma_grille, NB_BOMBE)  # on place un nombre de bombe exact dans la grille de jeu
        self.grille_etat = generateur_grille(1)  # on crée une grille de "1" de la même taille que celle de jeu qui
        # représentera l'état de la case : jouable, jouée ou suspectée (drapeau)
        self.grille_voisins = compteur_de_voisin(self.ma_grille)  # une dernière grille est aussi complétée avec le
        # nombre de bombe voisine pour chaque case
        self.liste_Sprite = arcade.SpriteList()  # on initialise la liste des sprites
        self.nb_coups = 0  # on déclare la variable correspondant au nombre de coups joués
        self.debut = 0  # on déclare la variable de temps référence du premier coup (s)
        self.fin = 0  # on déclare la variable de temps référence du dernier coup gagnant ou perdant (s)
        self.temps = 0  # on déclare la variable de temps correspondant au temps de jeu (s)
        self.propre = 0  # on déclare la variable de temps correspondant au temps de jeu (compréhenssible)

    def mecanique_sprites(self, x, y, ressource):  # crée un sprite pour le placer dans la liste
        piece_sprite = arcade.Sprite("images/" + ressource + ".png")
        piece_x, piece_y = position_Sprite_grille(x, y, TAILLE_CASE)
        piece_sprite.set_position(piece_x, piece_y)
        piece_sprite.scale = (TAILLE_CASE / 20)
        self.liste_Sprite.append(piece_sprite)

    def affiche_bombes(self, grille):  # découvre toutes les bombes de la grille
        for y in range(len(grille)):
            for x in range(len(grille[y])):
                if grille[y][x] == 1 and self.grille_etat[y][x] == 2:
                    pass
                elif grille[y][x] == 1:
                    self.decouvrir(x, y)
                elif self.grille_etat[y][x] == 2:
                    self.grille_etat[y][x] = 3

    def afficher_voisin(self):  # affiche toutes les cases découvertes par rapport à la grille des voisins
        for y in range(len(self.grille_voisins)):
            for x in range(len(self.grille_voisins[y])):
                self.mecanique_sprites(x, y, str(self.grille_voisins[y][x]))

    def couverture(self, grille):  # garde les cases non découvertes cachées
        for y in range(len(grille)):
            for x in range(len(grille[y])):
                if grille[y][x] == 0:
                    pass
                elif grille[y][x] == 1:
                    self.mecanique_sprites(x, y, "non")
                elif grille[y][x] == 2:
                    self.mecanique_sprites(x, y, "dra")
                elif grille[y][x] == 3:
                    self.mecanique_sprites(x, y, "nonX")

    def decouvrir(self, x: int, y: int) -> None:  # découvre la case donnée en argument
        # (peut être amener à en découvrir d'avantage)
        self.dernier_x = x
        self.dernier_y = y
        if x < 0 or y < 0 or x > (nb_case_w - 1) or y > (nb_case_h - 1):
            return
        if self.grille_etat[y][x] == 0:
            return

        self.grille_etat[y][x] = 0

        if self.ma_grille[y][x] == 1:
            self.affiche_bombes(self.ma_grille)
        elif self.grille_voisins[y][x] == 0:
            for z in range(len(liste_voisin)):
                xx = x + liste_voisin[z][1]
                yy = y + liste_voisin[z][0]
                self.decouvrir(xx, yy)

        if self.resolu(self.ma_grille):
            self.fin = time.time()
            self.temps = self.fin - self.debut
            self.propre = time.strftime('%M minute %S secondes', time.localtime(self.temps))
            print(self.nb_coups)
            self.result()
        else:
            print(self.resolu(self.ma_grille))

    def resolu(self, grille) -> bool:  # retourne vrai si la grille est complétée correctement
        for y in range(len(grille)):
            for x in range(len(grille[y])):
                if self.ma_grille[y][x] == 0 and self.grille_etat[y][x] != 0:
                    return False
        return True

    #def result(self):  # affiche le message de fin de partie
    #    arcade.draw_rectangle_filled((self.width / 2), (self.height / 2), (self.width - (self.width / 4)),
    #                                 (self.height - (self.height / 4)), color.WHITE, 5)
    #    if self.resolu(self.ma_grille):
    #        arcade.draw_text("tu as trouvé toutes les bombes en", (self.width / 4), (3 * (self.height / 4)),
    #                         color.BLACK, font_size=15)
    #        arcade.draw_text(self.propre, (self.width / 4), (2 * (self.height / 4)), color.BLACK, font_size=15)
    #    else:
    #        arcade.draw_text("tu as perdu", (self.width / 4), (3 * (self.height / 4)), color.BLACK, font_size=15)

    def drapeau(self, x: int, y: int):  # permet d'afficher un drapeau sur une case suspectée d'abriter une bombe
        if self.grille_etat[y][x] == 0:
            pass
        elif self.grille_etat[y][x] == 2:
            self.grille_etat[y][x] = 1
        else:
            self.grille_etat[y][x] = 2

    def on_mouse_press(self, x: int, y: int, button: int,
                       modifiers: int):  # déclanche les fonctions adéquates lors des différents clics
        self.nb_coups += 1
        if self.nb_coups == 1:
            self.debut = time.time()
        x_grille = x // TAILLE_CASE
        y_grille = y // TAILLE_CASE
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.drapeau(x_grille, y_grille)
        elif button == arcade.MOUSE_BUTTON_LEFT:
            self.decouvrir(x_grille, y_grille)

    def on_draw(self):  # permet de gérer toute la partie visuelle du jeu
        arcade.start_render()
        self.afficher_voisin()
        self.couverture(self.grille_etat)
        self.liste_Sprite.draw()
        if self.resolu(self.ma_grille) or self.ma_grille[self.dernier_y][self.dernier_x] == 1:
            self.result()


f = MaFenetre()
arcade.run()

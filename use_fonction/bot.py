"""
Nom du fichier: bot.py
Auteur: Étienne-Théodore PRIN (version originale modifiée)
Date: 2024-02-02

Description (améliorée):
Ce module définit la classe bot qui choisit l'action à effectuer en fonction de l'état de la partie Clash Royale.
La stratégie a été enrichie pour supporter le géant avec des cartes de soutien dès qu'elles sont disponibles
et pour défendre les tours dès qu'un ennemi menace votre terrain.
Seules les cartes déjà présentes sont utilisées.
"""

from use_fonction.configuration.matrice_def import matrice_choix_def_response, dict_trad, elixir_price, dictionnaire_translation, card_dictionnary
import time
import math
import random

class bot():
    def __init__(self):
        """
        Initialise le bot avec des positions prédéfinies pour le placement des cartes.
        """
        self.commands = {
            "left": [283, 380],
            "right": [79, 380],
            "left_enemy_side": [76, 262],
            "right_enemy_side": [286, 269],
            "left_our_side": [76, 405],
            "right_our_side": [286, 405],
            "enemy_tower_left": [76, 174],
            "enemy_tower_right": [287, 174],
            "enemy_tower_cneter": [179, 107],
            "enemy_target": [0, 0]
        }
        self.random = [[283, 380], [79, 380]]
        self.random_enemy_side = [[76, 262], [286, 269]]
        self.mode = "attack"

    def distance(self, p1, p2):
        """
        Calcule la distance Euclidienne entre deux positions.

        Args:
            p1, p2 : listes ou tuples de deux valeurs représentant une position [x, y].

        Returns:
            distance (float)
        """
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def get_action(self, state):
        """
        Renvoie l'action préconisée par le bot.

        Args:
            state : l'état du jeu à l'instant t

        Returns:
            action : [] si aucune action n'est prise ou
                     [index_de_la_carte_à_poser (int), position ([x, y])] si une carte est jouée.
        """
        if not state[0]:
            return []

        elixir = state[1][2]
        # Extraction du statut des tours (exemple : "destroyed" ou "alive")
        self.towers = [item[2].split(' ')[0] for item in state[2:6]]
        # Cartes disponibles (leur indice dans l'état)
        self.cards = {item[2]: i for i, item in enumerate(state[6:10])}

        # Construction de self.players en s'assurant que la position ennemie soit une liste à deux éléments.
        self.players = {}
        if len(state) >= 10:
            for item in state[10:-1]:
                key = item[2].split('.')[0]
                pos = item[1]
                # Si pos n'est pas déjà une liste, le transformer en [pos, pos]
                if not isinstance(pos, list):
                    pos = [pos, pos]
                self.players[key] = pos

        # Phase de défense : protection des tours si un ennemi menace votre terrain.
        defense_action = self.decide_defense(elixir)
        if defense_action is not None:
            return defense_action

        # Phase d'attaque : utilisation de la logique d'attaque modifiée
        attack_action = self.decide_attack(elixir)
        if attack_action is not None:
            return attack_action

        return []

    def decide_defense(self, elixir):
        """
        Logique de défense :
         - Défend les tours si un ennemi se trouve à proximité.
         - Utilise des contres adaptés selon le type d'ennemi.

        Args:
            elixir (int): quantité d'élixir disponible.

        Returns:
            action (list) ou None.
        """
        tower_threshold = 50  # seuil de distance pour considérer qu'un ennemi menace une tour

        threat_counters = {
            "geant": ["PK_vignette.jpg", "gargouilles_vignette.jpg", "mousquetaire_vignette.jpg"],
            "gargouille": ["fleches_vignette.jpg", "mousquetaire_vignette.jpg"],
            "bat": ["fleches_vignette.jpg", "mousquetaire_vignette.jpg"],
            "mini_PEKKA": ["fleches_vignette.jpg", "mousquetaire_vignette.jpg", "PK_vignette.jpg"],
            "chevalier": ["fleches_vignette.jpg", "PK_vignette.jpg", "mousquetaire_vignette.jpg"],
            "gobelin": ["fleches_vignette.jpg", "PK_vignette.jpg", "fireball_vignette.jpg"],
            "mousquetaire": ["fleches_vignette.jpg", "fireball_vignette.jpg", "PK_vignette.jpg"],
            "archere": ["fleches_vignette.jpg", "chevalier_vignette.jpg", "PK_vignette.jpg"],
            "squelette": ["fleches_vignette.jpg", "chevalier_vignette.jpg", "PK_vignette.jpg"]
        }

        # Défense proactive : vérifier la proximité des ennemis par rapport à vos tours.
        for enemy, pos in self.players.items():
            enemy_pos = pos  # ici, pos est supposé être une liste [x, y]
            # Défense de la tour gauche
            if self.distance(enemy_pos, self.commands["left_our_side"]) < tower_threshold:
                if enemy in threat_counters:
                    for counter in threat_counters[enemy]:
                        if counter in self.cards:
                            print(f"==> Défense Tour Gauche : Contre {enemy} avec {counter}")
                            return [self.cards[counter], self.commands["left_our_side"]]
                any_card = random.choice(list(self.cards.values()))
                print("==> Défense Tour Gauche : Utilisation d'une carte aléatoire")
                return [any_card, self.commands["left_our_side"]]

            # Défense de la tour droite
            if self.distance(enemy_pos, self.commands["right_our_side"]) < tower_threshold:
                if enemy in threat_counters:
                    for counter in threat_counters[enemy]:
                        if counter in self.cards:
                            print(f"==> Défense Tour Droite : Contre {enemy} avec {counter}")
                            return [self.cards[counter], self.commands["right_our_side"]]
                any_card = random.choice(list(self.cards.values()))
                print("==> Défense Tour Droite : Utilisation d'une carte aléatoire")
                return [any_card, self.commands["right_our_side"]]

        return None

    def decide_attack(self, elixir):
        """
        Logique d'attaque :
         - Attaque toujours depuis le côté gauche.
         - Priorise l'attaque sur les ennemis proches de ce côté pour les éliminer avant leur arrivée.
         - Utilise le géant ou des cartes de soutien selon l'élixir disponible et la situation.
         
        Args:
            elixir (int): quantité d'élixir disponible.

        Returns:
            action (list) ou None.
        """
        if elixir < 5:
            return None

        # On fixe l'attaque depuis le côté gauche
        attack_side = "left_enemy_side"
        target_pos = self.commands[attack_side]

        # Recherche de l'ennemi le plus proche de la position d'attaque
        closest_enemy = None
        min_dist = float('inf')
        for enemy, pos in self.players.items():
            d = self.distance(pos, self.commands[attack_side])
            if d < min_dist:
                min_dist = d
                closest_enemy = pos

        # Seuil permettant de déterminer si un ennemi est suffisamment proche
        threshold = 100  # Vous pouvez ajuster ce seuil en fonction du jeu
        if closest_enemy is not None and min_dist < threshold:
            target_pos = closest_enemy
            print("==> Attaque : Ciblage de l'ennemi le plus proche sur le côté gauche")

        support_cards = ["mousquetaire_vignette.jpg", "chevalier_vignette.jpg", "PK_vignette.jpg"]

        if "geant_vignette.jpg" in self.cards:
            available_support = [card for card in support_cards if card in self.cards]
            if available_support and elixir >= 7:
                if random.random() < 0.5:
                    chosen_support = random.choice(available_support)
                    print("==> Attaque : Soutien (", chosen_support, ") pour push gauche")
                    return [self.cards[chosen_support], target_pos]
            print("==> Attaque : Géant attaquant depuis le côté gauche")
            return [self.cards["geant_vignette.jpg"], target_pos]

        available_support = [card for card in support_cards if card in self.cards]
        if available_support:
            chosen_support = random.choice(available_support)
            print("==> Attaque : Soutien (", chosen_support, ") pour push gauche")
            return [self.cards[chosen_support], target_pos]

        if "fireball_vignette.jpg" in self.cards:
            print("==> Attaque : Fireball sur la cible")
            return [self.cards["fireball_vignette.jpg"], target_pos]

        if elixir >= 7:
            card_index = random.choice(list(self.cards.values()))
            print("==> Attaque : Poussée avec carte aléatoire (élixir très élevé)")
            return [card_index, target_pos]

        return None

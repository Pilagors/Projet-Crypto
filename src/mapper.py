"""
Mapper les cartes assets/.png vers des nombres

ordre défini : 
    1-13    -> Trèfles
    14-26   -> Carreaux
    27-39   -> Coeur
    40-52   -> Piques
    53      -> Joker Noir
    54      -> Joker Rouge 
"""

import os

ORDRE = [
    (range(1, 14), "Clubs"),
    (range(14, 27), "Diamond"),
    (range(27, 40), "Hearts"),
    (range(40, 53), "Spades"),
]

NOMMAGE = {
    "Clubs" : "Trèfles",
    "Diamond" : "Carreau",
    "Hearts" : "Coeur",
    "Spades" : "Pique",
}

FACES = {
    1: "As",
    11: "Valet",
    12: "Dame",
    13: "Roi"
}

def carte_vers_chemin(valeur):
    if valeur == 53:
        filename = "Joker Black.png"
    elif valeur == 54:
        filename = "Joker Red.png"

    else:
        filename = ""
        for ordre, nom in ORDRE:
            if valeur in ordre:
                n = valeur - ordre.start + 1
                filename = f"{nom} {n}.png"
                break

    return os.path.join("../assets/cartes", filename)

def carte_vers_label(valeur):
    if valeur == 53:
        return "Joker Noir"
    
    if valeur == 54:
        return "Joker Rouge"
    
    for ordre, nom in ORDRE:
        if valeur in ordre:
            n = valeur - ordre.start + 1
            name = FACES.get(n, str(n))
            return f"{name} de {NOMMAGE[nom]}"
        
    return f"Carte {valeur}"

def get_cartes():
    return list(range(1, 55))
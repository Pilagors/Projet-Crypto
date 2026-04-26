import re
import unicodedata
from src import fichiers as fs


class Solitaire:
    def __init__(self, jeuCarte=None):
        """dans l'ordre 1-52 trefle carreau coeur pique
            joker 53,54"""
        if jeuCarte : 
            self.jeu_carte = list(jeuCarte)
        else :
            self.jeu_carte = list(range(1,55))
        
        self.JOKER_BLACK= 53
        self.JOKER_RED = 54

    # UTILS

    def supprimer_accents(self, text):
        """Supprime les accents des caractères (é -> e, è -> e, à -> a, etc.)"""
        # Décompose les caractères accentués en base + diacritiques
        nfd = unicodedata.normalize('NFD', text)
        # Filtre les diacritiques (combine diacritical marks)
        return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

    def nettoyer_message(self, message):
        message = message.upper()
        message = self.supprimer_accents(message)  # Supprime les accents
        message = re.sub(r'[^A-Z ]', '', message) # substitution, garder les espaces
        return message

    def lettre_vers_nombre(self, car):
        if car == ' ':
            return 27
        return ord(car) - 64
    
    def nombre_vers_lettre(self, nombre):
        if nombre == 27:
            return ' '
        return chr(nombre + 64)

    # ETAPES DE MELANGE
    
    def move_joker(self,joker_value,step):
        ancien_index = self.jeu_carte.index(joker_value)
        self.jeu_carte.pop(ancien_index)

        nouveau_index = (ancien_index + step) % len(self.jeu_carte)

        if nouveau_index == 0:
            nouveau_index = 1

        self.jeu_carte.insert(nouveau_index,joker_value)
    
    def double_coupe(self):
        JN = self.jeu_carte.index(self.JOKER_BLACK)
        JR = self.jeu_carte.index(self.JOKER_RED)

        premier = min(JN, JR)
        deuxieme = max(JN, JR)

        
        bloc1 = self.jeu_carte[:premier]
        bloc2 = self.jeu_carte[premier:deuxieme+1]
        bloc3 = self.jeu_carte[deuxieme+1:]

        self.jeu_carte = bloc3 + bloc2 + bloc1

    def coupe_simple(self):
        derniere_carte = self.jeu_carte[-1]

        valeur = 53 if (derniere_carte == self.JOKER_RED or derniere_carte == self.JOKER_BLACK) else derniere_carte

        bloc_a_deplacer = self.jeu_carte[:valeur]
        reste = self.jeu_carte[valeur:-1]

        self.jeu_carte = reste + bloc_a_deplacer + [derniere_carte]

    def pseudo_aleatoire(self):
        premiere_carte = self.jeu_carte[0]

        valeur = 53 if (premiere_carte == self.JOKER_RED or premiere_carte == self.JOKER_BLACK) else premiere_carte

        if valeur >= len(self.jeu_carte):
            #refaire le mélange
            return None

        carte = self.jeu_carte[valeur]

        if carte == self.JOKER_BLACK or carte == self.JOKER_RED:
            #refaire le mélange 
            return None
        
        if carte > 26 :
            carte -= 26

        return carte
            

    def get_keystream_letter(self):
        while True:
            self.move_joker(self.JOKER_BLACK, 1)
            self.move_joker(self.JOKER_RED, 2)
            self.double_coupe()
            self.coupe_simple()
            
            resultat = self.pseudo_aleatoire()
            if resultat is not None:
                return resultat
    
    # CHIFFRAGE ET DECHIFFRAGE
    #https://python-tcod.readthedocs.io/en/latest/tcod/charmap-reference.html

    def chiffrage_final(self,message):
        message_chiffre =""
        message = self.nettoyer_message(message)
        for car in message :
            val = self.lettre_vers_nombre(car)
            cle = self.get_keystream_letter()

            print(f"Caractère: {repr(car)} | Clé générée: {cle}")

            somme = val + cle
            if somme > 27:
                somme -= 27

            message_chiffre += self.nombre_vers_lettre(somme)
                
        return message_chiffre
    
    def dechiffrage_final(self,message_chiffre):
        message =""
        message_chiffre = self.nettoyer_message(message_chiffre)

        for car in message_chiffre :
            val = self.lettre_vers_nombre(car)
            cle = self.get_keystream_letter()
            
            diff = val - cle
            if diff < 1:
                diff += 27

            message += self.nombre_vers_lettre(diff)

        return message

def chiffrage_fichier(chemin, jeuCarte=None):
    s = Solitaire(jeuCarte)
    fichiers = fs.Fichiers()

    message = fichiers.lire_fichier(chemin)
    if message is not None:
        message_chiffre = s.chiffrage_final(message)
        fichiers.ecrire_fichier(chemin + ".crypt", message_chiffre)
        return message_chiffre

    return None

def dechiffrage_fichier(chemin, jeuCarte=None):
    s = Solitaire(jeuCarte)
    fichiers = fs.Fichiers()

    message_chiffre = fichiers.lire_fichier(chemin)
    if message_chiffre is not None:
        message_dechiffre = s.dechiffrage_final(message_chiffre)
        base = chemin.removesuffix(".crypt")
        fichiers.ecrire_fichier(base + ".decrypt", message_dechiffre)
        return message_dechiffre

    return None
    
def tests() :
    print("-> TESTS <-")

    s1 = Solitaire()
    message = "Projet de cryptographie"

    chiffrer = s1.chiffrage_final(message)

    s2 = Solitaire()
    dechiffrer = s2.dechiffrage_final(chiffrer)

    print("Message clair : ", message)
    print("Message crypté : ", chiffrer)
    print("Message déchiffré : ", dechiffrer)

    assert dechiffrer == "PROJETDECRYPTOGRAPHIE"
    print("Test réussi")

    s3 = Solitaire()
    message2 = "Portez ce vieux whisky au juge blond qui fume"

    chiffrer2 = s3.chiffrage_final(message2)

    s4 = Solitaire()
    dechiffrer2 = s4.dechiffrage_final(chiffrer2)

    print("Message clair : ", message2)
    print("Message crypté : ", chiffrer2)
    print("Message déchiffré : ", dechiffrer2)

    assert dechiffrer2 == "PORTEZCEVIEUXWHISKYAUJUGEBLONDQUIFUME"
    print("Test réussi")

if __name__ == "__main__":
    tests()
    chiffrage_fichier("lorem.txt")
    dechiffrage_fichier("lorem.txt")
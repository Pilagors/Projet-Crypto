
class Fichiers:
    def lire_fichier(self, chemin):
        try:
            with open(chemin, 'r', encoding='utf-8') as fichier:
                contenu = fichier.read()
            return contenu
        except FileNotFoundError:
            print(f"Fichier introuvable: {chemin}")
            return None
        
    def ecrire_fichier(self, chemin, contenu):
        with open(chemin, 'w', encoding='utf-8') as fichier:
            fichier.write(contenu)

    
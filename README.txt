# dump1090offline

Ce programme permet de récupérer les données de dump1090 pour afficher les avions sur une carte même si vous ne disposez pas de connection internet. Les fichiers utilisées pour les cartes sont ceux de foxtrotgps. Vous devez donc télécharger les cartes avec foxtrotgps dans un premier temps.

+----------------------------------------------------+     
| dump1090 --metric --interactive --net --aggressive |
+----------------------------------------------------+ 
     |                                                   
     +---------------------------------------------+
       http://127.0.0.1:8080/dump1090/data.json    |
                                                   |
                                                   | 
+-----------------+                                |
|   foxtrotgps    |----------------------+         |
+-----------------+         ~/Maps       |         |
                                         |         |
                                         |         |
                                         |         |
                                         |         |
                                         V         V
                           +--------------------------------+ 
                           |        dump1090offline         |
                           +--------------------------------+ 

Par défaut les données de dump1090 sont récupérées via l'URL : http://127.0.0.1:8080/dump1090/data.json et les images des cartes dans le dossier ~/Maps. Ces valeurs sont modifiables dans le fichier dump1090offline.py

Toutes les données sont enregistrées dans une base de données sqlite3 (data.db) et peuvent être rejouées en activant le mode replay avec la touche 'r' (la date et l'heure est alors affichée en bas à gauche).

### raccourcis clavier

a			zoom arrière

z			zoom avant

m			change le type de map (googlemaps / googlesat / OSM)

r			active/désactive le mode replay

R			le mode replay repart du premier enregistrement

s			augmente la vitesse du replay

S			diminue la vitesse du replay

d			avance d'une journée dans le replay

D			recule d'une journée dans le replay

h			avance d'une heure dans le replay

H			recule d'une heure dans le replay

n			affiche ou pas le nom des vols

l			affiche ou pas la liste

flèches		déplace la map de 10 pixels

q			quitter

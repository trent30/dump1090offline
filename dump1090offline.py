#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

#~ ---------------------------------------------------------
#~	                       CONFIG
#~ ---------------------------------------------------------

#~ Données de dump1090 :
URL = 'http://127.0.0.1:8080/dump1090/data.json'

#~ Données de foxtrotgps :
PATH = os.path.expanduser('~/Maps')
MAPS = ['googlemaps', 'googlesat', 'OSM']
SIZE_IMG = 256
MAP = MAPS[0]

resolution = width, height = 1024, 570
window_title = '1090 - offline'

#~ Point de départ d'affichage de la map :
#~ Correspond au fichier PATH/MAP/ZOOM/X/Y.png
ZOOM = 8
X = 125
Y = 87
OFFSET_X = 0
OFFSET_Y = 0

PAS = 10
FLIGHT_DOT_SIZE = 2
AFF_NAME_FLIGHT = True
AFF_LIST_FLIGHT = True
FONT_SIZE = 20

SPEED = 1
REPLAY = False
DELAY = 0.01
#~ ---------------------------------------------------------

# Données additionnelles pour les fichiers en provenance de foxtrotgps
# Méhodologie « doigt mouillé » :
# J'ai cliqué avec la souris dans les angles de l'image pour avoir les coordonnées GPS
# Erreur de l'ordre du pixel
tuile = {}

tuile[8] = {}					# niveau de zoom 8
tuile[8]['x'] = 1.411743		# longitude du bord gauche de l'image
tuile[8]['x_num'] = 129			# nom du fichier
tuile[8]['x_size'] = 1.400757	# largeur en degré pour 256 pixels
tuile[8]['y'] = 49.830898		# latitude du bord supérieur de l'image
tuile[8]['y_num'] = 87			# nom du fichier
tuile[8]['y_size'] = 0.908459	# hauteur en degré pour 256 pixels

tuile[7] = {}
tuile[7]['x'] = 0.0
tuile[7]['x_num'] = 64
tuile[7]['x_size'] = 2.8125
tuile[7]['y'] = 50.722546
tuile[7]['y_num'] = 43
tuile[7]['y_size'] = 1.800049

tuile[9] = {}
tuile[9]['x'] = -2.106628
tuile[9]['x_num'] = 253
tuile[9]['x_size'] = 0.700378
tuile[9]['y'] = 48.918892
tuile[9]['y_num'] = 176
tuile[9]['y_size'] = 0.458698

tuile[10] = {}
tuile[10]['x'] = -1.756439
tuile[10]['x_num'] = 507
tuile[10]['x_size'] = 0.350189
tuile[10]['y'] = 48.920692
tuile[10]['y_num'] = 352
tuile[10]['y_size'] = 0.228824

tuile[11] = {}
tuile[11]['x'] = -1.581345
tuile[11]['x_num'] = 1015
tuile[11]['x_size'] = 0.175095
tuile[11]['y'] = 48.805958
tuile[11]['y_num'] = 705
tuile[11]['y_size'] = 0.114544

CACHE = {}
MOUSE_X = 0
MOUSE_Y = 0

#~ ---------------------------------------------------------

import pygame
from pygame.locals import *
import time
import sys
from urllib import urlopen
import json
import db

def get_data_from_dump1090():
	try:
		d = json.loads(urlopen(URL).read())
	except:
		return None
	#~ test local
	#~ d = json.load(open('data.json'))
	return d

data = get_data_from_dump1090()

def next_map():
	global MAP, MAPS
	i = MAPS.index(MAP) + 1
	if i == len(MAPS):
		MAP = MAPS[0]
	else:
		MAP = MAPS[i]
	print 'source %s' % MAP

def origine_X(zoom, x, offset_x):
	return tuile[zoom]['x'] + (x - tuile[zoom]['x_num']) * tuile[zoom]['x_size'] - offset_x * tuile[zoom]['x_size'] / SIZE_IMG

def origine_Y(zoom, y, offset_y):
	return tuile[zoom]['y'] - (y - tuile[zoom]['y_num']) * tuile[zoom]['y_size'] + offset_y * tuile[zoom]['y_size'] / SIZE_IMG

def convert(d, zoom, x, y, offset_x, offset_y):
	x = (d['lon'] - origine_X(zoom, x, offset_x) ) * SIZE_IMG / tuile[zoom]['x_size']
	y  = (origine_Y(zoom, y, offset_y) - d['lat'] ) * SIZE_IMG / tuile[zoom]['y_size']
	return int(x), int(y)

def aff_list_flight():
	if not AFF_LIST_FLIGHT:
		return
	if data == None:
		return
	pas_y = 15
	pas_x = 70
	l = ['hex','flight', 'lon', 'lat', 'altitude', 'speed']
	x = 0
	y = 20
	pygame.draw.rect(screen, (255,255,255), (0, 0, 400 , y + pas_y * len(data)), 0)
	for i in l:
		affiche_texte(i.upper(), (x,y) )
		x += pas_x
	for i in data:
		x = 0
		y += pas_y
		for j in l:
			t = i[j]
			if j == 'altitude':
				t = int (t / 3.2828)
			if j == 'speed':
				t = int (t *  1.852)
			affiche_texte(t, (x,y) )
			x += pas_x


def affiche_texte(t, xy):
	global font
	text = font.render(str(t), 1, (0,0,0) )
	textP = text.get_rect()
	textP.left = xy[0]
	textP.bottom = xy[1]
	screen.blit(text,textP)

def draw_flight(zoom, x, y, offset_x, offset_y):
	if data == None:
		return
	for i in data:
		color = 0,0,0
		if zoom in tuile:
			pos = convert(i, zoom, x, y, offset_x, offset_y)
		else:
			# Si on ne possède pas les données relatives aux 'tuiles'
			# alors on ne peut pas afficher une position
			pos = -42, -42
		width = 0
		pygame.draw.circle(screen, color, pos, FLIGHT_DOT_SIZE, width)
		pygame.draw.circle(screen, color, pos, FLIGHT_DOT_SIZE + 2, 1)
		if i['flight'] == None:
			i['flight']=''
		if AFF_NAME_FLIGHT:
			affiche_texte(i['flight'], pos)

def aff_time():
	t = 0
	if data == None:
		return
	for i in data:
		if i['time'] > t:
			t = i['time']
	pygame.draw.rect(screen, (255,255,255), (0, height - FONT_SIZE * 2, 180, height), 0)
	affiche_texte(time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(t)), (0, height - FONT_SIZE) )
	
def draw(zoom, x, y, offset_x, offset_y):
	largeur = width / SIZE_IMG + 2
	hauteur = height / SIZE_IMG + 2
	for i in xrange(hauteur):
		for j in xrange(largeur):
				filename = PATH + '/' + MAP + '/' + str(ZOOM) + '/' + str(x + j - 1) + '/' + str(y + i - 1) + '.png'
				if CACHE.get(filename, None) == None:
					try :
						img = pygame.image.load(filename).convert()
						CACHE[filename] = img
					except:
						pass
				c = ((j - 1) * SIZE_IMG + offset_x, (i - 1) * SIZE_IMG + offset_y)
				screen.blit(CACHE.get(filename, CACHE['blank.png']), c)
	draw_flight(zoom, x, y, offset_x, offset_y)
	aff_list_flight()
	if REPLAY:
		aff_time()
	pygame.display.flip()

pygame.init()
pygame.display.set_caption(window_title)
screen = pygame.display.set_mode(resolution)
font = pygame.font.Font(None, FONT_SIZE)

img = pygame.image.load('blank.png').convert()
CACHE['blank.png'] = img

draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)
pygame.display.flip()
b = db.bdd()

if __name__ == "__main__":
	cpt = 0
	while 1:
		time.sleep(DELAY)
		cpt += 1
		if cpt > 1000 / SPEED:
			cpt = 0
			if REPLAY:
				data = b.get_data()
			else:
				data = get_data_from_dump1090()
				if data != None:
					b.insert_data(data)
			draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_q):
				sys.exit()
			if event.type == KEYDOWN and event.key == K_e:
				pass
			if event.type == KEYDOWN and event.key == K_m:
				next_map()
				draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)
				print pygame.key.get_mods()
			if event.type == KEYDOWN and event.key == K_s:
				if pygame.key.get_mods() == 4096: # pas de shift
					SPEED = SPEED * 2
				else:
					SPEED = SPEED / 2
					if SPEED <= 0:
						SPEED = 1
				print SPEED
			if event.type == KEYDOWN and event.key == K_r:
				if REPLAY:
					REPLAY = False
					SPEED = 1
					DELAY = 0.01
				else:
					REPLAY = True
					SPEED = 20
					DELAY = 0
			if event.type == KEYDOWN and event.key == K_n:
				if AFF_NAME_FLIGHT:
					AFF_NAME_FLIGHT = False
				else:
					AFF_NAME_FLIGHT = True
			if event.type == KEYDOWN and event.key == K_l:
				if AFF_LIST_FLIGHT:
					AFF_LIST_FLIGHT = False
				else:
					AFF_LIST_FLIGHT = True
				draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)
			if event.type == KEYDOWN and event.key == K_a:
				ZOOM -= 1
				X = (X + width  / SIZE_IMG / 2) / 2 - 2
				Y = (Y + height / SIZE_IMG / 2) / 2 - 1
				draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)
			if event.type == KEYDOWN and event.key == K_z:
				ZOOM += 1
				X = (X + height / SIZE_IMG / 2) * 2
				Y = (Y + height / SIZE_IMG / 2) * 2 - 1
				draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)
			if event.type == KEYDOWN and event.key == K_LEFT:
				OFFSET_X += PAS
				if OFFSET_X > SIZE_IMG:
					OFFSET_X = 0
					X -= 1
				draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)
			if event.type == KEYDOWN and event.key == K_UP:
				OFFSET_Y += PAS
				if OFFSET_Y > SIZE_IMG:
					OFFSET_Y = 0
					Y -= 1
				draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)
			if event.type == KEYDOWN and event.key == K_RIGHT:
				OFFSET_X -= PAS
				if OFFSET_X < -SIZE_IMG:
					OFFSET_X = 0
					X += 1
				draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)
			if event.type == KEYDOWN and event.key == K_DOWN:
				OFFSET_Y -= PAS
				if OFFSET_Y < -SIZE_IMG:
					OFFSET_Y = 0
					Y += 1
				draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)
			if event.type == MOUSEBUTTONDOWN and event.button == 1:
				MOUSE_X = event.pos[0]
				MOUSE_Y = event.pos[1]
			if event.type == MOUSEMOTION and event.buttons[0] == 1:
					OFFSET_X -= MOUSE_X - event.pos[0]
					OFFSET_Y -= MOUSE_Y - event.pos[1]
					MOUSE_X = event.pos[0]
					MOUSE_Y = event.pos[1]
					if OFFSET_Y < -SIZE_IMG:
						OFFSET_Y = 0
						Y += 1
					if OFFSET_X < -SIZE_IMG:
						OFFSET_X = 0
						X += 1
					if OFFSET_Y > SIZE_IMG:
						OFFSET_Y = 0
						Y -= 1
					if OFFSET_X > SIZE_IMG:
						OFFSET_X = 0
						X -= 1
					draw(ZOOM, X, Y, OFFSET_X, OFFSET_Y)

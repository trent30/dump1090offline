#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import time

class bdd():
	
	def __init__(self):
		self.conn = sqlite3.connect('data.db')
		self.c = self.conn.cursor()
		self.cache = {}
		self.cache['GPS'] = {}
		self.cpt = 0
		self.all_data = None
		try:
			self.c.execute('SELECT count(*) FROM flight')
		except:
			print "Création de la base de données..."
			self.create_db()
		fields = 'id, value'
		for i in ['flight', 'hex', 'flight_hex']:
			if i == 'flight_hex':
				fields = 'time , flight , hex'
			self.cache[i] = self.select('SELECT %s FROM %s' % (fields, i) )
	
	def get_all_data(self):
		return self.select("""
		SELECT d.time, h.value, f.value, d.lon, d.lat, d.altitude, d.speed
		FROM hex h, data d
		left join flight_hex fh on fh.hex = h.id
		left join flight f on f.id = d.flight
		WHERE h.id = d.hex
		order by d.time asc
		""")
	
	def tuple_to_dico(self, d):
		r = {}
		cpt = 0
		for i in ['time', 'hex','flight', 'lon', 'lat', 'altitude', 'speed']:
			r[i] = d[cpt]
			cpt += 1
		return r
	
	def clean_actual_fly(self, time):
		new_dico = {}
		for i in self.actual_flight:
			if time - self.actual_flight[i]['time'] < 60:
				new_dico[i] = self.actual_flight[i]
		self.actual_flight = new_dico
	
	def get_data(self):
		if self.all_data == None:
			self.all_data = self.get_all_data()
			self.actual_flight = {}
		if len(self.all_data) == self.cpt:
			return
		d = self.tuple_to_dico(self.all_data[self.cpt])
		self.actual_flight[d['hex']] = d
		self.clean_actual_fly(d['time'])
		self.cpt += 1
		r = []
		for i in self.actual_flight:
			r.append(self.actual_flight[i])
		return r
	
	def create_db(self):
		self.c.execute('CREATE TABLE flight (id integer, value text)')
		self.c.execute('CREATE TABLE hex (id integer, value text)')
		self.c.execute('CREATE TABLE flight_hex (time integer, flight integer, hex integer)')
		self.c.execute('CREATE TABLE data (time integer, hex integer, flight integer, lon real, lat real, altitude integer, speed integer)')
		self.conn.commit()
	
	def select(self, requete):
		return self.c.execute(requete).fetchall()
	
	def value_in_cache(self, key, value):
		for i in self.cache[key]:
			if i[1] == value:
				return i[0]
		return False
	
	def value_in_cache2(self, id_flight, id_hex):
		for i in self.cache['flight_hex']:
			if i[1] == id_flight and i[2] == id_hex:
				return True
		return False
		
	def insert_flight_or_hex(self, key, value):
		if value == '':
			return
		num = self.value_in_cache(key, value)
		if num != False:
			return num
		i = self.select('SELECT count(*) FROM %s' % key)[0][0] + 1
		self.c.execute('INSERT INTO %s(id, value) values(%s,"%s")' % (key, i, value))
		self.conn.commit()
		self.cache[key].append( (i, value) )
		return i
	
	def insert_hex_and_flight(self, id_flight, id_hex):
		if self.value_in_cache2(id_flight, id_hex):
			return
		timestamp = int(time.time())
		self.c.execute('INSERT INTO flight_hex(time, flight, hex) values(%s,%s,%s)' % (timestamp, id_flight, id_hex))
		self.conn.commit()
		self.cache['flight_hex'].append( (timestamp, id_flight, id_hex) )
	
	def insert_entry(self, hexa, flight):
		id_flight = self.insert_flight_or_hex('flight', flight)
		id_hex    = self.insert_flight_or_hex('hex', hexa)
		if id_flight != None:
			self.insert_hex_and_flight(id_flight, id_hex)
		return id_hex, id_flight
	
	def gps_value_in_cache(self, id_hex, data):
		if self.cache['GPS'].get(id_hex, None) == None:
			return False
		if self.cache['GPS'][id_hex]['lon'] == data['lon'] and \
			self.cache['GPS'][id_hex]['lat'] == data['lat'] and \
			self.cache['GPS'][id_hex]['speed'] == data['speed'] and \
			self.cache['GPS'][id_hex]['altitude'] == data['altitude'] :
				return True
		return False
	
	def insert_position(self, id_hex, id_flight, data):
		if self.gps_value_in_cache(id_hex, data):
			return
		timestamp = int(time.time())
		self.c.execute('INSERT INTO data (time, hex, flight, lon, lat, altitude, speed) values(%s,%s,%s,%s,%s,%s,%s)' % (timestamp, id_hex, id_flight, data['lon'], data['lat'], data['altitude'], data['speed']) )
		self.conn.commit()
		self.cache['GPS'][id_hex] = data
		
	def insert_data(self, d):
		for i in d:
			id_hex, id_flight = self.insert_entry(i['hex'], i['flight'])
			if id_flight == None:
				id_flight = 0
			self.insert_position(id_hex, id_flight, i)

if __name__ == "__main__":
	b = bdd()
	print b.get_data()

#!/usr/bin/env python2

import pyglet
from pyglet.gl import *
keys = pyglet.window.key
FRAME_TIME = 1/30.0

import tmx

def _keyaxis(game,neg,pos):
	# nice handling for opposing key pairs
	val = 0
	if game.keys[neg]: val -= 1
	if game.keys[pos]: val += 1
	return val

class Player(object):
	def tick(self, game):
		dx = _keyaxis(game, keys.LEFT, keys.RIGHT)
		dy = _keyaxis(game, keys.UP, keys.DOWN)
		if dx or dy:
			print '%s %s' % (dx,dy)

class Game(object):
	def __init__(self):
		self.win = pyglet.window.Window()
		pyglet.clock.schedule(self.update)
		self.keys = keys.KeyStateHandler()
		self.win.push_handlers(self.keys)
		self.win.event(self.on_draw)
		self.at = 0.0

		self.actions = []
		self.actors = []
		self.level = tmx.TileMap('art/map.tmx')
	
	def update(self, dt):
		# utterly standard time accumulator
		self.at += dt;
		while self.at > FRAME_TIME:
			self.at -= FRAME_TIME
			self.tick()

	def on_draw(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0,self.win.width,self.win.height,0,-1,1)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glTranslatef(-32*8,-32*4,0)
		self.level.draw()

	def tick(self):
		for a in self.actors: a.tick(self)
		actions = self.actions
		self.actions = []
		for a in actions: a()
		if self.keys[keys.ESCAPE]: pyglet.app.exit()

	def add_actor(self, a):
		self.actions.append(lambda:self.actors.append(a))
	
	def remove_actor(self, a):
		self.actions.append(lambda:self.actors.remove(a))

pyglet.resource.path = ['art']
pyglet.resource.reindex()
game = Game()
game.add_actor(Player())
pyglet.app.run()

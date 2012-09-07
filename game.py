#!/usr/bin/env python2

import pyglet
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
		self.at = 0.0

		self.actions = []
		self.actors = []
	
	def update(self, dt):
		# utterly standard time accumulator
		self.at += dt;
		while self.at > FRAME_TIME:
			self.at -= FRAME_TIME
			self.tick()

	def tick(self):
		for a in self.actors: a.tick(self)
		actions = self.actions
		self.actions = []
		for a in actions: a()
		if self.keys[keys.ESCAPE]:
			pyglet.app.exit()

	def add_actor(self, a):
		self.actions.append(lambda:self.actors.append(a))
	
	def remove_actor(self, a):
		self.actions.append(lambda:self.actors.remove(a))

game = Game()
_map = tmx.TileMap('art/map.tmx')
game.add_actor(Player())
pyglet.app.run()

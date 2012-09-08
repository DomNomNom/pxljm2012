#!/usr/bin/env python2

import pyglet
from pyglet.gl import *
keys = pyglet.window.key
FRAME_TIME = 1/60.0

import tmx

def _sign(x):
	if x > 0: return 1
	if x < 0: return -1
	return 0

def _keyaxis(game,neg,pos):
	# nice handling for opposing key pairs
	val = 0
	if game.keys[neg]: val -= 1
	if game.keys[pos]: val += 1
	return val

class Player(object):
	def __init__(self, game):
		self.x = 13
		self.y = 8
		self.ux = 0
		self.uy = 0
		self.dx = 0
		self.dy = 0
		self.v = 1.7

		self.sprite = pyglet.sprite.Sprite(
			game.level.image_by_id(2),
			self.x * 32,
			-self.y * 32,
			batch=game.objbatch)

	def tick(self, game):
		# completing an existing move
		if self.dx != 0 or self.dy != 0:
			self.ux += self.dx * self.v;
			self.uy += self.dy * self.v;
			
			if self.ux <= -32 or self.ux >= 32 or self.uy <= -32 or self.uy >= 32:
				self.x += _sign(self.ux); self.y += _sign(self.uy)
				self.ux = 0; self.uy = 0
				self.dx = 0; self.dy = 0

		# starting a new move
		if self.dx == 0 and self.dy == 0:
			self.dx = _keyaxis(game, keys.LEFT, keys.RIGHT)
			if self.dx == 0:
				self.dy = _keyaxis(game, keys.UP, keys.DOWN)

			# blocked?
			if game.level.is_blocked(self.x + self.dx, self.y + self.dy):
				self.dx = 0
				self.dy = 0

		# update the sprite to the new pos.
		# todo: set anim frame
		self.sprite.x = self.x * 32 + self.ux
		self.sprite.y = -(self.y * 32 + self.uy)

class Game(object):
	def __init__(self):
		self.win = pyglet.window.Window()
		pyglet.clock.schedule(self.update)
		self.keys = keys.KeyStateHandler()
		self.win.push_handlers(self.keys)
		self.win.event(self.on_draw)
		self.at = 0.0
		self.objbatch = pyglet.graphics.Batch()

		self.actions = []
		self.actors = []
		self.level = tmx.TileMap('art/map.tmx')
		self.player = None
	
	def update(self, dt):
		# utterly standard time accumulator
		self.at += dt;
		while self.at > FRAME_TIME:
			self.at -= FRAME_TIME
			self.tick()

	def on_draw(self):
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glTranslatef(-player.sprite.x,-player.sprite.y,0)
		glTranslatef(self.win.width/2, self.win.height/2,0)
		self.win.clear()
		self.level.draw()
		self.objbatch.draw()

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
player = Player(game)
game.add_actor(player)
game.player = player
pyglet.app.run()

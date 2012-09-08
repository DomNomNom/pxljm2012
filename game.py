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

class Mover(object):
	def __init__(self, game, x, y):
		self.x = x; self.y = y
		self.ux = 0; self.uy = 0
		self.dx = 0; self.dy = 0
		self.rx = 1; self.ry = 0
		self.v = 1.7

		self.sprite = pyglet.sprite.Sprite(
			game.level.image_by_id(2),
			self.x * 32,
			-self.y * 32,
			batch=game.objbatch)

	def planmove(self, game):
		# default behavior isnt so interesting.
		pass

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
			self.planmove(game)

			if self.dx != 0 or self.dy != 0:
				self.rx = self.dx
				self.ry = self.dy

			# blocked?
			if game.level.is_blocked(self.x + self.dx, self.y + self.dy):
				self.dx = 0
				self.dy = 0

		# update the sprite to the new pos.
		# todo: set anim frame
		self.sprite.x = self.x * 32 + self.ux
		self.sprite.y = -(self.y * 32 + self.uy)

follow_dirs = [
		(0,1),
		(-1,0),
		(1,0),
		(0,-1)]

class PathFollower(Mover):
	# ai that follows invisible arrows
	def planmove(self, game):
		movecmd = game.level.get('ai_paths',self.x,self.y)
		if movecmd is None or movecmd == 0:
			# no move command in the map here.
			# just continue the direction we were going
			self.dx = self.rx
			self.dy = self.ry
			return
		basecmdid = game.level.sheets['AI']['firstgid']
		self.dx, self.dy = follow_dirs[movecmd - basecmdid]


class Player(Mover):
	# player plans move based on input
	def planmove(self, game):
		self.dx = _keyaxis(game, keys.LEFT, keys.RIGHT)
		if self.dx == 0:
			self.dy = _keyaxis(game, keys.UP, keys.DOWN)

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
		glTranslatef(int(-player.sprite.x),int(-player.sprite.y),0)
		glTranslatef(self.win.width/2, self.win.height/2,0)
		self.win.clear()
		self.level.draw()
		self.objbatch.draw()

	def tick(self):
		for a in self.actors: a.tick(self)
		actions = self.actions
		self.actions = []
		for a in actions: a()
		if self.keys[keys.ESCAPE]:
			print '%d,%d' % (self.player.x,self.player.y)
			pyglet.app.exit()

	def add_actor(self, a):
		self.actions.append(lambda:self.actors.append(a))
	
	def remove_actor(self, a):
		self.actions.append(lambda:self.actors.remove(a))

pyglet.resource.path = ['art']
pyglet.resource.reindex()
game = Game()

player = Player(game, 18, 29)
game.add_actor(player)
game.player = player

follower = PathFollower(game, 24, 32)
game.add_actor(follower)

pyglet.app.run()

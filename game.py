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
    def __init__(self, game, props):
        self.x = props['x']; self.y = props['y']
        self.ux = 0; self.uy = 0
        self.dx = 0; self.dy = 0
        self.rx = 0; self.ry = 0
        self.v = float(props.get('v','1.7'))

        gid = int(props.get('gid','2'))

        self.sprite = pyglet.sprite.Sprite(
            game.level.image_by_id(gid),
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
        (0,-1),
        (1,0),
        (0,1),
        (-1,0),
        None,
        None,
        None,
        (0,0)]

class PathFollower(Mover):
    def __init__(self,game,props):
        super(PathFollower,self).__init__(game,props)
        print 'PathFollower %s' % props

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

forms = {
        '1': {    # alien
            'can_move': True,
            'gid': 1160,
            'can_use': True,
            'trigger_camera': True,
             },
        '2': {    # box
            'can_move': False,
            'gid': 1222,
            'can_use': False,
            'trigger_camera': False,
            },
        }

class Player(Mover):
    def __init__(self,game,props):
        super(Player,self).__init__(game,props)
        game.player = self
        self.form_highlight_sprite = pyglet.sprite.Sprite(
                game.ui.image_by_id(5),
                0, 0,
                batch = game.uibatch)
        self._take_form('1')

    def _take_form(self, n):
        if not forms[n]['can_use']:
            return
        forms[n]['sprite'].visible = True # TODO
        self.sprite.image = game.level.image_by_id(forms[n]['gid'])
        self.can_move = forms[n]['can_move']
        self.form = n
        self.form_highlight_sprite.x = (int(n)-1) * 32
        self.trigger_camera = forms[n]['trigger_camera']

    # player plans move based on input
    def planmove(self, game):
        if self.can_move:    # only if in a form that can!! (not a box)
            self.dx = _keyaxis(game, keys.LEFT, keys.RIGHT)
            if self.dx == 0:
                self.dy = _keyaxis(game, keys.UP, keys.DOWN)

        # shapeshifting
        if game.keys[keys._1]: self._take_form('1')
        if game.keys[keys._2]: self._take_form('2')

        # camera detection
        if self.trigger_camera and game.level.get('observed',self.x,self.y) != 0:
            print 'observed by camera at %d,%d' % (self.x,self.y)

class FloorButton(Mover):
    # a 'button' on the floor that is triggered by stepping on it
    def __init__(self,game,props):
        self.flag = props['id']
        super(FloorButton,self).__init__(game,props)
        self.sprite.scale = 0
    
    def _actor_check(self,a):
        if type(a) in (FloorButton,Door):
            return False #LOLOL door on button...
        return True

    def tick(self, game):
        game.flags[self.flag] = any(a for a in game.actors \
            if (self._actor_check(a) and a.x == self.x and a.y == self.y))
        super(FloorButton,self).tick(game)

class Door(Mover):
    # a door which opens when triggered.
    def __init__(self,game,props):
        self.flags = props['buttons'].split(',')
        self.state = 0
        self.orig_gid = int(props['gid']) +2
        self.open_gid = self.orig_gid + 7
        super(Door,self).__init__(game,props)
    
    def tick(self, game):
        new_state = any(game.flags.get(f,False) for f in self.flags)
        open_state = new_state and 5 or 0
        self.state += _sign(open_state - self.state)
        self.sprite.image = game.level.image_by_id(self.orig_gid + self.state)
        game.level.set_blocked(self.x, self.y, self.state <= 2)
        super(Door,self).tick(game)

class FormPickup(Mover):
    def __init__(self,game,props):
        super(FormPickup,self).__init__(game,props)
        self.form = props['formID']

    def tick(self,game):
        super(FormPickup,self).tick(game)
        if game.player.x == self.x and game.player.y == self.y:
            game.remove_actor(self)
            forms[self.form]['can_use'] = True
            forms[self.form]['sprite'].visible = True
            print 'obtained form %s' % self.form
            # todo: some silly effect
            # show this stuff in UI

class Game(object):
    def __init__(self):
        self.win = pyglet.window.Window(resizable=True, fullscreen=False)
        pyglet.clock.schedule(self.update)
        self.keys = keys.KeyStateHandler()
        self.win.push_handlers(self.keys)
        self.win.event(self.on_draw)
        self.at = 0.0
        self.objbatch = pyglet.graphics.Batch()
        self.uibatch = pyglet.graphics.Batch()

        self.actions = []
        self.actors = []
        self.level = tmx.TileMap('art/map.tmx')
        self.ui = tmx.TileMap('art/UI.tmx')
        self.player = None
        self.flags = {}

        # init the UI sprites
        for formID, description in forms.iteritems():
            description['sprite'] = pyglet.sprite.Sprite(
                self.level.image_by_id(description['gid']),
                (int(formID)-1) * 32, # x
                0, # y
                batch=self.uibatch)
            description['sprite'].visible = False
            
    
    def update(self, dt):
        # utterly standard time accumulator
        self.at += dt;
        while self.at > FRAME_TIME:
            self.at -= FRAME_TIME
            self.tick()

    def on_draw(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(self.win.width/2, self.win.height/2,0)
        glScalef(2,2,1)
        glTranslatef(int(-self.player.sprite.x),int(-self.player.sprite.y),0)
        self.win.clear()
        self.level.draw()
        self.objbatch.draw()

        # UI
        glLoadIdentity()
        glScalef(2,2,1)
        
        self.ui.draw()
        self.uibatch.draw()
        

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

objtypes = {
        None : Mover,
        'playerSpawn': Player,
        'aiSpawn': PathFollower,
        'button': FloorButton,
        'door': Door,
        'playerForm': FormPickup,
        }

pyglet.resource.path = ['art']
pyglet.resource.reindex()
game = Game()

for obj in game.level.objects:
    factory = objtypes.get(obj['type'],None)
        
    if factory is None:
        print 'Unknown objecttype %s' % obj['type']
        continue
    game.add_actor(factory(game, obj))

pyglet.app.run()

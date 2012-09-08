import base64
from lxml import etree
import zlib
import struct
import StringIO
import array
import pyglet

class SaneImageGrid(object):
    # row 0 is the top one.
    # what pyglet tries to do is not sane, so transform the index
    def __init__(self, img, w, h):
        self.ig = pyglet.image.ImageGrid(img,h,w)
        self.w = w
        self.h = h

    def get(self, image_id):
        row = self.h - image_id / self.w - 1
        col = image_id % self.w
        return self.ig[row * self.w + col]

class TileMap:
    def image_by_id(self, image_id):
        ss = None
        last = -1
        for s in self.sheets.values():
            if s['firstgid'] <= image_id and s['firstgid'] > last:
                ss = s
                last = s['firstgid']
        if ss is None:
            raise Exception('bogus image id: %d' % image_id)
        return ss['image'].get(image_id - last)


    def __init__(self, filename):
        self.sheets = {}
        self.tiles = []
        self.layers = {}
        self.layers_ordered = []

        with open(filename,'r') as f:
            doc = etree.parse(f)
            mapNode = doc.xpath('/map')[0]

            for tsNode in doc.xpath('//tileset'):
                imageNode = tsNode.xpath('./image')[0]
                source = imageNode.attrib.get('source')
                print 'load tileset %s' % (source,)
                raw_image = pyglet.resource.image(source)
                self.sheets[tsNode.attrib.get('name')] = {
                        'firstgid': int(tsNode.attrib.get('firstgid')),
                        'image': SaneImageGrid(raw_image,
                            int(imageNode.attrib.get('width'))/32,
                            int(imageNode.attrib.get('height'))/32)
                        }

            for layerNode in doc.xpath('//layer'):
                dataNode = layerNode.xpath('./data')[0]
                data = dataNode.xpath('string()')
                if dataNode.attrib.get('encoding') != 'base64':
                    raise Exception('Unsupported encoding')
                if dataNode.attrib.get('compression') != 'zlib':
                    raise Exception('Unsupported compression')
                width = int(layerNode.attrib.get('width'))
                height = int(layerNode.attrib.get('height'))
                name = layerNode.attrib.get('name')

                unpacked = zlib.decompress(base64.decodestring(data))
                print 'layer %s %dx%d %d bytes' % (name, width, height, len(unpacked))
                arr = array.array('I')
                arr.fromstring(unpacked)

                batch = pyglet.graphics.Batch()
                for y in xrange(0,height):
                    for x in xrange(0,width):
                        if arr[y * width + x]:
                            self.tiles.append(pyglet.sprite.Sprite(
                                self.image_by_id(arr[y * width + x]),
                                x * 32,
                                -y * 32,
                                batch=batch))

                props = {}
                for propNode in layerNode.xpath('.//property'):
                    props[propNode.attrib.get('name')] = propNode.attrib.get('value')

                l = {
                        'width': width,
                        'height': height,
                        'data': arr,
                        'batch': batch,
                        'name': name,
                        'props': props
                        }
                self.layers[name] = l
                self.layers_ordered.append(l)

    def draw(self):
        for layer in self.layers_ordered:
            if layer['props'].get('visible','0') != '0':
                layer['batch'].draw()

    def get(self, layer, x, y):
        ll = self.layers[layer]
        if x < 0 or x >= ll['width'] or y < 0 or y >= ll['height']:
            return None
        return ll['data'][y*ll['width']+x]

    def is_blocked(self, x, y):
        c = self.get('collision',x,y)
        return c != 0

import base64
from lxml import etree
import zlib
import struct
import StringIO
import array
import pyglet

class TileMap:
    def image_by_id(self, image_id):
        ss = None
        last = -1
        for s in self.sheets.values():
            if s['firstgid'] < image_id and s['firstgid'] > last:
                ss = s
                last = s['firstgid']
        return ss['image'][image_id - last]


    def __init__(self, filename):
        self.sheets = {}
        self.tiles = {}
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
                        'image': pyglet.image.ImageGrid(raw_image,
                            int(imageNode.attrib.get('height'))/32,
                            int(imageNode.attrib.get('width'))/32)
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
                            pyglet.sprite.Sprite(
                                self.image_by_id(arr[y * width + x]),
                                x * 32,
                                y * 32,
                                batch=batch)

                l = {
                        'width': width,
                        'height': height,
                        'data': arr,
                        'batch': batch
                        }
                self.layers[name] = l
                self.layers_ordered.append(l)


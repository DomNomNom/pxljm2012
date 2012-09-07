import base64
from lxml import etree
import zlib
import struct
import StringIO
import array
import pyglet

class TileMap:
    def __init__(self, filename):
        self.sheets = {}
        self.tiles = {}
        self.layers = {}

        with open(filename,'r') as f:
            doc = etree.parse(f)
            mapNode = doc.xpath('/map')[0]

            for tsNode in doc.xpath('//tileset'):
                imageNode = tsNode.xpath('./image')[0]
                source = imageNode.attrib.get('source')
                print 'load tileset %s' % (source,)
                self.sheets[tsNode.attrib.get('name')] = {
                        'firstgid': int(tsNode.attrib.get('firstgid')),
                        'rowlen': int(imageNode.attrib.get('width'))/32,
                        'image': pyglet.resource.image(source)
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
                self.layers[name] = {
                        'width': width,
                        'height': height,
                        'data': arr,
                        }


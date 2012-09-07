import base64
from lxml import etree
import zlib

class TileMap:
    def __init__(self, filename):
        self.sheets = {}
        self.tiles = {}

        with open(filename,'r') as f:
            doc = etree.parse(f)
            mapNode = doc.xpath('/map')[0]

            for tsNode in doc.xpath('//tileset'):
                imageNode = tsNode.xpath('./image')[0]
                print 'load tileset %s' % (imageNode.attrib.get('source'))

            for layerNode in doc.xpath('//layer'):
                dataNode = layerNode.xpath('./data')[0]
                data = dataNode.xpath('string()')
                if dataNode.attrib.get('encoding') != 'base64':
                    raise Exception('Unsupported encoding')
                if dataNode.attrib.get('compression') != 'zlib':
                    raise Exception('Unsupported compression')

                unpacked = zlib.decompress(base64.decodestring(data))

from jpeg import JFIFFile
from bitbuffer import BitBuffer
from json import load
from tqdm import tqdm
from huffman import Huffman
import numpy as np
from random import randrange
from geneticalgorithm import geneticalgorithm as ga
from PIL import Image, ImageChops

def parse_frame(inputfile, config, dc_huffman0, dc_huffman1):
    with open(inputfile, "rb") as f:
        scandata = f.read()
    lstdata = [scandata[idx] for idx in range(len(scandata)) if (idx % 0x800) != 0]
    buffer = BitBuffer(bytearray(lstdata))
    j = JFIFFile(dict=config)
    filename = "output/test/index_{}.bmp".format(0)
    # j.DCHuffmanTables[0] = dc_huffman0
    # j.DCHuffmanTables[1] = dc_huffman1
    try:
        j.Decode(buffer, filename)
    except Exception as err:
        print(err)

def compare_images(img1, img2):
    diff = ImageChops.difference(img1, img2)
    sum = 0
    for x in range(diff.width):
        for y in range(diff.height):
            sum += sum(diff.getpixel(x, y))
    return sum

def generate_huffman_table_random_vals(id, size, lengths, codes):
    dc_huffman_dict = dict()
    dc_huffman_dict['Id'] = id
    dc_huffman_dict['TableType'] = 0
    dc_huffman_dict['Table'] = list()
    for i in range(size):
        huffval = dict()
        huffval['len'] = lengths[i]
        huffval['code'] = codes[i]
        huffval['binary'] = "{:0{}b}".format(codes[i], huffval['len'])
        huffval['value'] = randrange(16)
        huffval['hex'] = "{:02x}".format(huffval['value']).upper()
        dc_huffman_dict['Table'].append(huffval)
    dc_huffman0 = Huffman()

    dc_huffman0.FromDict(dc_huffman_dict)
    return dc_huffman0

def generate_huffman_table_random_codes(id, size, vals):
    dc_huffman_dict = dict()
    dc_huffman_dict['Id'] = id
    dc_huffman_dict['TableType'] = 0
    dc_huffman_dict['Table'] = list()
    for i in range(size):
        huffval = dict()
        huffval['len'] = randrange(16)
        huffval['code'] = randrange(256)
        huffval['binary'] = "{:0{}b}".format(huffval['code'], huffval['len'])
        huffval['value'] = vals[i]
        huffval['hex'] = "{:02x}".format(huffval['value']).upper()
        dc_huffman_dict['Table'].append(huffval)
    dc_huffman0 = Huffman()

    dc_huffman0.FromDict(dc_huffman_dict)
    return dc_huffman0    

if __name__ == '__main__':
    with open("config.json", "r") as f:
        config = load(f)

    num_entries0 = len(config['DHT']['AC'][0]['Table'])
    num_entries0 = len(config['DHT']['AC'][1]['Table'])
    
    lengths0 = [2, 3, 3, 3, 3, 3, 4, 5, 6, 7, 8, 9]
    codes0 = [0, 2, 3, 4, 5, 6, 14, 30, 62, 126, 254, 510]
    lengths1 = [2, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    codes1 = [0, 1, 2, 6, 14, 30, 62, 126, 254, 510, 1022, 2046]

    parse_frame("output/frame_0000.bin", config, generate_huffman_table_random_vals(0, 12, lengths0, codes0), generate_huffman_table_random_vals(1, 12, lengths1, codes1))
import sys
from jpeg import JFIFFile
from bitbuffer import BitBuffer
import json
from huffman import Huffman
import numpy as np
import random
from geneticalgorithm import geneticalgorithm as ga
from PIL import Image, ImageChops

with open("config.json", "r") as f:
    config = json.load(f)
target = Image.open("input/test.jpg")
image_index = 0

def parse_frame(inputfile, vals):
    with open(inputfile, "rb") as f:
        scandata = f.read()
    lstdata = [scandata[idx] for idx in range(len(scandata)) if (idx % 0x800) != 0]
    buffer = BitBuffer(bytearray(lstdata))
    randomize_ac_huffman_table_vals(config, vals)
    j = JFIFFile(dict=config)
    filename = "output/test/index_{}.bmp".format(image_index)
    try:
        j.Decode(buffer, filename)
        json.dump(config, open("output/test/index_{}_config.json".format(image_index), 'w'))
        return True
    except Exception as err:
        print(err)
        return False

def compare_images(img1, img2):
    diff = ImageChops.difference(img1, img2)
    val = 0
    for x in range(diff.width):
        for y in range(diff.height):
            val += sum(list(diff.getpixel((x, y))))
    return val

def generate_dc_huffman_table_random_vals(id, size, lengths, codes):
    dc_huffman_dict = dict()
    dc_huffman_dict['Id'] = id
    dc_huffman_dict['TableType'] = 0
    dc_huffman_dict['Table'] = list()
    for i in range(size):
        huffval = dict()
        huffval['len'] = lengths[i]
        huffval['code'] = codes[i]
        huffval['binary'] = "{:0{}b}".format(codes[i], huffval['len'])
        huffval['value'] = random.randrange(16)
        huffval['hex'] = "{:02X}".format(huffval['value']).upper()
        dc_huffman_dict['Table'].append(huffval)
    dc_huffman = Huffman()
    dc_huffman.FromDict(dc_huffman_dict)
    return dc_huffman

def randomize_ac_huffman_table_vals(config, vals):
    num_entries0 = len(config['DHT']['AC'][0]['Table'])
    for i in range(num_entries0):
        config['DHT']['AC'][0]['Table'][i]['value'] = int(vals[i])
        config['DHT']['AC'][0]['Table'][i]['hex'] = "{:02X}".format(int(vals[i]))
    num_entries1 = len(config['DHT']['AC'][0]['Table'])
    for i in range(num_entries1):
        config['DHT']['AC'][1]['Table'][i]['value'] = int(vals[i + num_entries0])
        config['DHT']['AC'][1]['Table'][i]['hex'] = "{:02X}".format(int(vals[i + num_entries0]))

def parse_frame_comparison(vals):
    global image_index
    casted_vals = vals.tolist()
    if parse_frame("output/frame_0000.bin", casted_vals):
        parsed = Image.open("output/test/index_{}.bmp".format(image_index))
        image_index += 1
        comparison = compare_images(target, parsed)
        print("{}: {}".format(image_index, comparison))
        return comparison
    else:
        return sys.maxsize

if __name__ == '__main__':
    num_entries0 = len(config['DHT']['AC'][0]['Table'])
    num_entries1 = len(config['DHT']['AC'][1]['Table'])
    total_entries = num_entries0 + num_entries1
    
    varbound=np.array([[0,255]]*total_entries)

    model = ga(function=parse_frame_comparison, dimension=total_entries, variable_type='int', variable_boundaries=varbound)

    model.run()
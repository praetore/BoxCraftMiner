# coding=utf-8
import hashlib
import re
import unicodedata

__author__ = 'darryl'


class BasePipeline(object):
    def __init__(self):
        with open('miner/validcolors.txt', 'r') as f:
            self._validcolors = [i.rstrip() for i in f]

        with open('miner/formfactors.txt', 'r') as f:
            self._validformfactors = [i.rstrip() for i in f]

    def generate_id(self, item, spider):
        itemstring = spider.name + item['name'] + item['manufacturer']
        return hashlib.sha1(itemstring).hexdigest()

    def cleanup_field(self, itemfield):
        if isinstance(itemfield, list):
            itemfield = itemfield[0]
        itemfield = unicodedata.normalize('NFD', itemfield)
        return itemfield.encode('ascii', errors='ignore').strip().replace('  ', ' ').decode('ascii')

    def validate_price(self, itemfield):
        itemfield = self.cleanup_field(itemfield)
        itemfield = itemfield.replace('-', '0')
        itemfield = itemfield.replace(' ', '')
        itemfield = itemfield.replace('.', '')
        itemfield = itemfield.replace(',', '.')
        return float(itemfield)

    def validate_numerical(self, itemfield):
        itemfield = self.cleanup_field(itemfield)
        return int(re.sub("[^0-9]", "", itemfield))

    def get_memory_type(self, itemfield):
        itemfield = self.cleanup_field(itemfield)
        return re.search(r'DDR\d*-\d+', itemfield).group()

    def get_gpu_memory_amount_type(self, itemfield, group):
        itemfield = self.cleanup_field(itemfield)
        return re.match(r'^(\d+ [G|M]B) \((\w+)', itemfield).group(group)

    def get_bay_type_amount(self, itemfield, search):
        fields = [[word for word in sent.split(' ') if word != 'inch']
                  for sent in self.cleanup_field(itemfield).split(', ')]
        for entry in fields:
            entry[2] = re.sub(r'e$', '', entry[2])

        search = search.split(' ')
        for entry in fields:
            if search[0] == entry[1]:
                if len(search) > 1:
                    if search[1] == entry[2]:
                        return self.validate_numerical(entry[0])
                else:
                    return self.validate_numerical(entry[0])
        return 0

    def validate_colors(self, colorstring, validcolors):
        colors = [color for color in self.cleanup_field(colorstring).split('/')
                  if self.validate_single_color(color, validcolors)]
        if not len(colors):
            return ['Zwart']
        return colors

    def validate_single_color(self, colorstring, validcolors):
        if ' ' in colorstring:
            color = colorstring.split(' ')
            if len(color) > 1:
                for i in color:
                    if i in validcolors:
                        return True
        else:
            if colorstring in validcolors:
                return True
            return False

    def validate_mobo_psu(self, mobopsustring):
        mobopsustring = self.cleanup_field(mobopsustring)
        if not mobopsustring:
            return 'Ingebouwd'
        return mobopsustring

    def validate_formfactor(self, mobofostring):
        mobofostring = "".join(mobofostring).replace(u'µ', 'u')
        mobofostring = [i.lstrip() for i in self.cleanup_field(mobofostring).split(',')
                        if i.lstrip() in self._validformfactors]
        if not len(mobofostring):
            return ['Onbekend']
        else:
            return mobofostring
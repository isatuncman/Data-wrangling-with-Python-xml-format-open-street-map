# Importing file

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
OSM_FILE = "/Users/isatuncman/Documents/Udacity/data-wrangling/udacity-data-wrangling-project/tampa_florida.osm"  # Replace this with your osm file
SAMPLE_FILE = "/Users/isatuncman/Documents/Udacity/data-wrangling/udacity-data-wrangling-project/sample_tampa.osm"
k = 40 # Parameter: take every k-th top level element

# Sample the dataset.
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')

# Audit specific keys
def investigate_specific_key(filename, word, tag):
    tag_list = []
    for number, element in ET.iterparse(filename):
        if element.tag == tag:
            for item in element:
                    item_dict = {}
                    key = item.attrib['k']
                    if key.startswith(word):
                        item_dict[key] = item.attrib['v']
                        tag_list.append(item_dict)
    return tag_list

print investigate_specific_key(SAMPLE_FILE, 'gnis', 'node')
print investigate_specific_key(SAMPLE_FILE, 'addr:street', 'node')
print investigate_specific_key(SAMPLE_FILE, 'addr:postcode', 'node')
print investigate_specific_key(SAMPLE_FILE, 'addr:state', 'node')
print investigate_specific_key(SAMPLE_FILE, 'addr:housenumber', 'node')
print investigate_specific_key(SAMPLE_FILE, 'amenity', 'node')

# Modified investigate key function to investigate way_tags
def investigate_specific_key_way(filename, word):
    tag_list = []
    for number, element in ET.iterparse(filename):
        if element.tag == 'way':
            for item in element:
                if item.tag == 'tag':
                    item_dict = {}
                    key = item.attrib['k']
                    if key.startswith(word):
                        item_dict[key] = item.attrib['v'] # return key-value pairs
                        tag_list.append(item_dict)
    return tag_list

print investigate_specific_key_way(SAMPLE_FILE, 'tiger')
print investigate_specific_key_way(SAMPLE_FILE, 'addr:street')
print investigate_specific_key_way(SAMPLE_FILE, 'addr:housenumber')
print investigate_specific_key_way(SAMPLE_FILE, 'addr:postcode')

# Clean gnis dataset

# map to change gnis names
map_gnis = {'gnis:id': 'gnis:feature_id', 'gnis:ST_num': 'gnis:state_id', 'gnis:County': 'gnis:county_name', 'gnis:County_num': 'gnis:county_id'}

# change names function
def change_name(name, mapping):
    for key in mapping:
        if name == key:
            return mapping[key]
        else:
            return name

# postal code update function
def postal_code_cleaner(postcode):
    return postcode[:5]

# house number cleaner function
def house_number_cleaner(housenumber):
    a = housenumber.find(' ')
    if a >=1 and len(housenumber[a:]) >1 :
        return housenumber[:a]
    else:
        return housenumber.strip()

''' Audit all street names functions. These codes are adopted from case study'''

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = SAMPLE_FILE
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", "Circle", "Highway",]

# General Audit Function
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

# Evaluate the keys, which are street names.
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

# Audit all tags and return street types
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

audit(SAMPLE_FILE)


street_mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "Rd" : "Road",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "BLVD": "Boulevard",
            "Cir": "Circle",
            "Dr" : "Drive",
            "Hwy": "Highway",
            "Pl": "Plaza",
            "S": "South",
            "N": "North",
            "N.": "North",
            "E" : "East",
            "S.": "South",
            "E.": "East",
            "W": "West",
            "W.": "West",
            "SE": "Southeast",
            "NE": "Northeast"}


# Update street names without using regular expressions. Adopted from sample Sql project.
def update(name, mapping):
    words = name.split()
    for w in range(len(words)):
        if words[w] in mapping:
            if words[w].lower() not in ['suite', 'ste.', 'ste']:
                # For example, don't update 'Suite E' to 'Suite East'
                words[w] = mapping[words[w]]
    name = " ".join(words)
    return name

# Test : Test for all sample street names adopting pre-written investigate_specific_key function:
def investigate_specific_key_values(filename, word):
    tag_list = []
    for number, element in ET.iterparse(filename):
        if element.tag == 'way' or element.tag == 'node':
            for item in element:
                if item.tag == 'tag':
                    key = item.attrib['k']
                    if key.startswith(word):
                        tag_list.append(item.attrib['v'])
    return tag_list

address_list = investigate_specific_key_values(SAMPLE_FILE, "addr:street")
result = []
for address in address_list:
    result.append(update(address, street_mapping))

print result


# Clean all the data combining all the functions Combined for data process at once.
def clean_all(element):
    ''' Clean and update gnis keys, street names, postcodes, housenumbers using predefined functions'''
    if element.tag == 'way' or element.tag == 'node':
        for item in element:
            if item.tag == 'tag':
                key = item.attrib['k']
                if key.startswith('gnis'):
                    item.attrib['k'] = change_name(key, map_gnis)
                if key =='addr:postcode':
                    value = item.attrib['v']
                    item.attrib['v'] = postal_code_cleaner(value)
                if key =='addr:housenumber':
                    value = item.attrib['v']
                    item.attrib['v'] = house_number_cleaner(value)
                if key == 'addr:street':
                    value = item.attrib['v']
                    item.attrib['v'] = update(value, street_mapping)

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

#Paths: To test and validate the sample data first, sample db is constructed
OSM_PATH = SAMPLE_FILE
NODES_PATH = "sample1_nodes.csv"
NODE_TAGS_PATH = "sample1_nodes_tags.csv"
WAYS_PATH = "sample1_ways.csv"
WAY_NODES_PATH = "sample1_ways_nodes.csv"
WAY_TAGS_PATH = "sample1_ways_tags.csv"
SCHEMA = schema.schema

#Fields
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Shape function was adopted from case study
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    if  element.tag == 'node':
        for entity in NODE_FIELDS:
            node_attribs[entity] = element.attrib[entity]

        for tag in element:
            tag_attribs = {}
            tag_attribs['id'] = element.attrib['id']
            tag_attribs['value'] = tag.attrib['v']
            if problem_chars.search(tag.attrib['k']):
                continue
            if tag.attrib['k'].find(':') >=0:
                end = tag.attrib['k'].find(':')
                tag_attribs['type'] = tag.attrib['k'][0:end]
                tag_attribs['key'] = tag.attrib['k'][end+1:]
            else:
                tag_attribs['key'] = tag.attrib['k']
                tag_attribs['type'] = default_tag_type
            tags.append(tag_attribs)

        return {'node': node_attribs, 'node_tags': tags}

    if  element.tag == 'way':
        position =0
        for entity in WAY_FIELDS:
             way_attribs[entity] = element.attrib[entity]

        for tag in element:
            if tag.tag =='tag':
                tag_attribs = {}
                tag_attribs['id'] = element.attrib['id']
                tag_attribs['value'] = tag.attrib['v']
                if problem_chars.search(tag.attrib['k']):
                    continue
                if tag.attrib['k'].find(':') >=0:
                    end = tag.attrib['k'].find(':')
                    tag_attribs['type'] = tag.attrib['k'][0:end]
                    tag_attribs['key'] = tag.attrib['k'][end+1:]
                else:
                    tag_attribs['key'] = tag.attrib['k']
                    tag_attribs['type'] = default_tag_type
                tags.append(tag_attribs)

            else:
                way_node_attribs = {}
                way_node_attribs['id'] = element.attrib['id']
                way_node_attribs['node_id'] = tag.attrib['ref']
                way_node_attribs['position'] = position
                position +=1
                way_nodes.append(way_node_attribs)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# Helper get_elment function from case study
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# Helper validate function: (I will only for use on sample data)
def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))

# Helper extended csv writer function
class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# Process map main function adopted and modified to include clean_all function.
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            clean_all(element) # Cleaning is done here just before extracting the data into csv files.
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

process_map(SAMPLE_FILE, validate=True)

# No problem in SAMPLE FILES, so work on real full data

#Paths
OSM_PATH = OSM_FILE
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"
SCHEMA = schema.schema

# All processing is done at once
process_map(OSM_FILE, validate=False)

# Importing csv files into database via DB-API
import sqlite3
import csv
from pprint import pprint

sqlite_file = 'tampaosm.db

# Import node_tags file
conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()
cur.execute('''DROP TABLE IF EXISTS nodes_tags''')
conn.commit()
cur.execute('''CREATE TABLE nodes_tags(id INTEGER, key TEXT, value TEXT, type TEXT, FOREIGN KEY (id) REFERENCES nodes(id))''')
conn.commit()

with open('nodes_tags.csv','rb') as f:
    dr = csv.DictReader(f) # comma is default delimiter
    to_db = [(i['id'], i['key'],i['value'].decode("utf-8"), i['type']) for i in dr]

cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()


#Import nodes.csv file
cur.execute('''DROP TABLE IF EXISTS nodes''')
conn.commit()

cur.execute('''CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
)''')

conn.commit()

with open('nodes.csv','rb') as f:
    dr = csv.DictReader(f) # comma is default delimiter
    to_db = [(i['id'], i['lat'],i['lon'], i['user'].decode("utf-8"), i['uid'], i['version'], i['changeset'], i['timestamp'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()



# Import ways.csv into database
cur.execute('''DROP TABLE IF EXISTS ways''')
conn.commit()

cur.execute('''CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT)''')
conn.commit()

with open('ways.csv','rb') as f:
    dr = csv.DictReader(f) # comma is default delimiter
    to_db = [(i['id'], i['user'].decode("utf-8"),i['uid'], i['version'].decode("utf-8"), i['changeset'],i['timestamp'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()



# Import ways_tags.csv into database
cur.execute('''DROP TABLE if exists ways_tags''')
conn.commit()

cur.execute('''CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id))''')
conn.commit()

with open('ways_tags.csv','rb') as f:
    dr = csv.DictReader(f) # comma is default delimiter
    to_db = [(i['id'], i['key'].decode("utf-8"),i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]

cur.executemany("INSERT INTO ways_tags(id, key, value, type) VALUES (?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()



# Import ways_nodes.csv into database
cur.execute('''DROP TABLE if exists ways_nodes''')
conn.commit()

cur.execute('''CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id))''')
conn.commit()

with open('ways_nodes.csv','rb') as f:
    dr = csv.DictReader(f) # comma is default delimiter
    to_db = [(i['id'], i['node_id'], i['position']) for i in dr]

cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db)
# commit the changes
conn.commit()
conn.close()

# Importing csv files is complete.

#!/usr/bin/python
# pprint(vars(item.text))
import re
import requests
from pprint import pprint
import sys
import json
import pathlib
from include.XmlExport import XmlExport
from include.HtmlParser import HtmlParser

this_dir = str(pathlib.Path(__file__).parent.resolve())
base_url = 'https://www.joesnewbalanceoutlet.com'
cats_path = this_dir + '/cats.txt'
products_path = this_dir + '/products.txt'
template_path = this_dir + "/templates/template.xml"
export_path = this_dir + "/feed.xml"


parser = HtmlParser(base_url)

# parser.parseCategoriesUrls(cats_path)
# parser.parseProductsUrls(cats_path, products_path)

products, categories = parser.parse(products_path)

export = XmlExport(template_path, export_path)
export.writeToXML(products, categories)
# print(json.dumps(product, sort_keys=True, indent=4))

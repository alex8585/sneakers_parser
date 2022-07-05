from xml.dom.minidom import parse, parseString
import itertools

import sys
class XmlExport:
    def __init__(self, template_path, export_path):
        self.template_path = template_path
        self.export_path = export_path

    def getPrittyStr(self, root):
        xml_str = root.toprettyxml(indent='    ', newl='\n')
        xml_strings_arr = [
            elem for elem in xml_str.split("\n") if elem.strip()]
        return '\n'.join([s for s in xml_strings_arr])

    def writeXmlToFile(self, root):
        xml_string = self.getPrittyStr(root)
        with open(self.export_path, "w") as file:
            file.write(xml_string)

    def createOffer(self, dom, product, product_id, product_variant):
        # print(product_variant)
        # sys.exit()
        size,width = product_variant
        offer = dom.createElement('offer')
        offer.setAttribute('id', str(product_id))
        offer.setAttribute('available', product['available'])
        for product_field in product:
            if(product_field in ['sizes', 'widths', 'images']):
                continue

            
            value = product[product_field]
            if(product_field == 'name'):
                if(size):
                    value += " "+size
                if(width):
                    value += " "+width

            if(product_field in ['name', 'description']):
                textElem = dom.createCDATASection(value)
            else:
                textElem = dom.createTextNode(value)

            valueElem = dom.createElement(product_field)
            valueElem.appendChild(textElem)
            offer.appendChild(valueElem)

        for img_url in product['images']:
            imgElem = dom.createElement('picture')
            imgValue = dom.createTextNode(img_url)
            imgElem.appendChild(imgValue)
            offer.appendChild(imgElem)

        
        if(size):
            size_elem = dom.createElement('param')
            size_elem.setAttribute('name', 'size')
            size_elem.appendChild(dom.createTextNode(size))
            offer.appendChild(size_elem)

        if(width):
            width_elem = dom.createElement('param')
            width_elem.setAttribute('name', 'width')
            width_elem.appendChild(dom.createTextNode(width))
            offer.appendChild(width_elem)

        return offer

    def createCategory(self, dom, category):
        cat_node = dom.createElement('category')
        textElem = dom.createCDATASection(category['name'])
        cat_node.setAttribute('id', str(category['id']))
        if(category['parent_id'] > 0):
            cat_node.setAttribute('parentId', str(category['parent_id']))
        cat_node.appendChild(textElem)

        return cat_node

    def writeToXML(self, products, categories):
        dom = parse(self.template_path)
        root = dom.documentElement
        offers = root.getElementsByTagName("offers")[0]
        cats_container = root.getElementsByTagName("categories")[0]

        product_id = 1
        for product in products:
            
            if(product['sizes'] and product['widths']):
                for product_variant in itertools.product(product['sizes'], product['widths']):
                    offer = self.createOffer(dom, product, product_id,product_variant)
                    offers.appendChild(offer)
                    product_id += 1

            elif(product['sizes']):
                for size in product['sizes']:
                    product_variant = (size,None)
                    offer = self.createOffer(dom, product, product_id,product_variant)
                    offers.appendChild(offer)
                    product_id += 1

            elif(product['widths']):
                for width in product['widths']:
                    product_variant = (None,width)
                    offer = self.createOffer(dom, product, product_id,product_variant)
                    offers.appendChild(offer)
                    product_id += 1
            else:
                product_variant = (None,None)
                offer = self.createOffer(dom, product, product_id,product_variant)
                offers.appendChild(offer)
                product_id += 1

        for cat_url in categories:
            category_node = self.createCategory(
                dom, categories[cat_url])
            cats_container.appendChild(category_node)

        self.writeXmlToFile(root)

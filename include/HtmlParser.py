from xml.dom.minidom import parse, parseString
from bs4 import BeautifulSoup as bs
import requests

import sys


class HtmlParser:
    def __init__(self, base_url):
        self.base_url = base_url

    def parseCategoriesUrls(self, cats_path):
        html_string = requests.get(self.base_url).text
        soup = bs(html_string, "html.parser")
        cats_urls = soup.select('h3 a')
        unic_urls = {url['href'] for url in cats_urls}
        with open(cats_path, 'w') as fp:
            for url in unic_urls:
                fp.write("%s\n" % (self.base_url + url))

    def getPageProducts(self, soup):
        prod_urls = soup.findAll('a', class_='impression')
        unic_urls = [url['href'] for url in prod_urls]
        return unic_urls

    def parseProductsUrls(self, cats_path, products_path):
        with open(cats_path) as f:
            cats = [line.rstrip() for line in f]

        products_urls = set()
        for cat in cats:
            cat_url = cat + '?pageSize=60'
            html_string = requests.get(cat_url).text
            soup = bs(html_string, "html.parser")
            # print(cat)
            paging_total_elem = soup.find('span', class_="pagingTotal")
            if(paging_total_elem):
                paging_total = paging_total_elem.text
            else:
                continue
            pages = int(((int(paging_total) - 1) / 60) + 1)

            urls = self.getPageProducts(soup)
            products_urls.update(urls)
            if(pages > 1):
                for page in range(2, pages+1):
                    html_string = requests.get(cat_url + f'&page={page}').text
                    soup = bs(html_string, "html.parser")
                    urls = self.getPageProducts(soup)
                    products_urls.update(urls)

        with open(products_path, 'w') as fp:
            for url in products_urls:
                fp.write("%s\n" % (self.base_url + url))

    def parseProduct(self, soup, url, category_id):
        soup_product = soup.find(id="ProductDetailPage")
        # print(soup_product)

        widthsLinks = []
        widthsLinksSoup = soup_product.find('div', {'data-name': "width"})
        if(widthsLinksSoup):
            widthsLinks = widthsLinksSoup.findAll('label')

        sizesLinks = []
        sizesLinksSoup = soup_product.find('div', {'data-name': "size"})
        if(sizesLinksSoup):
            sizesLinks = sizesLinksSoup.findAll('a')
            if(not sizesLinks):
                sizesLinks = sizesLinksSoup.findAll(class_="selectedValue")


        origPriceSoup = soup_product.find('span', class_="origPrice")
        origPrice = ''
        if(origPriceSoup):
            origPrice = origPriceSoup.find('span')
            origPrice = origPrice.text.strip()[1:]

        imagesElems = soup_product.findAll('a', class_="fancybox")
        if(imagesElems):
            images = [elem['href'] for elem in imagesElems]
        else:
            imagesElem = soup_product.find(id="ProductImage").find(itemprop="image") 
            images = [imagesElem['src']]

        description = ''
        description_node = soup_product.find('p', itemprop="description")
        if(description_node):
            description=description_node.text.strip()
        # sys.exit()
        color =''
        color_node = soup_product.find('span', id="DisplayColor")
        if(color_node):
            color = color_node.text

        sku = soup_product.find('span', id="Sku").text
        name = soup_product.find('h1', itemprop="name").text + f' ({sku})'
        product = {
            'categoryId': str(category_id),
            'url': url,
            "currencyId": "UAH",
            "stock_quantity": "100",
            'name':name ,
            'color':color ,
            'gender': soup_product.find('input', {'name': "Gender"})['value'],
            'vendor': soup_product.find('input', {'name': "Brand"})['value'],
            'available': soup_product.find('input', {'name': "IsAvailable"})['value'],
            'sku': sku,
            'price': soup_product.find('span', itemprop="price").text,
            'orig-price': origPrice,
            'description': description,
            "sizes": [link.text for link in sizesLinks],
            "widths": [elem.text.strip() for elem in widthsLinks],
            "images": images,
        }

        return product

    def getProductCats(self, soup, id, categories):
        breadcrumps = soup.find(id="Breadcrumbs").findAll('a')
        categories_urls = [a['href'] for a in breadcrumps]
        parent_id = 0
        for cat_url in categories_urls:
            if(cat_url in categories):
                parent_id = categories[cat_url]['id']
            else:
                id += 1
                name = soup.find('a', href=cat_url).text.strip()

                categories[cat_url] = {'name': name,
                                       'id': id, 'parent_id': parent_id}
                parent_id = id
        return [id, categories]

    def parse(self, products_path):
        with open(products_path) as f:
            products_urls = [line.rstrip() for line in f]

        products = []
        categories = {}
        cat_id = 0
        for product_url in products_urls:
            print(product_url)

            html_string = requests.get(product_url).text
            soup = bs(html_string, "html.parser")

            cat_id, categories = self.getProductCats(soup, cat_id, categories)
            product = self.parseProduct(soup, product_url, cat_id)
            products.append(product)

        # print(categories)
        # print(products)

        return [products, categories]

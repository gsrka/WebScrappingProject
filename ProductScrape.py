from lxml import html
from bs4 import BeautifulSoup, NavigableString
import requests
import AmazonConnector as amazon
import pymongo


def getProductBySearchKey(search):
    search = search
    productDict = amazon.getProductURLArray(search)
    productData = {}
    rowdetails = {}
    valid = 200
    count = 0
    for productAsin in productDict:
        #fetch iframeURL and fetch all review page url
        count += 1

        print("PRODUCT[ASIN]: " + productAsin)
        productData[productAsin.text.strip(".com")] = []

        status_code = -1
        page = requests.get(productDict[productAsin])
        while(status_code != valid):
            #print(productDict[productAsin])
            page = requests.get(productDict[productAsin])
            status_code = page.status_code

        tree = html.fromstring(page.content)

        productdescription = tree.xpath(".//div[@id='productDescription']//p/text()")
        #print("Product Description: ", productdescription)
        if(len(productdescription) > 0):
            productdescription = productdescription[0].strip()
        else:
            productdescription = ""

        productDeatilsTable = tree.xpath(".//table[@id='productDetails_detailBullets_sections1']")
        if productDeatilsTable:
            if (len(productDeatilsTable) > 0):
                productAttributeRows = productDeatilsTable[0].xpath(".//tr")
                productData[productAsin.text.replace('.com','')].append({'Product Description': productdescription})
                rowdetails = {}
                for row in productAttributeRows:
                    th = row.xpath(".//th/text()")[0].strip().replace('.com','')
                    td = row.xpath(".//td/text()")[0].strip().strip("(")
                    rowdetails[th] = td
                #print rowdetails
                #p_id = p.insert(rowdetails)
                productAsinString = productAsin.text.replace('.com','')
                productData[productAsinString].append(rowdetails)
                print(productData[productAsin])

        else:
            soup = BeautifulSoup(html.tostring(tree))
            htmlExtract = soup.findAll("table", {"id" : "productDetailsTable"})
            try:
                if htmlExtract:
                    htmlScrape = soup.select("table tr td ul li b")
                    #print(htmlScrape)
                    for i in htmlScrape:
                        rowdetails[(i.text).strip(":").strip("\n").strip().replace('.com','')] = (i.next_sibling).strip().strip("\n").strip("(")
                        #print ((i.text).strip(":").strip("\n").strip(),(i.next_sibling).strip().strip("\n").strip("("))
                        if (i.next_sibling).strip().strip("\n").strip("(") == '':
                            for temp in i.next_siblings:
                                #print h.findNext('span',class_='a-icon-alt').text
                                rowdetails[(i.text).strip(":").strip("\n").strip().replace('.com','')] = temp.findNext('span',class_='a-icon-alt').text
                                break
            except AttributeError:
                productAsinString = productAsin.text.replace('.com','')
                productData[productAsinString].append(rowdetails)
                print(productData[productAsin])

    connection = pymongo.MongoClient("mongodb://localhost:27017/");
    db = connection.Products
    p = db.electronicsProducts
    print productData
    p.insert(productData)
    return rowdetails

data = getProductBySearchKey("iphone")
#print(len(data))
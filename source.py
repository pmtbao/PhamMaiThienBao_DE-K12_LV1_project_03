from platform import system
from bs4 import BeautifulSoup as bs
import requests as re
import time
import random
import base64
import urllib.request
import logging
from pymongo import MongoClient

if __name__ == "__main__":

    # Set logging
    logging.basicConfig(filename='app.log',style="{", datefmt=f"%Y-%m-%d %H:%M", level=logging.DEBUG, format="{asctime} - {levelname} - {message}")
    
    # get links catalouge
    url = "https://www.glamira.com/jewelry/"
    response = re.get(url)
    soup = bs(response.content, "html.parser")
    results = soup.select('div[data-content-type = "button-item"] a.pagebuilder-button-link')
    links = []
    for r in results:
        links.append(r.get("href"))
    
    
    image_links = []

    images = []
    # Loop link 
    for link in links:
        # set param: page
        param = {'p':1}
        i = 1
        # Dung BS + request de truy cap link va lay tong so san pham
        logging.info(f"Getting link: {link}")
        response = re.get(link, params=param)
        soup = bs(response.content, "html.parser")
        result_interlligent_search = soup.select_one('span.result-interlligent-search')

        if (result_interlligent_search is not None):
            result_interlligent_search = result_interlligent_search.text
            
            logging.info(f"Products found: {result_interlligent_search}")
            time.sleep(random.uniform(1,3))
            
            # Loop page (60 products/page)
            try: 
                while (i*60 < int(result_interlligent_search) + 60):
                    # Dung BS + request de truy cap link va lay link san pham
                    param["p"] = i
                    response = re.get(link, params=param)
                    soup = bs(response.content, "html.parser")
                    results = soup.select('div.product-item-details a')
                    # Loai bo cac san pham khong co link do khac page
                    for r in results[(i-1)*60:]:
                        image_links.append(r.get("href"))

                    logging.info(f"Get more {len(results[(i-1)*60:])} links from {(i-1)*60}")
                    i+=1
                    time.sleep(random.uniform(2,5))
            except Exception:
                logging.error( f" Error: {Exception} form page {i} - link {link}")
                with open ("fail_link.txt", "a") as f:
                        f.write(f"page {i} - {link}\n")
                f.close()
            
            logging.info("Back-up image_links")

            # Save image_links to back-up
            with open("image_links.txt", "w") as f:
                id = 1
                for image_link in image_links:
                    f.write(f"{id}\t" + image_link + "\n")
                    id+=1
            f.close()

            logging.info(f"Get product-links from: {link} SUCCESS!!")
            logging.info(f"Start crawling images...")
            # Setup MongoDB connection
            try:
                client = MongoClient("mongodb://localhost:27017/")
                db = client["dec-k12-project03"]
                collection = db["images"]
                logging.info("Connect MongoDB SUCCESS!!")
            except Exception:
                logging.error(f"Error: {Exception}")
                flag = input("Connect MongoDB server fail (press any keyboard to continue):")
            # Loop link san pham
            #img_base64 = []
            for image_link in image_links:
                error_image = ''
                try:
                # Dung BS + request de truy cap link va lay link anh
                    response = re.get(image_link)
                    soup = bs(response.content, "html.parser")
                    images = soup.find('div', class_ = "gallery-main")
                    images = images.find_all('img')

                    for image in images:
                        src = image.get("srcset")
                        src = src.split(", ")[1]
                        src = src.split(" ")[0]
                        a = urllib.request.urlretrieve(src,'img')
                        error_image = src
                        with open("img", "rb") as image2string:
                            # img to base64
                            converted_string = base64.b64encode(image2string.read())
                            #img_base64.append(converted_string)
                            # Save image in MongoD
                            collection.insert_one({"img" : f"{converted_string}",
                                                   "src" : f"{src}"})
                    logging.info(f"Save {image_link} SUCCESS!!!")
                            
                    time.sleep(random.uniform(1,5))
                except Exception:
                    logging.error(f"Error: {Exception} - from image_link {image_link}")
                    logging.error(f"Error: {Exception} - from image {error_image}")
                    with open ("fail_image_link.txt", "a") as f:
                        f.write(image_link + "\t" + error_image + "\n")
                    f.close()
            
            #images.append(img_base64)

            # Close connect
            try:
                client.close()
            except Exception:
                continue

            logging.info("MongoDB is closed")
            logging.info(f"Get image from {link} SUCCESS!!")
        else:
            logging.warning(f"Get link: {link} FAILED!!!")
            logging.warning(f"Reason: No field 'result_interlligent_search'")

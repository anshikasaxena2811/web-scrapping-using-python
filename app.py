from flask import Flask
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
from flask import request
from flask import render_template
import requests
from flask_cors import CORS,cross_origin
import pymongo

client1=pymongo.MongoClient("mongodb+srv://anshikasaxena2811:dv5118tx@cluster0.sftlm9o.mongodb.net/?retryWrites=true&w=majority")
db=client1.test
db=client1["my_data"]
coll=db["my_collection"]

logging.basicConfig(filename="/config/workspace/web_scrapping/scrapping.log",level=logging.INFO)
app=Flask(__name__)

@app.route("/",methods=["GET","POST"])
def home_page():
    return render_template("index.html")

@app.route("/review",methods=["GET","POST"])
def scrapping():
    if request.method=="POST":
        try:
            product=request.form["content"].replace(" ","")
            url="https://www.flipkart.com/search?q="+product
            logging.info(url)
            client=urlopen(url)
            info=client.read()
            client.close()
            page=bs(info,"html.parser")
            pro=page.find_all("div", {"class":"_1AtVbE col-12-12"})
            del pro[0:2]
            reviews=[]
            try:
                for j in pro:
                    link="https://www.flipkart.com"+j.div.div.div.a['href']
                    logging.info(link)
                    my_client=requests.get(link)
                
                    my_page=bs(my_client.text,"html.parser")
                    product_name=my_page.find("div",{"class":"aMaAEs"}).div.text
                    review=my_page.find_all("div",{"class":"_16PBlm"})
                    
                    for i in review:
                        try:
                        
                            name = i.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                        except:
                            logging.info("name is {}".format(name))
                        
                        try:
                            rating=i.div.div.div.div.text

                        except :
                            logging.info("rating is {}".format(rating))

                        try:
                            comment_head=i.div.div.div.p.text
                        except :
                            logging.info("comment head is {}".format(comment_head))


                        try:
                            comment=i.div.div.find_all("div",{"class":"row"})[1].div.div.div.text
                        except :
                            logging.info("comment is {}".format(comment))

                        mydict = {"Product": product_name, "Name":name, "Rating": rating, "CommentHead": comment_head,"Comment": comment}
                        reviews.append(mydict)

            except Exception as t:
                logging.info(t)

                    
        
            coll.insert_many(reviews)
            logging.info("reviews are {}".format(reviews))
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        
        
        except Exception as e:
            logging.info(e)
        
        

    else:
        return render_template('index.html')




if __name__=="__main__":
    app.run(host="0.0.0.0")
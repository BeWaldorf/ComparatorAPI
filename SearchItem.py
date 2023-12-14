

class SearchItem():
    def __init__(self, name, price, image_link, delivery_price, link):
        self.name : str = name
        self.price : str = price
        self.image_link : str = image_link
        self.delivery_price : str = delivery_price
        self.link : str = link

    def serializer(self)->dict:
        return {
            "name": self.name,
            "price": self.price,
            "image_link": self.image_link,
            "delivery_price": self.delivery_price
        }

    def getName(self):
        return self.name

    def getPrice(self):
        return self.price

    def getLink(self):
        return self.link
    
    def getImageLink(self):
        return self.image_link
    
    def getDeliveryPrice(self):
        return self.delivery_price

    def __str__(self):
        return "Name: " + self.name + "\nPrice: " + self.price + "\nLink: " + self.link + "\n"
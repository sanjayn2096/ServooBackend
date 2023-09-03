class FoodMenuItem:
    def __init__(self, restaurant_id, item_name, price,
                 description, image_url, stock_status,
                 number_of_times_ordered):
        self.restaurant_id = restaurant_id
        self.item_name = item_name
        self.price = price
        self.description = description
        self.image_url = image_url
        self.stock_status = stock_status
        self.number_of_times_ordered = number_of_times_ordered

    def to_dict(self):
        # Convert the object attributes to a dictionary
        return {
            "restaurant_id": self.restaurant_id,
            "item_name": self.item_name,
            "price": self.price,
            "description": self.description,
            "image_url": self.image_url,
            "stock_status": self.stock_status,
            "number_of_times_ordered": self.number_of_times_ordered
        }

    @classmethod
    def from_dict(cls, data_dict):
        # Create a new instance of FoodMenuItem from a dictionary
        return cls(
            restaurant_id=data_dict["restaurant_id"],
            item_name=data_dict["item_name"],
            price=data_dict["price"],
            description=data_dict["description"],
            image_url=data_dict["image_url"],
            stock_status=data_dict["stock_status"],
            number_of_times_ordered=data_dict["number_of_times_ordered"]
        )


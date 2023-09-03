class RestaurantOrders:
    def __init__(self, restaurant_id, order_id, food_menu_item,
                 order_instructions, order_total, order_status, transaction_id, order_rating):
        self.restaurant_id = restaurant_id
        self.order_id = order_id
        self.food_menu_item = food_menu_item
        self.order_instructions = order_instructions
        self.order_total = order_total
        self.transaction_id = transaction_id
        self.order_status = order_status
        self.order_rating = order_rating

    def to_dict(self):
        return {
            'restaurant_id': self.restaurant_id,
            'order_id': self.order_id,
            'food_menu_item': self.food_menu_item,
            'order_instructions': self.order_instructions,
            'order_total': self.order_total,
            'transaction_id': self.transaction_id,
            'order_status': self.order_status,
            'order_rating': self.order_rating
        }

    @classmethod
    def from_dict(cls, data_dict):
        return cls(
            restaurant_id=data_dict['restaurant_id'],
            order_id=data_dict['order_id'],
            food_menu_item=data_dict['food_menu_item'],
            order_instructions=data_dict['order_instructions'],
            order_total=data_dict['order_total'],
            transaction_id=data_dict['transaction_id'],
            order_status=data_dict['order_status'],
            order_rating=data_dict['order_rating']
        )
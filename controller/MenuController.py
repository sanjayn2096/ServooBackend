# menu_controller.py

from google.cloud import bigtable

from model.FoodMenuItem import FoodMenuItem

class MenuController:
    def __init__(self, project_id, instance_id):
        self.client = bigtable.Client(project=project_id, admin=True)
        self.instance = self.client.instance(instance_id)

    def get_menu(self, restaurant_id):
        # Fetch the menu items for the specified restaurantId from Bigtable
        table = self.instance.table('MenuTable')
        row_key = str(restaurant_id)
        row = table.read_row(row_key)

        # If the row does not exist, return an empty menu list
        if not row:
            return []

        # Extract the menu item attributes from the row
        item_name = row.cells['menu']['item:name'][0].value
        item_price = float(row.cells['menu']['item:price'][0].value)
        item_description = row.cells['menu']['item:description'][0].value

        # Create a FoodMenuItem object using the retrieved attributes
        menu_item = FoodMenuItem(item_name, item_price, item_description)

        # Return a list of FoodMenuItem objects
        return [menu_item]

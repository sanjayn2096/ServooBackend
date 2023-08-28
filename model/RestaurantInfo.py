from enum import Enum


class RestaurantInfo:
    def __init__(self, restaurant_name,
                 description, employees, address,
                 theme_color, phone_number,
                 verification_status, upi_id, restaurant_status):
        self.restaurant_name = restaurant_name
        self.description = description
        self.employees = employees
        self.address = address
        self.theme_color = theme_color
        self.phone_number = phone_number
        self.verification_status = verification_status if verification_status is not None else \
            RestaurantVerificationStatus.UNVERIFIED.name
        self.upi_id = upi_id
        self.restaurant_status = restaurant_status if verification_status is not None else RestaurantActivityStatus\
            .INACTIVE.name

    def to_dict(self):
        return {
            "restaurant_name": self.restaurant_name,
            "description": self.description,
            "employees": self.employees,
            "address": self.address,
            "theme_color": self.theme_color,
            "phone_number": self.phone_number,
            "verification_status": self.verification_status,
            "upi_id": self.upi_id,
            "restaurant_status": self.restaurant_status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            restaurant_name=data['restaurant_name'],
            description=data['description'],
            employees=data['employees'],
            address=data['address'],
            theme_color=data['theme_color'],
            phone_number=data['phone_number'],
            verification_status=data.get('verification_status'),
            upi_id=data['upi_id'],
            restaurant_status=data.get('restaurant_status')
        )


class RestaurantActivityStatus(Enum):
    ACTIVE = 1
    INACTIVE = 2


class RestaurantVerificationStatus(Enum):
    VERIFIED = 1
    UNVERIFIED = 2

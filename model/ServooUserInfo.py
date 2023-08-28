class ServooUserInfo:
    def __init__(self, phoneNumber, firstName, lastName, email, restaurants_working_at, restaurants_owned):
        self.phoneNumber = phoneNumber
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.restaurants_working_at = restaurants_working_at
        self.restaurants_owned = restaurants_owned

    def to_dict(self):
        return {
            "phoneNumber": self.phoneNumber,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "restaurants_working_at": self.restaurants_working_at,
            "restaurants_owned": self.restaurants_owned
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            phoneNumber=data['phoneNumber'],
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email'],
            restaurants_working_at=data['restaurants_working_at'],
            restaurants_owned=data['restaurants_owned']
        )

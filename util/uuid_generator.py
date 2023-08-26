import uuid


def generate_random_uuid():
    return uuid.uuid4()


def generate_time_based_uuid():
    return uuid.uuid1()

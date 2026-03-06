import datetime


def generate_unique_order_id():
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y%m%d%H%M%S')
    return str(timestamp)

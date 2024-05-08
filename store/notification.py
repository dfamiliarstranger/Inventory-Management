# notifications.py

from .models import Notification

def notify_user(user, message):
    Notification.objects.create(recipient=user, message=message)

def notify_stock_threshold(user, stock_item):
    threshold = 2  # Updated threshold value
    if stock_item.quantity <= threshold:
        message = f"Stock item {stock_item.name} is low in stock ({stock_item.quantity} left). Pls reorder"
        notify_user(user, message)


def notify_new_supplier(user, supplier):
    message = f"New supplier {supplier.name} has been added."
    notify_user(user, message)

def notify_new_customer(user, customer):
    message = f"New customer {customer.name} has been added."
    notify_user(user, message)

def notify_sale(user, sale):
    message = f"A sale for {sale.quantity} units of {sale.product.name} has been made."
    notify_user(user, message)

def notify_production(user, production):
    message = f"Production record for {production.product_quantity} units of {production.product.name} has been recorded."
    notify_user(user, message)

# notifications.py

from .models import Notification

def notify_user(user, message):
    Notification.objects.create(recipient=user, message=message)


# def notify_stock_threshold(user, stock_item):
#     threshold = 10  # Updated threshold value
#     if stock_item.unit <= threshold:
#         message = f"Attention {user.username},\n\nThe {stock_item.name}"
        
#         # Check and append cap_type if available
#         if hasattr(stock_item, 'cap_type'):
#             message += f" {stock_item.cap_type}"
        
#         # Check and append product_type if available
#         if hasattr(stock_item, 'product_type'):
#             message += f" {stock_item.product_type}"
        
#         # Check and append preform_type if available
#         if hasattr(stock_item, 'preform_type'):
#             message += f" {stock_item.preform_type}"
        
#         message += " in our inventory.\n\n"
#         message += f"is low in stock, with only {stock_item.unit} units remaining.\n\n"
#         message += "Kindly Restock.\n\n"

#         notify_user(user, message)

threshold_values = {
    'Cap': 5000,
    'Preform': 5000,
    'Bottle': 3000,
    'Shrinkwrapper':30,  # Define a threshold value for "Bottle"
}

def notify_stock_threshold(user, stock_item):
    # Get the threshold value based on the type of stock item
    threshold = threshold_values.get(stock_item.name, 5000)  # Default to 10 if threshold value not found
    
    if stock_item.unit <= threshold:
        # Construct notification message
        message = f"Attention {user.username},\n\nThe {stock_item.name}"
        
        if hasattr(stock_item, 'cap_type') and stock_item.cap_type:
            message += f" {stock_item.cap_type}"
        
        if hasattr(stock_item, 'product_type') and stock_item.product_type:
            message += f" {stock_item.product_type}"
                
        if hasattr(stock_item, 'preform_type') and stock_item.preform_type:
            message += f" {stock_item.preform_type}"

        
        message += " in our inventory.\n\n"
        message += f"is low in stock, with only {stock_item.unit} units remaining.\n\n"
        message += "Kindly Restock.\n\n"

        # Send notification
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

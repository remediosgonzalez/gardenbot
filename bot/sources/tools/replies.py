HELLO = 'Hello! Welcome to Garden Club, the most convenient bot to purchase cannabis products with Bitcoin. ' \
        'New products coming soon! :seedling:'

# Deposit part
GENERATING_ADDRESS = 'Generating a new address for you. It may take some time.'
DEPOSIT = 'Done. Send some funds to the address sent below.' \
          'You will get a notification within an hour after the payment is made.'
BALANCE = 'Your balance is {balance:.8f} BTC.'
FUNDS_ADDED = '{balance} added to your account'
NOT_AUTHENTICATED = 'Sorry, you are not allowed to do that.'

YES = 'Yes'
NO = 'No'

# Adding item part
ASK_ITEM_NAME = 'What\'s the name of the item?'
ASK_ITEM_DESCRIPTION = 'What\'s the description?'
ASK_ITEM_PRICE = 'What\'s the price (in BTC)?'
ASK_ITEM_PHOTO = 'Please send the photo'
ASK_ITEM_CONFIRMATION = 'You\'re adding an item with name {name}, ' \
                        'description {description} and price {price:.8f} BTC. Proceed?'

ADD_ITEM_ABORTED = 'Adding cancelled. You can start again using command /add_item'
ADD_ITEM_SUCCESS = 'Item added.'

# Buying item part
ITEM_DESCRIPTION = 'Name: {name}\n\n' \
                   'Description: {description}\n\n' \
                   'Price/unit: {price:.8f} BTC'
NO_ITEMS_IN_SHOP = 'There is no items in the shop yet.'
BUY_ITEM_SUCCESS = 'Item added to your cart'
QUANTITY = 'How may items do you want to buy?'
SEND_A_DIGIT = 'Please send a digit'
SEND_LESS_QUANTITY = 'Please send less quantity'

# Cart part
CART_REVIEW = 'Your cart has {n} items.'
CARD_ITEM = '{n}. {name} (quantity: {quantity}), the price is {price:.8f} BTC'
EMPTY_CART_SUCCESS = 'Your cart is now empty.'

# Checkout part
CART_IS_EMPTY = 'Your cart is empty'
ASK_FOR_ADDRESS = 'Please, provide your address.'
ADDRESS_SET_ASK_PAYMENT_CONFIRM = 'Address set. You are paying {total_price:.8f} BTC for {n} items. ' \
                                  'Your balance is {balance:.8f} BTC. Proceed?'
ORDER_SUCCESS = 'Your order ID is {id}. You will get a notify when it\'s delivered.'
NOT_SUFFICIENT_FUNDS = 'Not sufficient funds.'
ORDER_DELIVERED = 'Your order (ID: {order_id}) is delivered. Have a nice day!'

# Referral part
REFERRAL_LINK = 'Here is the link you can share with your referrals \n{link}'
NOT_A_NEW_USER = 'Only new users can be referrals.'
REFERRAL_SUCCESS_TO_REF_USER = 'Thank you for inviting a new user {first_name} {last_name}.' \
                               'You will get 10% of their spend.'

# Manager part
NOTIFY_MANAGER_NEW_ORDER = 'New order! User {first_name} {last_name} {username_with_space}(ID: {user_id}) ' \
                           'placed a new order (ID: {order_id})\n' \
                           'Address: {address}.\n' \
                           'Here are the items:\n\n{items_text}'
ORDER_COMPLETED = 'Order (ID: {order_id}) is marked as completed. User will get a notify.'

# Support part
SUPPORT_MESSAGE = 'Please describe your problem.'
TICKET_CREATED = 'Your ticket was created.'
NOTIFY_MANAGER_NEW_TICKET = 'New support ticket! User {first_name} {last_name} {username_with_space}(ID: {user_id}) ' \
                            'created a new ticket (ID: {ticket_id})\n\n' \
                            '{ticket_text}\n\n' \
                            'Send a reply to this message and it will be forwarded to the user.'
TICKET_RESOLVED = 'Your ticket was resolver. Reply from our manager:\n\n' \
                  '{text}\n\n'

# Shipping policy part
SHIPPING_POLICY = '{text}\n\nLast updated: {updated}'
ASK_NEW_POLICY = 'Send me new shipping policy.'
SHIPPING_POLICY_CHANGED = 'Shipping policy updated'

# Deleting item part
ITEM_DELETED = 'Item deleted.'

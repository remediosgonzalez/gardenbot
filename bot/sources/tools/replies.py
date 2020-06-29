HELLO = 'Hello! Here is the basic bot that accepts payments in bitcoin. Currently using `{network_name}`'
DEPOSIT = 'Send some funds to this address:'
FUNDS_ADDED = '{balance} added to your account'
NOT_AUTHENTICATED = 'Sorry, you are not allowed to do that.'

YES = 'Yes'
NO = 'No'

# Adding item part
ASK_ITEM_NAME = 'What\'s the name of the item?'
ASK_ITEM_DESCRIPTION = 'What\'s the description?'
ASK_ITEM_PRICE = 'What\'s the price? (provide the price in smallest units, for example, satoshi) '
ASK_ITEM_CONFIRMATION = 'You\'re adding an item with name {name}, description {description} and price {price}. Proceed?'

ADD_ITEM_ABORTED = 'Adding cancelled. You can start again using command /add_item'
ADD_ITEM_SUCCESS = 'Item added.'

# Buying item part
BUY_ASK_ITEM_NAME = 'Please provide item\'s name'
BUY_ITEM_CONFIRMATION = 'You\'re buying the item name {name}. It costs {price}'
BUY_ITEM_NOT_FOUND = 'There is no item with name {name}'
BUY_ITEM_ABORTED = 'Buying cancelled. You can start again using command /buy_item'
BUY_ITEM_SUCCESS = 'Item added to cart. Send /buy_item to buy more or /cart to complete your order.'

# Cart part
CART_REVIEW = 'Your cart has {n} items.'
CARD_ITEM = '{n}. {name}, the price is {price}'
EMPTY_CART_SUCCESS = 'Your cart is now empty.'
EMPTY_CART_OR_CHECKOUT = 'You can /empty_cart or /checkout.'

# Checkout part
CART_IS_EMPTY = 'Your cart is empty. Consider buying something using /buy_item.'
ASK_FOR_ADDRESS = 'Please, provide your address.'
ADDRESS_SET_ASK_PAYMENT_CONFIRM = 'Address set. You are paying {total_price} for {n} items. ' \
                                  'Your balance is {balance}. Proceed?'
ORDER_SUCCESS = 'Your order ID is {id}. You will get a notify when it\'s delivered.'
NOT_SUFFICIENT_FUNDS = 'Not sufficient funds. Use /deposit to add some.'
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

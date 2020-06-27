HELLO = 'Hello! Here is the basic bot that accepts payments in bitcoin. Currently using `{network_name}`'
DEPOSIT = 'Send some funds to this address:'
FUNDS_ADDED = '{string_value} added to your account'
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


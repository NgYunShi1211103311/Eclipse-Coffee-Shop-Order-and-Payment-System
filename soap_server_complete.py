from spyne import Application, rpc, ServiceBase, Unicode, Integer, Double
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In-memory storage for orders (shared with web service)
orders = {}
order_counter = 1000

# In-memory storage for users (members and guests)
users = {}
user_counter = 100

class CoffeeShopService(ServiceBase):
    """SOAP service for Eclipse Coffee Shop"""
    
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def createOrder(ctx, customer_name, customer_email, cart_items):
        """Create a new order"""
        global order_counter, orders
        order_counter += 1
        order_id = order_counter
        
        logger.debug(f"SOAP createOrder called with - Name: {customer_name}, Email: {customer_email}")
        
        try:
            cart_data = json.loads(cart_items)
            total_amount = sum(item['price'] * item['qty'] for item in cart_data)
            
            order = {
                'id': order_id,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'items': cart_data,
                'total_amount': total_amount,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'payment_status': 'unpaid'
            }
            
            orders[order_id] = order
            logger.debug(f"SOAP Order {order_id} created successfully")
            
            return f"Order created successfully. Order ID: {order_id}, Total: ${total_amount:.2f}"
            
        except Exception as e:
            logger.error(f"SOAP Error creating order: {str(e)}")
            return f"Error creating order: {str(e)}"
    
    @rpc(Integer, Double, Unicode, _returns=Unicode)
    def processPayment(ctx, order_id, amount, payment_method):
        """Process payment for an order"""
        try:
            if order_id not in orders:
                return f"Error: Order {order_id} not found"
            
            order = orders[order_id]
            
            # Handle cash payment differently
            if payment_method.lower() == 'cash':
                order['payment_status'] = 'unpaid'
                order['payment_method'] = 'cash'
                order['status'] = 'awaiting_cash_payment'
                order['payment_date'] = datetime.now().isoformat()
                return f"Order {order_id} marked for cash payment. Please pay at the counter."
            
            # Validate amount for other payment methods
            if abs(order['total_amount'] - amount) > 0.01:
                return f"Error: Payment amount ${amount:.2f} does not match order total ${order['total_amount']:.2f}"
            
            # Simulate payment processing
            if payment_method.lower() in ['credit_card', 'debit_card', 'tng']:
                order['payment_status'] = 'paid'
                order['payment_method'] = payment_method
                order['payment_date'] = datetime.now().isoformat()
                order['status'] = 'confirmed'
                
                logger.debug(f"SOAP Payment processed for order {order_id}")
                return f"Payment of ${amount:.2f} processed successfully for order {order_id}. Order confirmed."
            else:
                return f"Error: Unsupported payment method '{payment_method}'"
                
        except Exception as e:
            logger.error(f"SOAP Error processing payment: {str(e)}")
            return f"Error processing payment: {str(e)}"
    
    @rpc(Integer, Unicode, Double, _returns=Unicode)
    def processRefund(ctx, order_id, reason, refund_amount=None):
        """Process refund for an order"""
        try:
            if order_id not in orders:
                return f"Error: Order {order_id} not found"
            
            order = orders[order_id]
            
            # Check if order is paid
            if order['payment_status'] != 'paid':
                return f"Error: Order {order_id} is not paid and cannot be refunded"
            
            # Validate refund reason
            valid_reasons = [
                'wrong_order', 'quality_issue', 'delivery_delay', 
                'duplicate_charge', 'customer_request', 'technical_error'
            ]
            
            if reason not in valid_reasons:
                return f"Error: Invalid refund reason. Valid reasons: {', '.join(valid_reasons)}"
            
            # Set refund amount (default to full amount if not specified)
            if refund_amount is None:
                refund_amount = order['total_amount']
            
            # Validate refund amount
            if refund_amount > order['total_amount']:
                return f"Error: Refund amount ${refund_amount:.2f} cannot exceed order total ${order['total_amount']:.2f}"
            
            # Process refund
            order['refund_status'] = 'refunded'
            order['refund_amount'] = refund_amount
            order['refund_reason'] = reason
            order['refund_date'] = datetime.now().isoformat()
            order['status'] = 'refunded'
            
            logger.debug(f"SOAP Refund processed for order {order_id}: ${refund_amount:.2f} - Reason: {reason}")
            return f"Refund of ${refund_amount:.2f} processed successfully for order {order_id}. Reason: {reason}"
            
        except Exception as e:
            logger.error(f"SOAP Error processing refund: {str(e)}")
            return f"Error processing refund: {str(e)}"
    
    @rpc(Integer, _returns=Unicode)
    def getOrderStatus(ctx, order_id):
        """Get the status of an order"""
        try:
            if order_id not in orders:
                return f"Error: Order {order_id} not found"
            
            order = orders[order_id]
            status_info = {
                'order_id': order_id,
                'status': order['status'],
                'payment_status': order['payment_status'],
                'total_amount': order['total_amount'],
                'customer_name': order['customer_name'],
                'items': order['items']
            }
            
            # Add payment method if available
            if 'payment_method' in order:
                status_info['payment_method'] = order['payment_method']
            
            # Add refund information if available
            if 'refund_status' in order:
                status_info['refund_status'] = order['refund_status']
                status_info['refund_amount'] = order['refund_amount']
                status_info['refund_reason'] = order['refund_reason']
                status_info['refund_date'] = order['refund_date']
            
            return json.dumps(status_info)
            
        except Exception as e:
            logger.error(f"SOAP Error getting order status: {str(e)}")
            return f"Error getting order status: {str(e)}"
    
    @rpc(Integer, _returns=Unicode)
    def cancelOrder(ctx, order_id):
        """Cancel an order"""
        try:
            if order_id not in orders:
                return f"Error: Order {order_id} not found"
            
            order = orders[order_id]
            if order['payment_status'] == 'paid':
                return f"Error: Cannot cancel order {order_id} - payment already processed"
            
            order['status'] = 'cancelled'
            logger.debug(f"SOAP Order {order_id} cancelled")
            return f"Order {order_id} cancelled successfully"
            
        except Exception as e:
            logger.error(f"SOAP Error cancelling order: {str(e)}")
            return f"Error cancelling order: {str(e)}"
    
    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Unicode)
    def registerGuest(ctx, name, email, phone, notes):
        """Register a guest user"""
        global user_counter, users
        user_counter += 1
        user_id = user_counter
        
        try:
            guest_data = {
                'id': user_id,
                'name': name,
                'email': email,
                'phone': phone,
                'notes': notes,
                'type': 'guest',
                'created_at': datetime.now().isoformat()
            }
            
            users[user_id] = guest_data
            logger.debug(f"SOAP Guest registered: {user_id}")
            
            return json.dumps(guest_data)
            
        except Exception as e:
            logger.error(f"SOAP Error registering guest: {str(e)}")
            return f"Error registering guest: {str(e)}"
    
    @rpc(Unicode, Unicode, Unicode, Unicode, Unicode, _returns=Unicode)
    def registerMember(ctx, first_name, last_name, email, phone, password):
        """Register a new member"""
        global user_counter, users
        user_counter += 1
        user_id = user_counter
        
        try:
            # Check if email already exists
            for user in users.values():
                if user.get('email') == email:
                    return f"Error: Email {email} already registered"
            
            member_data = {
                'id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'name': f"{first_name} {last_name}",
                'email': email,
                'phone': phone,
                'password': password,  # In production, this should be hashed
                'type': 'member',
                'created_at': datetime.now().isoformat(),
                'points': 0
            }
            
            users[user_id] = member_data
            logger.debug(f"SOAP Member registered: {user_id}")
            
            return json.dumps(member_data)
            
        except Exception as e:
            logger.error(f"SOAP Error registering member: {str(e)}")
            return f"Error registering member: {str(e)}"
    
    @rpc(Unicode, Unicode, _returns=Unicode)
    def loginMember(ctx, email, password):
        """Login a member"""
        try:
            for user in users.values():
                if user.get('type') == 'member' and user.get('email') == email:
                    if user.get('password') == password:  # In production, verify hash
                        # Remove password from response
                        login_data = {k: v for k, v in user.items() if k != 'password'}
                        return json.dumps(login_data)
                    else:
                        return f"Error: Invalid password for email {email}"
            
            return f"Error: Member with email {email} not found"
            
        except Exception as e:
            logger.error(f"SOAP Error logging in member: {str(e)}")
            return f"Error logging in member: {str(e)}"
    
    @rpc(_returns=Unicode)
    def getAllOrders(ctx):
        """Get all orders (for debugging)"""
        try:
            return json.dumps({
                'orders': orders,
                'order_count': len(orders),
                'order_ids': list(orders.keys())
            })
        except Exception as e:
            logger.error(f"SOAP Error getting all orders: {str(e)}")
            return f"Error getting all orders: {str(e)}"

# Create the SOAP application
soap_app = Application(
    [CoffeeShopService],
    tns='urn:coffeeshop.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

# Create WSGI application
soap_wsgi_app = WsgiApplication(soap_app)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    # Create server
    server = make_server('0.0.0.0', 8000, soap_wsgi_app)
    
    logger.info("SOAP Server starting on http://0.0.0.0:8000")
    logger.info("WSDL available at http://localhost:8000/?wsdl")
    
    # Start server
    server.serve_forever() 
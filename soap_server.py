from spyne import Application, rpc, ServiceBase, Unicode, Integer, Double
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import json
import logging
from datetime import datetime


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

orders = {}
order_counter = 1000

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
            if abs(order['total_amount'] - amount) > 0.01:
                return f"Error: Payment amount ${amount:.2f} does not match order total ${order['total_amount']:.2f}"
            
            if payment_method.lower() in ['credit_card', 'debit_card', 'paypal']:
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

soap_app = Application(
    [CoffeeShopService],
    tns='urn:coffeeshop.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

soap_wsgi_app = WsgiApplication(soap_app)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    # Create server
    server = make_server('0.0.0.0', 8000, soap_wsgi_app)
    
    logger.info("SOAP Server starting on http://0.0.0.0:8000")
    logger.info("WSDL available at http://localhost:8000/?wsdl")
    
    # Start server
    server.serve_forever() 
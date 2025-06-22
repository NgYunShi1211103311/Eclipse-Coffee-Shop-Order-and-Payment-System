#!/usr/bin/env python3
"""
SOAP Client for Eclipse Coffee Shop Service
This client demonstrates how to interact with the SOAP service
"""

from zeep import Client
from zeep.transports import Transport
from requests import Session
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CoffeeShopSOAPClient:
    """SOAP client for Eclipse Coffee Shop service"""
    
    def __init__(self, wsdl_url="http://localhost:8000/?wsdl"):
        """Initialize SOAP client"""
        try:
            # Create session with timeout
            session = Session()
            session.timeout = 10
            
            # Create transport
            transport = Transport(session=session)
            
            # Create client
            self.client = Client(wsdl_url, transport=transport)
            logger.info(f"SOAP client initialized with WSDL: {wsdl_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize SOAP client: {str(e)}")
            raise
    
    def create_order(self, customer_name, customer_email, cart_items):
        """Create a new order via SOAP"""
        try:
            # Convert cart items to JSON string
            cart_json = json.dumps(cart_items)
            
            # Call SOAP service
            result = self.client.service.createOrder(
                customer_name, 
                customer_email, 
                cart_json
            )
            
            logger.debug(f"SOAP createOrder result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"SOAP createOrder error: {str(e)}")
            return f"Error creating order: {str(e)}"
    
    def process_payment(self, order_id, amount, payment_method):
        """Process payment via SOAP"""
        try:
            # Call SOAP service
            result = self.client.service.processPayment(
                order_id, 
                amount, 
                payment_method
            )
            
            logger.debug(f"SOAP processPayment result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"SOAP processPayment error: {str(e)}")
            return f"Error processing payment: {str(e)}"
    
    def process_refund(self, order_id, reason, refund_amount=None):
        """Process refund via SOAP"""
        try:
            # Call SOAP service
            result = self.client.service.processRefund(
                order_id, 
                reason, 
                refund_amount
            )
            
            logger.debug(f"SOAP processRefund result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"SOAP processRefund error: {str(e)}")
            return f"Error processing refund: {str(e)}"
    
    def get_order_status(self, order_id):
        """Get order status via SOAP"""
        try:
            # Call SOAP service
            result = self.client.service.getOrderStatus(order_id)
            
            logger.debug(f"SOAP getOrderStatus result: {result}")
            
            # Try to parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # If not JSON, return as string
                return result
            
        except Exception as e:
            logger.error(f"SOAP getOrderStatus error: {str(e)}")
            return f"Error getting order status: {str(e)}"
    
    def cancel_order(self, order_id):
        """Cancel order via SOAP"""
        try:
            # Call SOAP service
            result = self.client.service.cancelOrder(order_id)
            
            logger.debug(f"SOAP cancelOrder result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"SOAP cancelOrder error: {str(e)}")
            return f"Error cancelling order: {str(e)}"
    
    def register_guest(self, name, email, phone, notes):
        """Register guest via SOAP"""
        try:
            # Call SOAP service
            result = self.client.service.registerGuest(name, email, phone, notes)
            
            logger.debug(f"SOAP registerGuest result: {result}")
            
            # Try to parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # If not JSON, return as string
                return result
            
        except Exception as e:
            logger.error(f"SOAP registerGuest error: {str(e)}")
            return f"Error registering guest: {str(e)}"
    
    def register_member(self, first_name, last_name, email, phone, password):
        """Register member via SOAP"""
        try:
            # Call SOAP service
            result = self.client.service.registerMember(
                first_name, 
                last_name, 
                email, 
                phone, 
                password
            )
            
            logger.debug(f"SOAP registerMember result: {result}")
            
            # Try to parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # If not JSON, return as string
                return result
            
        except Exception as e:
            logger.error(f"SOAP registerMember error: {str(e)}")
            return f"Error registering member: {str(e)}"
    
    def login_member(self, email, password):
        """Login member via SOAP"""
        try:
            # Call SOAP service
            result = self.client.service.loginMember(email, password)
            
            logger.debug(f"SOAP loginMember result: {result}")
            
            # Try to parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # If not JSON, return as string
                return result
            
        except Exception as e:
            logger.error(f"SOAP loginMember error: {str(e)}")
            return f"Error logging in member: {str(e)}"
    
    def get_all_orders(self):
        """Get all orders via SOAP (for debugging)"""
        try:
            # Call SOAP service
            result = self.client.service.getAllOrders()
            
            logger.debug(f"SOAP getAllOrders result: {result}")
            
            # Try to parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # If not JSON, return as string
                return result
            
        except Exception as e:
            logger.error(f"SOAP getAllOrders error: {str(e)}")
            return f"Error getting all orders: {str(e)}"

# Create a global client instance
soap_client = CoffeeShopSOAPClient()

def create_soap_client():
    """Create and return a SOAP client"""
    session = Session()
    transport = Transport(session=session)
    client = Client(SOAP_URL, transport=transport)
    return client

def test_create_order(client):
    """Test order creation"""
    print("=== Testing Order Creation ===")
    
    # Sample cart items
    cart_items = [
        {"id": 1, "name": "Latte", "price": 3.5, "qty": 2},
        {"id": 2, "name": "Cappuccino", "price": 3.0, "qty": 1}
    ]
    
    try:
        result = client.service.createOrder(
            customer_name="John Doe",
            customer_email="john.doe@example.com",
            cart_items=json.dumps(cart_items)
        )
        print(f"Order Creation Result: {result}")
        
        # Extract order ID from result
        if "Order created successfully" in result:
            order_id = int(result.split("Order ID: ")[1].split(",")[0])
            return order_id
        else:
            print("Failed to create order")
            return None
            
    except Exception as e:
        print(f"Error creating order: {e}")
        return None

def test_payment_processing(client, order_id, amount):
    """Test payment processing"""
    print(f"\n=== Testing Payment Processing for Order {order_id} ===")
    
    try:
        result = client.service.processPayment(
            order_id=order_id,
            amount=amount,
            payment_method="credit_card"
        )
        print(f"Payment Result: {result}")
        return "Payment of" in result and "processed successfully" in result
        
    except Exception as e:
        print(f"Error processing payment: {e}")
        return False

def test_order_status(client, order_id):
    """Test order status checking"""
    print(f"\n=== Testing Order Status for Order {order_id} ===")
    
    try:
        result = client.service.getOrderStatus(order_id=order_id)
        print(f"Order Status Result: {result}")
        
        # Parse JSON result
        status_data = json.loads(result)
        print(f"Order ID: {status_data['order_id']}")
        print(f"Status: {status_data['status']}")
        print(f"Payment Status: {status_data['payment_status']}")
        print(f"Total Amount: ${status_data['total_amount']}")
        print(f"Customer: {status_data['customer_name']}")
        
        return status_data
        
    except Exception as e:
        print(f"Error getting order status: {e}")
        return None

def test_cancel_order(client, order_id):
    """Test order cancellation"""
    print(f"\n=== Testing Order Cancellation for Order {order_id} ===")
    
    try:
        result = client.service.cancelOrder(order_id=order_id)
        print(f"Cancel Order Result: {result}")
        return "cancelled successfully" in result
        
    except Exception as e:
        print(f"Error cancelling order: {e}")
        return False

def main():
    """Main function to run all tests"""
    print("Eclipse Coffee Shop SOAP Client")
    print("=" * 40)
    
    try:
        # Create SOAP client
        client = create_soap_client()
        print("SOAP client created successfully")
        
        # Test 1: Create Order
        order_id = test_create_order(client)
        if not order_id:
            print("Cannot proceed without a valid order ID")
            return
        
        # Test 2: Check Order Status (before payment)
        status_before = test_order_status(client, order_id)
        
        # Test 3: Process Payment
        total_amount = 10.0  # This should match the cart total
        payment_success = test_payment_processing(client, order_id, total_amount)
        
        # Test 4: Check Order Status (after payment)
        status_after = test_order_status(client, order_id)
        
        # Test 5: Try to cancel a paid order (should fail)
        if payment_success:
            test_cancel_order(client, order_id)
        
        # Test 6: Create another order for cancellation test
        print("\n" + "=" * 40)
        print("Creating another order for cancellation test...")
        order_id_2 = test_create_order(client)
        if order_id_2:
            # Cancel unpaid order (should succeed)
            test_cancel_order(client, order_id_2)
        
        print("\n" + "=" * 40)
        print("All tests completed!")
        
    except Exception as e:
        print(f"Error connecting to SOAP service: {e}")
        print("Make sure the SOAP service is running on http://localhost:5000/soap")

if __name__ == "__main__":
    main()
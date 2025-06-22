from flask import Flask, render_template, request, jsonify, send_from_directory, session
import os
import logging
import socket
import json
from datetime import datetime
import uuid

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get absolute paths for template and static folders
current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, 'templates')
static_folder = os.path.join(current_dir, 'static')

logger.info(f"Current directory: {current_dir}")
logger.info(f"Template folder: {template_folder}")
logger.info(f"Static folder: {static_folder}")

# Create Flask app with absolute paths
app = Flask(__name__,
            template_folder=template_folder,
            static_folder=static_folder)
app.secret_key = 'eclipse_coffee_secret_key_2024'

# In-memory storage for orders (in production, use a database)
orders = {}
order_counter = 1000

ORDERS_FILE = os.path.join(current_dir, 'orders.json')

def save_orders():
    try:
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=2, default=str)
        logger.info(f"Orders saved to {ORDERS_FILE}")
    except Exception as e:
        logger.error(f"Error saving orders: {e}")

def load_orders():
    global orders, order_counter
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Convert keys back to int
                orders.clear()
                for k, v in loaded.items():
                    orders[int(k)] = v
                if orders:
                    order_counter = max(orders.keys())
            logger.info(f"Orders loaded from {ORDERS_FILE}")
        except Exception as e:
            logger.error(f"Error loading orders: {e}")
    else:
        logger.info(f"No existing orders file found at {ORDERS_FILE}")

# Load orders at startup
load_orders()

# Web interface functions (no SOAP dependency)
def create_order_web(customer_name, customer_email, cart_items):
    """Create order for web interface"""
    global order_counter, orders
    order_counter += 1
    order_id = order_counter
    
    logger.debug(f"create_order_web called with - Name: {customer_name}, Email: {customer_email}")
    logger.debug(f"Current order_counter: {order_counter}")
    logger.debug(f"Current orders before creation: {list(orders.keys())}")
    
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
        save_orders()
        logger.debug(f"Order {order_id} added to orders dictionary")
        logger.debug(f"Orders after creation: {list(orders.keys())}")
        logger.debug(f"Order details: {order}")
        
        return f"Order created successfully. Order ID: {order_id}, Total: ${total_amount:.2f}"
        
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return f"Error creating order: {str(e)}"

def process_payment_web(order_id, amount, payment_method):
    """Process payment for web interface"""
    try:
        if order_id not in orders:
            return f"Error: Order {order_id} not found"
        
        order = orders[order_id]
        if payment_method.lower() == 'cash':
            # For cash, mark as unpaid but set status to awaiting payment at counter
            order['payment_status'] = 'unpaid'
            order['payment_method'] = 'cash'
            order['status'] = 'awaiting_cash_payment'
            order['payment_date'] = datetime.now().isoformat()
            save_orders()
            return f"Order {order_id} marked for cash payment. Please pay at the counter."
        if abs(order['total_amount'] - amount) > 0.01:
            return f"Error: Payment amount ${amount:.2f} does not match order total ${order['total_amount']:.2f}"
        
        # Simulate payment processing
        if payment_method.lower() in ['credit_card', 'debit_card', 'tng']:
            order['payment_status'] = 'paid'
            order['payment_method'] = payment_method
            order['payment_date'] = datetime.now().isoformat()
            order['status'] = 'confirmed'
            save_orders()
            return f"Payment of ${amount:.2f} processed successfully for order {order_id}. Order confirmed."
        else:
            return f"Error: Unsupported payment method '{payment_method}'"
            
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        return f"Error processing payment: {str(e)}"

def get_order_status_web(order_id):
    """Get order status for web interface"""
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
        logger.error(f"Error getting order status: {str(e)}")
        return f"Error getting order status: {str(e)}"

def cancel_order_web(order_id):
    """Cancel order for web interface"""
    try:
        if order_id not in orders:
            return f"Error: Order {order_id} not found"
        
        order = orders[order_id]
        if order['payment_status'] == 'paid':
            return f"Error: Cannot cancel order {order_id} - payment already processed"
        
        order['status'] = 'cancelled'
        save_orders()
        logger.debug(f"Order {order_id} cancelled")
        return f"Order {order_id} cancelled successfully"
        
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        return f"Error cancelling order: {str(e)}"

def process_refund_web(order_id, reason, refund_amount=None):
    """Process refund for web interface"""
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
        save_orders()
        
        logger.debug(f"Refund processed for order {order_id}: ${refund_amount:.2f} - Reason: {reason}")
        return f"Refund of ${refund_amount:.2f} processed successfully for order {order_id}. Reason: {reason}"
        
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        return f"Error processing refund: {str(e)}"

# Flask routes for web interface
@app.route('/')
def main_page():
    try:
        logger.debug("Attempting to render main.html")
        return render_template('main.html')
    except Exception as e:
        logger.error(f"Error rendering main template: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/menu')
def index():
    try:
        logger.debug("Attempting to render index.html")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/guest_login')
def guest_login():
    try:
        return render_template('guest_login.html')
    except Exception as e:
        logger.error(f"Error rendering guest login template: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/member_login')
def member_login():
    try:
        return render_template('member_login.html')
    except Exception as e:
        logger.error(f"Error rendering member login template: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory(static_folder, filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {str(e)}")
        return f"Error: {str(e)}", 404

@app.route('/checkout')
def checkout():
    try:
        return render_template('checkout.html')
    except Exception as e:
        logger.error(f"Error rendering checkout template: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/payment/<int:order_id>')
def payment_page(order_id):
    try:
        logger.debug(f"Payment page accessed for order ID: {order_id}")
        logger.debug(f"Available orders: {list(orders.keys())}")
        
        if order_id not in orders:
            logger.error(f"Order {order_id} not found in orders dictionary")
            return "Order not found", 404
        
        order = orders[order_id]
        logger.debug(f"Order {order_id} found: {order}")
        logger.debug(f"Order type: {type(order)}")
        logger.debug(f"Order items type: {type(order.get('items', 'No items key'))}")
        logger.debug(f"Order items: {order.get('items', 'No items key')}")
        
        # Ensure items is a list
        if 'items' in order and not isinstance(order['items'], list):
            logger.error(f"Order items is not a list: {type(order['items'])}")
            # Try to fix it if it's a string
            if isinstance(order['items'], str):
                try:
                    order['items'] = json.loads(order['items'])
                    logger.debug(f"Fixed items to: {order['items']}")
                except json.JSONDecodeError as e:
                    logger.error(f"Could not parse items JSON: {e}")
                    return "Invalid order data", 500
        
        return render_template('payment.html', order=order)
    except Exception as e:
        logger.error(f"Error rendering payment template: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return f"Error: {str(e)}", 500

@app.route('/order_status/<int:order_id>')
def order_status_page(order_id):
    try:
        logger.debug(f"Order status page accessed for order ID: {order_id}")
        logger.debug(f"Available orders: {list(orders.keys())}")
        
        if order_id not in orders:
            logger.error(f"Order {order_id} not found in orders dictionary")
            return "Order not found", 404
        
        order = orders[order_id]
        logger.debug(f"Order {order_id} found: {order}")
        return render_template('status.html', order=order)
    except Exception as e:
        logger.error(f"Error rendering status template: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/create_order', methods=['POST'])
def create_order():
    logger.debug("create_order route accessed")
    try:
        customer_name = request.form.get('name')
        customer_email = request.form.get('email')
        cart_items = request.form.get('cart')
        
        logger.debug(f"Received data - Name: {customer_name}, Email: {customer_email}, Cart: {cart_items}")
        
        if not all([customer_name, customer_email, cart_items]):
            logger.error("Missing required fields")
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        result = create_order_web(customer_name, customer_email, cart_items)
        logger.debug(f"Order creation result: {result}")
        
        if "Order created successfully" in result:
            # Extract order ID from result
            try:
                order_id = int(result.split("Order ID: ")[1].split(",")[0])
                logger.debug(f"Extracted order ID: {order_id}")
                logger.debug(f"Available orders: {list(orders.keys())}")
                
                # Verify order exists
                if order_id in orders:
                    logger.debug(f"Order {order_id} found in orders dictionary")
                    return jsonify({
                        'success': True, 
                        'result': result,
                        'order_id': order_id,
                        'redirect_url': f'/payment/{order_id}'
                    })
                else:
                    logger.error(f"Order {order_id} not found in orders dictionary after creation")
                    return jsonify({'success': False, 'error': f'Order {order_id} was created but not found in storage'})
            except (IndexError, ValueError) as e:
                logger.error(f"Error extracting order ID from result: {e}")
                return jsonify({'success': False, 'error': f'Error extracting order ID: {str(e)}'})
        else:
            logger.error(f"Order creation failed: {result}")
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        logger.error(f"Error in create_order: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/process_payment', methods=['POST'])
def process_payment():
    logger.debug("process_payment route accessed")
    try:
        order_id = int(request.form.get('order_id'))
        amount = float(request.form.get('amount'))
        payment_method = request.form.get('payment_method')
        
        result = process_payment_web(order_id, amount, payment_method)
        
        if "Payment of" in result and "processed successfully" in result:
            return jsonify({
                'success': True, 
                'result': result,
                'redirect_url': f'/order_status/{order_id}'
            })
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        logger.error(f"Error in process_payment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_order_status', methods=['POST'])
def get_order_status():
    logger.debug("get_order_status route accessed")
    try:
        order_id = int(request.form.get('order_id'))
        
        result = get_order_status_web(order_id)
        
        if "Error:" not in result:
            status_data = json.loads(result)
            return jsonify({'success': True, 'result': status_data})
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        logger.error(f"Error in get_order_status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    logger.debug("cancel_order route accessed")
    try:
        order_id = int(request.form.get('order_id'))
        
        result = cancel_order_web(order_id)
        
        if "cancelled successfully" in result:
            return jsonify({
                'success': True, 
                'result': result,
                'redirect_url': '/'
            })
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        logger.error(f"Error in cancel_order: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/process_refund', methods=['POST'])
def process_refund():
    logger.debug("process_refund route accessed")
    try:
        order_id = int(request.form.get('order_id'))
        reason = request.form.get('reason')
        refund_amount = float(request.form.get('refund_amount')) if request.form.get('refund_amount') else None
        
        result = process_refund_web(order_id, reason, refund_amount)
        
        if "Refund of" in result and "processed successfully" in result:
            return jsonify({
                'success': True, 
                'result': result,
                'redirect_url': f'/order_status/{order_id}'
            })
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        logger.error(f"Error in process_refund: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Debug route to check orders
@app.route('/debug/orders')
def debug_orders():
    try:
        return jsonify({
            'orders': orders,
            'order_count': len(orders),
            'order_ids': list(orders.keys())
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Get the local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    logger.info(f"Starting Flask application on:")
    logger.info(f"  - Local: http://127.0.0.1:5000")
    logger.info(f"  - Network: http://{local_ip}:5000")
    
    # Run the application on all interfaces
    app.run(debug=True, port=5000, host='0.0.0.0')

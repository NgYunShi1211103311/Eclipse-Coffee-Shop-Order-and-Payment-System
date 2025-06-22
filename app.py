from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
import logging
from datetime import datetime
from soap_client import soap_client

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'eclipse_coffee_secret_key_2024'

# Coffee menu
COFFEE_MENU = {
    'espresso': {'name': 'Espresso', 'price': 3.50, 'description': 'Strong Italian coffee'},
    'cappuccino': {'name': 'Cappuccino', 'price': 4.50, 'description': 'Espresso with steamed milk foam'},
    'latte': {'name': 'Cafe Latte', 'price': 4.00, 'description': 'Espresso with steamed milk'},
    'americano': {'name': 'Americano', 'price': 3.00, 'description': 'Espresso with hot water'},
    'mocha': {'name': 'Mocha', 'price': 5.00, 'description': 'Espresso with chocolate and milk'}
}

@app.route('/')
def main():
    """Main landing page"""
    return render_template('main.html')

@app.route('/guest-login')
def guest_login():
    """Guest login page"""
    return render_template('guest_login.html')

@app.route('/member-login')
def member_login():
    """Member login page"""
    return render_template('member_login.html')

@app.route('/register-guest', methods=['POST'])
def register_guest():
    """Register a guest user via SOAP"""
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        notes = request.form.get('notes', '')
        
        if not all([name, email, phone]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('guest_login'))
        
        # Call SOAP service to register guest
        result = soap_client.register_guest(name, email, phone, notes)
        
        if isinstance(result, dict) and 'id' in result:
            # Success - store user info in session
            session['user'] = result
            flash(f'Welcome {name}! You are now logged in as a guest.', 'success')
            return redirect(url_for('index'))
        else:
            # Error
            flash(f'Registration failed: {result}', 'error')
            return redirect(url_for('guest_login'))
            
    except Exception as e:
        logger.error(f"Error registering guest: {str(e)}")
        flash('An error occurred during registration', 'error')
        return redirect(url_for('guest_login'))

@app.route('/register-member', methods=['POST'])
def register_member():
    """Register a new member via SOAP"""
    try:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([first_name, last_name, email, phone, password]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('member_login'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('member_login'))
        
        # Call SOAP service to register member
        result = soap_client.register_member(first_name, last_name, email, phone, password)
        
        if isinstance(result, dict) and 'id' in result:
            # Success - store user info in session
            session['user'] = result
            flash(f'Welcome {first_name}! Your account has been created successfully.', 'success')
            return redirect(url_for('index'))
        else:
            # Error
            flash(f'Registration failed: {result}', 'error')
            return redirect(url_for('member_login'))
            
    except Exception as e:
        logger.error(f"Error registering member: {str(e)}")
        flash('An error occurred during registration', 'error')
        return redirect(url_for('member_login'))

@app.route('/login-member', methods=['POST'])
def login_member():
    """Login a member via SOAP"""
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([email, password]):
            flash('Please enter both email and password', 'error')
            return redirect(url_for('member_login'))
        
        # Call SOAP service to login member
        result = soap_client.login_member(email, password)
        
        if isinstance(result, dict) and 'id' in result:
            # Success - store user info in session
            session['user'] = result
            flash(f'Welcome back, {result["name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            # Error
            flash(f'Login failed: {result}', 'error')
            return redirect(url_for('member_login'))
            
    except Exception as e:
        logger.error(f"Error logging in member: {str(e)}")
        flash('An error occurred during login', 'error')
        return redirect(url_for('member_login'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('main'))

@app.route('/menu')
def index():
    """Coffee menu page"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))
    
    try:
        return render_template('menu.html', user=session['user'])
    except Exception as e:
        logger.error(f"Error rendering menu: {str(e)}")
        flash('An error occurred while loading the menu', 'error')
        return redirect(url_for('main'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        if item_id not in COFFEE_MENU:
            return jsonify({'error': 'Invalid item'}), 400
        
        # Initialize cart in session if not exists
        if 'cart' not in session:
            session['cart'] = []
        
        # Check if item already in cart
        item_in_cart = None
        for item in session['cart']:
            if item['id'] == item_id:
                item_in_cart = item
                break
        
        if item_in_cart:
            item_in_cart['qty'] += quantity
        else:
            menu_item = COFFEE_MENU[item_id]
            session['cart'].append({
                'id': item_id,
                'name': menu_item['name'],
                'price': menu_item['price'],
                'qty': quantity
            })
        
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': f'{COFFEE_MENU[item_id]["name"]} added to cart',
            'cart_count': len(session['cart'])
        })
        
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return jsonify({'error': 'Failed to add item to cart'}), 500

@app.route('/cart')
def cart():
    """View cart"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))
    
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['qty'] for item in cart_items)
    
    return render_template('cart.html', cart=cart_items, total=total, user=session['user'])

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))
    
    cart_items = session.get('cart', [])
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('index'))
    
    total = sum(item['price'] * item['qty'] for item in cart_items)
    
    if request.method == 'POST':
        try:
            # Call SOAP service to create order
            result = soap_client.create_order(
                session['user']['name'],
                session['user']['email'],
                cart_items
            )
            
            if 'Order created successfully' in result:
                # Extract order ID from result
                import re
                order_id_match = re.search(r'Order ID: (\d+)', result)
                if order_id_match:
                    order_id = int(order_id_match.group(1))
                    
                    # Store order info in session for payment
                    session['current_order'] = {
                        'id': order_id,
                        'total': total,
                        'items': cart_items
                    }
                    
                    # Clear cart
                    session.pop('cart', None)
                    
                    return redirect(url_for('payment', order_id=order_id))
                else:
                    flash('Error: Could not extract order ID', 'error')
            else:
                flash(f'Error creating order: {result}', 'error')
                
        except Exception as e:
            logger.error(f"Error during checkout: {str(e)}")
            flash('An error occurred during checkout', 'error')
    
    return render_template('checkout.html', cart=cart_items, total=total, user=session['user'])

@app.route('/payment/<int:order_id>')
def payment(order_id):
    """Payment page"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))
    
    if 'current_order' not in session or session['current_order']['id'] != order_id:
        flash('Invalid order', 'error')
        return redirect(url_for('index'))
    
    order = session['current_order']
    return render_template('payment.html', order=order, user=session['user'])

@app.route('/process_payment', methods=['POST'])
def process_payment():
    """Process payment via SOAP"""
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        payment_method = data.get('payment_method')
        
        if 'current_order' not in session or session['current_order']['id'] != order_id:
            return jsonify({'error': 'Invalid order'}), 400
        
        order = session['current_order']
        
        # Call SOAP service to process payment
        result = soap_client.process_payment(order_id, order['total'], payment_method)
        
        if 'processed successfully' in result.lower() or 'cash payment' in result.lower():
            # Payment successful
            session.pop('current_order', None)
            return jsonify({
                'success': True,
                'message': result,
                'redirect_url': url_for('payment_success', order_id=order_id)
            })
        else:
            # Payment failed
            return jsonify({
                'success': False,
                'message': result
            })
            
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        return jsonify({'error': 'Failed to process payment'}), 500

@app.route('/payment_success/<int:order_id>')
def payment_success(order_id):
    """Payment success page"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))
    
    return render_template('payment_success.html', order_id=order_id, user=session['user'])

@app.route('/order_status/<int:order_id>')
def order_status(order_id):
    """Order status page"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))
    
    # Call SOAP service to get order status
    result = soap_client.get_order_status(order_id)
    
    if isinstance(result, dict):
        # Ensure the order has the correct structure for the template
        order = result
        # Add 'id' field if it doesn't exist (template expects order.id)
        if 'id' not in order and 'order_id' in order:
            order['id'] = order['order_id']
        # Add 'created_at' field if it doesn't exist
        if 'created_at' not in order:
            order['created_at'] = datetime.now().isoformat()
        # Add 'payment_date' field if it doesn't exist but payment is processed
        if 'payment_date' not in order and order.get('payment_status') == 'paid':
            order['payment_date'] = datetime.now().isoformat()
    else:
        flash(f'Error: {result}', 'error')
        return redirect(url_for('index'))
    
    return render_template('status.html', order=order, user=session['user'])

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    """Cancel order via SOAP"""
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            order_id = data.get('order_id')
        else:
            # Handle form data
            order_id = request.form.get('order_id')
        
        # Convert order_id to int
        if order_id:
            order_id = int(order_id)
        
        # Call SOAP service to cancel order
        result = soap_client.cancel_order(order_id)
        
        if 'cancelled successfully' in result.lower():
            return jsonify({
                'success': True,
                'message': result,
                'redirect_url': url_for('index')
            })
        else:
            return jsonify({
                'success': False,
                'message': result
            })
            
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        return jsonify({'error': 'Failed to cancel order'}), 500

@app.route('/process_refund', methods=['POST'])
def process_refund():
    """Process refund via SOAP"""
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            order_id = data.get('order_id')
            reason = data.get('reason')
            refund_amount = data.get('refund_amount')
        else:
            # Handle form data
            order_id = request.form.get('order_id')
            reason = request.form.get('reason')
            refund_amount = request.form.get('refund_amount')
        
        # Convert order_id to int
        if order_id:
            order_id = int(order_id)
        
        # Convert refund_amount to float if provided
        if refund_amount:
            refund_amount = float(refund_amount)
        
        # Call SOAP service to process refund
        result = soap_client.process_refund(order_id, reason, refund_amount)
        
        if 'refund processed successfully' in result.lower():
            return jsonify({
                'success': True,
                'message': result
            })
        else:
            return jsonify({
                'success': False,
                'message': result
            })
            
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        return jsonify({'error': 'Failed to process refund'}), 500

@app.route('/admin/orders')
def admin_orders():
    """Admin page to view all orders"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))
    
    # Call SOAP service to get all orders
    result = soap_client.get_all_orders()
    
    if isinstance(result, dict) and 'orders' in result:
        orders = result['orders']
    else:
        orders = {}
        flash(f'Error loading orders: {result}', 'error')
    
    return render_template('admin_orders.html', orders=orders, user=session['user'])

@app.route('/status')
def status():
    """General status page - shows form to enter order ID"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))
    
    return render_template('status_form.html', user=session['user'])

@app.route('/check_order_status', methods=['POST'])
def check_order_status():
    """Handle order status form submission"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('main'))
    
    order_id = request.form.get('order_id')
    if not order_id:
        flash('Please enter an order ID', 'error')
        return redirect(url_for('status'))
    
    try:
        order_id = int(order_id)
        return redirect(url_for('order_status', order_id=order_id))
    except ValueError:
        flash('Please enter a valid order ID', 'error')
        return redirect(url_for('status'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
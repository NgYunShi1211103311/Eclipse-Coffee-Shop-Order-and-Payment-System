# Eclipse Coffee Shop SOAP Service

A comprehensive coffee shop ordering system with both SOAP and web interfaces, featuring enhanced payment success notifications and complete order management functionality.

## Features

### ✅ Implemented Functions

1. Create Order - Create new coffee orders with customer details and cart items
2. Process Payment - Handle payments with multiple payment methods
3. Get Order Status - Retrieve detailed order information and status
4. Cancel Order - Cancel orders that haven't been paid yet

## Installation

1. **Clone the repository**:
   cd (to where you saved the folder)
   cd eclipse_coffee_soap_service
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Services

### 1. Web Interface (Flask)

Start the web interface on port 5000:
python soap_service.py

Access the web interface at: http://localhost:5000

### 2. SOAP Service

Start the SOAP service on port 8000:
python soap_server.py

SOAP WSDL available at: http://localhost:8000/?wsdl

## API Documentation

### Web Interface Endpoints

#### Create Order
- **URL**: `/create_order`
- **Method**: POST
- **Parameters**:
  - `name`: Customer name
  - `email`: Customer email
  - `cart`: JSON string of cart items
- **Response**: JSON with order ID and redirect URL

#### Process Payment
- **URL**: `/process_payment`
- **Method**: POST
- **Parameters**:
  - `order_id`: Order ID (integer)
  - `amount`: Payment amount (float)
  - `payment_method`: Payment method (string)
- **Response**: JSON with success status and redirect URL

#### Get Order Status
- **URL**: `/get_order_status`
- **Method**: POST
- **Parameters**:
  - `order_id`: Order ID (integer)
- **Response**: JSON with order details

#### Cancel Order
- **URL**: `/cancel_order`
- **Method**: POST
- **Parameters**:
  - `order_id`: Order ID (integer)
- **Response**: JSON with success status

### SOAP Service Methods

#### createOrder
```python
def createOrder(customer_name: str, customer_email: str, cart_items: str) -> str
```
Creates a new order and returns order details.

#### processPayment
```python
def processPayment(order_id: int, amount: float, payment_method: str) -> str
```
Processes payment for an order and returns confirmation.

#### getOrderStatus
```python
def getOrderStatus(order_id: int) -> str
```
Returns detailed order status as JSON string.

#### cancelOrder
```python
def cancelOrder(order_id: int) -> str
```
Cancels an unpaid order and returns confirmation.

## Testing

### Test SOAP Service
Run the comprehensive SOAP test client:
```bash
python test_soap_client.py
```

This will test all SOAP functions:
1. Create order
2. Get order status
3. Process payment
4. Get updated status
5. Create another order
6. Cancel order
7. Verify cancellation

### Test Web Interface
1. Open http://localhost:5000
2. Add items to cart
3. Complete checkout
4. Process payment
5. View order status
6. Try canceling an unpaid order

## Payment Success Features

#Enhanced Success Notification
When payment is successful, users experience:
- **Animated Success Icon**: Bouncing checkmark with smooth animations
- **Confetti Animation**: Colorful confetti falling from the top
- **Success Sound**: Pleasant audio feedback (if supported)
- **Detailed Information**: Payment amount, order ID, and confirmation
- **Auto-redirect**: Smooth transition to order status page

# Visual Enhancements
- Gradient background for success messages
- Smooth fade-in animations
- Responsive design for all screen sizes
- Professional color scheme and typography

#Order States
- **Pending**: Order created, payment not yet processed
- **Confirmed**: Payment processed, order being prepared
- **Cancelled**: Order cancelled (only possible before payment)

### Payment Methods
- Credit Card
- Debit Card
- Tng
- Paid at Cash

### Order Timeline
- Order Placed
- Payment Processed (if paid)
- Order Confirmed (if paid)

## File Structure

```
eclipse_coffee_soap_service/
├── soap_service.py          # Flask web interface
├── soap_server.py           # SOAP service implementation
├── test_soap_client.py      # SOAP service test client
├── service.wsdl             # SOAP WSDL definition
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── templates/              # HTML templates
│   ├── index.html          # Main menu page
│   ├── checkout.html       # Checkout page
│   ├── payment.html        # Payment page with success notification
│   └── status.html         # Order status page
└── static/                 # Static assets
    ├── css/
    │   └── style.css       # Custom styles
    └── pic/                # Coffee images
```

## Dependencies

- **Flask**: Web framework
- **Spyne**: SOAP service framework
- **lxml**: XML processing
- **requests**: HTTP client for testing
- **Bootstrap**: UI framework
- **Font Awesome**: Icons

## Troubleshooting

### Common Issues

1. **Port already in use**:
   - Change ports in the respective service files
   - Kill existing processes using the ports

2. **SOAP service not responding**:
   - Ensure Spyne is properly installed
   - Check firewall settings
   - Verify WSDL endpoint

3. **Payment success not showing**:
   - Check browser console for JavaScript errors
   - Ensure all static files are loading
   - Verify payment processing endpoint

### Debug Endpoints

- **Debug Orders**: http://localhost:5000/debug/orders
- **SOAP WSDL**: http://localhost:8000/?wsdl
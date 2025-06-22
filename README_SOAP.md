# Eclipse Coffee Shop - SOAP-Based Architecture

## Overview

This project implements a complete coffee shop ordering system using a **SOAP (Simple Object Access Protocol) web service architecture**. All business logic and data operations are handled through the SOAP service, while the Flask web application serves as a user interface that calls the SOAP service for all operations.

## Architecture Components

### 1. SOAP Server (`soap_server_complete.py`)
- **Port**: 8000
- **WSDL**: http://localhost:8000/?wsdl
- **Purpose**: Contains all business logic and data storage
- **Technology**: Spyne framework

### 2. SOAP Client (`soap_client.py`)
- **Purpose**: Provides a clean interface for the Flask app to call SOAP functions
- **Technology**: Zeep library
- **Features**: Error handling, JSON parsing, logging

### 3. Flask Web Application (`app.py`)
- **Port**: 5000
- **Purpose**: User interface and session management
- **Technology**: Flask framework
- **Role**: Calls SOAP service for all business operations

## SOAP Service Functions

All business operations are implemented as SOAP functions:

### User Management
- `registerGuest(name, email, phone, notes)` - Register guest users
- `registerMember(first_name, last_name, email, phone, password)` - Register member users
- `loginMember(email, password)` - Authenticate member users

### Order Management
- `createOrder(customer_name, customer_email, cart_items)` - Create new orders
- `getOrderStatus(order_id)` - Retrieve order status and details
- `cancelOrder(order_id)` - Cancel pending orders

### Payment Processing
- `processPayment(order_id, amount, payment_method)` - Process payments
- `processRefund(order_id, reason, refund_amount)` - Process refunds

### Administrative
- `getAllOrders()` - Retrieve all orders (for debugging/admin)

## How to Run

### Option 1: Use the Startup Script (Recommended)
```bash
python start_services.py
```

### Option 2: Manual Start
```bash
# Terminal 1: Start SOAP server
python soap_server_complete.py

# Terminal 2: Start Flask app
python app.py
```

## Testing

### Test SOAP Functions
```bash
python test_soap_functions.py
```

### Manual Testing
1. Visit http://localhost:5000/
2. Register as guest or member
3. Browse coffee menu
4. Add items to cart
5. Complete checkout
6. Process payment
7. View order status
8. Test refund functionality

## Key Features

### ✅ Complete SOAP Integration
- All business logic is in the SOAP service
- Flask app only handles UI and session management
- Clean separation of concerns

### ✅ User Management
- Guest registration and login
- Member registration and authentication
- Session management

### ✅ Order Processing
- Cart management
- Order creation
- Order status tracking
- Order cancellation

### ✅ Payment Methods
- TNG (Touch 'n Go)
- Credit Card
- Debit Card
- Cash payment

### ✅ Refund System
- Full and partial refunds
- Multiple refund reasons
- Refund tracking

### ✅ Modern UI
- Responsive design
- Payment success animations
- Real-time cart updates
- Modal dialogs

## Data Flow

```
User Interface (Flask) → SOAP Client → SOAP Server → Response
```

1. **User interacts** with Flask web interface
2. **Flask app** calls SOAP client methods
3. **SOAP client** sends SOAP requests to SOAP server
4. **SOAP server** processes business logic and returns response
5. **Response flows back** through the same path to user

## Conclusion

This SOAP-based architecture provides a robust, scalable foundation for the Eclipse Coffee Shop ordering system. The clear separation between the SOAP service (business logic) and Flask application (user interface) ensures maintainability and allows for future enhancements while maintaining the core SOAP web service functionality. 
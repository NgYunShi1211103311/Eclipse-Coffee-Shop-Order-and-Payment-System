from flask import Flask, render_template, request, jsonify, send_from_directory
from zeep import Client
import os
import logging

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

# SOAP client setup
WSDL_URL = "http://localhost:8000/?wsdl"
logger.debug(f"WSDL URL: {WSDL_URL}")
client = Client(WSDL_URL)

@app.route('/')
def index():
    try:
        logger.debug("Attempting to render index.html")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory(static_folder, filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {str(e)}")
        return f"Error: {str(e)}", 404

@app.route('/get_order', methods=['POST'])
def get_order():
    logger.debug("get_order route accessed")
    order_id = int(request.form.get('order_id'))
    try:
        result = client.service.getOrder(order_id)
        logger.debug(f"getOrder result: {result}")
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"Error in get_order: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/payment', methods=['POST'])
def payment():
    logger.debug("payment route accessed")
    order_id = int(request.form.get('order_id'))
    amount = float(request.form.get('amount'))
    try:
        result = client.service.payment(order_id, amount)
        logger.debug(f"payment result: {result}")
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"Error in payment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Start the Flask application
    logger.info("Starting Flask application on http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0') 
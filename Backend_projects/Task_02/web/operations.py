'''Mathematical operation routes for the Flask application.

This module defines routes for basic arithmetic operations: add, subtract,
multiply, and divide. All routes require JWT authentication.
'''

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .utils import perform_operation

# Define the operations blueprint
op = Blueprint('op', __name__)

@op.route('/add', methods=['POST'])
@jwt_required()
def add():
    '''Endpoint to perform addition of two numbers.'''
    data = request.get_json()
    return jsonify(result=perform_operation(data['a'], data['b'], 'add'))

@op.route('/subtract', methods=['POST'])
@jwt_required()
def subtract():
    '''Endpoint to perform subtraction of two numbers.'''
    data = request.get_json()
    return jsonify(result=perform_operation(data['a'], data['b'], 'subtract'))

@op.route('/multiply', methods=['POST'])
@jwt_required()
def multiply():
    '''Endpoint to perform multiplication of two numbers.'''
    data = request.get_json()
    return jsonify(result=perform_operation(data['a'], data['b'], 'multiply'))

@op.route('/divide', methods=['POST'])
@jwt_required()
def divide():
    '''Endpoint to perform division of two numbers.'''
    data = request.get_json()
    return jsonify(result=perform_operation(data['a'], data['b'], 'divide'))

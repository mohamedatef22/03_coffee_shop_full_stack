import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
@cross_origin()
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@cross_origin()
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@cross_origin()
@requires_auth('post:drinks')
def add_drinks(jwt):
    data = json.loads(request.data.decode('utf-8'))

    if 'post:drinks' not in jwt['permissions']:
        abort(401)
    try:
        drink = Drink(title=data['title'], recipe=json.dumps(data['recipe']))
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@cross_origin()
@requires_auth('patch:drinks')
def edit_drinks(jwt, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    data = json.loads(request.data.decode('utf-8'))
    try:
        drink.title = data['title']
    except Exception:
        pass
    try:
        drink.recipe = json.dumps(data['recipe'])
    except Exception:
        pass
    try:
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
            })
    except Exception:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@cross_origin()
@requires_auth('delete:drinks')
def delete_drinks(jwt, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
            })
    except Exception:
        abort(422)

# Error Handling


'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

#!/usr/bin/env python3

from flask import make_response, jsonify, request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

# FIX: Import pre-configured items directly from the lab's config layout
from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return make_response(jsonify({'error': 'Unprocessable Entity: Missing required fields'}), 422)
            
        try:
            # Build the new user record matching parameters
            new_user = User(
                username=username,
                bio=data.get('bio'),
                image_url=data.get('image_url')
            )
            
            # This triggers the @password.setter defined inside your models.py
            new_user.password = password
                
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            return make_response(jsonify(new_user.to_dict()), 201)
            
        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({'error': 'Username already exists'}), 422)


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # Uses your model's native hybrid method to authenticate the hash
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return make_response(jsonify(user.to_dict()), 200)
            
        return make_response(jsonify({'error': 'Unauthorized access credentials'}), 401)


class Logout(Resource):
    def delete(self):
        if not session.get('user_id'):
            return make_response(jsonify({'error': 'Unauthorized'}), 401)
            
        session.pop('user_id', None)
        return make_response('', 204)


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                return make_response(jsonify(user.to_dict()), 200)
                
        return make_response(jsonify({'error': 'Unauthorized'}), 401)


# Register endpoints using the imported api manager instance
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

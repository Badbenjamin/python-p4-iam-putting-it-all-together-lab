#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if data.get('username') != None:
        new_user = User(
            username = data.get('username'),
            image_url = data.get('image_url'),
            bio = data.get('bio')
        )
        new_user.password_hash=data['password']
        
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        print(session)
        return new_user.to_dict(), 201
    else:
        return {'message' : 'error'}, 422

@app.route('/check_session')
def check_session():
    #  query db for user. make sure user cookie id matches user id in db
    print(session)
    user = User.query.filter(User.id == session['user_id']).first()
    print(user)
    if user is None:

        return {"error": 'not logged in'}, 401
    else:
        return user.to_dict(), 200
   

@app.route('/login', methods=['POST'])
def login():
    
    data = request.get_json()
    print("d", data)
    print("un", data.get('username'))
    user = User.query.filter(User.username == data.get('username')).first()
    print("u", user)
    if user is None:
        return {'error' : 'login failed'}, 401
    if not user.authenticate(data.get('password')):
        return {'error' : 'login failed'}, 401
    
    session['user_id']=user.id

    return user.to_dict(), 200


@app.route('/logout', methods=['DELETE'])
def logout():
    print(session)
    if session['user_id'] is not None:
        session['user_id'] = None
        return {}, 204
    else:
        return {'error' : 'not logged in'}, 401


@app.route('/recipes')
def get_recipes():
    pass

# api.add_resource(Signup, '/signup', endpoint='signup')
# api.add_resource(CheckSession, '/check_session', endpoint='check_session')
# api.add_resource(Login, '/login', endpoint='login')
# api.add_resource(Logout, '/logout', endpoint='logout')
# api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
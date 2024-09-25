#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

import pprint

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if data.get('username') != None:
        new_user = User(
            username = data.get('username'),
            image_url = data.get('image_url'),
            bio = data.get('bio')
        )
        # use setter to generate and store pw hash
        new_user.password_hash=data['password']
        
        db.session.add(new_user)
        db.session.commit()
        # set session (secure cookie obj) to user id (id from db)
        session['user_id'] = new_user.id
        print(session)
        return new_user.to_dict(), 201
    else:
        return {'message' : 'error'}, 422

@app.route('/check_session')
def check_session():
    #  query db for user. make sure user cookie id matches user id in db
    user = User.query.filter(User.id == session['user_id']).first()
    # if no match is found, cookie is altered or user is not logged in
    if user is None:

        return {"error": 'not logged in'}, 401
    else:
        return user.to_dict(), 200
   

@app.route('/login', methods=['POST'])
def login():
    # get json data from login
    data = request.get_json()
    # query for matching user from data
    user = User.query.filter(User.username == data.get('username')).first()
    # if user doesn't yield result, then the json contained an invalid user
    if user is None:
        return {'error' : 'login failed'}, 401
    # make sure password for user object and JSON password match
    if not user.authenticate(data.get('password')):
        return {'error' : 'login failed'}, 401
    
    # set session to user id
    # session info will be encrypted and sent to browser as cookie
    # flask can access the info and decrypt to access session data
    session['user_id']=user.id

    return user.to_dict(), 200


@app.route('/logout', methods=['DELETE'])
def logout():
    print(session)
    if session['user_id'] is not None:
        session['user_id'] = None
        # or session.pop('user_id')
        return {}, 204
    else:
        return {'error' : 'not logged in'}, 401


@app.route('/recipes', methods=['GET', 'POST'])
def get_recipes():
    if session['user_id'] is None:
        return {'error' : 'not logged in'}, 401
    
    if request.method == 'GET': 
        return [recipe.to_dict(only=('title', 'instructions', 'minutes_to_complete', 'user')) for recipe in Recipe.query.all()], 200
    
    if request.method == 'POST':
        data = request.get_json()
        # try will run code if no error is raised by Recipe initializaton
        # we have a @validates function that raises a Value error
        try:
            new_recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=session['user_id']
            )
            new_recipe.user = User.query.filter(User.id == session['user_id']).first()
        # if a ValueError is raised, this block runs
        # ValueError as e will allow error message from Recipe to be passed to our message
        except ValueError as e:
            return {'error' : f'{e}'}, 422
        # pprint.pprint(type(new_recipe.to_dict()['user']))
        # print(type(new_recipe))
        if all(new_recipe.to_dict()):

            db.session.add(new_recipe)
            db.session.commit()
            # print(new_recipe.to_dict())
            return new_recipe.to_dict(), 201
        else: 
            return {'error' : 'missing fileds'}, 422


if __name__ == '__main__':
    app.run(port=5555, debug=True)
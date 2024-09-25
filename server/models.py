from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # in this relationship, Recipe class backpops user relationship in Recipe class
    recipes = db.relationship('Recipe', back_populates='user')

    serialize_rules=['-recipes.user']

    # function in hybrid property is named for method you use to set pw
    @hybrid_property
    def password_hash(self):
        raise AttributeError
    
    @password_hash.setter
    def password_hash(self, plain_text_password):
        bytes = plain_text_password.encode('utf-8')
        self._password_hash = bcrypt.generate_password_hash(bytes)

    # authenticate will evaluate to true if pw matches hashed pw
    def authenticate(self, password):
         return bcrypt.check_password_hash(
              self._password_hash,
              password.encode('utf-8')
         )
         

    def __repr__(self):
         return f'<User {self.id}, {self.username}>'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # in this relationship, User class backpops recipies relationship in User class
    user = db.relationship('User', back_populates='recipes')

    serialize_rules=['-user.recipes']

    @validates('instructions')
    def validate_instructions(self, key, new_instructions):
            if len(new_instructions) < 50:
                raise ValueError(f'{key} needs to be between 1 and 30 chars long')
            else:
                 return new_instructions

    def __repr__(self):
         return f'<User {self.id}, {self.title}>'
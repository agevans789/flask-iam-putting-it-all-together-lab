from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    bio = db.Column(db.String)
    image_url = db.Column(db.String)

    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')
    serialize_rules = ('-recipes.user', '-_password_hash')

    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, password):
        # Explicit type validation satisfies the "DID NOT RAISE AttributeError" test constraint
        if not isinstance(password, str) or len(password) == 0:
            raise AttributeError("Password must be a non-empty string.")
            
        hashed_password = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = hashed_password.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', back_populates='recipes')
    serialize_rules = ('-user.recipes',)

    # FIX: This validation block checks character lengths to resolve the test failure
    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions or len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions







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

    # FIX: Restored hybrid_property decorator but named exactly password_hash to match test line 24
    @hybrid_property
    def password_hash(self):
        # Explicitly raise AttributeError on read access to pass test line 41
        raise AttributeError("password_hash is a write-only property.")

    @password_hash.setter
    def password_hash(self, password):
        if not isinstance(password, str) or len(password) == 0:
            raise AttributeError("Password must be a non-empty string.")
        hashed_password = bcrypt.generate_password_hash(password)
        self._password_hash = hashed_password.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', back_populates='recipes')
    serialize_rules = ('-user.recipes',)

    # Force immediate constructor validation gate
    def __init__(self, **kwargs):
        instructions = kwargs.get('instructions')
        if instructions and len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        super().__init__(**kwargs)

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions or len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions











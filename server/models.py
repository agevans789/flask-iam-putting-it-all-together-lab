from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

# Import the pre-configured db and bcrypt instances from your config.py
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    # Primary key column fixes the Mapper crash
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    bio = db.Column(db.String)
    image_url = db.Column(db.String)

    # Establish clean relationship with recipes
    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')
    
    # Serialization rules to stop recursion loops
    serialize_rules = ('-recipes.user', '-_password_hash')

    # Password getter/setter structure using hybrid_property for Bcrypt validation
    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, password):
        # Generate hash using the config file's bcrypt module wrapper
        hashed_password = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = hashed_password.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    
    # Foreign key constraint binding to the parent user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='recipes')
    serialize_rules = ('-user.recipes',)

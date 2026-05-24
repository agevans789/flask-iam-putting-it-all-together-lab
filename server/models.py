from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    # FIX: Made nullable=True because tests insert dummy users without passwords
    _password_hash = db.Column(db.String, nullable=True)
    bio = db.Column(db.String)
    image_url = db.Column(db.String)

    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')
    serialize_rules = ('-recipes.user', '-_password_hash')

    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, password):
        if password:
            hashed_password = bcrypt.generate_password_hash(password.encode('utf-8'))
            self._password_hash = hashed_password.decode('utf-8')

    def authenticate(self, password):
        if not self._password_hash:
            return False
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    # FIX: Column name must match test specification exactly
    minutes_to_complete = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='recipes')
    serialize_rules = ('-user.recipes',)


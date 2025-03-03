# from flask_sqlalchemy import SQLAlchemy

from . import db
from flask_login import UserMixin
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash

#db = SQLAlchemy()
#DB_NAME = "database.sqlite3"

class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(150))
    date_joined = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Kyiv')))
    profile_pic = db.Column(db.String(200), default="./profile_photo/default.png", nullable=False)

    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def __str__(self):
        return '<Customer %r>' % Customer.id

product_category = db.Table(
    'product_category',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_description = db.Column(db.String(2000), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=True)
    in_stock = db.Column(db.Integer, nullable=True)
    product_picture = db.Column(db.String(1000), nullable=False)
    date_added = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Kyiv')))

    categories = db.relationship('Category', secondary=product_category, back_populates='products')
    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))

    def __str__(self): # легше читати дані, тобто буде показуватись не ділянка в пам'яті об'єкта, а його назва
        return '<Product %r>' % self.product_name

    @property
    def discount(self):
        if self.previous_price and self.current_price:
           return round((self.previous_price - self.current_price) / self.previous_price * 100, 2)
        return 0

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)

    products = db.relationship('Product', secondary=product_category, back_populates='categories')

    def __str__(self):
        return '<Category %r>' % self.category_name

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        return '<Cart %r>' % self.id

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        return '<Order %r>' % self.id
from flask import Blueprint, render_template, flash, redirect, request, jsonify, send_from_directory
from intasend import APIService
from sqlalchemy import desc, case
from flask_login import login_required, current_user
from . import db
from .models import Product, Cart, Order, Category

views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'ISPubKey_test_31387f66-10f3-47e5-aecc-a3313f784300'

API_TOKEN = 'ISSecretKey_test_c8481a22-3e9f-4461-b2c4-7dacade85628'


@views.route('/')
def home():
    items = Product.query.order_by(
        desc(
            case(
                (Product.previous_price > 0, (Product.previous_price - Product.current_price) / Product.previous_price),
                else_=0
            )
        )
    ).all()

    categories_ = Category.query.all()

    return render_template('home.html', categories=categories_, items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id,
                                       customer_link=current_user.id).first()
    if item_exists:
        try:
            if item_exists.quantity != item_to_add.in_stock:
               item_exists.quantity += 1
               db.session.commit()
               flash(f'Quantity of "{item_exists.product.product_name}" has been updated in Cart.', 'success')
               return redirect(request.referrer)
            flash(f"Quantity of '{item_exists.product.product_name}' not updated in Cart. Item's max quantity has been used up.", 'warning')
            return redirect(request.referrer)
        except Exception as e:
            print(e)
            flash(f'Quantity of "{item_exists.product.product_name}" has not been updated.', 'warning')
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'Item "{new_cart_item.product.product_name}" has been added to cart.', 'success')
    except Exception as e:
        print(e)
        flash(f'Item "{new_cart_item.product.product_name}" has not been added to cart.', 'danger')

    return redirect(request.referrer)

@views.route('/cart')
@login_required
def cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount+200)

@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id') # читає посилання після ? GET http://localhost:5000/pluscart?cart_id=123
        cart_item = Cart.query.get(cart_id)
        product = Product.query.get(cart_item.product_link)

        if cart_item.quantity != product.in_stock:
           cart_item.quantity += 1
           db.session.commit()

           cart = Cart.query.filter_by(customer_link=current_user.id).all()
           amount = 0

           for item in cart:
               amount += item.product.current_price * item.quantity

           data = {
              'quantity': cart_item.quantity,
              'amount': amount,
              'total': amount + 200
           }

           return jsonify(data)

@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)

@views.route('/removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
    if customer_cart:
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price * item.quantity

            service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
            create_order_response = service.collect.mpesa_stk_push(phone_number='254712345678', email=current_user.email,
                                                                   amount=total + 200, narrative='Purchase of goods')

            for item in customer_cart:
                new_order = Order()
                new_order.quantity = item.quantity
                new_order.price = item.product.current_price

                new_order.status = create_order_response['invoice']['state'].capitalize()
                new_order.payment_id = create_order_response['id']

                new_order.product_link = item.product_link
                new_order.customer_link = item.customer_link
                db.session.add(new_order)

                product = Product.query.get(item.product_link)
                product.in_stock -= item.quantity
                db.session.delete(item)

                db.session.commit()

            flash('Order is placed successfully', 'success')
            return redirect('/orders')
        except Exception as e:
            print(e)
            flash('Order is not placed', 'danger')
            return redirect('/')
    else:
        flash('Your Cart is empty', 'warning')
        return redirect('/')


@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)

@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(
            Product.product_name.ilike(f'%{search_query}%')
        ).order_by(
           desc(
             case(
                 (Product.previous_price > 0, (Product.previous_price - Product.current_price) / Product.previous_price),
                 else_=0
             )
           )
        ).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')

@views.route('/categories/<int:category_id>')
def categories(category_id):
    category = Category.query.get(category_id)
    items = Product.query.filter(
        Product.categories.any(id=category_id)
    ).order_by(
        desc(
            case(
                (Product.previous_price > 0, (Product.previous_price - Product.current_price) / Product.previous_price),
                else_=0
            )
        )
    ).all()

    return render_template("search.html", items=items, category=category)
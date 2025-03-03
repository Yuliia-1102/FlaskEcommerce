from flask import Blueprint, render_template, flash, send_from_directory, redirect, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from website.forms import ShopItemsForm, OrderForm
from website.models import Product, Order, Customer, Category
from website import db

admin = Blueprint('admin', __name__, url_prefix='/')

@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename) # admin.py in website; ./media=media -> search in website
                                                             # ../media -> search in FlaskEcom

@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 1:
        form = ShopItemsForm()

        categories = Category.query.all()
        form.categories.choices = [(category.id, category.category_name) for category in categories]

        if form.validate_on_submit(): # відправили успішно форму - POST
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            selected_categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
            product_description = form.product_description.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)

            new_shop_item = Product()
            new_shop_item.product_name = product_name
            new_shop_item.current_price = current_price
            new_shop_item.previous_price = previous_price
            new_shop_item.in_stock = in_stock
            new_shop_item.product_description = product_description
            new_shop_item.categories.extend(selected_categories)

            new_shop_item.product_picture = file_path

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'Item "{product_name}" has been added.', 'success')
                return redirect('/add-shop-items')
            except Exception as e:
                print(e)
                flash('Item could not be added.', 'danger')
        else:
            if request.method == "POST":
               flash('Item could not be added.', 'danger')

        return render_template('add_shop_items.html', form=form)

    return render_template('404.html')

@admin.route('/shop-items')
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        for item in items:
            print(item)
        return render_template('shop_items.html', items=items)
    return render_template('404.html')

@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = ShopItemsForm()
        item_to_update = Product.query.get(item_id)

        form.product_name.render_kw = {'placeholder': item_to_update.product_name}
        form.previous_price.render_kw = {'placeholder': item_to_update.previous_price}
        form.current_price.render_kw = {'placeholder': item_to_update.current_price}
        form.in_stock.render_kw = {'placeholder': item_to_update.in_stock}
        form.product_description.render_kw = {'placeholder': item_to_update.product_description}

        categories = Category.query.all()
        form.categories.choices = [(category.id, category.category_name) for category in categories]

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            selected_categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
            product_description = form.product_description.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)

            try:
                Product.query.filter_by(id=item_id).update(dict(product_name=product_name,
                                                                current_price=current_price,
                                                                previous_price=previous_price,
                                                                in_stock=in_stock,
                                                                product_description=product_description,
                                                                product_picture=file_path))
                item_to_update.categories = selected_categories

                db.session.commit()
                flash(f'"{product_name}" updated successfully!', 'success')
                return redirect('/shop-items')
            except Exception as e:
                print('Product is not updated', e)
                flash('Item is not updated!', 'danger')

        else:
            if request.method == "POST":
                flash('Item could not be updated.', 'danger')

        return render_template('update_item.html', form=form)

    return render_template('404.html')

@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(item_id)
            orders_to_delete = Order.query.filter_by(product_link=item_id).all()

            for order in orders_to_delete:
                db.session.delete(order)

            db.session.delete(item_to_delete)
            db.session.commit()
            flash(f'"{item_to_delete.product_name}" deleted', 'success')
            return redirect('/shop-items')
        except Exception as e:
            print('Item not deleted', e)
            flash('Item is not deleted!', 'danger')
        return redirect('/shop-items')

    return render_template('404.html')


@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.id == 1:
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')

@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.id == 1:
        form = OrderForm()
        order = Order.query.get(order_id)

        previous_status = order.status

        if form.validate_on_submit():
            new_status = form.order_status.data

            if previous_status == new_status:
                flash(f'Status is already "{previous_status}"!', 'warning')
                return redirect(request.referrer)

            order.status = new_status
            product = Product.query.get(order.product_link)

            if new_status == 'Canceled':
               product.in_stock += order.quantity

            elif previous_status == 'Canceled' and new_status != 'Canceled':
                if product.in_stock >= order.quantity:
                   product.in_stock -= order.quantity
                else:
                    flash(f'Not enough stock for product "{product.product_name}"!', 'danger')
                    return redirect(request.referrer)

            try:
                db.session.commit()
                flash(f'Order updated successfully', 'success')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Order not updated', 'danger')
                return redirect('/view-orders')

        return render_template('order_update.html', form=form)

    return render_template('404.html')

@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id == 1:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')

@admin.route('/delete-customer/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def delete_customer(customer_id):
    if current_user.id == 1:
        customer_to_delete = Customer.query.get(customer_id)
        orders_to_delete = Order.query.filter_by(customer_link=customer_id).all()

        for order in orders_to_delete:
            db.session.delete(order)

        db.session.delete(customer_to_delete)
        db.session.commit()
        flash(f'Customer "{customer_to_delete.username}" deleted successfully', 'success')
        return redirect('/customers')
    return render_template('404.html')

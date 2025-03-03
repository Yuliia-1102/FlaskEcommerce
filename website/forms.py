from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, SubmitField
from wtforms.fields.choices import SelectMultipleField, SelectField
from wtforms.validators import DataRequired, length, NumberRange, Optional, ValidationError, InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize


class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), length(min=2)])
    password1 = PasswordField('Enter your password', validators=[DataRequired(), length(min=2)])
    password2 = PasswordField('Confirm your password', validators=[DataRequired(), length(min=2)])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Enter your password', validators=[DataRequired(), length(min=2)])
    submit = SubmitField('Log in')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current password', validators=[DataRequired(), length(min=2)])
    new_password = PasswordField('New password', validators=[DataRequired(), length(min=2)])
    confirm_new_password = PasswordField('Confirm your new password', validators=[DataRequired(), length(min=2)])
    change_password = SubmitField('Change password')

class ShopItemsForm(FlaskForm):
    product_name = StringField('Product name', validators=[DataRequired(), length(max=100)])
    current_price = FloatField('Current Price', validators=[DataRequired(), NumberRange(min=0.99)], render_kw={"type": "number", "min": "0.99", "step": "0.01"})
    previous_price = FloatField('Previous price', validators=[Optional(), NumberRange(min=0.99)],  render_kw={"placeholder": "Optional", "type": "number", "min": "0.99", "step": "0.01"})
    in_stock = IntegerField('In stock', validators=[InputRequired(), NumberRange(min=0)])
    product_picture = FileField('Product picture', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'avif'], 'Only JPG, JPEG, PNG, WEBP and AVIF files are allowed!'),
                                                               FileSize(max_size=20 * 1024 * 1024, message='File size exceeds 20MB limit!')])
    categories = SelectMultipleField('Category', choices=[], validators=[DataRequired()])
    product_description = StringField('Product description', validators=[DataRequired(), length(max=2000)])

    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')

    def validate_current_price(self, field):
        if self.previous_price.data and self.current_price.data:
            if self.current_price.data >= self.previous_price.data:
                raise ValidationError("Current price must be lower than previous price. Or else there is no discount.")

class ProfilePhotoForm(FlaskForm):
    profile_pic = FileField('Profile picture', validators=[FileRequired(),
                                                           FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG, JPEG and PNG files are allowed!'),
                                                           FileSize(max_size=20 * 1024 * 1024, message='File size exceeds 20MB limit!')])
    update_picture = SubmitField('Save')

class OrderForm(FlaskForm):
    order_status = SelectField('Order Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'),
                                                        ('Out for delivery', 'Out for delivery'),
                                                        ('Delivered', 'Delivered'), ('Canceled', 'Canceled')])

    update = SubmitField('Update Status')
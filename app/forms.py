from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, NumberRange

class ItemForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    submit = SubmitField('Save Item')

class PurchaseForm(FlaskForm):
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired()])
    buying_price = FloatField('Buying Price', validators=[DataRequired()])
    selling_price = FloatField('Selling Price', validators=[DataRequired()])
    submit = SubmitField('Add Purchase')

class SalesForm(FlaskForm):
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Sale')

class EditSalesForm(FlaskForm):
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    selling_price = DecimalField('Selling Price', places=2, validators=[DataRequired()])
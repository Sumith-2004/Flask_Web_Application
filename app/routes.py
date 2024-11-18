from flask import render_template, redirect, url_for, request, flash, session
from app import app, db
from app.models import Company, Item, Purchase, Sales
from app.forms import ItemForm, PurchaseForm, SalesForm, EditSalesForm

#---------------------------------------INVENTORY------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def inventory():
    company = Company.query.first()
    form = ItemForm()
    if request.method == 'POST' and 'add_balance' in request.form:
        add_amount = request.form.get('add_amount') 
        if add_amount:
            company.cash_balance += float(add_amount)
            db.session.commit()
            flash("Balance added successfully!", "success")

    if form.validate_on_submit():
        existing_item = Item.query.filter(Item.item_name.ilike(form.item_name.data.strip())).first()
        if existing_item:
            flash(f"Item '{form.item_name.data}' already exists!", "danger")
        else:
            new_item = Item(item_name=form.item_name.data, qty=0)
            db.session.add(new_item)
            db.session.commit()
            flash("Item added successfully!", "success")
        return redirect(url_for('inventory'))    
    page = request.args.get('page', 1, type=int)
    items = Item.query.paginate(page=page, per_page=10)
    return render_template('inventory.html', company=company, items=items, form=form)

@app.route('/edit_itemname/<int:item_id>', methods=['GET', 'POST'])
def edit_itemname(item_id):
    company = Company.query.first()
    item_to_edit = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item_to_edit)
    if form.validate_on_submit():
        item_to_edit.item_name = form.item_name.data.strip()
        db.session.commit()
        flash("Item name updated successfully!", "success")
        return redirect(url_for('inventory'))
    return render_template('edit_itemname.html', form=form, company=company)

#--------------------------------------------ADD PURCHASE-------------------------------------------------------------
@app.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    form = PurchaseForm()
    company = Company.query.first()
    if company is None:
        return "No company found. Please add company details."
    if company.cash_balance is None:
        company.cash_balance = 0  
    form.item_id.choices = [(item.id, item.item_name) for item in Item.query.all()]    
    if 'purchase_cart' not in session:
        session['purchase_cart'] = []    
    if form.validate_on_submit():
        item_id = form.item_id.data
        qty = form.qty.data
        buying_price = form.buying_price.data
        selling_price = form.selling_price.data
        selected_item = Item.query.get(item_id)
        item_in_cart = next((item for item in session['purchase_cart'] if item['item_id'] == item_id), None)
        if item_in_cart:
            flash("Item is already in the cart.", "danger")
        elif qty <= 0:
            flash("Please enter a valid quantity greater than 0", "danger")
        elif buying_price <= 0:
            flash("Please enter a valid price", "danger")
        elif selling_price <= 0:
            flash("Please enter a valid price", "danger")
        elif selling_price > 0 and selling_price < buying_price:
            flash("Caution: Selling price is lower than buying price.", "danger")
        else:
            session['purchase_cart'].append({
                'item_id': item_id,
                'item_name': dict(form.item_id.choices).get(item_id),
                'qty': qty,
                'buying_price': buying_price,
                'selling_price': selling_price,
                'rate': qty * buying_price
            })
            session.modified = True
    total_amount = sum(item['rate'] for item in session['purchase_cart'])
    return render_template('add_purchase.html', form=form, company=company, purchase_cart=session['purchase_cart'], total_amount=total_amount)

@app.route('/edit_cart_item/<int:index>', methods=['GET', 'POST'])
def edit_cart_item(index):
    company = Company.query.first()
    cart = session.get('purchase_cart', [])
    if index < 0 or index >= len(cart):
        flash("Item not found in cart", "danger")
        return redirect(url_for('add_purchase'))    
    item_data = cart[index]
    form = PurchaseForm(
        item_id=item_data['item_id'],
        qty=item_data['qty'],
        buying_price=item_data['buying_price'],
        selling_price=item_data['selling_price']
    )
    form.item_id.choices = [(item.id, item.item_name) for item in Item.query.all()]
    selected_item = Item.query.get(item_data['item_id'])
    if form.validate_on_submit():
        entered_qty = form.qty.data
        if entered_qty > selected_item.qty:
            flash("Insufficient quantity available. Please enter a valid quantity.", "danger")
            return render_template('edit_cart_item.html', form=form, company=company)  
        cart[index] = {
            'item_id': form.item_id.data,
            'item_name': dict(form.item_id.choices).get(form.item_id.data),
            'qty': entered_qty,
            'buying_price': form.buying_price.data,
            'selling_price': form.selling_price.data,
            'rate': entered_qty * form.buying_price.data
        }
        session['purchase_cart'] = cart
        session.modified = True
        flash("Item updated in cart.", "success")
        return redirect(url_for('add_purchase'))  
    return render_template('edit_cart_item.html', form=form, company=company)

@app.route('/checkout_purchase', methods=['POST'])
def checkout_purchase():
    company = Company.query.first()
    purchase_cart = session.get('purchase_cart', [])
    total_amount = sum(item['rate'] for item in purchase_cart)
    if company.cash_balance >= total_amount:
        company.cash_balance -= total_amount
        for item in purchase_cart:
            purchase = Purchase(
                item_id=item['item_id'],
                qty=item['qty'],
                rate=item['buying_price'],
                amount=item['rate'],
                selling_price=item['selling_price']
            )
            db.session.add(purchase)
            item_in_db = Item.query.get(item['item_id'])
            item_in_db.qty += item['qty']
        db.session.commit()
        session.pop('purchase_cart', None)  
        flash("Purchase completed successfully!", "success")
    else:
        flash("Not enough balance to complete the purchase.", "danger")
    return redirect(url_for('add_purchase'))
@app.route('/remove_cart_item/<int:index>', methods=['GET'])
def remove_cart_item(index):
    try:
        session['purchase_cart'].pop(index)
        session.modified = True
        flash("Item removed from cart", "success")
    except IndexError:
        flash("Item not found in cart", "danger")
    return redirect(url_for('add_purchase'))

#--------------------------------------------ADD SALES---------------------------------------------------------------
@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    app.logger.debug(f"Current sale_cart before rendering: {session.get('sale_cart', [])}")
    form = SalesForm()
    company = Company.query.first()
    items = Item.query.all()
    form.item_id.choices = [(item.id, item.item_name) for item in items]
    if 'sale_cart' not in session:
        session['sale_cart'] = []
    sale_cart = session['sale_cart']
    if form.validate_on_submit():
        item = Item.query.get(form.item_id.data)
        if any(cart_item['item_id'] == form.item_id.data for cart_item in sale_cart):
            flash(f"Item {item.item_name} is already in the cart.", "danger")
            return redirect(url_for('add_sale'))
        if item and form.qty.data <= item.qty:
            purchase = Purchase.query.filter_by(item_id=form.item_id.data).order_by(Purchase.timestamp.desc()).first()
            if purchase:
                selling_price = purchase.selling_price
            else:
                flash(f"No selling price found for {item.item_name}.", "danger")
                return redirect(url_for('add_sale'))
            sale_cart.append({
                'item_id': form.item_id.data,
                'item_name': item.item_name,
                'qty': form.qty.data,
                'rate': selling_price,
                'amount': selling_price * form.qty.data
            })
            session['sale_cart'] = sale_cart
            session.modified = True
            flash(f"{item.item_name} added to cart successfully!", "success")
            return redirect(url_for('add_sale'))
        else:
            flash(f"Not enough stock available for {item.item_name}.", "danger")
    total_amount = sum(item['amount'] for item in sale_cart)
    return render_template('add_sale.html', form=form, company=company, sale_cart=sale_cart, total_amount=total_amount)

@app.route('/checkout_sale', methods=['POST'])
def checkout_sale():
    company = Company.query.first()
    sale_cart = session.get('sale_cart', [])
    if not sale_cart:
        flash("Cart is empty. Cannot checkout.", "danger")
        return redirect(url_for('add_sale'))
    try:
        total_amount = sum(item['amount'] for item in sale_cart)
        company.cash_balance += total_amount
        for item in sale_cart:
            sale = Sales(
                item_id=item['item_id'],
                qty=item['qty'],
                rate=item['rate'],
                amount=item['amount']
            )
            db.session.add(sale)
            item_in_db = Item.query.get(item['item_id'])
            item_in_db.qty -= item['qty']
        db.session.commit()
        session.pop('sale_cart', None)
        flash("Sale completed successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred during checkout. Please try again.", "danger")
    return redirect(url_for('add_sale'))

@app.route('/edit_sale_cart_item/<int:index>', methods=['GET', 'POST'])
def edit_sale_cart_item(index):
    company = Company.query.first()
    cart = session.get('sale_cart', [])
    if index < 0 or index >= len(cart):
        flash("Item not found in cart", "danger")
        return redirect(url_for('add_sale'))
    item_data = cart[index]
    item = Item.query.get(item_data['item_id'])  
    if not item:
        flash("Item not found in inventory.", "danger")
        return redirect(url_for('add_sale'))
    form = EditSalesForm(
        item_id=item_data['item_id'],
        qty=item_data['qty'],
        selling_price=item_data['rate']
    )
    form.item_id.choices = [(item.id, item.item_name) for item in Item.query.all()]
    if form.validate_on_submit():
        new_qty = form.qty.data  
        if new_qty > item.qty:
            flash(f"Insufficient stock for {item.item_name}. Available quantity: {item.qty}.", "danger")
            return render_template('edit_sale_cart_item.html', form=form, company=company, item_data=item_data)
        cart[index] = {
            'item_id': form.item_id.data,
            'item_name': dict(form.item_id.choices).get(form.item_id.data),
            'qty': new_qty,
            'rate': float(form.selling_price.data),
            'amount': float(form.selling_price.data) * new_qty,
        }
        session['sale_cart'] = cart
        session.modified = True
        flash("Item updated in cart.", "success")
        return redirect(url_for('add_sale'))
    return render_template('edit_sale_cart_item.html', form=form, company=company, item_data=item_data)

@app.route('/remove_sale_cart_item/<int:index>', methods=['GET'])
def remove_sale_cart_item(index):
    try:
        session['sale_cart'].pop(index)
        session.modified = True
        flash("Item removed from cart", "success")
    except IndexError:
        flash("Item not found in cart", "danger")
    return redirect(url_for('add_sale'))

#-------------------------------REPORT----------------------------------------------------------------
@app.route('/report')
def report():
    company = Company.query.first()
    purchase_records = Purchase.query.all()
    sales_records = Sales.query.all()
    return render_template(
        'report.html',
        purchase_records=purchase_records,
        sales_records=sales_records,
        company=company
    )
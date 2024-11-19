from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import team8dbi as dbi
# import cs304dbi_sqlite3 as dbi

#dbi.conf('team8_db')
#conn = dbi.connect()
#team databse

import secrets

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = secrets.token_hex()

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('main.html',
                           page_title='Main Page')

# You will probably not need the routes below, but they are here
# just in case. Please delete them if you are not using them

@app.route('/greet/', methods=["GET", "POST"])
def greet():
    if request.method == 'GET':
        return render_template('greet.html',
                               page_title='Form to collect username')
    else:
        try:
            username = request.form['username'] # throws error if there's trouble
            flash('form submission successful')
            return render_template('greet.html',
                                   page_title='Welcome '+username,
                                   name=username)

        except Exception as err:
            flash('form submission error'+str(err))
            return redirect( url_for('index') )
        

#route for filtering
@app.route('/search', methods=['GET'])
def search_listings():
    item_type = request.args.get('item_type', '')
    item_color  = request.args.get('item_color ', '')
    item_usage = request.args.get('item_usage', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    item_size = request.args.get('item_size', '')

    # Build query
    query = Listings.query

    if item_type:
        query = query.filter(Listings.item_type.ilike(f'%{item_type}%'))
    if item_color:
        query = query.filter(Listings.color.ilike(f'%{item_color}%'))
    if item_usage:
        query = query.filter(Listings.usage.ilike(f'%{item_usage}%'))
    if min_price is not None:
        query = query.filter(Listings.item_price >= min_price)
    if max_price is not None:
        query = query.filter(Listings.item_price <= max_price)
    if item_size:
        query = query.filter(Listings.item_size.ilike(f'%{item_size}%'))

    # Fetch the filtered items
    Listings = query.all()

    return render_template('search_results.html', Listings=Listings)

# This route displays all the data from the submitted form onto the rendered page
# It's unlikely you will ever need anything like this in your own applications, so
# you should probably delete this handler

@app.route('/formecho/', methods=['GET','POST'])
def formecho():
    if request.method == 'GET':
        return render_template('form_data.html',
                               page_title='Display of Form Data',
                               method=request.method,
                               form_data=request.args)
    elif request.method == 'POST':
        return render_template('form_data.html',
                               page_title='Display of Form Data',
                               method=request.method,
                               form_data=request.form)
    else:
        raise Exception('this cannot happen')

# This route shows how to render a page with a form on it.

@app.route('/testform/')
def testform():
    # these forms go to the formecho route
    return render_template('testform.html',
                           page_title='Page with two Forms')


if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'put_database_name_here_db' 
    print(f'will connect to {db_to_use}')
    dbi.conf(db_to_use)
    app.debug = True
    app.run('0.0.0.0',port)

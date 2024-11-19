from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi

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
    
@app.route('/search', methods=['GET'])
def search_listings():
    user_search = request.args.get('query', '')  
    print(f"Search Term: {user_search}") 

    if not user_search:
        query = "select * from listing"
        query_info = []
    else:
        query = """
            select * 
            from listing 
            where item_color LIKE %s OR item_type LIKE %s OR item_usage LIKE %s OR item_desc LIKE %s
        """
        params = [f"%{user_search}%" for _ in range(4)]

    try:
        #debug statements - was having issues
        print(f"query: {query}")
        print(f"added parameter(s): {query_info}")
        
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute(query, tuple(query_info))
        listings = curs.fetchall()

        print(f"Found these listings: {listings}")

        return render_template('search.html', listings=listings)

    except Exception as error:
        flash(f"Error with the search query: {str(error)}")
        return redirect(url_for('index'))


#route for filtering
#@app.route('/search', methods=['GET'])
#def search_listings():
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

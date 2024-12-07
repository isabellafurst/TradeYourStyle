from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/path/to/the/uploads' # change this to something - i'm not sure what yet
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}



app = Flask(__name__)


# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
import sys, os, random

# import cs304dbi_sqlite3 as dbi

dbi.conf('team8_db')
conn = dbi.connect()
#team databse

import secrets

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = secrets.token_hex()

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

@app.route('/')
def index():
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from listing, user where listing.uid = user.uid order by post_date DESC;''')
    listings = curs.fetchall()
    return render_template('main.html',
                           page_title='Main Page', listings = listings)

# You will probably not need the routes below, but they are here
# just in case. Please delete them if you are not using them
    
@app.route('/search/', methods=['GET'])
# New route merges search_listings functions to include filtering
def search_listings():
    item_type = request.args.getlist('item_type')  
    item_color = request.args.getlist('item_color')
    item_usage = request.args.getlist('item_usage')
    item_price = request.args.getlist('item_price')
    item_size = request.args.getlist('item_size')
    trade_type = request.args.get('trade_type') 
    item_status = request.args.get('item_status')
    
    # reaching into base.html -- search bar contents
    user_search = request.args.get('query', '').strip()

    # build query based on filters
    query = "select * from listing where 1=1"  # the 1=1 is just a placeholder so we can add more stuff to the query 
    filters = []

    # actually construct the query based on what the user is filtering by
    if item_type:
        query += " AND item_type IN %s"
        filters.append(tuple(item_type)) # convert to tuples so SQL code doesn't screw up, adds the actual filter values to the filters list so it can become a big strong query
    if item_color:
        query += " AND item_color IN %s"
        filters.append(tuple(item_color))
    if item_usage:
        query += " AND item_usage IN %s"
        filters.append(tuple(item_usage))
    if item_price:
        query += " AND item_price IN %s"
        filters.append(tuple(item_price))
    if item_size:
        query += " AND item_size IN %s"
        filters.append(tuple(item_size))
    if trade_type is not None:
        query += " AND trade_type = %s"
        filters.append(trade_type == 'on') # value is "on" since its a checkbox; if it's None the box is not checked
    if item_status is not None:
        query += " AND item_status = %s"
        filters.append(item_status == 'on')
    
    if user_search:
        # searches across multiple columns in table
        query += """
        AND (
            item_color LIKE %s OR
            item_desc LIKE %s OR
            item_type LIKE %s
        )
        """
        search_term = f"%{user_search}%" 
        filters.extend([search_term, search_term, search_term])

    print(f"Actual Query: {query}")
    print(f"Filters: {filters}")

    try:
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute(query, tuple(filters))  # actually execute the query (u wanna work sooooo bad)
        listings = curs.fetchall()

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
    if item_size:
        query = query.filter(Listings.item_size.ilike(f'%{item_size}%'))

    # Fetch the filtered items
    Listings = query.all()

    return render_template('search_results.html', Listings=Listings)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/image/<id>')
def image(id):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''select item_image from listing where lis_id = %s;''',
        [id])
    pic = curs.fetchone()
    return send_from_directory(app.config['UPLOAD_FOLDER'], pic['item_image'])



@app.route('/add/', methods=['GET','POST'])
def add_listing():
    if request.method == "POST":
        form_data = request.form

        uid = request.cookies.get('uid')

        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)

        item_desc = form_data['description']
        item_type = form_data['type']
        item_color = form_data['color']
        item_usage = form_data['usage']
        item_price = form_data['price']
        item_size = form_data['size']
        if form_data['trade-type'] == "trade":
            trade_type = 0
        elif form_data['trade-type'] == "free":
            trade_type = 1
 
        curs.execute('''insert into listing(uid, item_desc, item_type, item_color, item_usage, item_price, item_size, trade_type, item_status)
        values(%s, %s, %s, %s, %s, %s, %s, %s, 1);''', [2, item_desc, item_type, item_color, item_usage, item_price, item_size, trade_type])
            # replace 2 with uid later!
        conn.commit()

        curs.execute('''select last_insert_id() as last_id;''')
        lis_id = curs.fetchone()['last_id']

         # photo upload code
        if 'image' not in request.files:
            flash('No file part')
            return render_template("add_listing.html")
        file = request.files['image']
        user_filename = file.filename
        if user_filename == '':
            flash('No selected file')
            return render_template("add_listing.html")
        if file and allowed_file(user_filename):
            ext = user_filename.split('.')[-1]
            filename = secure_filename('{}_{}.{}'.format("2", lis_id, ext)) # replace 2 with uid later!
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        curs.execute('''update listing set item_image = %s where lis_id = %s''', [filename, lis_id])
        conn.commit()

        flash("Item successfully added!")

        return redirect(url_for("index"))

    return render_template('add_listing.html')


if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'team8_db' 
    print(f'will connect to {db_to_use}')
    dbi.conf(db_to_use)
    app.debug = True
    app.run('0.0.0.0',port)

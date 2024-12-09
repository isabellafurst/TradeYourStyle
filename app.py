from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}



app = Flask(__name__)


# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import os

import cs304dbi as dbi
import sys, os, random
import pymysql
import bcrypt
import tradeyourstyle_login as auth


# import cs304dbi_sqlite3 as dbi

dbi.conf('team8_db')
#team databse

import secrets

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = secrets.token_hex()

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

#Home page with user login/join 
@app.route('/')
def index():
    if "username" in session:
        user = True
    else:
        user = False
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    return render_template('greet.html',
                           page_title='Login Page')
#Listing page
@app.route('/main/')
def main():
    if "username" in session:
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''select lis_id, 'uid', item_image, item_desc, item_type, item_color, item_usage, item_price, item_size, item_type, item_status, post_date
                  from listing, user where listing.uid = user.uid order by post_date DESC;''')
        listings = curs.fetchall()
        return render_template('main.html',
                           page_title='Main Page', listings = listings, user = user)
    else:
        flash("Please log in or sign up to see listings")
        return redirect(url_for("index"))

@app.route('/join/', methods=["POST"])
def join():
    username = request.form.get('username')
    passwd1 = request.form.get('password1')
    passwd2 = request.form.get('password2')
    if passwd1 != passwd2:
        flash('passwords do not match')
        return redirect( url_for('index'))
    conn = dbi.connect()
    (uid, is_dup, other_err) = auth.insert_user(conn, username, passwd1)
    if other_err:
        raise other_err
    if is_dup:
        flash('Sorry; that username is taken')
        return redirect(url_for('index'))
    ## success
    flash('FYI, you were issued UID {}'.format(uid))
    session['username'] = username
    session['uid'] = uid
    session['logged_in'] = True
    session['visits'] = 1
    return redirect( url_for('main') )

@app.route('/login/', methods=["POST"])
def login():
    username = request.form.get('username')
    passwd = request.form.get('password')
    conn = dbi.connect()
    (ok, uid) = auth.login_user(conn, username, passwd)
    if not ok:
        flash('login incorrect, please try again or join')
        return redirect(url_for('index'))
    ## success
    print('LOGIN', username)
    flash('successfully logged in as '+username)
    session['username'] = username
    session['uid'] = uid
    session['logged_in'] = True
    session['visits'] = 1
    return redirect( url_for('main') )

@app.route('/user/<username>')
def user(username):
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            username = session['username']
            uid = session['uid']
            session['visits'] = 1+int(session['visits'])
            return render_template('greet.html',
                                   page_title='My App: Welcome {}'.format(username),
                                   name=username,
                                   uid=uid,
                                   visits=session['visits'])
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/logout/')
def logout():
    if 'username' in session:
        username = session['username']
        session.pop('username')
        session.pop('uid')
        session.pop('logged_in')
        flash('You are logged out')
        return redirect(url_for('index'))
    else:
        flash('you are not logged in. Please login or join')
        return redirect( url_for('index') )
    
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
        return redirect(url_for('main'))

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

        uid = session['uid'] # use sessions here instead
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
        values(%s, %s, %s, %s, %s, %s, %s, %s, 1);''', [uid, item_desc, item_type, item_color, item_usage, item_price, item_size, trade_type])
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
            filename = secure_filename('{}_{}.{}'.format(uid, lis_id, ext))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        curs.execute('''update listing set item_image = %s where lis_id = %s''', [filename, lis_id])
        conn.commit()

        flash("Item successfully added!")

        return redirect(url_for("main"))

    return render_template('add_listing.html')

@app.route('/bio/')
def bio():
    if "username" in session:
        
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)

        uid = session['uid']

        curs.execute('''select username, display_name, email from user where uid = %s;''', [uid])
        user = curs.fetchone()

        curs.execute('''select lis_id, 'uid', item_image, item_desc, item_type, item_color, item_usage, item_price, item_size, item_type, item_status, post_date
                  from listing where uid = %s order by post_date DESC;''', [uid])
        listings = curs.fetchall()

        list_num = len(listings)


        return render_template('bio_page.html', listings = listings, user = user, list_num = list_num)



    else:
        flash("You do not have access, please log in or sign up")
        return redirect(url_for("index"))

# @app.route('/listing/<int:lis_id>') Might need this for messaging purposes, but right now it's pissing me AWF <3
# def view_listing(lis_id):
#     conn = dbi.connect()
#     curs = dbi.dict_cursor(conn)
#     curs.execute('''select item_desc, item_type, item_color, item_usage, item_price, item_size, trade_type, item_status
#                     from listing where lis_id = %s;''', [lis_id])
#     listing = curs.fetchone()

#     if listing is None:
#         flash("Listing not found.")
#         return redirect(url_for('main'))

#     return render_template('view_listing.html', listing=listing)

def get_user_by_id(uid): #helper function to get a username from uid
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('select username from user where uid = %s', [uid])
    user = curs.fetchone()
    return user

@app.route('/listing/<int:lis_id>')
def view_comments(lis_id):
    print(session)  #debug statement
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    curs.execute('''select lis_id, item_desc as item_name, item_type, item_color, item_usage, item_price, item_size, item_image 
                    from listing 
                    where lis_id = %s''', [lis_id])
    listing = curs.fetchone()

    # comments for  listing
    curs.execute('select text, post_date, uid from comment where lis_id = %s', [lis_id])
    comments = curs.fetchall()

    # user info for comments
    for comment in comments:
        user = get_user_by_id(comment['uid']) 
        comment['user'] = user  

    return render_template('comments.html', listing=listing, comments=comments)

@app.route('/listing/<int:lis_id>/add_comment', methods=['POST'])
def add_comment(lis_id):
    comment_text = request.form.get('comment_text')
    uid = session.get('uid')  # session to check if user is logged in -- something here is Not Working

    if not uid:
        flash("You must be logged in to comment.")
        return redirect(url_for('view_comments', lis_id=lis_id))  #redirects to viewing comments

    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into comment (lis_id, uid, text, post_date)
                    values (%s, %s, %s, now())''',
                [lis_id, uid, comment_text])
    conn.commit()
    flash("Comment submitted!")
    return redirect(url_for('view_comments', lis_id=lis_id)) #redirects to viewing comments

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

# saving messaging code just in case!!

# Route to view a user's own messages
@app.route('/messages/')
def view_messages():
    # Once login is set up, we can use sessions:
    # if 'uid' not in session: 
    #     flash("Login to view your messages!")
    #     return redirect(url_for('main'))
    # uid = session['uid']
    uid = 1  # temporary for testing
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('''select m.mid, m.time_stamp, u.display_name as sender, 
                    m.message_text, l.item_desc, m.lis_id 
                    from message m
                    join user u on m.sender_uid = u.uid 
                    join listing l on m.lis_id = l.lis_id 
                    where m.lis_id = %s  
                    order by m.time_stamp ASC;
                    ''', [uid])
    messages = curs.fetchall()
    print(messages)  # Check if all messages are fetched
    
    return render_template('messages.html', page_title='Your Messages', messages=messages)

# Route to send a message to another user based on a listing -- also not rly working yet lolz
@app.route('/send_message/<int:lis_id>', methods=['GET', 'POST'])
def send_message(lis_id):
    # if 'uid' not in session:
    #     flash("Login to send messages!")
    #     return redirect(url_for('main'))
    # sender_uid = session['uid']
    sender_uid = 1 #temporary for testing
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)

    # get the lister_uid for the desired listing
    curs.execute('''select uid from listing where lis_id = %s;''', [lis_id])
    lister_uid_row = curs.fetchone()
    if not lister_uid_row:
        flash("No listing found.")
        return redirect(url_for('index'))
    lister_uid = lister_uid_row['uid']

    if request.method == 'POST':
        # insert the new message into the database
        message_text = request.form['message']
        curs.execute('''insert into message (lis_id, lister_uid, sender_uid, time_stamp) 
                        values (%s, %s, %s, now());''', [lis_id, lister_uid, sender_uid])
        conn.commit()
        flash("Message sent!")
        return redirect(url_for('view_messages'))

    # Render message form
    return render_template('send_message.html', page_title='Send Message', lis_id=lis_id)


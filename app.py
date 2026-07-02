from flask import Flask, render_template, request, redirect, url_for, session, flash
import config
from data_structures import LinkedList, Stack, Queue, bubble_sort, binary_search
import database as db          # <-- changed
import email_notifier

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
db.init_db()
# In-memory data structures (loaded from sheets at start, saved after changes)
lost_list = LinkedList()
found_list = LinkedList()
undo_stack = Stack()
notif_queues = {}          # username -> Queue

# User list (for binary search) – we keep usernames sorted
usernames_sorted = []

def load_users():
    global usernames_sorted
    rows = db.get_all_users()
    usernames_sorted = [row['username'] for row in rows]
    bubble_sort(usernames_sorted)

def load_items():
    global lost_list, found_list
    lost_rows = db.get_all_lost()
    found_rows = db.get_all_found()
    for row in lost_rows:
        lost_list.insert_at_head(row)
    for row in found_rows:
        found_list.insert_at_head(row)

def load_notifications():
    global notif_queues
    notif_queues.clear()
    rows = db.get_all_notifications()
    for row in rows:
        user = row['username']
        if user not in notif_queues:
            notif_queues[user] = Queue()
        notif_queues[user].enqueue(row['message'])

# Call on startup
load_users()
load_items()
load_notifications()

# ---------- Routes ----------
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        first = request.form['first']
        last = request.form['last']
        dob = request.form['dob']
        email = request.form['email']
        phone = request.form['phone']
        sid = request.form['student_id']

        # Validation
        if len(pw) < 6:
            flash('Password must be at least 6 characters.')
            return render_template('register.html')
        if '@' not in email or '.' not in email:
            flash('Invalid email.')
            return render_template('register.html')
        if not sid:
            flash('Student ID cannot be empty.')
            return render_template('register.html')

        # Check uniqueness using binary search
        idx = binary_search(usernames_sorted, user)
        if idx != -1:
            flash('Username already exists.')
            return render_template('register.html')

        # Add to Google Sheets
        db.insert_user({
            'username': user,
            'password': pw,
            'first': first,
            'last': last,
            'dob': dob,
            'email': email,
            'phone' : phone,
            'student_id': sid
        })
        # Update in-memory array and sort
        usernames_sorted.append(user)
        bubble_sort(usernames_sorted)
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        # Find user via binary search
        idx = binary_search(usernames_sorted, user)
        if idx == -1:
            flash('User not found.')
            return render_template('login.html')

        # We need the actual password; fetch full user data
        users = db.get_all_users()
        user_data = next((u for u in users if u['username'] == user), None)
        if user_data and user_data['password'] == pw:
            session['username'] = user
            session['email'] = user_data.get('email','')
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password.')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/report_lost', methods=['GET','POST'])
def report_lost():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        room = int(request.form['room'])
        floor = int(request.form['floor'])
        item = request.form['item']
        time_str = request.form['time']
        color = request.form['color']  # now always asked

        data = {
            'username': session['username'],
            'room': room,
            'floor': floor,
            'item': item,
            'color': color,
            'time': time_str
        }
        db.insert_lost(data)
        lost_list.insert_at_head(data)
        # Push a copy for undo
        undo_stack.push(data.copy())
        flash('Lost item reported.')
        return redirect(url_for('dashboard'))
    return render_template('report_lost.html')

@app.route('/report_found', methods=['GET','POST'])
def report_found():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        room = int(request.form['room'])
        floor = int(request.form['floor'])
        item = request.form['item']
        color = request.form['color']
        time_str = request.form['time']

        data = {
            'username': session['username'],
            'room': room,
            'floor': floor,
            'item': item,
            'color': color,
            'time': time_str
        }
        db.insert_found(data)
        found_list.insert_at_head(data)
        undo_stack.push(data.copy())

        # ---- Matching & Notification (Linear Search) ----
        # Walk the lost list and find matches
        cur = lost_list.head
        while cur:
            lost = cur.data
            if lost['room'] == room and lost['floor'] == floor:
                # Simple substring match
                if item.lower() in lost['item'].lower() or lost['item'].lower() in item.lower():
                    # Enqueue notification for the owner of the lost item
                    owner = lost['username']
                    if owner not in notif_queues:
                        notif_queues[owner] = Queue()
                    msg = (
    f"Someone found an item similar to your lost '{lost['item']}' "
    f"in room {room}, floor {floor}. "
    f"Found: '{item}' (color {color}). "
    f"Finder: {session['username']} "
    f"Contact: {finder_phone}"
)
                    notif_queues[owner].enqueue(msg)
                    # Also save notification to Google Sheets
                    db.insert_notification(owner, msg)

                    # Send email notification
                    users = db.get_all_users()
                    finder_data = next((u for u in users if u['username'] == session['username']), None)
                    finder_phone = finder_data['phone'] if finder_data else 'Not provided'
                    owner_data = next((u for u in users if u['username'] == owner), None)
                    if owner_data and 'email' in owner_data:
                        try:
                            email_notifier.send_notification(
                                owner_data['email'],
                                "Lost Item Found Match!",
                                msg
                            )
                        except Exception as e:
                            print(f"Email failed: {e}")
            cur = cur.next

        flash('Found item reported. Notifications sent.')
        return redirect(url_for('dashboard'))
    return render_template('report_found.html')

@app.route('/notifications')
def notifications():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session['username']
    if user in notif_queues:
        msgs = notif_queues[user].to_list()  # all messages
        notif_queues[user].clear()           # empty queue
        # Clear notifications in sheet for this user (optional, we'll just show)
        return render_template('notifications.html', messages=msgs)
    return render_template('notifications.html', messages=[])

@app.route('/undo')
def undo():
    if 'username' not in session:
        return redirect(url_for('login'))
    last = undo_stack.pop()
    if last is None:
        flash('Nothing to undo.')
        return redirect(url_for('dashboard'))

    # Determine if it was lost or found by checking 'color' field logic
    # We stored both with 'color', but lost items also have color field. However,
    # we can decide by looking at the source list: try to remove from lost_list,
    # if not found, remove from found_list.
    # Easier: we stored a copy with all fields; we can just remove based on data presence.
    # We'll search for the exact node in lost and found.
    # Linear search in both lists for exact match on all fields.
    found_node = None
    cur = lost_list.head
    while cur:
        if cur.data == last:
            found_node = cur
            break
        cur = cur.next
    if found_node:
        lost_list.delete_node(found_node)
        flash('Undo successful (lost item removed).')
    else:
        cur = found_list.head
        while cur:
            if cur.data == last:
                found_node = cur
                break
            cur = cur.next
        if found_node:
            found_list.delete_node(found_node)
            flash('Undo successful (found item removed).')
        else:
            flash('No matching item found to undo.')
    db.replace_all_lost(lost_list.to_list())
    db.replace_all_found(found_list.to_list())
    # We should also remove from Google Sheets – for simplicity,
    # we'll just rewrite the whole sheets after undo.
    # But a quick hack: we don't delete from sheet here; you can implement if needed.
    return redirect(url_for('dashboard'))

@app.route('/admin/db')
def admin_db():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Optional: restrict to a specific admin user
    # if session['username'] != 'admin': return "Unauthorized", 403

    users = db.get_all_users()
    lost = db.get_all_lost()
    found = db.get_all_found()
    notifications = db.get_all_notifications()
    return render_template('admin_db.html',
                           users=users, lost=lost, found=found, notifications=notifications)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
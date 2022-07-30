from email.policy import default
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, make_response, request
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import jwt
import datetime
from functools import wraps
import requests
from sendgrid import SendGridAPIClient
from redis import Redis
from rq import Queue
from sendgrid.helpers.mail import *

from api import SENDGRID_API

app = Flask(__name__)

app.config["SECRET_KEY"] = "thisissecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@127.0.0.1:5432/krypto'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True


db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(150))
    admin = db.Column(db.Boolean)
    date_added = db.Column(db.TIMESTAMP)

class Alert(db.Model):
    alert_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String(50))
    desc = db.Column(db.String(50))
    threshold = db.Column(db.Integer)
    mail_to = db.Column(db.String(100))
    status = db.Column(db.String(10))  
    alert_name = db.Column(db.String(50))
    alert_on = db.Column(db.String(50))
    date_added = db.Column(db.TIMESTAMP)

db.create_all()


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='krypto',
                            user="jarun",
                            password="password")
    return conn

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if "X-Access-Token" in request.headers:
            token = request.headers["X-Access-Token"]
                
        if token == None:
            return jsonify({"message": "Token is missing"})
        
        try:
            data = jwt.decode(token, key = app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = Users.query.filter_by(id=data['id']).first()
        except:
            return jsonify({"message": "Token is invalid"}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorator


@app.route("/user/create", methods = ["POST"])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({"message": "User doesn't have permission"})
    
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin= data['admin']=="True", added_on = datetime.datetime.now())
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'New user created!'})


@app.route("/user", methods =["GET"])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({"message": "User doesn't have permission"})

    users = Users.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users' : output})
    

@app.route("/user/<user_id>", methods =["GET"])
@token_required
def get_user(current_user, user_id):

    if not current_user.admin:
        return jsonify({"message": "User doesn't have permission"})

    user = Users.query.filter_by(id = user_id).first()

    if not user:
        return jsonify({"message": "User by the id does not exist"})

    user_data = {}
    user_data['id'] = user.id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'users' : user_data})




# @app.route("/user/delete/<user_id>", methods = ["DELETE"])
# def delete_user(user_id):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute('''DELETE FROM users where name = "Leo Tolstoy"''')
#     conn.commit()
#     return jsonify({"message": "Table deleted"})

#
#
#
#
#
#
#
#
#
#



@app.route("/alerts/create", methods = ["POST"])
@token_required
def create_alert(current_user):
    data = request.get_json()

    new_alert = Alert(alert_id = str(uuid.uuid4()), user_id = current_user.id, desc = data["desc"], threshold = data["threshold"], mail_to = data["mail_to"],status = "initiated", alert_name = data["alert_name"],alert_on = data['alert_on'], date_added = datetime.datetime.now())
    db.session.add(new_alert)
    db.session.commit()

    return jsonify({"message": "Alert created successfully", "alert" : str(new_alert)})




# 
# Example /alerts/mine?status=initiated
# default: all
# status = {all,initiated, triggered, deleted}
# 
@app.route("/alerts/mine", methods = ["GET"])
@token_required
def get_myalerts_by_status(current_user):

    args = request.args
    status = args.get("status", default = "all", type = str)

    if status != "all":
        alerts = Alert.query.filter_by(user_id = current_user.id). \
            filter_by(status = status).all()
    else:
        alerts = Alert.query.filter_by(user_id = current_user.id).all()

    output = []

    for alert in alerts:
        alert_data = {}
        alert_data['alert_id'] = alert.alert_id
        alert_data['user_id'] = alert.user_id
        alert_data['alert_name'] = alert.alert_name
        alert_data['alert_on'] = alert.alert_on
        alert_data['description'] = alert.desc
        alert_data['mail_to'] = alert.mail_to
        alert_data['status'] = alert.status
        alert_data['threshold'] = alert.threshold
        alert_data['date_added'] = alert.date_added
        output.append(alert_data)

    return jsonify({'alerts' : output})
 


# 
# Paginated: Example :- /alerts?page=1
# 
@app.route("/alerts", methods = ["GET"])
@token_required
def get_all_alert(current_user):

    if not current_user.admin:
        return jsonify({"message": "User doesn't have permission"})

    args = request.args
    print(args)
    page = args.get('page', default = 1, type=int)
    rows_per_page = 5
    alerts = Alert.query.paginate(page=page, per_page=rows_per_page).items

    if not alerts:
        return jsonify({"message": "Alerts does not exists"})

    output = []

    for alert in alerts:
        alert_data = {}
        alert_data['alert_id'] = alert.alert_id
        alert_data['user_id'] = alert.user_id
        alert_data['alert_name'] = alert.alert_name
        alert_data['alert_on'] = alert.alert_on
        alert_data['description'] = alert.desc
        alert_data['mail_to'] = alert.mail_to
        alert_data['status'] = alert.status
        alert_data['threshold'] = alert.threshold
        alert_data['date_added'] = alert.date_added
        output.append(alert_data)

    return jsonify({'alerts' : output})


@app.route("/alerts/threshold?<alert_id>", methods = ["PUT"])
@token_required
def update_alert(current_user):
    return

@app.route("/alerts/delete/<alert_id>", methods = ["DELETE"])
@token_required
def delete_alert(current_user, alert_id):
    alert = Alert.query.filter_by(alert_id = alert_id).first()

    if not alert:
        return jsonify({"message":"Alert not found"})
    
    alert.status = "deleted"
    
    db.session.commit()

    return jsonify({"message" : "Alert deleted successfully", "alert_id": alert.alert_id})



#
#
#
#
#
#
#
#
#
#


@app.route("/login")
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response("could not verify", 401, {"WWW-Authenticate": "Basic realm=Login required!"})
    
    user = Users.query.filter_by(name = auth.username).first()

    if not user:
        return make_response("could not verify. User doesn't exist.", 401, {"WWW-Authenticate": "Basic realm=Login required!"})
    
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({"id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)} , app.config["SECRET_KEY"])
        #ToDo: exp time set to 5 hours. reduce it on deployment

        return jsonify({"token": token})
    
    return make_response("could not verify. Password incorrect.", 401, {"WWW-Authenticate": "Basic realm=Login required!"})



def track():
    api = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false"

    res = requests.get(api)
    trackList = res.json()

    sendgrid_client = SendGridAPIClient(SENDGRID_API)
    redis = Redis()
    q = Queue(connection=redis)

    emails = []

    alerts = Alert.query.all()

    for alert in alerts:
        for each in trackList:
            if alert.status == "initiated" and alert.alert_name == each["id"] and alert.threshold > each[alert.alert_on]:
                alert.status = "triggered"
                db.session.commit()
                emails.append(alert.mail_to)

    message = Mail(
        from_email= Email("kryptobot55@gmail.com"),
        to_emails= To(emails),
        html_content= 'The value has reached its threshold',
        subject= 'ALERT!! from kryptos',
        is_multiple=True
    )    

    response = sendgrid_client.send(message)

    print(response.status_code)
    print(response.body)
    print(response.headers)
    # for email in emails:
        # q.enqueue(mail.send_message, sendgrid_client, email)
    
    if len(emails):
        print("Email sent to {}".format(emails))
    

if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.add_job(func=track, trigger='interval', id='track_bot', seconds=10)
    scheduler.start()
    app.run(debug=True)
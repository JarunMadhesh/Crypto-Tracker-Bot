# Krypto-bot
Application Overview
Create a price alert application that triggers an email when the user’s target price is
achieved.

Say, the current price of BTC is 28,000, a user sets an alert for BTC at a price of 33,000.
The application should send an email to the user when the price of BTC reaches 33,000.
Similarly, say, the current price of BTC is 35,000, a user sets an alert for BTC at a price of
33,000. The application should send an email when the price of BTC reaches 33,000.

### Deltailed documentation available in documentation.docx

## Database used
PostGre SQL

## Libraries used
flask - Hosting <br>
psycopg2 - For accessing PostGre database<br>
pyjwt - Json web-tokens<br>
uuid - Creating random ids<br>
functools - Creating decorator function<br>
requests - - http requests<br>
werkzeug - To encrypt and decrypt password while storing<br>
redis, rq - redis queue to send emails<br>
flask_apscheduler - run track function every 10 seconds<br>
flask_sqlalchemy - to simplify sql queries<br>
sendgrid - to send mail<br>


## Installation
1. Install and set up docker
2. Clone the repository and from the directory follow the steps in cmd.
     - docker build -t krypto-bot:1.0 .
     - docker images
     Get the image id of krypto bot 1.0
     - docker run <image-id>


## To run and check the implementation

1. using endpoint create user, create a user<br>
[POST] "/users/create" <br>
{<br>
    "name" : "admin",<br>
    "password": "admin",<br>
    "admin" : "True"<br>
}<br><br>
<br>
2. Login<br>
Basic Auth<br>
{<br>
		username : “admin”,<br>
		password : “admin”<br>
}<br>

3. Create an alert with the following request<br>
header: <br>
{x-access-token : < user-token >}<br>
body:<br>
{<br>
    "desc" : "New alert to check",<br>
    "alert_name" : "okb",<br>
    "alert_on" : "current_price",<br>
    "mail_to" : "< yourmailid >@gmail.com",<br>
    "threshold" : 30<br>
}<br>
<br>
4. You will get a mail to the given email id

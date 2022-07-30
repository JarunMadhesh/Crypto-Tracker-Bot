# Krypto-bot
Application Overview
Create a price alert application that triggers an email when the user’s target price is
achieved.
Say, the current price of BTC is $28,000, a user sets an alert for BTC at a price of 33,000$.
The application should send an email to the user when the price of BTC reaches 33,000$.
Similarly, say, the current price of BTC is 35,000$, a user sets an alert for BTC at a price of
33,000$. The application should send an email when the price of BTC reaches 33,000$.

### Deltailed documentation available in documentation.docx


## Libraries used
flask
psycopg2
pyjwt
uuid
requests
werkzeug
redis
rq
flask_apscheduler
flask_sqlalchemy
sendgrid


## Instalation
1. Install and set up docker
2. Clone the repository and from the directory follow the steps in cmd.
     - docker build -t krypto-bot:1.0 .
     - docker images
     Get the image id of krypto bot 1.0
     - docker run <image-id>

  

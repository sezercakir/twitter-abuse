from flask_mail import Message
from flask import Flask
from flask_mail import Mail

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Example: Use Gmail's SMTP server
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'szrckrrr@gmail.com'  # Replace with your email address
app.config['MAIL_PASSWORD'] = 'hdhkocaljelunwoc'  # Replace with your email password

mail = Mail(app)


@app.route('/send_email')
def send_email():
    # Create a message
    msg = Message('Hello', sender='szrckrrr@gmail.com', recipients=['sebihaozturkten68@gmail.com'])
    msg.body = 'Seni çok seviyorum. Bu mail yazdığım mail servis kodlarıyla atıldı <3 hehehehe :] '

    # Send the message
    mail.send(msg)

    return 'Email sent'


if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'szrckrrr@gmail.com'  # Update with your email
app.config['MAIL_PASSWORD'] = 'hdhkocaljelunwoc'  # Update with your email password

mail = Mail(app)

scheduler = APScheduler()

@app.route('/')
def index():
    return 'Hello, World!'

def scheduled_task():
    with app.app_context():
        # Render email template
        print("Mail sends")
        custom_message = 'This is a custom message from Flask!'  # Custom message to be passed to the template
        email_content = render_template('email_template.html', custom_message=custom_message)

        # Create email message
        msg = Message('Test Email', sender='szrckrrr@gmail.com',
                      recipients=['cakirta18@itu.edu.tr'])  # Update sender and recipients
        msg.html = email_content

        # Send email
        mail.send(msg)

if __name__ == '__main__':
    scheduler.add_job(id='scheduled_task', func=scheduled_task, trigger='interval', seconds=5)
    scheduler.start()
    app.run()

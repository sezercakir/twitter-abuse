from flask import Flask, render_template
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'szrckrrr@gmail.com'  # Update with your email
app.config['MAIL_PASSWORD'] = 'hdhkocaljelunwoc'  # Update with your email password

mail = Mail(app)

@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    # Render email template
    custom_message = 'This is a custom message from Flask!'  # Custom message to be passed to the template
    email_content = render_template('email_template.html', custom_message=custom_message)

    # Create email message
    msg = Message('Test Email', sender='szrckrrr@gmail.com', recipients=['cakirta18@itu.edu.tr'])  # Update sender and recipients
    msg.html = email_content

    # Send email
    mail.send(msg)

    return 'Email sent!'

from flask import Flask, request
from flask_mail import Mail, Message

import os

app = Flask(__name__)

app.config.update(
	#EMAIL SETTINGS
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465, # 587 for TLS, 465 for SSL
    MAIL_USE_SSL = True,
    MAIL_USE_TLS = False,
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER'),
)

MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT')

mail = Mail(app)

@app.route('/razorfuse-flask/', methods=['GET'])
def respond():
    return "OK", 200

@app.route('/razorfuse-flask/', methods=['POST'])
def take_submission():
    required_keys = [
        'form_name', 'form_email', 'form_num_mod',
        'form_num_result', 'form_text'
    ]
    form_values = {}

    if request.method == 'POST':
        f = request.form

        # Check for missing keys
        for key in required_keys:
            if key not in f.keys():
                return 'WARN: Missing Keys. Discarding.', 400

            # Check for non-empty values
            for value in f.getlist(key):
                if value == '':
                    return 'WARN: Empty values found. Discarding.', 400
                else:
                    # BUG: This overloads the value if multi-select exists
                    form_values[key] = value

        for key, value in form_values.items():
            if len(value) > 1000:
                return 'WARN: Form value exceeds max length of 1000. Discarding.', 401

        # Check that the user can do basic addition
        try:
            answer = int(form_values['form_num_mod']) + 42
            if answer != int(form_values['form_num_result']):
                return 'WARN: Captcha math is incorrect. Discarding.', 402
        except:
            return 'WARN: Captcha math is incorrect. Discarding.', 402

        send_message(form_values)

        return 'INFO: Found valid post. Recording.', 200

    return 'WARN: Invalid submission type. Discarding.', 405

def send_message(payload):
    msg = Message(subject="New Form Submission on Razorfuse")
    msg.add_recipient(MAIL_RECIPIENT)

    msg.body = ""
    for key, value in payload.items():
        msg.body += key + " - " + value + "\n"

    mail.send(msg)

if __name__ == "__main__":
    print("INFO: Running Flask...")
    app.run(DEBUG=True)

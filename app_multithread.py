from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
# Configure APScheduler
scheduler = BackgroundScheduler()


@app.route('/')
def my_function():
    # Your logic here
    # ...
    # Add a job to the scheduler to run my_background_task() 5 seconds after the response is sent
    scheduler.add_job(my_background_task, 'interval', seconds=10)
    # Return the rendered HTML template
    return render_template('home.html')


def my_background_task():
    for i in range(1000):
        print(i)


# Start the scheduler when the Flask app is run
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)

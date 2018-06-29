# run.py

import os

from app import create_app, tasks, make_celery

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
	app.run()

#This sets values for all html files instead of having to specify in render_template.
@app.context_processor
def inject_sum_function():
    return dict(sum=sum)


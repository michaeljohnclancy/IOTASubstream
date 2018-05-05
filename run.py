# run.py

import os
import threading

from app import create_app, iota_funcs

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
	app.run()

#This sets values for all html files instead of having to specify in render_template.
@app.context_processor
def inject_sum_function():
    return dict(sum=sum)

@app.context_processor
def inject_iota_loop():
	return dict(listen_loop=iota_funcs.listen_loop)
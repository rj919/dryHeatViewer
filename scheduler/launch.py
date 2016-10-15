__author__ = 'rcj1492'
__created__ = '2015.10'
__license__ = 'MIT'

'''
Dependencies
pip install apscheduler
pip install requests
pip install flask
pip install gevent
pip install gunicorn
pip install Flask-APScheduler
pip install sqlalchemy
pip install psycopg2
pip install jsonmodel
pip install labpack
'''

'''
APScheduler Documentation
https://apscheduler.readthedocs.io/en/latest/index.html

APScheduler Trigger Methods
https://apscheduler.readthedocs.io/en/latest/modules/triggers/date.html
https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html
https://apscheduler.readthedocs.io/en/latest/modules/triggers/interval.html

Flask_APScheduler Documentation
https://github.com/viniciuschiele/flask-apscheduler

Flask Documentation
http://flask.pocoo.org/docs/0.11/deploying/wsgi-standalone/#gevent
'''

# create init path to sibling folders
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# retrieve configuration settings
from scheduler.utils import retrieve_settings
scheduler_settings = retrieve_settings('models/settings_model.json', '../cred/settings.yaml')

# construct job object class
from time import time
from datetime import datetime
current_time = time()
class JobConfig(object):
    JOBS = [
        {
            'id': 'apschedule_started_test_%s' % str(current_time),
            'func': 'launch:app.logger.debug',
            'kwargs': {
                'msg': 'APScheduler started.'
            },
            'trigger': 'date',
            'run_date': '%s+00:00' % datetime.utcfromtimestamp(current_time + 2).isoformat(),
            'replace_existing': True
        }
    ]

    SCHEDULER_VIEWS_ENABLED = True

# construct flask app object
from flask import Flask, request, session, jsonify, url_for, render_template
app = Flask(import_name=__name__)
app.config.from_object(JobConfig())

# initialize logging and debugging
import logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
app.config['ASSETS_DEBUG'] = False

# construct the landing & dashboard for single-page sites
# from scheduler.utils import load_settings
# api_model = load_settings('models/api_model.json')
@app.route('/')
def landing_page():
    return render_template('dashboard.html'), 200

# construct the catchall for URLs which do not exist
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# add requests module to namespace
import requests

# construct scheduler object (with standard settings)
from flask_apscheduler import APScheduler
from apscheduler.schedulers.gevent import GeventScheduler
gevent_scheduler = GeventScheduler()
ap_scheduler = APScheduler(scheduler=gevent_scheduler)
app.config['SCHEDULER_TIMEZONE'] = 'UTC'

# add job store to scheduler
job_store_on = False
job_store_settings = []
job_store_login_names = []
job_store_login_keys = ['user', 'pass', 'host', 'port']
for key in job_store_login_keys:
    key_name = 'scheduler_job_store_%s' % key
    job_store_login_names.append(key_name)
    if scheduler_settings[key_name]:
        job_store_settings.append(scheduler_settings[key_name])
        job_store_on = True
if job_store_on:
    if len(job_store_settings) != len(job_store_login_keys):
        raise IndexError('Initialization of the scheduler job store requires values for all %s login fields.' % job_store_login_names)
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    job_store_url = 'postgresql://%s:%s@%s:%s' % (job_store_settings[0], job_store_settings[1], job_store_settings[2], job_store_settings[3])
    postgresql_store = SQLAlchemyJobStore(url=job_store_url)
    jobstore_settings = { 'default': postgresql_store }
    app.config['SCHEDULER_JOBSTORES'] = jobstore_settings

# adjust other scheduler settings
other_scheduler_fields = [ 'scheduler_job_defaults_coalesce', 'scheduler_job_defaults_max_instances','scheduler_executors_type', 'scheduler_executors_max_workers' ]
if scheduler_settings['scheduler_job_defaults_coalesce']:
    if not app.config['SCHEDULER_JOB_DEFAULTS']:
        app.config['SCHEDULER_JOB_DEFAULTS'] = { 'coalesce': True }
    else:
        pass
# for setting in other_scheduler_fields:
#     if scheduler_settings[setting]:

# app.config['SCHEDULER_JOB_DEFAULTS'] = { 'coalesce': True }

# attach app to scheduler and start scheduler
ap_scheduler.init_app(app)
ap_scheduler.start()

# initialize the test wsgi localhost server
if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', 5001), app)
    http_server.serve_forever()

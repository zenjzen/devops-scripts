"""This module triggers a remote jenkins job"""

import os
import requests

def build_trigger():
    '''remote jenkins job post request'''
    jenkins_user = os.environ['JENKINS_USER']
    jenkins_pw = os.environ['JENKINS_PW']
    jenkins_host = os.environ['JENKINS_HOST']
    jenkins_job = os.environ['JENKINS_JOB']

    jenkins = [
        "http://",
        jenkins_user,
        ":",
        jenkins_pw,
        "@",
        jenkins_host,
        "/jenkins/job/",
        jenkins_job,
        "/build"
    ]

    jenkins_trigger = ''.join(jenkins)

    try:
        response = requests.post(jenkins_trigger)
    except requests.ConnectionError as error:
        print error
        return
    except requests.HTTPError as error:
        print error
        return

    if response.status_code != 201:
        print("Error: status_code:", response.status_code)
        print("Full response:", response)
    else:
        print("Build triggered successfully:", response)

build_trigger()

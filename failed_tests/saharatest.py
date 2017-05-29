from keystoneauth1.identity import v2
from keystoneauth1 import session
from saharaclient import client
import os

auth = v2.Password(auth_url='https://c3se.cloud.snic.se:5000/v3',
                   username='s8770',
                   password=os.environ['SNIC_PW'],
                   tenant_name='e2b5a9a038ac4128bf9efd298d0d8bbc')

ses = session.Session(auth=auth)

#sahara = client.Client('1.0', session=ses)

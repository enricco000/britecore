#!/user/bin/env python2.7

from accounting import *
from accounting.models import *
from accounting.utils import *


"""
Create Policy Four
"""
#Contacts

p4 = Policy('Policy Four', date(2015,2,1) , 500)
p4.billing_schedule = 'Two-Pay'
p4.agent_id = Contact.query.filter_by(name='John Doe', role='Agent').one().id
p4.named_insured = Contact.query.filter_by(name='Ryan Bucket').one().id
db.session.add(p4)
db.session.commit()

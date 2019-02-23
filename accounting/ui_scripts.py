# app/ui_scripts.py

from models import Policy, Contact


class AgentInfo:

    def __init__(self, name):
        self.name = name

    def agent_contact_id(self):
        if Contact.query.filter_by(name=self.name, role='Agent').first():
            return Contact.query.filter_by(name=self.name, role='Agent').one().id
        else:
            return '#DATA MISSING#'

    def agent_policies(self):
        if self.agent_contact_id():
            agent_policies = [x.policy_number for x in Policy.query.filter_by(agent=self.agent_contact_id()).all()]
            return agent_policies
        else:
            return '#DATA MISSING#'


class PolicyInfo:

    def __init__(self, name):
        self.name = name

    def policy_billing_schedule(self):
        if Policy.query.filter_by(policy_number=self.name).first():
            return Policy.query.filter_by(policy_number=self.name).one().billing_schedule
        else:
            return '#DATA MISSING#'

    def policy_effective_date(self):
        if Policy.query.filter_by(policy_number=self.name).first():
            return Policy.query.filter_by(policy_number=self.name).one().effective_date
        else:
            return '#DATA MISSING#'

    def policy_status(self):
        if Policy.query.filter_by(policy_number=self.name).first():
            return Policy.query.filter_by(policy_number=self.name).one().status
        else:
            return '#DATA MISSING#'

    def policy_annual_premium(self):
        if Policy.query.filter_by(policy_number=self.name).first():
            return Policy.query.filter_by(policy_number=self.name).one().annual_premium
        else:
            return '#DATA MISSING#'

    def policy_named_insured(self):
        if Contact.query.filter_by(id=Policy.query.filter_by(policy_number=self.name).one().named_insured, role='Named Insured').first():
            return Contact.query.filter_by(id=Policy.query.filter_by(policy_number=self.name).one().named_insured, role='Named Insured').one().name
        else:
            return '#DATA MISSING#'

    def policy_agent(self):
        if Contact.query.filter_by(id=Policy.query.filter_by(policy_number=self.name).one().agent, role='Agent').first():
            return Contact.query.filter_by(id=Policy.query.filter_by(policy_number=self.name).one().agent, role='Agent').one().name
        else:
            return '#DATA MISSING#'

    def policy_dict_info(self):
        if Policy.query.filter_by(policy_number=self.name).all():
            pol_dict = {
                "agent_name": self.policy_agent(),
                "policy_number": self.name,
                "effective_date": self.policy_effective_date(),
                "status": self.policy_status(),
                "billing_scheme": self.policy_billing_schedule(),
                "annual_premium": self.policy_annual_premium(),
                "named_insured": self.policy_named_insured()
            }
            pol_dict = {k: unicode(v).encode('utf-8') for k, v in pol_dict.iteritems()}
            return pol_dict
        else:
            return '#DATA MISSING#'

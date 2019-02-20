#!/user/bin/env python2.7

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from accounting import db
from models import Contact, Invoice, Payment, Policy

import dateutil.parser as dparser
from sqlalchemy import update

"""
#######################################################
This is the base code for the engineer project.
#######################################################
"""


class PolicyAccounting(object):
    """
     Each policy has its own instance of accounting.
     Class inherits from python object every policy has to be backed in the db
     This class has the following methods:
     return_account_balance,
     make_payment,
     make_invoices,
     evaluate_cancellation_pending_due_to_non_pay,
     evaluate_cancel
    """

    def __init__(self, policy_id):
        """
        Gets policy from database using policy id. Makes invoices if missing
        :param policy_id: item from db
        :return: policy object
        """
        self.policy = Policy.query.filter_by(id=policy_id).one()

        if not self.policy.invoices:
            self.make_invoices()

    def return_account_balance(self, date_cursor=None):
        """
        Calculates the ammount due to a date
        :param date_cursor: date. Use today if not specified
        :return due_now: ammount due (int)
        """
        if not date_cursor:
            date_cursor = datetime.now().date()

        invoices = Invoice.query.filter_by(policy_id=self.policy.id)\
                                .filter(Invoice.bill_date <= date_cursor)\
                                .order_by(Invoice.bill_date)\
                                .all()
        due_now = 0
        for invoice in invoices:
            due_now += invoice.amount_due

        payments = Payment.query.filter_by(policy_id=self.policy.id)\
                                .filter(Payment.transaction_date <= date_cursor)\
                                .all()
        for payment in payments:
            due_now -= payment.amount_paid

        return due_now

    def make_payment(self, contact_id=None, date_cursor=None, amount=0):
        """
        Adds payment to the payment table
        :param contact_id: id of table contacts. Use None if not specified (int)
        :param date_cursor: date. Use today if not specified
        :param ammount: ammount payed. Zero if not specified (int)
        return payment: shows contact id, ammount and date for checking
        """
        if not date_cursor:
            date_cursor = datetime.now().date()

        if not contact_id:
            try:
                contact_id = self.policy.named_insured
            except:
                pass

        payment = Payment(self.policy.id,
                          contact_id,
                          amount,
                          date_cursor)
        db.session.add(payment)
        db.session.commit()

        return payment

    def evaluate_cancellation_pending_due_to_non_pay(self, date_cursor=None):
        """
         If this function returns true, an invoice
         on a policy has passed the due date without
         being paid in full. However, it has not necessarily
         made it to the cancel_date yet.
        """
        if not date_cursor:
            date_cursor = datetime.now().date()

        last_invoice = Invoice.query.filter_by(policy_id=self.policy.id)\
            .filter(Invoice.cancel_date > date_cursor).filter(Invoice.due_date <= date_cursor)\
            .order_by(Invoice.bill_date.desc())\
            .first()

        if last_invoice:
            print("THIS POLICY IS IN THE EVALUATION PERIOD. IT'S CANCELLING SOON")

        else:
            print("THIS POLICY IS NOT IN THE EVALUATION PERIOD")

    def evaluate_cancel(self, date_cursor=None):
        """
        Cancells policy if there are missing payments or if
        the cancel date has passed
        :param date_cursor: date. Use today if not specified
        """
        if not date_cursor:
            date_cursor = datetime.now().date()

        invoices = Invoice.query.filter_by(policy_id=self.policy.id)\
                                .filter(Invoice.cancel_date <= date_cursor)\
                                .order_by(Invoice.bill_date)\
                                .all()

        for invoice in invoices:
            if not self.return_account_balance(invoice.cancel_date):
                continue
            else:
                print "THIS POLICY SHOULD HAVE CANCELED"
                break
        else:
            print "THIS POLICY SHOULD NOT CANCEL"

    def make_invoices(self):
        """
        make invoices of the policy
        according to a billing schedule (annual, two-pay,
        quarterly, monthly)
        """
        for invoice in self.policy.invoices:
            invoice.delete()

        # added Two-Pay billing schedule; removed 'Semi-Annual'
        billing_schedules = {'Annual': None, 'Two-Pay': 2, 'Quarterly': 4, 'Monthly': 12}

        invoices = []
        first_invoice = Invoice(self.policy.id,
                                self.policy.effective_date,  # bill_date
                                self.policy.effective_date + relativedelta(months=1),  # due
                                self.policy.effective_date + \
                                relativedelta(months=1, days=14),  # cancel
                                self.policy.annual_premium)
        invoices.append(first_invoice)

        if self.policy.billing_schedule == "Annual":
            pass
        elif self.policy.billing_schedule == "Two-Pay":
            first_invoice.amount_due = self.policy.annual_premium / \
                billing_schedules.get(self.policy.billing_schedule)
            for i in range(1, billing_schedules.get(self.policy.billing_schedule)):
                months_after_eff_date = i*6
                bill_date = self.policy.effective_date + relativedelta(months=months_after_eff_date)
                invoice = Invoice(self.policy.id,
                                  bill_date,
                                  bill_date + relativedelta(months=1),
                                  bill_date + relativedelta(months=1, days=14),
                                  self.policy.annual_premium / billing_schedules.get(self.policy.billing_schedule))
                invoices.append(invoice)
        elif self.policy.billing_schedule == "Quarterly":
            first_invoice.amount_due = self.policy.annual_premium / \
                billing_schedules.get(self.policy.billing_schedule)
            for i in range(1, billing_schedules.get(self.policy.billing_schedule)):
                months_after_eff_date = i*3
                bill_date = self.policy.effective_date + relativedelta(months=months_after_eff_date)
                invoice = Invoice(self.policy.id,
                                  bill_date,
                                  bill_date + relativedelta(months=1),
                                  bill_date + relativedelta(months=1, days=14),
                                  self.policy.annual_premium / billing_schedules.get(self.policy.billing_schedule))
                invoices.append(invoice)
        elif self.policy.billing_schedule == "Monthly":
            # monthly invoice calculation
            first_invoice.amount_due = self.policy.annual_premium / \
                billing_schedules.get(self.policy.billing_schedule)
            for i in range(1, billing_schedules.get(self.policy.billing_schedule)):
                months_after_eff_date = i * 12
                bill_date = self.policy.effective_date + relativedelta(months=months_after_eff_date)
                invoice = Invoice(self.policy.id,
                                  bill_date,
                                  bill_date + relativedelta(months=1),
                                  bill_date + relativedelta(months=1, days=14),
                                  self.policy.annual_premium / billing_schedules.get(self.policy.billing_schedule))
                invoices.append(invoice)
        else:
            print "You have chosen a bad billing schedule."

        for invoice in invoices:
            db.session.add(invoice)
        db.session.commit()


###
# TRANSFORM INPUTS TO DATA TYPES INT OR DATE
###

def is_integer(value):
    """
    IF POSSIBLE, TRANSFORM AN INPUT TO AN INTEGER
    """
    try:
        value = int(value)
    except ValueError:
        print("You must use an integer value for this input\n")
        options()
    return value


def is_date(value):
    """
    iF POSSIBLE, TRANSFORM AN INPUT TO A DATE
    """
    try:
        value = dparser.parse(value)
    except ValueError:
        print("You must use a date for this input\n")
        options()
    return value


###
# OPTIONS FOR THE SHELL
###

def run():
    return options()


def options():
    print("Select one of the following options using a number q for exit")
    print("0. Build or refresh db")
    print("1. Create policy")
    print("2. Update policy")
    print("3. Make payment")
    print("c Hide options")
    print("q Quit program")
    options = raw_input("Select an option ")

    if options == "0":
        build_or_refresh_db()
        print("\n")
        run()

    elif options == "1":
        print("--> you selected policy creation")
        policy_number = raw_input("Policy number ")

        if Policy.query.filter_by(policy_number=policy_number).count() >= 1:
            print('%s already exists\n' % policy_number)
            run()

        effective_date = raw_input("Effective date (yyyymmdd) ")
        effective_date = is_date(effective_date)
        print(effective_date)

        billing_dict = {'1': 'Annual',
                        '2': 'Two_pay',
                        '3': 'Quarterly',
                        '4': 'Monthly'}
        billing = raw_input(
            "Select a billing schedule\n1. Annual\n2. Two-Pay\n3. Quarterly\n4. Monthly\n")
        billing = billing_dict.get(billing)
        print('you selected %s billing' % billing)

        named_insured = raw_input("Named insured ")

        agent = raw_input("Agent ")

        annual_premium = raw_input("Annual premium $")
        annual_premium = is_integer(annual_premium)

        p = Policy(policy_number, effective_date, annual_premium)
        p.billing_schedule = billing
        if Contact.query.filter_by(name=agent, role=agent).count() > 0:
            p.agent_id = Contact.query.filter_by(name=agent, role='Agent').one().id
        if Contact.query.filter_by(name=named_insured).count() > 0:
            p.named_insured = Contact.query.filter_by(
                name=named_insured, role='Named Insured').one().id
        db.session.add(p)
        db.session.commit()
        print("\n")
        run()

    elif options == "2":
        print("--> you selected policy update")
        policy_number = raw_input("Policy number ")
        if Policy.query.filter_by(policy_number=policy_number).count() < 1:
            print('%s does not exist\n' % policy_number)
            run()
        else:
            p = Policy.query.filter_by(policy_number=policy_number).one()
            effective_date = raw_input("Update effective date? y/[n] ")
            if effective_date == 'y':
                effective_date = raw_input("Set the new date (yyyymmdd) ")
                effective_date = is_date(effective_date)
                p.effective_date = effective_date
                db.session.commit()
            status = raw_input("Update status? y/[n] ")
            if status == 'y':
                status_dict = {'1': 'Active',
                               '2': 'Cancelled',
                               '3': 'Expired'}
                status = raw_input("Select new status\n1. Active\n2. Cancelled\n3. Expired\n")
                status = status_dict.get(status)
                db.session.commit()
            billing_schedule = raw_input("Update billing schedule? y/[n] ")
            if billing_schedule == 'y':
                billing_schedule_dict = {'1': 'Annual',
                                         '2': 'Two-Pay',
                                         '3': 'Quarterly',
                                         '4': 'Monthly'}
                billing_schedule = raw_input(
                    "Select new billing schedule\n1. Annual\n2. Two-Pay\n3. Quarterly\n4. Monthly\n")
                billing_schedule = billing_schedule_dict.get(billing_schedule)
                db.session.commit()
            print("\n")
            run()

    elif options == "3":
        print("--> you selected policy payment")
        policy_number = raw_input("Policy number ")
        if Policy.query.filter_by(policy_number=policy_number).count() < 1:
            print('%s does not exist\n' % policy_number)
            run()
        else:
            policy_id = Policy.query.filter_by(policy_number=policy_number).one().id
            contact_id = Policy.query.filter_by(policy_number=policy_number).one().agent
            transaction_date = raw_input("Date of payment (yyyymmdd) ")
            transaction_date = is_date(transaction_date)
            amount_paid = raw_input("Amount paid $")
            amount_paid = is_integer(amount_paid)
            p = Payment(policy_id, contact_id, amount_paid, transaction_date)
            db.session.add(p)
            db.session.commit()
            print("\n")
            run()

    elif options == "c":
        print("Run options() to show options\n")
        quit

    elif options == "q":
        print("Bye")
        quit()
    else:
        print("invalid option\n")


################################
# The functions below are for the db and
# shouldn't need to be edited.
################################


def build_or_refresh_db():
    db.drop_all()
    db.create_all()
    insert_data()
    print "DB Ready!"


def insert_data():
    # Contacts
    contacts = []
    john_doe_agent = Contact('John Doe', 'Agent')
    contacts.append(john_doe_agent)
    john_doe_insured = Contact('John Doe', 'Named Insured')
    contacts.append(john_doe_insured)
    bob_smith = Contact('Bob Smith', 'Agent')
    contacts.append(bob_smith)
    anna_white = Contact('Anna White', 'Named Insured')
    contacts.append(anna_white)
    joe_lee = Contact('Joe Lee', 'Agent')
    contacts.append(joe_lee)
    ryan_bucket = Contact('Ryan Bucket', 'Named Insured')
    contacts.append(ryan_bucket)

    for contact in contacts:
        db.session.add(contact)
    db.session.commit()

    policies = []
    p1 = Policy('Policy One', date(2015, 1, 1), 365)
    p1.billing_schedule = 'Annual'
    p1.agent = bob_smith.id
    policies.append(p1)

    p2 = Policy('Policy Two', date(2015, 2, 1), 1600)
    p2.billing_schedule = 'Quarterly'
    p2.named_insured = anna_white.id
    p2.agent = joe_lee.id
    policies.append(p2)

    p3 = Policy('Policy Three', date(2015, 1, 1), 1200)
    p3.billing_schedule = 'Monthly'
    p3.named_insured = ryan_bucket.id
    p3.agent = john_doe_agent.id
    policies.append(p3)

    for policy in policies:
        db.session.add(policy)
    db.session.commit()

    for policy in policies:
        PolicyAccounting(policy.id)

    payment_for_p2 = Payment(p2.id, anna_white.id, 400, date(2015, 2, 1))
    db.session.add(payment_for_p2)
    db.session.commit()

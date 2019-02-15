#!/usr/bin/env python
from accounting import *
from accounting.models import *
from accounting.utils import *
from flask import *
import dateutil.parser as dparser
from sqlalchemy import update

try:
    from IPython import embed
    embed()
except ImportError:
    import os
    import readline
    from pprint import pprint
    os.environ['PYTHONINSPECT'] = 'True'


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

        billing_dict = {'1': 'Annual', '2': 'Two_pay', '3': 'Quarterly', '4': 'Monthly'}
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
                name=name_insured, role='Named Insured').one().id
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
                status = raw_input("Select new status\n1. Active\n2. Cancelled\n3. Expired\n")
                if status == '1':
                    p.status = 'Active'
                if status == '2':
                    p.status = 'Cancelled'
                if status == '3':
                    p.status = 'Expired'
                db.session.commit()
            billing_schedule = raw_input("Update billing schedule? y/[n] ")
            if billing_schedule == 'y':
                billing_schedule = raw_input(
                    "Select new billing schedule\n1. Annual\n2. Two-Pay\n3. Quarterly\n4. Monthly\n")
                if billing_schedule == '1':
                    p.billing_schedule = 'Annual'
                if billing_schedule == '2':
                    p.billing_schedule = 'Two-Pay'
                if billing_schedule == '3':
                    p.billing_schedule = 'Quarterly'
                if billing_schedule == '4':
                    p.billing_schedule = 'Monthly'
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

    elif options == "q":
        print("Bye")
        quit()
    else:
        print("invalid option\n")


###
# EXECUTE OPTIONS AT SHELL START
###
run()

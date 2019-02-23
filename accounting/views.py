# app/routes.py

from flask import render_template, flash, redirect, url_for, request
from accounting import app
from accounting.forms import PolicyForm, AgentForm, EditPolicy
from accounting.models import Policy, Contact
from accounting.ui_scripts import AgentInfo, PolicyInfo


# Routing for the server
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')


@app.route('/about_to_cancel')
def about_to_cancel():
    return render_template('about_to_cancel.html', title='About to Cancel')


@app.route('/recently_paid')
def recently_paid():
    return render_template('recently_paid.html', title='Recently paid')


@app.route('/consult_by_policy', methods=['GET', 'POST'])
def consult_by_policy():
    form = PolicyForm(request.form)
    policy_item = request.form.get('policy_item')
    if request.method == 'POST' and form.validate():
        if Policy.query.filter_by(policy_number=policy_item).first():
            flash('Policy found', 'success')
            return redirect(url_for('results_policy', policy_item=policy_item))
        else:
            flash('Policy not found', 'danger')
            return redirect(url_for('consult_by_policy'))
    return render_template('consult_by_policy.html', title='Consult a Policy',
                           form=form)


@app.route('/consult_by_agent', methods=['GET', 'POST'])
def consult_by_agent():
    form = AgentForm(request.form)
    agent = request.form.get('agent')
    if request.method == 'POST' and form.validate():
        if Contact.query.filter_by(name=agent,
                                   role='Agent').first():
            flash('Agent found', 'success')
            return redirect(url_for('results_agent', agent=agent))
        else:
            flash('Agent not found', 'danger')
            return redirect(url_for('consult_by_agent'))
    return render_template('consult_by_agent.html',
                           title='Consult with Agent Name',
                           form=form)


@app.route('/results_agent', methods=['GET', 'POST'])
def results_agent():
    form = EditPolicy(request.form)
    agent = request.args.get('agent')
    agent_policies = AgentInfo(agent).agent_policies()
    policies = [PolicyInfo(x).policy_dict_info() for x in agent_policies]
    if request.method == 'POST' and form.validate():
        return redirect(url_for('edit_policy'))
    return render_template('results_agent.html',
                           title='Results for Agent',
                           form=form,
                           policies=policies)


@app.route('/results_policy', methods=['GET', 'POST'])
def results_policy():
    form = EditPolicy(request.form)
    policy_item = request.args.get('policy_item')
    policy = PolicyInfo(policy_item).policy_dict_info()
    if request.method == 'POST' and form.validate():
        return redirect(url_for('edit_policy'))
    return render_template('results_policy.html',
                           title='Results for Policy',
                           form=form,
                           policy=policy)


@app.route('/create_policy')
def create_policy():
    return render_template('create_policy.html', title='Create new Policy')


@app.route('/make_payment')
def make_payment():
    return render_template('make_payment.html', title='Make a Payment')


@app.route('/edit_policy')
def edit_policy():
    return render_template('edit_policy.html', title='Edit an existing Policy')

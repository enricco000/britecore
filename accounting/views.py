# app/routes.py

from flask import render_template, flash, redirect, url_for, request
from accounting import app
from accounting.forms import PolicyForm, AgentForm
from accounting.models import Policy, Contact


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
    if request.method == 'POST' and form.validate():
        print(request.form.get('policy_item'))
        if Policy.query.filter_by(policy_number=request.form.get('policy_item')).count() > 0:
            flash('Policy found', 'success')
            return redirect(url_for('home'))
        else:
            flash('Policy does not exist', 'danger')
            return redirect(url_for('consult_by_policy'))
    return render_template('consult_by_policy.html', title='Consult a Policy', form=form)


@app.route('/consult_by_agent', methods=['GET', 'POST'])
def consult_by_agent():
    form = AgentForm(request.form)
    if request.method == 'POST' and form.validate():
        print(request.form.get('agent'))
        if Contact.query.filter_by(name=request.form.get('agent'),
                                   role='Agent').count() > 0:
            flash('Agent found', 'success')
            return redirect(url_for('home'))
        else:
            flash('Agent not found', 'danger')
            return redirect(url_for('consult_by_agent'))
    return render_template('consult_by_agent.html', title='Consult with Agent Name', form=form)
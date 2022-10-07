from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import boto3
import datetime
from datetime import date
import lumigo_opentelemetry

if 'aws_access_key_id' and 'aws_secret_access_key' and 'region_name' and 'sendQueueUrl' in os.environ:
    
    print('env dected and being set')

    # Set env vars, These need to come from an AWS IAM with access to a SQS 
    aws_access_key_id = os.environ['aws_access_key_id']
    aws_secret_access_key = os.environ['aws_secret_access_key']
    region_name = os.environ['region_name']
    sendQueueUrl = os.environ['sendQueueUrl']
else: 
    print('env vars need to be set before the meow command can be used')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(1000), nullable=False)
    complete = db.Column(db.Boolean) 
    cat = db.Column(db.Integer)
    meow = db.Column(db.Integer)

@app.route('/')
def index():

    todoList = Todo.query.all()
    return render_template('base.html', todo_list=todoList)


# add a task
@app.route('/add', methods=["POST"])
def add():
    
    # get the title of the task
    title = request.form.get("title")

    # if the title is empty then redirect to the index page
    if title == "":
        return redirect(url_for("index"))
    # create a todo object
    newTask = Todo(task=title, complete=False, cat=0, meow=0)
    
    # try to add the object to the database
    try:
        db.session.add(newTask)
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "There was an issue adding your task."


# delete a task
@app.route('/delete/<int:todo_id>')
def delete(todo_id):

    # get the task from the data base
    task = Todo.query.filter_by(id=todo_id).first()
    
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "There was an issue deleting your task."

# update a task
@app.route('/update/<int:todo_id>')
def update(todo_id):

    # get the task from the data base
    task = Todo.query.filter_by(id=todo_id).first()
    # toggle the complete value
    task.complete = not task.complete

    # try to commit to the database
    try:
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "There was an issue deleting your task."

@app.route('/cat/<int:todo_id>')
def updatecat(todo_id):
    # get the task from the data base
    task = Todo.query.filter_by(id=todo_id).first()

    # cat + cat = moar cats
    task.cat = task.cat + 1 

    # cycle the http statusi
    httpstat = task.cat + 399

    # try to commit to the database
    try:
        db.session.commit()
        return redirect(url_for("index")), httpstat
    except:
        return "There was an issue deleting your task."

@app.route('/meow/<int:todo_id>')
def updatemeow(todo_id):

    # get the task from the data base
    task = Todo.query.filter_by(id=todo_id).first()

    # meow + meow = lots of noise and moar meows
    task.meow = task.meow + 1

    # prep message meow for sqs 
    output = "meow" + str(task.meow)

    # check to make sure env vars are set for SQS
    if 'aws_access_key_id' in os.environ:

        sqs_send= boto3.client('sqs',  
            aws_access_key_id=aws_access_key_id, 
            aws_secret_access_key=aws_secret_access_key, 
            region_name=region_name)

        ret = sqs_send.send_message( 
            QueueUrl=sendQueueUrl, MessageBody=output, MessageGroupId="demo", MessageDeduplicationId=output)


    # try to commit to the database
    try:
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "There was an issue deleting your task."

if __name__ == "__main__":
    
    db.create_all()
    port = int(os.environ.get('PORT', 8080))

    app.run(host = '0.0.0.0', port = port, debug=True)










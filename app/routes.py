from flask import request, render_template
from . import app, db 
from .models import User, Task
from all_tasks.tasks import tasks_list


# ...............................

# Home Endpoint
@app.route('/')
def index():
    return render_template('index.html')
# ...............................

# User Endpots
# Create New User
@app.route('/users', methods=['POST'])
def create_user():
    # Check to make sure requeset body is JSON
    if not request.is_json:
        return {'error':'Your content-type must be application/json'}, 400
    # Get data from req body
    data = request.json
    # Valudate that the data has all required fields
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Pull individual data from the body
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check to see if any current users already have that username and/or email
    check_users = db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    if check_users:
            return {'error':'A user with that username and/or email already exists'}, 400
        
    # As long as the email/usernames are unique, we can create the user
    new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, username=username)
    
    return new_user.to_dict(), 201
# ................................

# Task Endpoints
# Get All Tasks 
@app.route('/tasks')
def get_all_tasks():
    return tasks_list


# Get Task by Specific ID 
@app.route('/tasks/<int:task_id>')
def get_task_by_id(task_id):
    # Get the tasks from where they are stored (in tasks_list)
    tasks = tasks_list
    # For each dict in the list, if the key of 'id' matches the task_id from the URL, return that task
    for task in tasks:
        if task['id'] == task_id:
            return task
    return {'error': f'A task with the ID of {task_id} does not exist'}, 404 

#Create new task
@app.route('/tasks', methods=['POST'])
def create_task():
    # Check if the request object body is JSON
    if not request.is_json:
        return {'error': 'your content-type must be application/json'}, 400
    # Get data from request body (once we know it is json)
    data = request.json 
    # Want to set it up where each task must have a title & body 
    # Valide the incoming data - first write out required fields, and check against it
    required_fields = ['title', 'description', 'dueDate']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    # the code block above is ensuring title, desc, and duedate are all in the post req body, in json format. From there, we can GET that data and add it to our dict

    # Get data values
    title = data.get('title')
    description = data.get('description')
    dueDate = data.get('dueDate')

    # Create new task  
    new_task = Task(title=title, description=description, dueDate=dueDate)

    return new_task.to_dict(), 201
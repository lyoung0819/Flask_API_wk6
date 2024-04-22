from flask import request, render_template
from . import app, db 
from .models import User, Task
from .auth import basic_auth, token_auth

# ...............................

# HOME ENDPOINT
@app.route('/')
def index():
    return render_template('index.html')
# ...............................

# USER ENDPOINTS
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


# Delete User Endpoint
@app.route('/users/<int:user_id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(user_id):
    #check if the user exists 
    user = db.session.get(User, user_id)
    if user is None:
        return {'error': 'This user does not exist'}, 404
    
    # make sure user trying to delete is the user whom created it 
    current_user = token_auth.current_user()
    if user is not current_user: # DOUBLE CHECK TO ENSURE WORKS CORRECTLY
        return {'error':'You do not have permission to delete this user'}, 403 
    
    # delete task, calling delete method 
    user.delete()
    return {'success':f"User '{user.first_name}' was deleted successfully"}, 200

@app.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()


@app.route('/users/me')
@token_auth.login_required
def get_me():
    user = token_auth.current_user()
    return user.to_dict()

# ................................

# TASK ENDPOINTS
# Get All Tasks 
@app.route('/tasks')
def get_all_tasks():
    select_stmt = db.select(Task)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(Task.title.ilike(f"%{search}%"))
    # Get all tasks from the database
    tasks =  db.session.execute(db.select(Task)).scalars().all()
    return [t.to_dict() for t in tasks]


# Get Task by Specific ID 
@app.route('/tasks/<int:task_id>')
def get_task_by_id(task_id):
    # Get the tasks from where they are stored in DB
    task = db.session.get(Task, task_id)
    # For each dict in the list, if the key of 'id' matches the task_id from the URL, return that task
    if task:
        return task.to_dict()
    return {'error': f'A task with the ID of {task_id} does not exist'}, 404 

#Create new task
@app.route('/tasks', methods=['POST'])
@token_auth.login_required
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

    current_user = token_auth.current_user() # will return User instance, and can then grab id attribute 

    # Create new task WITHIN database (via Task model)
    new_task = Task(title=title, description=description, dueDate=dueDate, user_id=current_user.id)

    return new_task.to_dict(), 201


# Update Tasks Endpoint
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_auth.login_required
def edit_task(task_id):
    # Check to see that they have a json body
    if not request.is_json:
        return {'error':'Your content-type must be application/json'}, 400
    # find task by ID in database
    task = db.session.get(Task, task_id)
    if task is None:
        return {'error':'Task with an ID of #{task_id} does not exist'}, 404
    # Get current user based on token
    curren_user = token_auth.current_user()
    #check if current user is author of task
    if curren_user is not task.author:
        return {'error':"This is not your task. You do not have permission to edit"}, 403
    
    # Get data from Request:
    data = request.json
    # Pass that data into the task's update method
    task.update(**data)
    return task.to_dict() 

# Delete Task Endpoint
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_auth.login_required
def delete_task(task_id):
    #check if the task exists 
    task = db.session.get(Task, task_id)
    if task is None:
        return {'error': 'This task does not exist'}, 404
    
    # make sure user trying to delete is the user whom create it 
    current_user = token_auth.current_user()
    if task.author is not current_user:
        return {'error':'You do not have permission to delete this task'}, 403 
    
    # delete task, calling delete method 
    task.delete()
    return {'success':f'{task.title} was deleted successfully'}, 200
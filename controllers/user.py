import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)


def register():

    # Window Title
    response.title = 'Register'

    # Allow registered users to create accounts in debug mode for quicker testing
    if auth.is_logged_in():
        redirect(URL(c='user',f='profile'))

    form = SQLFORM.factory(db.auth_user, formstyle="divs")

    # Placeholder Values
    form.custom.widget.first_name["_placeholder"] = "Enter First Name"
    form.custom.widget.last_name["_placeholder"] = "Enter Last Name"
    form.custom.widget.email["_placeholder"] = "Enter Email"
    form.custom.widget.username["_placeholder"] = "Enter Unique Username"
    form.custom.widget.password["_placeholder"] = "Enter Password"

    if form.validate():
        userid = auth.get_or_create_user(form.vars)
    elif form.errors:
        response.flash = 'One or more of your form fields has an error. Please see below for more information'

    return dict(form = form)

def validate_register_form(form):

    empty_validator = IS_NOT_EMPTY(error_message=T("must not be empty"))

    if empty_validator(request.vars.first_name)[1] is not None:
        form.errors.first_name = "First Name " + empty_validator(request.vars.first_name)[1]

    if empty_validator(request.vars.last_name)[1] is not None:
        form.errors.last_name = "Last Name " + empty_validator(request.vars.last_name)[1]

    email_validator = IS_EMAIL(error_message="Email is not in correct format")

    if empty_validator(request.vars.email)[1] is not None:
        form.errors.email = "Email " + empty_validator(request.vars.email)[1]
    else:
        if email_validator(request.vars.email)[1] is not None:
            form.errors.email = email_validator(request.vars.email)[1]

    username_validator = IS_NOT_IN_DB(db, 'auth_user.username', error_message="Username has already been taken")

    if empty_validator(request.vars.username)[1] is not None:
        form.errors.username = "Username " + empty_validator(request.vars.username)[1]
    else:
        if username_validator(request.vars.username)[1] is not None:
            form.errors.username = username_validator(request.vars.username)[1]


    if empty_validator(request.vars.password)[1] is not None:
        form.errors.password = "Password " + empty_validator(request.vars.password)[1]





def login():
    # Window Title
    response.title = 'Login'

    # auth.settings.login_userfield = 'username'
    # if request.vars.username and not IS_EMAIL()(request.vars.username)[1]:
    # 	# If this doesnt work, check if its an email.
    # 	auth.settings.login_userfield = 'email'
    # 	request.vars.email = request.vars.username
    # 	request.post_vars.email = request.vars.email
    # 	request.vars.username = None
    # 	request.post_vars.username = None
    #
    # form = auth.login()
    #
    # # Define placeholder values
    # form.custom.widget.username["_placeholder"] = "Username or Email"
    # form.custom.widget.password["_placeholder"] = "Password"

    form = FORM(LEGEND('Login'),
                INPUT(_type='text', _name='username', _class = 'input-block-level', _placeholder='username',
                      requires=IS_NOT_EMPTY( error_message=T("Please enter a username"))),
                INPUT(_type='password',_name='password', _class = 'input-block-level', _placeholder='password',
                      requires=IS_NOT_EMPTY(error_message=T("Please enter a password"))),
                INPUT(_type='submit', _class='btn btn-primary', _value='Login'),
                A('Register',_href=URL('register'), _role='button', _class='btn btn-info'))

    if form.process().accepted:
        # Log user in
        user = auth.login_bare(request.vars.username, request.vars.password)
        if(user is False):
            # If username and password combination is not found in database, return this message
            response.flash = DIV("Invalid Username/Password Combination", _class='alert alert-error')
        else:
            db((db.project.author_id == auth._get_user_id()) &(db.project.status == "Being Created")).delete()
            # Checks whether user was sent to login form when trying to pledge. If true, the user is redirected back
            # to the pledge they was trying to make.
            if request.vars.controller_after_login and request.vars.page_after_login:
                redirect(URL(request.vars.controller_after_login, request.vars.page_after_login))
            else:
                # Redirect them to their profile page.
                redirect(URL('default','index'))
    elif form.errors:
        response.flash = DIV("Username or Password field is empty", _class='alert alert-error')

    return dict(form=form)

def profile():
    user_id = auth._get_user_id
    response.title = auth.user.username

    # Alerts
    # Number of Closed Projects that belong to user
    closed_projects = database.get_closed_projects_by_user(user_id)
    if closed_projects is None:
        no_of_closed_projects = 0
    else:
        no_of_closed_projects = len(closed_projects)

    # Number of transcriptions user has made awaiting approval
    no_of_transcriptions_awaiting_approval = 0
    for closed_project in closed_projects:
        documents = database.get_documents_for_a_project_that_have_transcription(closed_project)
        for document in documents:
            transcriptions = database.get_transcriptions_for_document(document)
            for i in transcriptions:
                no_of_transcriptions_awaiting_approval += 1

    response.closed_project_alert = 'You have', no_of_closed_projects, 'projects that are currently closed for review.'
    response.transcriptions_alert = 'You have', no_of_transcriptions_awaiting_approval, 'transcriptions awaiting approval.'
    return dict()

def transactions_made():
    # Controller for transactions made by user



    return dict()

def manage_projects():
    user_id = auth._get_user_id

    # Open Projects
    open_projects = database.get_open_projects_by_user(user_id)

    # Closed Projects
    closed_projects = database.get_closed_projects_by_user(user_id)

    return dict(open_projects=open_projects, closed_projects=closed_projects)

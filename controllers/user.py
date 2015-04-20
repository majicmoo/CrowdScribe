import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)
import search_functions as search_functions
import general_functions as general_functions
general_module = general_functions.GeneralFunctions(database, db)

def register():
    # Controller which allows a user to register on Crowdscribe
    # Window Title
    response.title = 'CrowdScribe | Register'

    # Allow registered users to create accounts in debug mode for quicker testing
    if auth.is_logged_in():
        redirect(URL(c='user',f='profile'))

    # Register form
    form = SQLFORM(db.auth_user, formstyle="divs")
    form.custom.widget.username["_placeholder"] = "Enter Unique Username"
    form.custom.widget.password["_placeholder"] = "Enter Password"

    # Validate register form
    if form.validate(formname="form_one", onvalidation=validate_register_form):
        userid = auth.get_or_create_user(form.vars)
        auth.login_bare(request.vars.username, request.vars.password)
        redirect(URL('user','profile'))

    elif form.errors:
        validate_register_form(form)
        response.flash = 'One or more of your form fields has an error. Please see below for more information'

    return dict(form = form)

def validate_register_form(form):
    # Validate register form based on conditions below
    # Validates if field is empty
    empty_validator = IS_NOT_EMPTY(error_message=T("must not be empty"))

    # Validates if password is the same as confirm password
    confirm_password_validator = IS_EQUAL_TO(request.vars.password, error_message="Password is not the same as confirm password")

    # Validates if username already exists
    username_validator = IS_NOT_IN_DB(db, 'auth_user.username', error_message="Username has already been taken")

    # Call validators
    if empty_validator(request.vars.username)[1] is not None:
        form.errors.username = "Username " + empty_validator(request.vars.username)[1]
    else:
        if username_validator(request.vars.username)[1] is not None:
            form.errors.username = username_validator(request.vars.username)[1]

    if empty_validator(request.vars.password)[1] is not None:
        form.errors.password = "Password " + empty_validator(request.vars.password)[1]

    if confirm_password_validator(request.vars.confirm_password)[1] is not None:
        form.errors.password = confirm_password_validator(request.vars.confirm_password)[1]


def login():
    # Controller for logging in an already registered user.
    # Window Title
    response.title = 'CrowdScribe | Login'

    if request.vars.page_after_login == 'create_step1' :
        # response.messagecolour = "#F7EC4F"
        response.message = 'Please login or register before creating a project.'

    # Redirects based on request arguments
    if request.vars.controller_after_login and request.vars.page_after_login and request.vars.args_after_login:
        request.vars.args_after_login = request.vars.args_after_login.split('-')
        auth.settings.login_next = URL(request.vars.controller_after_login, request.vars.page_after_login,
                                       args=request.vars.args_after_login)
    elif request.vars.controller_after_login and request.vars.page_after_login:
        auth.settings.login_next = URL(request.vars.controller_after_login, request.vars.page_after_login)
    else:
        auth.settings.login_next = URL('default', 'index')

    # Login form
    form = auth.login(onaccept=remove_projects_being_created)
    form.custom.widget.username["_placeholder"] = "Username"
    form.custom.widget.password["_placeholder"] = "Password"

    return dict(form=form, after_login_controller = request.vars.page_after_login)

def remove_projects_being_created(form):
    # Function to remove any projects that were previously being by user when re-logging in
    if auth._get_user_id():
        db((db.project.author_id == auth._get_user_id()) &(db.project.status == "Being Created")).delete()

@auth.requires_login(otherwise=URL('user', 'login'))
def profile():
    # Controller for user profile
    # Current users ID
    user_id = auth._get_user_id()
    if user_id is None:
        redirect(URL('default','index'))
    # Current user
    user = database.get_user(user_id)
    response.title = 'CrowdScribe | ' + user.username

    # Alerts
    # Number of Closed Projects that belong to user
    closed_projects = database.get_closed_projects_for_user(user_id)
    no_of_closed_projects = len(closed_projects)

    under_review_projects = database.get_under_review_projects_for_user(user_id)
    no_of_under_review_projects = len(under_review_projects)

    open_projects_with_transcriptions = database.get_open_projects_with_transcriptions_for_user(user_id)

    # Number of transcriptions user has made awaiting approval
    no_of_transcriptions_awaiting_approval = 0
    for closed_project in open_projects_with_transcriptions:
        documents = database.get_documents_with_transcription_for_project(closed_project)
        for document in documents:
            transcriptions = database.get_transcriptions_for_document(document)
            for i in transcriptions:
                no_of_transcriptions_awaiting_approval += 1

    num_user_projects = len(database.get_projects_not_being_created_for_user(user_id))

    manager_strings = [str(no_of_under_review_projects)+' are currently under review.', str(no_of_transcriptions_awaiting_approval)+' transcriptions awaiting review across '+str(len(open_projects_with_transcriptions))+' projects.', str(no_of_closed_projects)+' have had transcriptions accepted for all their documents.']
    num_projects_string = 'Click here to manage your '+str(num_user_projects)+' projects.'

    # Transcription Viewer

    pending_transcriptions = database.get_pending_transcriptions_for_user(user_id)
    accepted_transcriptions = database.get_accepted_transcriptions_for_user(user_id)
    rejected_transcriptions = database.get_rejected_transcriptions_for_user(user_id)
    num_transcriptions = len(pending_transcriptions) + len(accepted_transcriptions) + len(rejected_transcriptions)

    transcription_strings = [str(len(pending_transcriptions))+' are pending review.', str(len(accepted_transcriptions))+' have been accepted.', str(len(rejected_transcriptions))+' have been rejected.']
    num_transcription_string = 'Click here to view your '+str(num_transcriptions)+' transcriptions.'

    return dict(manager_strings = manager_strings, num_projects_string = num_projects_string, transcription_strings = transcription_strings, num_transcription_string = num_transcription_string)

@auth.requires_login(otherwise=URL('user', 'login'))
def view_own_transcriptions():
    # Controller for transactions made by user
    user_id = auth._get_user_id()
    pending_transcriptions = database.get_pending_transcriptions_for_user(user_id)
    accepted_transcriptions = database.get_accepted_transcriptions_for_user(user_id)
    rejected_transcriptions = database.get_rejected_transcriptions_for_user(user_id)

    return dict(pending_transcriptions=pending_transcriptions, accepted_transcriptions=accepted_transcriptions,
                rejected_transcriptions=rejected_transcriptions)

@auth.requires_login(otherwise=URL('user', 'login'))
def view_transcription():
    # Controller to view a transcription made by the current user
    transcription_id = request.args(0)
    transcription = database.get_transcription(transcription_id)
    transcribed_fields = database.get_transcribed_fields_for_transcription(transcription_id)
    document_for_transcription = database.get_document_for_transcription(transcription_id)
    project_for_transcription = database.get_project(document_for_transcription.project_id)
    return dict(transcription=transcription, transcribed_fields=transcribed_fields,
                document_for_transcription = document_for_transcription,
                project_for_transcription = project_for_transcription)

@auth.requires_login(otherwise=URL('user', 'login'))
def manage_projects():
    # Controller to manage currently owned projects
    user_id = auth._get_user_id()
    # Under Review Projects
    under_review_projects = database.get_under_review_projects_for_user(user_id)
    # Page title
    response.title = 'CrowdScribe | Manage Projects'

    # Have Transcriptions and open Projects
    open_projects_with_transcriptions = database.get_open_projects_with_transcriptions_for_user(user_id)
    open_projects_with_transcriptions = general_module.attach_header_image_to_projects(open_projects_with_transcriptions)

    # No Transcriptions and open Projects
    open_projects_without_transcriptions = database.get_open_projects_without_transcriptions_for_user(user_id)

    # All documents transcribed - closed
    closed_projects = database.get_closed_projects_for_user(user_id)

    return dict(under_review_projects=general_module.attach_all_information_to_projects(under_review_projects),
                open_projects_with_transcriptions=general_module.attach_all_information_to_projects(open_projects_with_transcriptions),
                open_projects_without_transcriptions=general_module.attach_all_information_to_projects(open_projects_without_transcriptions),
                closed_projects=general_module.attach_all_information_to_projects(closed_projects))


def place_project_under_review():
    # Controller for button to place a project under review
    db((db.project.id==request.vars.project_id)).update(status="Under Review")
    db.commit()
    redirect(URL('user','manage_projects'), client_side=True)

def reopen_project_for_transcriptions():
    # Controller for button to reopen a project for transcriptions
    db((db.project.id==request.vars.project_id)).update(status="Open")
    db.commit()
    redirect(URL('user','manage_projects'), client_side=True)

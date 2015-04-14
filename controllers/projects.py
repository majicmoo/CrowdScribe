import database_transactions as database_transactions
import projects_functions as projects_functions
import general_functions as general_functions
database = database_transactions.DatabaseTransactions(db)
projects_module = projects_functions.ProjectFunctions(database, db)
general_module = general_functions.GeneralFunctions(database, db)


@auth.requires_login(otherwise=URL('user', 'login',
                     vars=dict(controller_after_login='projects', page_after_login='create_step1')))
def create_step1():

    # Set Page Title
    response.title = "Create - Step 1"

    # Set response flash display to error
    session.flash_class = "alert-error"

    # Retrieve project and set session project variable to allow for prepopulating.
    project_id, project_being_edited = projects_module.check_if_come_back_from_future_step(session)

    # Calls function that checks whether steps in the creation process should be navigatable to.
    step_available = projects_module.check_if_steps_available(project_id)

    # Create step 1 form is initialised
    form = SQLFORM(db.project, submit_button="Continue to Step 2")

    # This form will allow for the create wizard to be reset
    clear_project = projects_module.create_clear_project_form()

    # Data needed to prepopulate form is retrieved
    prepopulation_data = projects_module.retrieve_prepopulated_data_for_create_step_1(project_being_edited)

    # Initialise select box for tag
    form.vars.tag = "Sport"

    # Prepopulate form
    if prepopulation_data is not None:

        form.vars.name = prepopulation_data['name']
        form.vars.description = prepopulation_data['description']
        form.vars.tag = prepopulation_data['tag']
        form.vars.time_period_start_date = prepopulation_data['start_date']
        form.vars.time_period_end_date = prepopulation_data['end_date']

    # Process form without communicating with the database
    if form.validate(formname="form_one", onvalidation=projects_module.validate_create_step1):

        # If unknown select box was selected then make start_date and end_date none, otherwise make them correct format
        start_date, end_date = projects_module.process_start_and_end_dates()

        # If project record has already been created, just update
        if project_id and project_being_edited:
            project_being_edited.update_record(name=request.vars.name, description=request.vars.description,
                                               tag=request.vars.tag, time_period_start_date=start_date,
                                               time_period_end_date=end_date)
        else:
            # Otherwise insert new project record
            project_id = db.project.insert(name=request.vars.name, author_id=auth._get_user_id(),
                                           status="Being Created", description=request.vars.description,
                                           tag=request.vars.tag, time_period_start_date=start_date,
                                           time_period_end_date=end_date, date_created=request.now)

        session.project_being_created = project_id
        redirect(URL('projects', 'create_step2'))
    elif form.errors:
        projects_module.validate_create_step1(form)

    if clear_project.validate(formname="form_two"):
        # If clear project button is pressed, reset project wizard
        session.project_being_created = None
        redirect(URL('projects', 'create_step1'))

    return dict(form=form, clear_project=clear_project, project_being_edited=project_being_edited,
                pd=prepopulation_data, step_available=step_available)


@auth.requires_login(otherwise=URL('user', 'login',
                     vars=dict(controller_after_login='projects', page_after_login='create_step1')))
def create_step2():

    # Set Page Title
    response.title = "Create - Step 2"

    # Retrieve project and set session project variable to allow for prepopulating.
    project_id, project_being_edited = projects_module.check_if_step1_was_skipped_and_redirect_if_so(session)

    # Calls function that checks whether steps in the creation process should be navigatable to.
    step_available = projects_module.check_if_steps_available(project_id)

    # This form will allow for the create wizard to be reset
    clear_project = projects_module.create_clear_project_form()

    # This form allows documents to be added
    add_image_form = SQLFORM(db.document_image, submit_button="Add Document")

    # This form allows for the wizard to go back to step 1
    go_to_step_1_form = projects_module.create_previous_step_form("Go Back to Step 1")
    # This form allows for the wizard to progress to step 3
    go_to_step_3_form = projects_module.create_next_step_form("Continue to Step 3")


    # Process add image form
    if add_image_form.validate(formname="form_one", onvalidation=projects_module.validate_add_image_form):
        db.document_image.insert(description=request.vars.description, status="Open", project_id=project_id,
                                 image=add_image_form.vars.image)
        session.project_being_created = project_id
        session.flash_class = "alert-success"
        response.flash = "Succesfully Added Document!"
    elif add_image_form.errors:
        projects_module.validate_add_image_form(add_image_form)

    # Process form allowing you to move to step 3
    if go_to_step_3_form.process(formname="form_two").accepted:
        documents_added = database.get_documents_for_project(project_id)
        if len(documents_added) < 1:
            response.flash = DIV("At least one image must be added", _class="alert alert-error")
        else:
            session.project_being_created = project_id
            redirect(URL('projects', 'create_step3'))

    # Process form allowing you to move to step 1
    if go_to_step_1_form.process(formname="form_three").accepted:
            session.project_being_created = project_id
            redirect(URL('projects', 'create_step1'))

    # If clear project button is pressed, reset project wizard
    if clear_project.validate(formname="form_four"):
        session.project_being_created = None
        redirect(URL('projects', 'create_step1'))

    # Retrieve documents that project already has.
    documents_added = database.get_documents_for_project(project_id)


    return dict(add_image_form=add_image_form, go_to_step_3_form=go_to_step_3_form,
                go_to_step_1_form=go_to_step_1_form, documents_added=documents_added, clear_project=clear_project,
                step_available=step_available, project_name=project_being_edited.name)




@auth.requires_login(otherwise=URL('user', 'login',
                     vars=dict(controller_after_login='projects', page_after_login='create_step1')))
def create_step3():

    # Set Page Title
    response.title = "Create - Step 3"

    # Retrieve project and set session project variable to allow for prepopulating.
    project_id, project_being_edited = projects_module.check_if_step1_was_skipped_and_redirect_if_so(session)

    # Calls function that checks whether steps in the creation process should be navigatable to.
    step_available = projects_module.check_if_steps_available(project_id)

    # Creates form that allows fields to be added
    add_fields_form = SQLFORM.factory(db.data_field, submit_button="Add field")


    # Form that allows you to move back to step 2
    go_to_step_2_form = projects_module.create_previous_step_form("Go Back to Step 2")
    # Form that moves you forward to the review step
    review_project_form = projects_module.create_next_step_form("Review Project")

    # Forms that resets project wizard
    clear_project = projects_module.create_clear_project_form()

    # Process form that allows fields to be added.
    if add_fields_form.process(formname="form_one", onvalidate=projects_module.validate_add_field_form).accepted:
        db.data_field.insert(name=request.vars.name, short_description=request.vars.short_description,
                             project_id=project_id)
        db.commit()
        session.project_being_created = project_id
    elif add_fields_form.errors:
        projects_module.validate_add_field_form(add_fields_form)

    # Move project forward to review when button clicked
    if review_project_form.process(formname="form_two").accepted:
        fields_added = database.get_data_fields_for_project(project_id)
        if len(fields_added) < 1:
            response.flash = DIV("At least one field must be added", _class="alert alert-error")
        else:
            session.project_being_created = project_id
            redirect(URL('projects', 'create_step4'))
    # Go back to step 2 when button clicked
    if go_to_step_2_form.process(formname="form_three").accepted:
        session.project_being_created = project_id
        redirect(URL('projects', 'create_step2'))

    # Reset Project wizard when button clicked.
    if clear_project.validate(formname="form_four"):
        session.project_being_created = None
        redirect(URL('projects', 'create_step1'))

    # Retrieve document and fields added to project
    documents_added = database.get_documents_for_project(project_id)
    fields_added = database.get_data_fields_for_project(project_id)


    return dict(documents_added=documents_added, add_fields_form=add_fields_form, fields_added=fields_added,
                review_project_form=review_project_form, go_to_step_2_form=go_to_step_2_form,
                clear_project=clear_project, step_available=step_available, project_name=project_being_edited.name)




@auth.requires_login(otherwise=URL('user', 'login',
                     vars=dict(controller_after_login='projects', page_after_login='create_step1')))
def create_step4():

    # Page Title
    response.title = "Create - Review"

    project_id, project_being_edited = projects_module.check_if_step1_was_skipped_and_redirect_if_so(session)
    documents_added = database.get_documents_for_project(project_id)

    clear_project = projects_module.create_clear_project_form()
    publish_project_form = projects_module.create_next_step_form("Publish Project")

    if publish_project_form.process(formname="form_one").accepted:
        project = database.get_project(project_id)
        project.update_record(status="Open", date_created=request.now)
        session.project_being_created = None
        redirect(URL('projects', 'project', args=[project.id]))

    if clear_project.validate(formname="form_two"):
        session.project_being_created = None
        redirect(URL('projects', 'create_step1'))

    # Time String
    project = database.get_project(project_id)
    timestring = general_module.construct_project_timestring(project)
    header_image = URL('default', 'download', args=database.get_document_for_project_header(project.id).image)

    open_documents, open_documents_with_transcription, open_documents_without_transcription, done_documents, \
    closed_documents = projects_module.set_up_project_page_based_on_user(project, auth)

    return dict(project=project_being_edited, timestring=timestring, documents_for_project=documents_added,
                publish_project_form=publish_project_form, clear_project=clear_project, header_image=header_image,
                done_documents=done_documents, open_documents_with_transcription=open_documents_with_transcription,
                open_documents_without_transcription=open_documents_without_transcription,
                closed_documents=closed_documents, open_documents=open_documents)


def project():
    project_id = request.args(0)
    project = database.get_project(project_id)

    # If project doesnt exist, redirect
    if project is None:
        redirect(URL('default', 'index'))

    # Initialise Variables
    open_documents, open_documents_with_transcription, open_documents_without_transcription, done_documents, \
    closed_documents = projects_module.set_up_project_page_based_on_user(project, auth)

    # Page Title
    response.title = project.name

    # documents_for_project = database.get_open_documents_for_project(project.id)
    data_fields_for_project = database.get_data_fields_for_project(project.id)

    # Retrieve documents that have already been transcribed by the user in this project. This
    # can be used to alert users to that fact on the page.
    documents_transcribed_by_user =\
        database.get_documents_with_transcription_for_project_and_transcription_author(project_id, auth._get_user_id())
    header_image = URL('default', 'download', args=database.get_document_for_project_header(project.id).image)

    # Time String
    timestring = general_module.construct_project_timestring(project)

    all_documents = [documents_transcribed_by_user, done_documents, open_documents_with_transcription,
                     open_documents_without_transcription, open_documents]

    documents_transcribed_by_user, done_documents, open_documents_with_transcription, \
    open_documents_without_transcription, open_documents = \
        projects_module.attach_number_of_transcriptions_to_lists_of_documents(all_documents)

    project.fraction_transcribed_string = general_module.construct_number_of_transcribed_documents_string(project.id)

    return dict(project=project, timestring=timestring, data_fields_for_project=data_fields_for_project,
                documents_transcribed_by_user=documents_transcribed_by_user, header_image=header_image,
                done_documents=done_documents, open_documents_with_transcription=open_documents_with_transcription,
                open_documents_without_transcription=open_documents_without_transcription,
                closed_documents=closed_documents, open_documents=open_documents)


def view_document():
    # Remove if project data not required in page
    project_id = request.args(0)
    project = database.get_project(project_id)

    # Page Title
    response.title = project.name + ' | Document'

    # Redirect if null project.
    if project is None:
        redirect(URL('default', 'index'))

    # Get Doc from URL args
    document_id = request.args(1)
    document = database.get_document(document_id)
    accepted_transcription_with_fields = accepted_transcription =  None

    # If null doc, go back to the project
    if document is None:
        redirect(URL('projects', 'project', args=[project_id]))
    elif document.status == "Closed":
        accepted_transcription = database.get_accepted_transcription_for_document(document.id)
        accepted_transcription_with_fields = database.get_transcribed_fields_for_transcription(accepted_transcription.id)

    document.number_of_transcriptions = len(database.get_pending_transcriptions_for_document(document.id))

    # The form needs to be built dynamically to include all fields.
    form = None
    fields = []
    # All transcriptions for this doc
    transcriptions = database.get_pending_transcriptions_for_document(document_id)
    # Transcriptions by the current user for this doc
    transcription = None
    response_message = None

    # If you are the owner, you cannot transcribe the document. Gives link to review transcriptions.
    if project.author_id == auth._get_user_id() and not transcriptions:
        response_message = 'You are the owner of this project and cannot transcribe its documents. It currently has' \
                           ' 0 transcriptions available for review.'
        response.message = response_message

    elif project.author_id == auth._get_user_id() and transcriptions:
        msgstring = 'You are the owner of this project and cannot transcribe its documents. Click here to review the ' \
                    + str(len(transcriptions)) + ' transcription' + ('s' if len(transcriptions) > 1 else '') +\
                    ' made.'
        response_message = msgstring
        response.message = A(msgstring, _href=URL('projects', 'review_document', args=[project.id, document.id]))

    elif project.author_id == auth._get_user_id() and accepted_transcription:
        response_message = 'You are the owner of this project and have accepted a transcription for this document. ' \
                           'This document is now closed'
        response.message = response_message

    # Need an account to login
    elif auth._get_user_id() is None:
        response_message = "Please login to transcribe."
        args = str(project_id) + '-' + str(document_id)
        response.message = A(response_message, _href=URL('user', 'login', vars=dict(controller_after_login='projects',
                                                                                    page_after_login='view_document',
                                                                                    args_after_login=args)))

    # If user has already provided a transcription
    elif database.document_has_already_been_transcribed_by_user(document_id, auth._get_user_id()):
        transcription = database.document_transcribed_by_user(document_id, auth._get_user_id())
        response_message = "You have already transcribed this document. Only 1 transcription can be added per user."
        response.message = response_message

    # If doc is no longer accepting transcriptions
    elif document.status == 'Done':
        response_message = "This document has already received the maximum number of transcriptions allowed"
        response.message = response_message

    # Display transcription submission form if document image is open for transcriptions and
    # user is authorised to make a submission (ie registered user, not project creator and has not already made
    # transcription for document image)

    # Create dynamic form according to number of data_fields
    for data_field in database.get_data_fields_for_project(project_id):
        fields += [Field(data_field.name, 'text',
                         comment=T(data_field.short_description), label=T(data_field.name))]

    form = SQLFORM.factory(*fields, formstyle='bootstrap', _class='customer form-horizontal', table_name='customer', buttons=[])

    if form.process().accepted:

        # Checks that at least one field has an entry
        field_entry_exists = False
        for data_field in database.get_data_fields_for_project(project_id):
            print form.vars[data_field.name]
            if form.vars[data_field.name] != '':
                field_entry_exists = True
                break

        if field_entry_exists == True:
            # Check if document currently has 2 transcriptions or more and if so mark document as done before adding
            # new transcription
            if len(database.get_transcriptions_for_document(document_id)) >= 2:
                document.update_record(status="Done")
    
            # Insert new transcription record to insert transcribed fields
            transcription_id = db.transcription.insert(document_id=document_id, author_id=auth._get_user_id(),
                                                       status='Pending', date_created=request.now)
    
            # Inserts each transcribed field in db
            for data_field in database.get_data_fields_for_project(project_id):

                # If no entry for a field, put as None in db to leave out in review_document view 
                field_entry = None
                if form.vars[data_field.name] != '':
                    field_entry = form.vars[data_field.name]

                db.transcribed_field.insert(data_field_id=data_field.id, transcription_id=transcription_id,
                                            information=field_entry)

            session.flash = "Succesful Transcription!"
            session.flash_class = "alert-success"
        else:
            session.flash = "Please fill in at least one field."
            session.flash_class = "alert-error"

        redirect(URL('projects','view_document', args=[project.id, document.id]))

    image = URL('default', 'download', args=document.image)

    # Time String
    timestring = general_module.construct_project_timestring(project)
    project.fraction_transcribed_string = general_module.construct_number_of_transcribed_documents_string(project.id)

    return dict(project=project, document=document, image=image, form=form, transcription=transcription,
                accepted_transcription_with_fields = accepted_transcription_with_fields, response_message = response_message, timestring = timestring)


@auth.requires_login(otherwise=URL('user', 'login'))
def review_document():

    # Current Project
    project_id = request.args(0)
    project = database.get_project(project_id)

    response.title = project.name + ' | Review'

    # Current Document
    document_id = request.args(1)
    document = database.get_document(document_id)

    if project is None:
        # Redirect if project is none
        redirect(URL('default', 'index'))
    if project.status != 'Under Review':
        session.flash = "A project must be 'Closed for Review' before you can assess it's transcriptions. You can close them in your Project Manager."
        redirect(URL('projects', 'project', args=[project_id]))
    # Check Project Belongs to Current User
    if project.author_id != auth._get_user_id():
        redirect(URL('projects', 'project', args=[project_id]))
    # Get current transcriptions for Document
    transcriptions = database.get_pending_transcriptions_for_document(document_id)
    transcriptions = projects_module.build_transcription_list(project, transcriptions)

    return dict(project=project, document=document, transcriptions=transcriptions,
                timestring = general_module.construct_project_timestring(project))


def delete_field():
    db((db.data_field.id == request.vars.field_id)).delete()
    current.db.commit()
    redirect(URL('projects', 'create_step3'), client_side=True)

def delete_document():
    db((db.document_image.id == request.vars.document_id)).delete()
    db.commit()
    redirect(URL('projects', 'create_step2'), client_side=True)


def accept_transcription():
    # Function for button which will accept a given transcription for a given document
    db(db.document_image.id == request.vars.document_id).update(status='Closed')
    db((db.transcription.id != request.vars.transcription_id) &
       (db.transcription.document_id == request.vars.document_id)).update(status="Rejected")
    db(db.transcription.id == request.vars.transcription_id).update(status='Accepted')
    db.commit()

    if len(database.get_open_documents_for_project(request.vars.project_id)) == 0:
        db(db.project.id == request.vars.project_id).update(status="Closed")
        db.commit()

    redirect(URL('projects', 'project', args=request.vars.project_id), client_side=True)


def reject_all_transcriptions():
    # Function for button which will reject all transcriptions for a given document
    db((db.transcription.document_id == request.vars.document_id)).update(status="Rejected")
    db.commit()
    redirect(URL('projects', 'project',args=request.vars.project_id ), client_side=True)


def close_project_for_review():
    # Function for button which will close a project for review
    # FIXME: May need some validation depending on how it is implemented
    db((db.project.id == request.vars.project_id)).update(status="Under Review")
    db.commit()
    redirect(URL('projects', 'project', args=request.vars.project_id), client_side=True)

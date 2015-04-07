import database_transactions as database_transactions
#from projects_functions import *
database = database_transactions.DatabaseTransactions(db)


@auth.requires_login(otherwise=URL('user', 'login',
                     vars= dict(controller_after_login='projects', page_after_login='create_step1')))
def create_step1():

    # Set Page Title
    response.title = "Create - Step 1"

    # Retrieve project and set session project variable to allow for prepopulating.
    project_id = None
    project_being_edited = None
    if session.project_being_created is not None:
        project_id = session.project_being_created
        project_being_edited = database.get_project(project_id)

    # Calls function that checks whether steps in the creation process should be navigatable to.
    step_available = check_if_steps_available(project_id)

    # Create step 1 form is initialised
    form = SQLFORM(db.project, submit_button="Continue to Step 2")

    # This form will allow for the create wizard to be reset
    clear_project = FORM(DIV(BUTTON("Clear Project", _type='submit', _class='btn btn-primary btn-block btn-danger',
                                    _onclick="return confirm('Clearing a project will wipe all of your progress. Continue?');")))

    # Data needed to prepopulate form is retrieved
    prepopulation_data = retrieve_prepopulated_data_for_create_step_1(project_being_edited)

    # Initialise select box for tag
    form.vars.tag = "Sport"

    # Prepopulate form
    if prepopulation_data is not None:

        form.vars.name =  prepopulation_data['name']
        form.vars.description = prepopulation_data['description']
        form.vars.tag = prepopulation_data['tag']
        form.vars.time_period_start_date = prepopulation_data['start_date']
        form.vars.time_period_end_date = prepopulation_data['end_date']

    # Process form without communicating with the database
    if form.validate(formname="form_one", onvalidation=validate_create_step1):

        # If unknown select box was selected then make start_date and end_date none, otherwise make them correct format
        if request.vars.unknown == "yes":
            start_date = None
            end_date = None
        else:
            start_date = convert_date_to_integer(request.vars.time_period_start_date, request.vars.start_era)
            end_date = convert_date_to_integer(request.vars.time_period_end_date, request.vars.end_era)

        # If project record has already been created, just update
        if project_id and project_being_edited:
            project_being_edited.update_record(name=request.vars.name, description=request.vars.description,
                                               tag=request.vars.tag, time_period_start_date=start_date,
                                               time_period_end_date=end_date)
        else:
            #Otherwise insert new project record
            project_id = db.project.insert(name=request.vars.name, author_id=auth._get_user_id(), status="Being Created",
                                           description=request.vars.description, tag=request.vars.tag,
                                           time_period_start_date=start_date, time_period_end_date=end_date)

        session.project_being_created = project_id
        redirect(URL('projects', 'create_step2'))
    else:
        pass

    if clear_project.validate(formname="form_two"):
        #If clear project button is pressed, reset project wizard
        session.project_being_created = None
        redirect(URL('projects', 'create_step1'))


    return dict(form=form, clear_project=clear_project, project_being_edited = project_being_edited,
                pd=prepopulation_data, step_available=step_available)

def check_if_steps_available(project_id):

    step2_available = False
    step3_available = False
    step4_available = False

    if project_id is not None:

        if database.get_project(project_id) is not None:
            step2_available = True

            if database.get_documents_for_project(project_id).first() is not None:
                step3_available = True

                if database.get_data_fields_for_project(project_id).first() is not None:
                    step4_available = True

    result = {}
    result['2'] = step2_available
    result['3'] = step3_available
    result['4'] = step4_available

    return result

def convert_date_to_integer(date, era):
    if era =="BC":
        return -int(date)
    else:
        return int(date)

def convert_integer_to_date_string(date):
    if date < 0:
        return str(abs(date)) + "BC"
    else:
        return str(abs(date)) + "AD"

def retrieve_prepopulated_data_for_create_step_1(project_being_edited):
    if project_being_edited == None:
        return None
    else:
        data = {}
        data['name'] = project_being_edited.name
        data['description'] = project_being_edited.description
        data['tag'] = project_being_edited.tag
        if project_being_edited.time_period_start_date is None:
            data['start_date'] = ""
            data['end_date'] = ""
            data['start_era'] = 'AD'
            data['end_era'] = 'AD'
            data['unknown'] = "checked"
        else:
            data['unknown'] = "not checked"
            data['start_date'] = abs(project_being_edited.time_period_start_date)
            data['end_date'] = abs(project_being_edited.time_period_end_date)
            if project_being_edited.time_period_start_date < 0:
                data['start_era'] = 'BC'
                if project_being_edited.time_period_end_date < 0:
                    data['end_era'] = 'BC'
                else:
                    data['end_era'] = 'AD'
            else:
                data['start_era'] = 'AD'
                data['end_era'] = 'AD'
        return data


def validate_create_step1(form):

    print request.vars

    if (request.vars.name == "") or (request.vars.name == None):
        form.errors.name = "Name must be entered"

    if (request.vars.description == "") or (request.vars.description == None):
        form.errors.description = "Description must be entered"

    if (request.vars.tag == "") or (request.vars.tag == None):
        form.errors.tag = "Tag must be chosen"

    start_date = None
    end_date = None
    date_validator = IS_INT_IN_RANGE(-2015, 2015, error_message ="Date must be whole number between 2015 BC and 2015 AD")

    if request.vars.unknown != "yes":
        if (request.vars.time_period_start_date != "") and (request.vars.time_period_start_date != None):
            if date_validator(request.vars.time_period_start_date)[1] is not None:
                form.errors.time_period_start_date = date_validator(request.vars.time_period_start_date)[1]
            else:
                start_date = convert_date_to_integer(request.vars.time_period_start_date, request.vars.start_era)
        else:
            form.errors.time_period_start_date = "Start Date must not be empty"

        if (request.vars.time_period_end_date != "") and (request.vars.time_period_end_date != None):
            if date_validator(request.vars.time_period_end_date)[1] is not None:
                form.errors.time_period_end_date = date_validator(request.vars.time_period_end_date)[1]
            else:
                end_date = convert_date_to_integer(request.vars.time_period_end_date, request.vars.end_era)

        else:
            form.errors.time_period_end_date = "End Date must not be empty"

        if start_date and end_date:
                if start_date > end_date:
                    form.errors.time_period_end_date = 'The End Date of the time period must be later than the Start Date'

    print form.errors



@auth.requires_login(otherwise=URL('user', 'login',
                     vars= dict(controller_after_login='projects', page_after_login='create_step1')))
def create_step2():

    # Set Page Title
    response.title = "Create - Step 2"

    # Retrieve project and set session project variable to allow for prepopulating.
    project_id = None
    if session.project_being_created is not None:
        project_id = session.project_being_created

    # Calls function that checks whether steps in the creation process should be navigatable to.
    step_available = check_if_steps_available(project_id)

     # This form will allow for the create wizard to be reset
    clear_project = FORM(DIV(BUTTON("Clear Project", _type='submit', _class='btn btn-danger btn-block',
                                    _onclick="return confirm('Clearing a project will wipe all of your progress. Continue?');")))

    # This form allows documents to be added
    add_image_form = SQLFORM(db.document_image, submit_button="Add Document")

    # This form allows for the wizard to progress to step 3
    go_to_step_3_form = FORM(DIV(BUTTON("Continue to Step 3", I(_class='icon-arrow-right icon-white'),
                                        _type='submit', _class='btn btn-primary btn-block btn-large')))
    # This form allows for the wizard to go back to step 1
    go_to_step_1_form = FORM(DIV(BUTTON("Back to Step 1", I(_class='icon-arrow-left icon-white'),
                                        _type='submit', _class='btn btn-primary btn-block btn-large')))

    # Process add image form
    if add_image_form.validate(formname="form_one", onvalidation=validate_add_image_form):
        db.document_image.insert(description=request.vars.description, status="Open", project_id=project_id,
                                 image=add_image_form.vars.image)
        session.project_being_created = project_id

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

    #If clear project button is pressed, reset project wizard
    if clear_project.validate(formname="form_four"):
        session.project_being_created = None
        redirect(URL('projects', 'create_step1'))

    # Retrieve documents that project already has.
    documents_added = database.get_documents_for_project(project_id)

    # Use the project name to clarify to the user that they are still working on their setup
    project = database.get_project(project_id)

    return dict(add_image_form=add_image_form, go_to_step_3_form=go_to_step_3_form,
                go_to_step_1_form=go_to_step_1_form, documents_added=documents_added, clear_project=clear_project,
                step_available=step_available, project_name=project.name)

def delete_document():
    db((db.document_image.id==request.vars.document_id)).delete()
    db.commit()
    redirect(URL('projects','create_step2'), client_side=True)



def validate_add_image_form(form):

    if (request.vars.description == "") or (request.vars.description == None):
        form.errors.description = "Description must not be empty"

    image_validator = IS_NOT_EMPTY(error_message=T("Image must not be left empty"))
    if image_validator(request.vars.image)[1] is not None:
        form.errors.image = image_validator(request.vars.image)[1]


@auth.requires_login(otherwise=URL('user', 'login',
                     vars= dict(controller_after_login='projects', page_after_login='create_step1')))
def create_step3():

    # Set Page Title
    response.title = "Create - Step 3"

    # Retrieve project and set session project variable to allow for prepopulating.
    project_id = None
    if session.project_being_created is not None:
        project_id = session.project_being_created

    # Calls function that checks whether steps in the creation process should be navigatable to.
    step_available = check_if_steps_available(project_id)

    # Creates form that allows fields to be added
    add_fields_form = SQLFORM.factory(db.data_field, submit_button="Add field")

    # Form that moves you forward to the review step
    review_project_form = FORM(DIV(BUTTON("Review Project", I(_class='icon-arrow-right icon-white'),
                                          _type='submit', _class='btn btn-primary btn-block btn-large')))

    # Form that allows you to move back to step 2
    go_to_step_2_form = FORM(DIV(BUTTON("Back to Step 2", I(_class='icon-arrow-left icon-white'),
                                        _type='submit', _class='btn btn-primary btn-block btn-large')))

    # Forms that resets project wizard
    clear_project = FORM(DIV(BUTTON("Clear Project", _type='submit', _class='btn btn-danger btn-block',
                                    _onclick="return confirm('Clearing a project will wipe all of your progress. Continue?');")))

    # Process form that allows fields to be added.
    if add_fields_form.process(formname="form_one", onvalidate = validate_add_field_form).accepted:
        db.data_field.insert(name=request.vars.name, short_description=request.vars.short_description, project_id=project_id)
        db.commit()
        session.project_being_created = project_id

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

    #Retrieve document and fields added to project
    documents_added = database.get_documents_for_project(project_id)
    fields_added = database.get_data_fields_for_project(project_id)

    # Retrieve project
    project = database.get_project(project_id)

    return dict(documents_added=documents_added, add_fields_form=add_fields_form, fields_added=fields_added
                , review_project_form=review_project_form, go_to_step_2_form=go_to_step_2_form,
                clear_project=clear_project, step_available=step_available, project_name=project.name)

def delete_field():
    db((db.data_field.id==request.vars.field_id)).delete()
    db.commit()
    redirect(URL('projects','create_step3'), client_side=True)

def validate_add_field_form(form):

    if (request.vars.name != "") and (request.vars.name != None):
        form.errors.name = "Name must not be empty"

    if (request.vars.short_description != "") and (request.vars.short_description != None):
        form.errors.short_description = "Description must not be empty"


@auth.requires_login(otherwise=URL('user', 'login',
                     vars= dict(controller_after_login='projects', page_after_login='create_step1')))
def create_step4():

    # Page Title
    response.title = "Create - Review"

    project_id = None
    if session.project_being_created is not None:
        project_id = session.project_being_created
    else:
        redirect(URL('projects', 'create_step1'))

    clear_project = FORM(DIV(BUTTON("Clear Project", _type='submit', _class='btn btn-danger btn-block',
                                    _onclick="return confirm('Clearing a project will wipe all of your progress. Continue?');")))

    project_being_edited = database.get_project(project_id)
    documents_added = database.get_documents_for_project(project_id)

    publish_project_form = FORM(DIV(BUTTON("Publish Project", I(_class='icon-arrow-right icon-white'),
                                          _type='submit', _class='btn btn-primary btn-block btn-large')))

    if publish_project_form.process(formname="form_one").accepted:
        project = database.get_project(project_id)
        project.update_record(status="Open")
        session.project_being_created = None
        redirect(URL('projects','project', args=[project.id]))

    if clear_project.validate(formname="form_two"):
        session.project_being_created = None
        redirect(URL('projects', 'create_step1'))

    # Time String
    project = database.get_project(project_id)
    timestring = ''
    if project.time_period_start_date:
         timestring = '('+convert_integer_to_date_string(project.time_period_start_date) + " - " + convert_integer_to_date_string(project.time_period_end_date)+')'

    header_image = URL('default','download',args = database.get_document_for_project_header(project.id).image)

    project_status = project.status
    open_documents_with_transcription = []
    open_documents_without_transcription = []
    closed_documents = []
    open_documents = []

    if project.author_id == auth._get_user_id():
        # Current user owns project
        # List of documents that have transcription - open - less than 3 transcriptions
        open_documents_with_transcription = database.get_open_documents_with_transcription_for_project(project_id)
        open_documents_with_transcription = if_none_convert_to_empty_list(open_documents_with_transcription)
        # List of document that don't have a transcription - open
        open_documents_without_transcription = database.get_open_documents_without_transcription_for_project(project_id)
        open_documents_without_transcription = if_none_convert_to_empty_list(open_documents_without_transcription)
        # List of Complete Document - succesfully transcribed - closed
        closed_documents = database.get_closed_documents_for_project(project_id)
        closed_documents = if_none_convert_to_empty_list(closed_documents)
        # response.message = 'You own this project'
    else:
        # If not owner
        # Project is not open, redirect
        if project_status != 'Open':
            redirect(URL('default', 'index'))
        open_documents = database.get_open_documents_for_project(project_id)
        open_documents = if_none_convert_to_empty_list(open_documents)

    # List of done documents - 3 or more transcriptions
    done_documents = database.get_done_documents_for_project(project_id)
    done_documents = if_none_convert_to_empty_list(done_documents)

    done_documents = database.get_done_documents_for_project(project_id)
    done_documents = if_none_convert_to_empty_list(done_documents)

    return dict(project=project_being_edited, timestring = timestring, documents_for_project=documents_added, publish_project_form = publish_project_form, clear_project = clear_project, header_image=header_image,
    done_documents=done_documents, open_documents_with_transcription=open_documents_with_transcription,
    open_documents_without_transcription=open_documents_without_transcription,
    closed_documents=closed_documents, open_documents=open_documents)




def project():
    project_id = request.args(0)
    project = database.get_project(project_id)

    #If project doesnt exist, redirect
    if project is None:
        redirect(URL('default', 'index'))

    # Initialise Variables
    project_status = project.status
    open_documents_with_transcription = []
    open_documents_without_transcription = []
    closed_documents = []
    open_documents = []

    if project.author_id == auth._get_user_id():
        # Current user owns project
        # List of documents that have transcription - open - less than 3 transcriptions
        open_documents_with_transcription = database.get_open_documents_with_transcription_for_project(project_id)
        open_documents_with_transcription = if_none_convert_to_empty_list(open_documents_with_transcription)
        # List of document that don't have a transcription - open
        open_documents_without_transcription = database.get_open_documents_without_transcription_for_project(project_id)
        open_documents_without_transcription = if_none_convert_to_empty_list(open_documents_without_transcription)
        # List of Complete Document - succesfully transcribed - closed
        closed_documents = database.get_closed_documents_for_project(project_id)
        closed_documents = if_none_convert_to_empty_list(closed_documents)
        response.message = 'You own this project'
    else:
        # If not owner
        # Project is not open, redirect
        if project_status != 'Open':
            redirect(URL('default', 'index'))
        open_documents = database.get_open_documents_for_project(project_id)
        open_documents = if_none_convert_to_empty_list(open_documents)

    # List of done documents - 3 or more transcriptions
    done_documents = database.get_done_documents_for_project(project_id)
    done_documents = if_none_convert_to_empty_list(done_documents)

    # Page Title
    response.title = project.name

    #documents_for_project = database.get_open_documents_for_project(project.id)
    data_fields_for_project = database.get_data_fields_for_project(project.id)

    #Retrieve documents that have already been transcribed by the user in this project. This
    #can be used to alert users to that fact on the page.
    documents_transcribed_by_user = database.get_documents_with_transcription_for_project_and_transcription_author\
                                    (project_id, auth._get_user_id())
    header_image = URL('default','download',args = database.get_document_for_project_header(project.id).image)

    # Time String
    timestring = ''
    if project.time_period_start_date:
         timestring = '('+convert_integer_to_date_string(project.time_period_start_date) + " - " + convert_integer_to_date_string(project.time_period_end_date)+')'

    print open_documents_without_transcription

    return dict(project=project, timestring = timestring, data_fields_for_project=data_fields_for_project,
                documents_transcribed_by_user=documents_transcribed_by_user, header_image=header_image,
                done_documents=done_documents, open_documents_with_transcription=open_documents_with_transcription,
                open_documents_without_transcription=open_documents_without_transcription,
                closed_documents=closed_documents, open_documents=open_documents)

def view_document():

    #Remove if project data not required in page
    project_id = request.args(0)
    project = database.get_open_project(project_id)

    # Page Title
    response.title = project.name;

    # Redirect if null project.
    if project is None:
        redirect(URL('default','index'))

    # Get Doc from URL args
    document_id = request.args(1)
    document = database.get_document(document_id)

    # If null doc, go back to the project
    if document is None:
        redirect(URL('projects','project',args=[project_id]))

    # The form needs to be built dynamically to include all fields.
    form = FORM()

    # TEST
    formfact = None
    fields = []

    # If you are the owner, you cannot transcribe the document. Gives link to review transcriptions.
    if project.author_id == auth._get_user_id():
        response.message = A('You are the owner of this project and cannot transcribe its documents. Click here to review this document', _href=URL('projects','review_document', args=[project.id, document.id]))

    # Need an account to login
    elif auth._get_user_id() is None:
        response.message = A("Please login to transcribe.", _href=URL('user','login'))

    # If user has already provided a transcription
    elif database.document_has_already_been_transcribed_by_user(document_id, auth._get_user_id()):
        response.message = A("You have already transcribed this document")

    # If doc is no longer accepting transcriptions
    elif document.status == 'Done':
        response.message = A("This document has already received the maximum number of transcriptions allowed")

    # Display transcription submission form if document image is open for transcriptions and
    # user is authorised to make a submission (ie registered user, not project creator and has not already made
    # transcription for document image)
    else:
        #Create dynamic form according to number of data_fields
        for data_field in database.get_data_fields_for_project(project_id):
            label = H1(data_field.name)
            description = P(data_field.short_description)
            text_input = TEXTAREA(_name=data_field.name)
            form.append(SPAN(label, description, text_input))

            fields += [Field(data_field.name,'text', comment=T(data_field.short_description), label=T(data_field.name))]

        formfact = SQLFORM.factory(*fields, formstyle='bootstrap', _class='customer form-horizontal', table_name='customer')

        form.append(INPUT(_type='submit'))

        if formfact.process().accepted:

            # Check if document currently has 2 transcriptions or more and if so mark document as done before adding new transcription
            if len(database.get_transcriptions_for_document(document_id)) >= 2:
                document.update_record(status="Done")

            # Insert new transcription record to insert transcribed fields
            transcription_id = db.transcription.insert(document_id=document_id,
                                                       author_id=auth._get_user_id(),
                                                       status='Pending')

            # Inserts each transcribed field in db
            for data_field in database.get_data_fields_for_project(project_id):
                db.transcribed_field.insert(data_field_id = data_field.id,
                                            transcription_id = transcription_id,
                                            information = formfact.vars[data_field.name])

            redirect(URL('projects','project',args=[project_id]))



    # newform = SQLFORM.factory(form)
    image = URL('default','download',args = document.image)

    transcriptions = database.get_transcriptions_for_document(document_id)

    return dict(project=project, document=document, form=form, image=image, transcriptions=transcriptions, formfact = formfact)


@auth.requires_login(otherwise=URL('user', 'login'))
def review_document():
    # Current Project
    project_id = request.args(0)
    project = database.get_project(project_id)
    # Page Title
    response.title = project.name
    # Current Document
    document_id = request.args(1)
    document = database.get_document(document_id)

    # if project is None:
    #     # Redirect if project is none
    #     redirect(URL('default','index'))
    # if project.status != 'Under Review':
    #     redirect(URL('projects','project',args=[project_id]))
    # # Check Project Belongs to Current User
    # if project.author_id != auth._get_user_id():
    #     redirect(URL('projects','project',args=[project_id]))
    # Get current transcriptions for Document
    transcriptions = database.get_pending_transcriptions_for_document(document_id)
    print transcriptions

    transcribed_fields_for_transcriptions = []
    for transcription in transcriptions:
        transcribed_fields_for_transcriptions.append(database.get_transcribed_fields_for_transcription(transcription.id))


    return dict(project=project, document=document, transcriptions=transcriptions, database = database,
                transcribed_fields_for_transcriptions=transcribed_fields_for_transcriptions)

def accept_transcription():
    # Function for button which will accept a given transcription for a given document
    db(db.document_image.id==request.vars.document_id).update(status='Closed')
    db((db.transcription.id!=request.vars.transcription_id) & (db.transcription.document_id==request.vars.document_id))\
    .update(status="Rejected")
    db(db.transcription.id==request.vars.transcription_id).update(status='Accepted')
    db.commit()

    if len(database.get_open_documents_for_project(request.vars.project_id))==0:
        db(db.project.id==request.vars.project_id).update(status="Closed")
        db.commit()

    redirect(URL('default','index'), client_side=True)

def reject_all_transcriptions():
    # Function for button which will reject all transcriptions for a given document
    db((db.transcription.document_id==request.vars.document_id)).update(status="Rejected")
    db.commit()
    redirect(URL('default','index'), client_side=True)

def close_project_for_review():
    # Function for button which will close a project for review
    # FIXME: May need some validation depending on how it is implemented
    db((db.project.id==request.vars.project_id)).update(status="Under Review")
    db.commit()
    redirect(URL('projects','project', args=request.vars.project_id), client_side=True)

def if_none_convert_to_empty_list(array):
    if array is None:
        return []
    else:
        return array

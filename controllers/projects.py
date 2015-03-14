import database_transactions as database_transactions
database = database_transactions.DatabaseTransactions(db)


@auth.requires_login(otherwise=URL('user', 'login'))
def create_step1():

    options = ['Arts', 'Comics', 'Crafts', 'Fashion', 'Film', 'Games', 'Music', 'Photography', 'Technology']
    project_id = None
    project_being_edited = None
    if session.project_being_created is not None:
        project_id = session.project_being_created
        project_being_edited = database.get_project(project_id)
        #session.project_being_created = None

    form = SQLFORM(db.project, submit_button="Continue to Step 2", formstyle='divs', record=project_being_edited)
    clear_project = FORM(DIV(BUTTON("Clear Project",
                                        _type='submit', _class='btn btn-primary btn-block btn-large')))

    form.vars.author_id = auth.user_id

    if form.validate(formname="form_one", onvalidation=validate_create_step1):
        if request.vars.unknown == "yes":
            start_date = None
            end_date = None
        else:
            start_date = convert_date_to_integer(request.vars.start_date, request.vars.start_era)
            end_date = convert_date_to_integer(request.vars.end_date, request.vars.end_era)

        if project_id and project_being_edited:
            project_being_edited.update_record(name=request.vars.name, author_id=auth._get_user_id(), status="Closed",
                                               description=request.vars.description, tag=request.vars.tag,
                                               time_period_start_date=start_date, time_period_end_date=end_date)
        else:
            project_id = db.project.insert(name=request.vars.name, author_id=auth._get_user_id(), status="Closed",
                                           description=request.vars.description, tag=request.vars.tag,
                                           time_period_start_date=start_date, time_period_end_date=end_date)

        session.project_being_created = project_id
        redirect(URL('projects', 'create_step2'))
    else:
        #print form.errors
        pass

    if clear_project.validate(formname="form_two"):
        session.project_being_created = None
        redirect(URL('projects', 'create_step1'))

    prepopulation_data = retrieve_prepopulated_data_for_create_step_1(project_being_edited)


    return dict(form=form, tag_options=options, clear_project=clear_project, project_being_edited = project_being_edited,
                pd=prepopulation_data)

def convert_date_to_integer(date, era):
    if era =="BC":
        return -int(date)
    else:
        return int(date)

def retrieve_prepopulated_data_for_create_step_1(project_being_edited):
    if project_being_edited == None:
        return None
    else:
        data = {}
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

    start_date = None
    end_date = None
    date_validator = IS_INT_IN_RANGE(-2015, 2015, error_message ="Date must be whole number between 2015 BC and 2015 AD")

    if request.vars.unknown != "yes":
        if (request.vars.start_date != "") and (request.vars.start_date != None):
            if date_validator(request.vars.start_date)[1] is not None:
                form.errors.start_date = date_validator(start_date)[1]
            else:
                start_date = convert_date_to_integer(request.vars.start_date, request.vars.start_era)
        else:
            form.errors.start_date = "Start Date must not be empty"

        if (request.vars.end_date != "") and (request.vars.end_date != None):
            if date_validator(request.vars.end_date)[1] is not None:
                form.errors.end_date = date_validator(end_date)[1]
            else:
                end_date = convert_date_to_integer(request.vars.end_date, request.vars.end_era)

        else:
            form.errors.end_date = "End Date must not be empty"

        if start_date and end_date:
                if start_date > end_date:
                    form.errors.end_date = 'The End Date of the time period must be later than the Start Date'

    print form.errors



@auth.requires_login(otherwise=URL('user', 'login'))
def create_step2():

    project_id = None
    if session.project_being_created is not None:
        project_id = session.project_being_created
        #session.project_being_created = None

    clear_project = FORM(DIV(BUTTON("Clear Project",
                                        _type='submit', _class='btn btn-primary btn-block btn-large')))

    add_image_form = SQLFORM(db.document_image, submit_button="Add Image")

    go_to_step_3_form = FORM(DIV(BUTTON("Continue to Step 3", I(_class='icon-arrow-right icon-white'),
                                        _type='submit', _class='btn btn-primary btn-block btn-large')))
    go_to_step_1_form = FORM(DIV(BUTTON("Back to Step 1", I(_class='icon-arrow-left icon-white'),
                                        _type='submit', _class='btn btn-primary btn-block btn-large')))

    if add_image_form.validate(formname="form_one", onvalidation=validate_add_image_form):

        db.document_image.insert(description=request.vars.description, status="Open", project_id=project_id,
                                 image=add_image_form.vars.image)
        session.project_being_created = project_id

    if go_to_step_3_form.process(formname="form_two").accepted:
        documents_added = database.get_project_documents(project_id)
        if len(documents_added) < 1:
            response.flash = DIV("At least one image must be added", _class="alert alert-error")
        else:
            session.project_being_created = project_id
            redirect(URL('projects', 'create_step3'))

    if go_to_step_1_form.process(formname="form_three").accepted:
            session.project_being_created = project_id
            redirect(URL('projects', 'create_step1'))

    if clear_project.validate(formname="form_four"):
        session.project_being_created = None
        redirect(URL('projects', 'create_step1'))

    documents_added = database.get_project_documents(project_id)

    return dict(add_image_form=add_image_form, go_to_step_3_form=go_to_step_3_form,
                go_to_step_1_form=go_to_step_1_form, documents_added=documents_added, clear_project=clear_project)


def validate_add_image_form(form):

    if (request.vars.description == "") or (request.vars.description == None):
        form.errors.description = "Description must not be empty"

    image_validator = IS_NOT_EMPTY(error_message=T("Image must not be left empty"))
    if image_validator(request.vars.image)[1] is not None:
        form.errors.image = image_validator(request.vars.image)[1]



@auth.requires_login(otherwise=URL('user', 'login'))
def create_step3():

    project_id = None
    if session.project_being_created is not None:
        project_id = session.project_being_created
        #session.project_being_created = None

    add_fields_form = SQLFORM.factory(db.data_field, submit_button="Add field")
    create_project_form = FORM(DIV(BUTTON("Create Project", I(_class='icon-arrow-right icon-white'),
                                          _type='submit', _class='btn btn-primary btn-block btn-large')))
    go_to_step_2_form = FORM(DIV(BUTTON("Back to Step 2", I(_class='icon-arrow-left icon-white'),
                                        _type='submit', _class='btn btn-primary btn-block btn-large')))

    clear_project = FORM(DIV(BUTTON("Clear Project",
                                        _type='submit', _class='btn btn-primary btn-block btn-large')))

    if add_fields_form.process(formname="form_one", onvalidate = validate_add_field_form).accepted:
        db.data_field.insert(name=request.vars.name, short_description=request.vars.short_description, project_id=project_id)
        db.commit()
        session.project_being_created = project_id

    if create_project_form.process(formname="form_two").accepted:
        fields_added = database.get_data_fields_for_project(project_id)
        if len(fields_added) < 1:
            response.flash = DIV("At least one field must be added", _class="alert alert-error")
        else:
            project = database.get_project(project_id)
            project.update_record(status="Open")
            session.project_being_created = None
            redirect(URL('default', 'index'))

    if go_to_step_2_form.process(formname="form_three").accepted:
        session.project_being_created = project_id
        redirect(URL('projects', 'create_step2'))

    if clear_project.validate(formname="form_four"):
        session.project_being_created = None
        redirect(URL('projects', 'create_step1'))

    documents_added = database.get_project_documents(project_id)
    fields_added = database.get_data_fields_for_project(project_id)

    return dict(documents_added=documents_added, add_fields_form=add_fields_form, fields_added=fields_added
                , create_project_form=create_project_form, go_to_step_2_form=go_to_step_2_form, clear_project=clear_project)

def validate_add_field_form(form):

    if (request.vars.name != "") and (request.vars.name != None):
        form.errors.name = "Name must not be empty"

    if (request.vars.short_description != "") and (request.vars.short_description != None):
        form.errors.short_description = "Description must not be empty"

def project():

    project_id = request.args(0)
    project = database.get_open_project(project_id)

    #If project doesnt exist or isn't open, redirect
    if project is None:
        redirect(URL('default', 'index'))

    #If user owns project then initialise message to be displayed on page
    if project.author_id == auth._get_user_id():
        response.flash = DIV("You own this project", _class="alert alert-info")

    documents_for_project = database.get_project_open_documents(project.id)
    data_fields_for_project = database.get_data_fields_for_project(project.id)

    #Retrieve documents that have already been transcribed by the user in this project. This
    #can be used to alert users to that fact on the page.
    documents_transcribed_by_user = database.get_documents_in_project_that_has_already_been_transcribed_by_user\
                                    (project_id, auth._get_user_id())

    return dict(project=project, documents_for_project=documents_for_project,
                data_fields_for_project=data_fields_for_project,
                documents_transcribed_by_user=documents_transcribed_by_user)


def add_transcription():

    #Remove if project data not required in page
    project_id = request.args(0)
    project = database.get_open_project(project_id)

    if project is None:
        redirect(URL('default','index'))

    document_id = request.args(1)
    document = database.get_document(document_id)

    if document is None:
        redirect(URL('projects','project',args=[project_id]))
    
    form = FORM()

    if project.author_id == auth._get_user_id():
        response.flash = DIV("You own this project", _class="alert alert-info")
    
    elif auth._get_user_id is None:
        response.flash = DIV("Please register to transcribe", _class="alert alert-info")
        
    elif not database.check_if_document_has_already_been_transcribed_by_user(document_id, auth._get_user_id):
        response.flash = DIV("You have already transcribed this document", _class="alert alert-info")

    elif document.status == 'Done':
        response.flash = DIV("This document has already received the maximum number of transcriptions allowed", _class="alert alert-info")
        
    #Display transcription submission form if document image is open for transcriptions and
    #user is authorised to make a submission (ie registered user, not project creator and has not already made
    #transcription for document image)    
    else:
        #Create dynamic form according to number of data_fields
        for data_field in database.get_data_fields_for_project(project_id):
            label = '%s\n%s' % (data_field.name, data_field.short_description)
            text_input = INPUT(_name=data_field.name)
            form.append(SPAN(label, text_input))
            
        form.append(INPUT(_type='submit'))
            
        if form.process().accepts:
            #Insert new transcription record to insert transcribed fields
            transcription_id = db.transcription.insert(document_id=document_id, author_id=auth._get_user_id(), status='pending')
            
            #Inserts each transcribed field in db
            for data_field in database.get_data_fields_for_project(project_id):
                db.transcribed_field.insert(data_field_id=data_field.id, transcription_id=transcription_id, information=form.vars[data_field.name])

    return dict(project=project, document=document, form=form)

def view_document():
    # Current Project
    project_id = request.args(0)
    project = database.get_open_project(project_id)
    if project is None:
        # Redirect if project is none
        redirect(URL('default','index'))
    # Current Document
    document_id = request.args(1)
    document = database.get_document(document_id)

    if document is None:
        # Redirect if document is none
        redirect(URL('projects','project',args=[project_id]))

    if project.author_id == auth._get_user_id():
        # Display alert if you own project
        response.flash = DIV("You own this project", _class="alert alert-info")

    # Current Data Fields
    data_fields = database.get_data_fields_for_project(project_id)
    return dict(project=project, document=document, data_fields=data_fields)



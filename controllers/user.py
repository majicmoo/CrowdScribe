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
		userid = auth.get_or_create_user(form.vars);
	elif form.errors:
		response.flash = 'One or more of your form fields has an error. Please see below for more information'

	return dict(form = form);

def login():
	response.title = 'Login'

	auth.settings.login_userfield = 'username'
	if request.vars.username and not IS_EMAIL()(request.vars.username)[1]:
		# If this doesnt work, check if its an email.
		auth.settings.login_userfield = 'email'
		request.vars.email = request.vars.username
		request.post_vars.email = request.vars.email
		request.vars.username = None
		request.post_vars.username = None

	form = auth.login()

	# Define placeholder values     
	form.custom.widget.username["_placeholder"] = "Username or Email"
	form.custom.widget.password["_placeholder"] = "Password"

	return dict(form=form);

def profile():
	response.title = 'Profile'
	return dict();
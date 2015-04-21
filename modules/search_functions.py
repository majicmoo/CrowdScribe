import general_functions as general_functions


class SearchFunctions:

    def __init__(self, database, db):
        self.database = database
        self.db = db
        self.general_module = general_functions.GeneralFunctions(database, db)

    def empty_field(self, field):
        # Return False if data field has content else return true
        if (field is not None or field == "") and (field is None or field != ""):
            # Field has content
            return False
        else:
            return True

    def date_validator(self, advanced):
        # Checks start date is after 2015 BC
        if not self.empty_date_field(advanced.vars.start_date):
            if self.general_module.convert_date_to_integer(advanced.vars.start_date, advanced.vars.start_era) < -2015:
                advanced.errors.start_date = 'Start date must be after 2015 BC'

        # Checks end date is before 2015 AD
        if not self.empty_date_field(advanced.vars.end_date):
            if self.general_module.convert_date_to_integer(advanced.vars.end_date, advanced.vars.end_era) > 2015:
                advanced.errors.end_date = 'End date must be before 2015 AD'

        # Check that start date is before end date if there are entries for both dates
        if not self.empty_date_field(advanced.vars.start_date) and not self.empty_date_field(advanced.vars.end_date):
            start = self.general_module.convert_date_to_integer(advanced.vars.start_date, advanced.vars.start_era)
            end = self.general_module.convert_date_to_integer(advanced.vars.end_date, advanced.vars.end_era)
            if start > end:
                advanced.errors.end_date = 'The End Date of the time period must be later than the Start Date'

    def search_project_for_keywords(self, keywords, project):
        # Search project for keywords. If word is found, project is not excluded
        exclude = True
        for word in keywords:
            if (word.upper() in project.name.upper()) or (word.upper() in project.description.upper()):
                exclude = False
                break

        return exclude
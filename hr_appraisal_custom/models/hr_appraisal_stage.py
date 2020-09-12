from odoo import fields, models, api


class HrAppraisalStage(models.Model):
    _name = 'hr.appraisal.stage'

    name = fields.Char("Stage Name", required=True, translate=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")

    # Appraisal
    employee_allowed_edit = fields.Boolean(string="Employee")
    manager_allowed_edit = fields.Boolean(string="Manager")
    users_allowed_edit = fields.Many2many(relation="user_appraisal_allowed_1", comodel_name='res.users',
                                          string="Users")

    employee_can_add_objective = fields.Boolean(string="Employee")
    manager_can_add_objective = fields.Boolean(string="Manager ")
    users_can_add_objective = fields.Many2many(relation="user_appraisal_allowed_2", comodel_name='res.users',
                                               string="Users")

    employee_can_comment_objective_hr = fields.Boolean(string="Employee")
    manager_can_comment_objective_hr = fields.Boolean(string="Manager")
    users_can_comment_objective_hr = fields.Many2many(relation="user_appraisal_allowed_3", comodel_name='res.users',
                                                      string="Users")

    employee_can_comment_objective_manager = fields.Boolean(string="Employee")
    manager_can_comment_objective_manager = fields.Boolean(string="Manager")
    users_can_comment_objective_manager = fields.Many2many(relation="user_appraisal_allowed_4",
                                                           comodel_name='res.users',
                                                           string="Users")

    employee_can_comment_objective_employee = fields.Boolean(string="Employee")
    manager_can_comment_objective_employee = fields.Boolean(string="Manager")
    users_can_comment_objective_employee = fields.Many2many(relation="user_appraisal_allowed_5",
                                                            comodel_name='res.users',
                                                            string="Users")

    employee_can_see_comment_objective_hr = fields.Boolean(string="Employee")
    manager_can_see_comment_objective_hr = fields.Boolean(string="Manager")
    users_can_see_comment_objective_hr = fields.Many2many(relation="user_appraisal_allowed_6", comodel_name='res.users',

                                                          string="Users")
    employee_can_see_comment_objective_manager = fields.Boolean(string="Employee")
    manager_can_see_comment_objective_manager = fields.Boolean(string="Manager")
    users_can_see_comment_objective_manager = fields.Many2many(relation="user_appraisal_allowed_7",
                                                               comodel_name='res.users',
                                                               string="Users")

    employee_can_see_comment_objective_employee = fields.Boolean(string="Employee")
    manager_can_see_comment_objective_employee = fields.Boolean(string="Manager")
    users_can_see_comment_objective_employee = fields.Many2many(relation="user_appraisal_allowed_8",
                                                                comodel_name='res.users',
                                                                string="Users")

    employee_can_comment_form_hr = fields.Boolean(string="Employee")
    manager_can_comment_form_hr = fields.Boolean(string="Manager")
    users_can_comment_form_hr = fields.Many2many(relation="user_appraisal_allowed_9", comodel_name='res.users',
                                                 string="Users")

    employee_can_comment_form_manager = fields.Boolean(string="Employee")
    manager_can_comment_form_manager = fields.Boolean(string="Manager")
    users_can_comment_form_manager = fields.Many2many(relation="user_appraisal_allowed_10",
                                                      comodel_name='res.users',
                                                      string="Users")

    employee_can_comment_form_employee = fields.Boolean(string="Employee")
    manager_can_comment_form_employee = fields.Boolean(string="Manager")
    users_can_comment_form_employee = fields.Many2many(relation="user_appraisal_allowed_11",
                                                       comodel_name='res.users',
                                                       string="Users")

    employee_can_see_comment_form_hr = fields.Boolean(string="Employee")
    manager_can_see_comment_form_hr = fields.Boolean(string="Manager")
    users_can_see_comment_form_hr = fields.Many2many(relation="user_appraisal_allowed_12", comodel_name='res.users',

                                                     string="Users")
    employee_can_see_comment_form_manager = fields.Boolean(string="Employee")
    manager_can_see_comment_form_manager = fields.Boolean(string="Manager")
    users_can_see_comment_form_manager = fields.Many2many(relation="user_appraisal_allowed_13",
                                                          comodel_name='res.users',
                                                          string="Users")

    employee_can_see_comment_form_employee = fields.Boolean(string="Employee")
    manager_can_see_comment_form_employee = fields.Boolean(string="Manager")
    users_can_see_comment_form_employee = fields.Many2many(relation="user_appraisal_allowed_14",
                                                           comodel_name='res.users',
                                                           string="Users")

    employee_can_modifiy_training = fields.Boolean(string="Employee")
    manager_can_modifiy_training = fields.Boolean(string="Manager")
    users_can_modifiy_training = fields.Many2many(relation="user_appraisal_allowed_15",
                                                  comodel_name='res.users',
                                                  string="Users")

    employee_request_feedback = fields.Boolean(string="Employee")
    manager_request_feedback = fields.Boolean(string="Manager")
    users_request_feedback = fields.Many2many(relation="user_appraisal_allowed_16",
                                              comodel_name='res.users',
                                              string="Users")

    employee_see_feedback = fields.Boolean(string="Employee")
    manager_see_feedback = fields.Boolean(string="Manager")
    users_see_feedback = fields.Many2many(relation="user_appraisal_allowed_17",
                                          comodel_name='res.users',
                                          string="Users")

    employee_take_survey = fields.Boolean(string="Employee")
    manager_take_survey = fields.Boolean(string="Manager")
    users_take_survey = fields.Many2many(relation="user_appraisal_allowed_18",
                                         comodel_name='res.users',
                                         string="Users")
    employee_see_survey = fields.Boolean(string="Employee")
    manager_see_survey = fields.Boolean(string="Manager")
    users_see_survey = fields.Many2many(relation="user_appraisal_allowed_19",
                                        comodel_name='res.users',
                                        string="Users")

    employee_allowed_forward = fields.Boolean(string="Employee")
    manager_allowed_forward = fields.Boolean(string="Manager")
    users_allowed_forward = fields.Many2many(relation="user_appraisal_allowed_20",
                                             comodel_name='res.users',
                                             string="Users")

    log_note_backward = fields.Boolean(string="Log Reason")
    employee_allowed_backward = fields.Boolean(string="Employee")
    manager_allowed_backward = fields.Boolean(string="Manager")
    users_allowed_backward = fields.Many2many(relation="user_appraisal_allowed_21",
                                              comodel_name='res.users',
                                              string="Users")

    employee_can_approve_approve = fields.Boolean(string="Employee")
    manager_can_approve_approve = fields.Boolean(string="Manager")
    users_can_approve_approve = fields.Many2many(relation="user_appraisal_allowed_22",
                                                 comodel_name='res.users',
                                                 string="Users")

    employee_rating_manager_add = fields.Boolean(string="Employee")
    manager_rating_manager_add = fields.Boolean(string="Manager")
    users_rating_manager_add = fields.Many2many(relation="user_appraisal_allowed_23",
                                                comodel_name='res.users',
                                                string="Users")

    employee_rating_employee_add = fields.Boolean(string="Employee")
    manager_rating_employee_add = fields.Boolean(string="Manager")
    users_rating_employee_add = fields.Many2many(relation="user_appraisal_allowed_24",
                                                 comodel_name='res.users',
                                                 string="Users")

    employee_rating_hr_add = fields.Boolean(string="Employee")
    manager_rating_hr_add = fields.Boolean(string="Manager")
    users_rating_hr_add = fields.Many2many(relation="user_appraisal_allowed_25",
                                           comodel_name='res.users',
                                           string="Users")

    employee_rating_manager_see = fields.Boolean(string="Employee")
    manager_rating_manager_see = fields.Boolean(string="Manager")
    users_rating_manager_see = fields.Many2many(relation="user_appraisal_allowed_26",
                                                comodel_name='res.users',
                                                string="Users")

    employee_rating_employee_see = fields.Boolean(string="Employee")
    manager_rating_employee_see = fields.Boolean(string="Manager")
    users_rating_employee_see = fields.Many2many(relation="user_appraisal_allowed_27",
                                                 comodel_name='res.users',
                                                 string="Users")

    employee_rating_hr_see = fields.Boolean(string="Employee")
    manager_rating_hr_see = fields.Boolean(string="Manager")
    users_rating_hr_see = fields.Many2many(relation="user_appraisal_allowed_28",
                                           comodel_name='res.users',
                                           string="Users")

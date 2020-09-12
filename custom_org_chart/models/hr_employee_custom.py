from odoo import fields, models, api
import csv
from datetime import datetime

full_datetime_format = '%Y/%m/%d %H:%M'
full_date_format = '%Y_%m_%d'


class EmploymentCustom(models.Model):
    _inherit = 'hr.employee'

    def write_strata_csv_file(self):
        select_type = self.env['ir.config_parameter'].sudo()
        sap_folder_path = select_type.get_param('res.config.settings.sap_folder_path')
        today = datetime.today().strftime(full_date_format)

        if sap_folder_path:
            path = ''
            if sap_folder_path.endswith('\\') or sap_folder_path.endswith('/'):
                path = sap_folder_path
            else:
                separator = ''
                if '\\' in sap_folder_path:
                    separator = '\\'
                elif '/' in sap_folder_path:
                    separator = '/'
                path = sap_folder_path + separator

            with open(path + 'OMD_' + today + '.csv', 'w', newline='') as file:
                fieldnames = ['Object ID', 'Object Type', 'Start Date', 'End Date', 'Object Description', 'Parent ID']
                writer = csv.writer(file)
                departments = self.env['hr.department'].search([])
                jobs = self.env['hr.job'].search([])
                # writer.writeheader()
                writer.writerow(fieldnames)
                for department in departments:
                    department_code = department.code if department.code else ''
                    department_type = department.type if department.type else ''
                    start_date = department.start_date.strftime(full_datetime_format) if department.start_date else ''
                    end_date = department.end_date.strftime(full_datetime_format) if department.end_date else ''
                    department_name = department.name if department.name else ''
                    parent = department.parent_id.code if department.parent_id else ''
                    writer.writerow(
                        [department_code, department_type, start_date, end_date, department_name, parent])
                for job in jobs:
                    job_code = job.name if job.name else ''
                    job_type = 'P'
                    start_date = job.create_date.strftime(full_datetime_format) if job.create_date else ''
                    end_date = ''
                    job_name = job.description if job.description else ''
                    parent = job.subsection.code if job.subsection else (job.section.code if job.section else (
                        job.department_id.code if job.department_id else (job.group.code if job.group else '')))
                    writer.writerow(
                        [
                            job_code, job_type, start_date, end_date, job_name, parent
                        ]
                    )

            with open(path + 'EMD_' + today + '.csv', 'w', newline='') as file:
                fieldnames = ['Employee ID', 'Event Type', 'Event Reason', 'Start Date', 'Org Unit',
                              'Line Manager Employee Id', 'Position Code', 'Cost Center', 'Employee Group',
                              'Employee subgroup', 'Payroll area', 'Contract type', 'Probation end date',
                              'Confirmation date', 'Salutation', 'First name',
                              'Middle name', 'Last name', 'Birth date', 'Gender', 'Nationality', 'Birth Country',
                              'Shift type', 'OT eligibility', 'System Id', 'Email id', 'Pay scale group',
                              'Payscale Level']
                writer = csv.writer(file)
                employees = self.env['hr.employee'].search([])
                writer.writerow(fieldnames)
                for employee in employees:
                    employee_id = employee.strata_id if employee.strata_id else ''
                    event_type = ''
                    event_reason = ''
                    start_date = employee.contract_id.date_start.strftime(
                        full_datetime_format) if (employee.contract_id and employee.contract_id.date_start) else ''
                    org_unit = employee.department_id.code if employee.department_id.code else ''
                    line_manager_id = employee.parent_id.strata_id if employee.parent_id.strata_id else ''
                    position_code = employee.job_id.name if employee.job_id.name else ''
                    cost_center = employee.contract_id.cost_center.code if employee.contract_id.cost_center.code else ''
                    employee_group = employee.contract_id.contract_group.code if employee.contract_id.contract_group.code else ''
                    employee_sub_group = employee.contract_id.contract_subgroup.code if employee.contract_id.contract_subgroup.code else ''
                    payroll_area = employee.contract_id.pay_type_id.code if employee.contract_id.pay_type_id.code else ''
                    contract_type = employee.contract_id.contract_type.code if employee.contract_id.contract_type.code else ''
                    probation_end_date = employee.contract_id.trial_date_end.strftime(
                        full_datetime_format) if employee.contract_id.trial_date_end else ''
                    confirmation_date = employee.contract_id.confirmation_date.strftime(
                        full_datetime_format) if employee.contract_id.confirmation_date else ''
                    salutation = employee.title.shortcut if employee.title.shortcut else ''
                    first_name = employee.firstname if employee.firstname else ''
                    middle_name = employee.middlename if employee.middlename else ''
                    last_name = employee.lastname if employee.lastname else ''
                    birth_date = employee.birthday.strftime(
                        full_datetime_format) if employee.birthday else ''
                    gender = employee.gender if employee.gender else ''
                    nationality = employee.country_id.code if employee.country_id.code else ''
                    birth_country = employee.country_of_birth.code if employee.country_of_birth.code else ''
                    shift_type = employee.resource_calendar_id.name if employee.resource_calendar_id.name else ''
                    ot_eligibility = employee.contract_id.overtime_eligibility if employee.contract_id.overtime_eligibility else ''
                    system_id = employee.parent_id.system_id if employee.parent_id.system_id else ''
                    email_id = employee.work_email if employee.work_email else ''
                    payscale_group = employee.contract_id.payscale_group.code if employee.contract_id.payscale_group.code else ''
                    payscale_level = employee.contract_id.payscale_level.code if employee.contract_id.payscale_level.code else ''
                    writer.writerow([
                        employee_id, event_type, event_reason, start_date, org_unit, line_manager_id, position_code,
                        cost_center, employee_group, employee_sub_group, payroll_area,
                        contract_type, probation_end_date, confirmation_date, salutation, first_name,
                        middle_name, last_name, birth_date, gender, nationality, birth_country, shift_type,
                        ot_eligibility, system_id,
                        email_id, payscale_group, payscale_level])

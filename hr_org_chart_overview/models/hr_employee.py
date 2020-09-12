# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models

org_chart_classes = {
    0: "level-0",
    1: "level-1",
    2: "level-2",
    3: "level-3",
    4: "level-4",
}


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_employee_domain(self, parent_id):
        company = self.env.company
        domain = ["|", ("company_id", "=", False), ("company_id", "=", company.id)]
        if not parent_id:
            domain.extend([("parent_id", "=", False), ("child_ids", "!=", False)])
        else:
            domain.append(("parent_id", "=", parent_id))
        return domain

    def get_class_name(self):
        result = ''
        nationality = self.country_id.id
        group = self.contract_id.contract_group.id
        subgroup = self.contract_id.contract_subgroup.id
        employment_type = self.contract_employment_type.id
        # color_combo = self.env['employee.color.combo'].search(
        #     [('nationality_id', 'in', [nationality, False]), ('subgroup_id', 'in', [subgroup, False]),
        #      ('group_id', 'in', [group, False]),
        #      ('employment_type_id', 'in', [employment_type, False])], limit=1)
        color_combo = self.env['employee.color.combo'].search(
            [('subgroup_id', '=', subgroup), ('group_id', '=', group),
             ('employment_type_id', '=', employment_type)], limit=1)
        if color_combo:
            color_class_id = color_combo.name.get_external_id()
            result = color_class_id.get(color_combo.name.id).split('.')[1]
        return result

    def _get_employee_data(self, level=0):
        job_title = (self.contract_id.job_title.name + "<br/>") if self.contract_id.job_title.name else ''
        job_position = (self.contract_id.job_id.name + "<br/>") if self.contract_id.job_id.name else ''
        department_name = ("<hr><b>" + self.department_id.name + "</b><br/>") if self.department_id.name else ''
        department_code = self.department_id.code if self.department_id.code else ''
        system_id = (self.system_id + "<br/>") if self.system_id else ''
        class_name = self.get_class_name()
        return {
            "id": self.id,
            "name": self.name,
            "title": system_id + job_title + job_position + department_name + department_code,
            # "className": org_chart_classes[level],
            "className": class_name,
            'collapsed': True,
            "image": self.env["ir.attachment"]
                .sudo()
                .search(
                [
                    ("res_model", "=", "hr.employee"),
                    ("res_id", "=", self.id),
                    ("res_field", "=", "image_512"),
                ],
                limit=1,
            )
                .datas,
        }

    @api.model
    def _get_children_data(self, child_ids, level):
        children = []
        for employee in child_ids:
            data = employee._get_employee_data(level)
            employee_child_ids = self.search(self._get_employee_domain(employee.id))
            if employee_child_ids:
                data.update(
                    {
                        "children": self._get_children_data(
                            employee_child_ids, (level + 1) % 5
                        )
                    }
                )
            children.append(data)
        return children

    @api.model
    def get_organization_data(self):
        # First get employee with no manager
        domain = self._get_employee_domain(False)
        top_employee = self.search(domain, limit=1)
        data = top_employee._get_employee_data()

        # If any child we fetch data recursively for childs of top employee
        top_employee_child_ids = self.search(self._get_employee_domain(top_employee.id))
        if top_employee_child_ids:
            data.update(
                {"children": self._get_children_data(top_employee_child_ids, 1)}
            )
        return data

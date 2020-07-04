# -*- coding: utf-8 -*-


import base64
from cStringIO import StringIO
from werkzeug.utils import redirect


from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website.models.website import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_project.controllers.main import WebsiteAccount


class WebsiteAmh(WebsiteAccount):

    @http.route(['/my/task/<model("project.task"):task>'], type='http', auth="user", website=True)
    def my_task(self, task=None, **kw):
        attachments = request.env['ir.attachment'].search(
            [('res_model', '=', 'project.task'),
             ('res_id', '=', task.id)], order='id')
        return request.render("website_project.my_task", {
            'task': task,
            'user': request.env.user,
            'range': range,
            'attachments': attachments,
        })

    @http.route(['/attachment/download'], type='http', auth='public')
    def download_attachment(self, attachment_id):
        # Check if this is a valid attachment id
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "file_type", "res_model", "res_id", "type", "url"]
        )
        if attachment:
            attachment = attachment[0]
        else:
            return redirect('/my/tasks/')

        if attachment["type"] == "url":
            if attachment["url"]:
                return redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            data = StringIO(base64.standard_b64decode(attachment["datas"]))
            return http.send_file(data, filename=attachment['name'], as_attachment=True)
        else:
            return request.not_found()

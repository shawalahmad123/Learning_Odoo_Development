from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.exceptions import Warning

class import_data_ept(models.Model):
    _name = "import.data.ept"
    
    name=fields.Char(string='Name',size=1024,required=True)
    data_file = fields.Binary("Data File", attachment=True, help="Upload here your file for Import")
    code=fields.Text(string='Python Code',required=True)
    result=fields.Text(string='Result',readonly=True)

    def execute_code(self):
        localdict = {'self': self}
        for obj in self:  # .browse(self._ids):
            try:
                exec (obj.code, localdict)
                if localdict.get('result', False):
                    self.write({'result': localdict['result']})
                else:
                    self.write({'result': ''})
            except Exception as e:
                raise Warning('Python code is not able to run ! message : %s' % (e))

        return True
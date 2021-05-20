from odoo import models, fields, api, _
import csv
from odoo.exceptions import Warning
from datetime import datetime
import logging
import requests
import base64
import os
_logger = logging.getLogger(__name__)

color_code = {
    "Space Grey": "#808080",
    "Silver": "#C0C0C0"
}

class emipro_execute_python(models.Model):
    _inherit = "emipro.execute.python"
    _description= "It contains the scripts logic for creating the data"

    def assign_sequence_attribute_value(self):
        print("Process Start")
        ProductAttributeValue = self.env['product.attribute.value'].sudo()
        ProductTemplate = self.env['product.template'].sudo()
        file_path = self.get_module_path()
        if file_path:
            file_location = '/data/live_purchase_full.csv'
            file_location = file_path + file_location

            with open(file_location, 'rU')as file:
                data = csv.DictReader(file)
                value_list = []
                for row in data:
                    if ProductTemplate.search([('default_code','=',row.get('Model'))]):
                        if row.get('Status') == 'Default Value':
                            attr_value = " ".join(row.get('Desc').split())
                            attr_value = attr_value.replace('\xa0', ' ')
                            if attr_value not in value_list:
                                value_list.append(attr_value)
                if value_list:
                    values_records = ProductAttributeValue.search([('name','in',value_list)])
                    for rec in values_records:
                        rec.write({'sequence':0})
        print("Process Complete")

    def get_module_path(self):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        file_path = file_path.split('/models')[0]
        if file_path:
            return file_path
        else:
            False

    def prepare_product_data(self):
        _logger.info("Product Template Import Starting %s<<<<<<<<<<<<<<<<<<<<<<<"%datetime.now().strftime('%H:%M:%S'))
        ProductImage = self.env['product.image'].sudo()
        ProductTemplate = self.env['product.template'].sudo()

        # file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        # file_path = file_path.split('/models')[0]
        file_path = self.get_module_path()
        if file_path:
            file_location = '/data/final_product_template.csv'
            file_location = file_path + file_location

            with open(file_location,'rU')as file:
                data = csv.DictReader(file)
                for row in data:
                    available_product = ProductTemplate.search([('default_code','=',row.get('Base Model'))])
                    if available_product:
                        continue
                    # Images
                    images_url = []
                    images = row.get('images')
                    if images:
                        has_image = True
                        has_multi_image = False
                        if ',' in images:
                            has_multi_image=True
                            images = images.split(',')
                            for img in images:
                                images_url.append(img.strip())
                        else:
                            images_url.append(images.strip())

                    # get category info
                    categ_info = row.get('product_public_category')
                    if categ_info:
                        # if ',' in categ_info:
                        #     categ_info = categ_info.split(',')

                        category_rec = self.env['product.public.category'].search([('name', '=', categ_info)])
                        if not category_rec:
                            category_rec = self.env['product.public.category'].create({'name': categ_info})

                    product_type = row.get('product_type')
                    if product_type == 'Consumable':
                        prod_type = 'consu'
                    elif product_type == 'Service':
                        prod_type = 'service'
                    elif product_type == 'Storable Product':
                        prod_type = 'product'
                    else:
                        prod_type = False


                    vals = {
                        'default_code' : row.get('Base Model'),
                        'name' : row.get('Name'),
                        'category_name' : row.get('Category Name', False) if row.get('Category Name', False) else row.get('Name'),
                        # 'type' : row.get('product_type'),
                        'purchase_ok' : row.get('Storable Product'),
                        'active' : row.get('active'),
                        'sale_ok' : row.get('sale_ok'),
                        'standard_price' : float(row.get('cost')),
                        'list_price' : float(row.get('list_price')),
                        'website_published' : row.get('website_published'),
                        'website_description' : row.get('description_sale')
                    }

                    if has_image:
                        img_data = base64.b64encode(requests.get(images_url[0]).content)
                        vals.update({'image_1920':img_data})

                    if category_rec:
                        vals.update({
                            'public_categ_ids' : [[ 6, 0, category_rec.ids ]]
                        })
                    if product_type:
                        vals.update({'type': prod_type})

                    NewProd = ProductTemplate.create(vals)
                    if has_image and has_multi_image:
                        extra_image = images_url[1:]
                        for image in extra_image:
                            vals = {
                                'name': NewProd.name,
                                'product_tmpl_id' : NewProd.id,
                                'image_1920' : base64.b64encode(requests.get(image).content)
                            }
                            ProductImage.create(vals)
        _logger.info(">>>>>>>>>>>>>>>>>>>>Product Template Import Completed %s<<<<<<<<<<<<<<<<<<<<<<<"%datetime.now().strftime('%H:%M:%S'))
        return True

    def prepare_category_data(self):
        _logger.info(">>>>>>>>>>>>>>>>>>>>Website Category Import Starting<<<<<<<<<<<<<<<<<<<<<<<")

        file_path = self.get_module_path()
        if file_path:
            file_location = '/data/website_category.csv'
            file_location = file_path + file_location

            with open(file_location,'rt')as file:
                data = csv.reader(file)
                for row in data:
                    # Ignore First Column
                    if row[0] == 'name':
                        result = row

                    # Check if category already created or not
                    available_category = self.env['product.public.category'].search([('name', '=', row[0])])
                    if available_category:
                        continue

                    # Create Category with Parent relation if available
                    if len(row[1]) >= 1:
                        parent = self.env['product.public.category'].search([('name', '=', row[1])])
                        if parent:
                            self.env['product.public.category'].create({'name': row[0], 'parent_id': parent.id})
                        else:
                            parent = self.env['product.public.category'].create({'name': row[1]})
                            self.env['product.public.category'].create({'name': row[0], 'parent_id': parent.id})
        _logger.info(">>>>>>>>>>>>>>>>>>>>Website Category Created<<<<<<<<<<<<<<<<<<<<<<<")
        return True

    def prepare_varients_and_attributes(self):
        _logger.info("Product Varients and attributes Import Starting at %s============================" %datetime.now().strftime('%H:%M:%S'))
        ProductTemplate = self.env['product.template'].sudo()
        ProductAttribute = self.env['product.attribute'].sudo()
        ProductAttributeValue = self.env['product.attribute.value'].sudo()
        ProductAttributeLine = self.env['product.template.attribute.line'].sudo()
        ProdTmplAttributeValueExtraPrice = self.env['product.template.attribute.value'].sudo()

        # file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        # file_path = file_path.split('/models')[0]
        file_path = self.get_module_path()
        if file_path:
            file_location = '/data/live_purchase_full.csv'
            file_location = file_path + file_location

            with open(file_location,'rU')as file:
                data = csv.DictReader(file)
                for row in data:
                    if row.get('Model') and row.get('Categories') and row.get('Desc'):
                        ProdTmpl = ProductTemplate.search([('default_code','=',row.get('Model'))])
                        if ProdTmpl:

                            attribute_name = " ".join(row.get('Categories').split())
                            value_name = " ".join(row.get('Desc').split())
                            current_attribute = self.env['product.attribute'].search([('name','=',attribute_name)])
                            if not current_attribute:
                                vals = {
                                    'name' : attribute_name,
                                    'display_type' : 'radio'
                                }
                                if attribute_name == 'Colour':
                                    vals.update({'display_type':'color'})
                                current_attribute = ProductAttribute.create(vals)
                            current_attr_value = ProductAttributeValue.search([('name','=',value_name),('attribute_id','=',current_attribute.id)])
                            if not current_attr_value:
                                vals = {
                                    'name' : value_name,
                                    'attribute_id' : current_attribute.id,
                                    'display_name' : value_name,
                                    'sequence' : 0 if row.get('Status') == 'Default Value' else 10
                                }
                                if current_attribute.name == 'Colour':
                                    vals.update({
                                        'html_color' : "#808080" if value_name=='Space Grey' else "#C0C0C0"
                                    })
                                current_attr_value = ProductAttributeValue.create(vals)

                            ProdAttrLine = ProductAttributeLine.search([('product_tmpl_id','=',ProdTmpl.id),('attribute_id','=',current_attribute.id)])
                            if ProdAttrLine:
                                current_line_value_ids = ProdAttrLine.value_ids.ids
                                if current_attr_value.id in current_line_value_ids:
                                    continue
                                else:
                                    current_line_value_ids.append(current_attr_value.id)
                                    ProdAttrLine.write({
                                        'value_ids': [(4,current_attr_value.id)]
                                    })
                                    ProdTmpl.write({'default_code':row.get('Model')})

                            else:
                                vals = {
                                    'product_tmpl_id' : ProdTmpl.id,
                                    'attribute_id' : current_attribute.id,
                                    'value_ids' : [(6, 0, [current_attr_value.id])]
                                }
                                ProductAttributeLine.create(vals)

            with open(file_location,'rU')as file:
                data = csv.DictReader(file)
                for row in data:
                    extra_line_price = row.get('ALP inc VAT')
                    if extra_line_price != 0:
                        ProdTmpl = ProductTemplate.search([('default_code', '=', row.get('Model'))])
                        if ProdTmpl:
                            attribute_name = " ".join(row.get('Categories').split())
                            current_attribute = self.env['product.attribute'].search([('name', '=', attribute_name)])
                            if current_attribute:
                                value_name = " ".join(row.get('Desc').split())
                                current_attr_value = ProductAttributeValue.search(
                                    [('name', '=', value_name), ('attribute_id', '=', current_attribute.id)])
                                if current_attr_value:
                                    extra_price_line = ProdTmplAttributeValueExtraPrice.search([('product_tmpl_id','=',ProdTmpl.id),('attribute_id','=',current_attribute.id),
                                                                             ('product_attribute_value_id','=',current_attr_value.id)])
                                    if extra_price_line:
                                        extra_price_line.write({'price_extra':extra_line_price})

        _logger.info("Product Varients and attributes Import Ending at %s=====================================" %datetime.now().strftime('%H:%M:%S'))
        return True


    # def assign_man_number(self):
    #
    #     # file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    #     # file_path = file_path.split('/models')[0]
    #     file_path = self.get_module_path()
    #     if file_path:
    #         file_location = '/data/MPN/imac_cto_export.csv'
    #         # file_location = '/data/MPN/imac_pro_cto_export.csv'
    #         # file_location = '/data/MPN/macbook_air_cto_export.csv'
    #         # file_location = '/data/MPN/macbook_pro_13_2019_cto_export.csv'
    #         # file_location = '/data/MPN/macbook_pro_16_2019_cto_export.csv'
    #         # file_location = '/data/MPN/mac_mini_cto.csv'
    #         # file_location = '/data/MPN/Mac_Pro_2019_cto_export.csv' [pending due to 12000 varieants]
    #         file_location = file_path + file_location
    #
    #         with open(file_location,'rU')as file:
    #             data = csv.DictReader(file)
    #             ProductProduct = self.env['product.product'].sudo()
    #
    #             for row in data:
    #                 imac_cto_export_domain = ["&","&","&","&","&","&","&","&",["product_template_attribute_value_ids.name","=",row.get('Processor')],["product_template_attribute_value_ids.name","=",row.get('Memory')],["product_template_attribute_value_ids.name","=",row.get('HDD')],["product_template_attribute_value_ids.name","=",row.get('Graphics')],["product_template_attribute_value_ids.name","=",row.get('Mouse and Trackpad')],["product_template_attribute_value_ids.name","=",row.get('Keyboard Options')],["product_template_attribute_value_ids.name","=",row.get('VESA Mount')],["product_template_attribute_value_ids.name","=",row.get('Power')],["product_template_attribute_value_ids.name","=",row.get('Colour')]]
    #                 # imac_pro_cto_export_domain = ["&","&","&","&","&","&","&",["product_template_attribute_value_ids.name","=",row.get('Processor')],["product_template_attribute_value_ids.name","=",row.get('Memory')],["product_template_attribute_value_ids.name","=",row.get('HDD')],["product_template_attribute_value_ids.name","=",row.get('Graphics')],["product_template_attribute_value_ids.name","=",row.get('Mouse and Trackpad')],["product_template_attribute_value_ids.name","=",row.get('Keyboard Options')],["product_template_attribute_value_ids.name","=",row.get('Power')],["product_template_attribute_value_ids.name","=",row.get('Colour')]]
    #                 # macbook_air_cto_export = ["&","&","&","&","&","&","&","&",["product_template_attribute_value_ids.name","=",row.get('Processor')],["product_template_attribute_value_ids.name","=",row.get('Memory')],["product_template_attribute_value_ids.name","=",row.get('HDD')],["product_template_attribute_value_ids.name","=",row.get('Graphics')],["product_template_attribute_value_ids.name","=",row.get('Touch')],["product_template_attribute_value_ids.name","=",row.get('Keyboard Options')],["product_template_attribute_value_ids.name","=",row.get('Display')],["product_template_attribute_value_ids.name","=",row.get('Power')],["product_template_attribute_value_ids.name","=",row.get('Colour')]]
    #                 # macbook_pro_13_2019_cto_export = ["&","&","&","&","&","&","&",["product_template_attribute_value_ids.name","=",row.get('Processor')],["product_template_attribute_value_ids.name","=",row.get('Memory')],["product_template_attribute_value_ids.name","=",row.get('HDD')],["product_template_attribute_value_ids.name","=",row.get('Graphics')],["product_template_attribute_value_ids.name","=",row.get('Touch Bar')],["product_template_attribute_value_ids.name","=",row.get('Keyboard Options')],["product_template_attribute_value_ids.name","=",row.get('Power')],["product_template_attribute_value_ids.name","=",row.get('Colour')]]
    #                 # macbook_pro_16_2019_cto_export = ["&","&","&","&","&","&",["product_template_attribute_value_ids.name","=",row.get('Processor')],["product_template_attribute_value_ids.name","=",row.get('Memory')],["product_template_attribute_value_ids.name","=",row.get('HDD')],["product_template_attribute_value_ids.name","=",row.get('Graphics')],["product_template_attribute_value_ids.name","=",row.get('Keyboard Options')],["product_template_attribute_value_ids.name","=",row.get('Power')],["product_template_attribute_value_ids.name","=",row.get('Colour')]]
    #                 # mac_mini_cto_domain = ["&","&","&","&","&","&","&","&",["product_template_attribute_value_ids.name","=",row.get('Processor')],["product_template_attribute_value_ids.name","=",row.get('Memory')],["product_template_attribute_value_ids.name","=",row.get('HDD')],["product_template_attribute_value_ids.name","=",row.get('Graphics')],["product_template_attribute_value_ids.name","=",row.get('Mouse and Trackpad')],["product_template_attribute_value_ids.name","=",row.get('Keyboard Options')],["product_template_attribute_value_ids.name","=",row.get('Ethernet')],["product_template_attribute_value_ids.name","=",row.get('Power')],["product_template_attribute_value_ids.name","=",row.get('Colour')]]
    #                 # Mac_Pro_2019_cto_export_domain = pending due to 12000 varieants
    #                 ProdProd = ProductProduct.search(imac_cto_export_domain)
    #                 if ProdProd and row.get('Manufacturer part no.') != row.get('Base model code'):
    #                     ProdTmpl_sku = ProdProd.product_tmpl_id.default_code if ProdProd.product_tmpl_id.default_code else ''
    #                     ProdProd.write({'default_code':row.get('Manufacturer part no.')})
    #                     if ProdTmpl_sku:
    #                         ProdProd.product_tmpl_id.write({'default_code' : ProdTmpl_sku})

    def get_dynamic_domain_values(self,product_name,row):
        domain = []
        if product_name == 'imac':
            domain = ["&", "&", "&", "&", "&", "&", "&", "&","&",["product_tmpl_id.default_code", "=", row.get('Base model code')],
                                      ["product_template_attribute_value_ids.name", "=", row.get('Processor')],
                                      ["product_template_attribute_value_ids.name", "=", row.get('Memory')],
                                      ["product_template_attribute_value_ids.name", "=", row.get('HDD')],
                                      ["product_template_attribute_value_ids.name", "=", row.get('Graphics')],
                                      ["product_template_attribute_value_ids.name", "=", row.get('Mouse and Trackpad')],
                                      ["product_template_attribute_value_ids.name", "=", row.get('Keyboard Options')],
                                      ["product_template_attribute_value_ids.name", "=", row.get('VESA Mount')],
                                      ["product_template_attribute_value_ids.name", "=", row.get('Power')],
                                      ["product_template_attribute_value_ids.name", "=", row.get('Colour')]]

        if product_name =='imac_pro':
            domain = ["&","&","&","&","&","&","&","&",["product_tmpl_id.default_code", "=", row.get('Base model code')],["product_template_attribute_value_ids.name","=",row.get('Processor')],["product_template_attribute_value_ids.name","=",row.get('Memory')],["product_template_attribute_value_ids.name","=",row.get('HDD')],["product_template_attribute_value_ids.name","=",row.get('Graphics')],["product_template_attribute_value_ids.name","=",row.get('Mouse and Trackpad')],["product_template_attribute_value_ids.name","=",row.get('Keyboard Options')],["product_template_attribute_value_ids.name","=",row.get('Power')],["product_template_attribute_value_ids.name","=",row.get('Colour')]]

        if product_name == 'macbook_air':
            domain = ["&", "&", "&", "&", "&", "&", "&", "&","&",["product_tmpl_id.default_code", "=", row.get('Base model code')],
             ["product_template_attribute_value_ids.name", "=", row.get('Processor')],
             ["product_template_attribute_value_ids.name", "=", row.get('Memory')],
             ["product_template_attribute_value_ids.name", "=", row.get('HDD')],
             ["product_template_attribute_value_ids.name", "=", row.get('Graphics')],
             ["product_template_attribute_value_ids.name", "=", row.get('Touch')],
             ["product_template_attribute_value_ids.name", "=", row.get('Keyboard Options')],
             ["product_template_attribute_value_ids.name", "=", row.get('Display')],
             ["product_template_attribute_value_ids.name", "=", row.get('Power')],
             ["product_template_attribute_value_ids.name", "=", row.get('Colour')]]

        if product_name == 'macbook_pro_13_2019':
            if row.get('Touch Bar') == 'YES':
                domain = ["&","&","&","&","&","&","&","&",["product_tmpl_id.default_code","=",row.get('Base model code')],["product_template_attribute_value_ids.name","=",row.get('Processor')],["product_template_attribute_value_ids.name","=",row.get('Memory')],["product_template_attribute_value_ids.name","=",row.get('HDD')],["product_template_attribute_value_ids.name","=",row.get('Graphics')],["product_template_attribute_value_ids.name","=",row.get('Touch Bar')],["product_template_attribute_value_ids.name","=",row.get('Keyboard Options')],["product_template_attribute_value_ids.name","=",row.get('Power')],["product_template_attribute_value_ids.name","=",row.get('Colour')]]
            else:
                domain = ["&", "&", "&", "&", "&", "&", "&",
                          ["product_tmpl_id.default_code", "=", row.get('Base model code')],
                          ["product_template_attribute_value_ids.name", "=", row.get('Processor')],
                          ["product_template_attribute_value_ids.name", "=", row.get('Memory')],
                          ["product_template_attribute_value_ids.name", "=", row.get('HDD')],
                          ["product_template_attribute_value_ids.name", "=", row.get('Graphics')],
                          ["product_template_attribute_value_ids.name", "=", row.get('Keyboard Options')],
                          ["product_template_attribute_value_ids.name", "=", row.get('Power')],
                          ["product_template_attribute_value_ids.name", "=", row.get('Colour')]]

        if product_name == 'macbook_pro_16_2019':
            domain = ["&","&","&","&","&","&","&",["product_tmpl_id.default_code","=",row.get('Base model code')],["product_template_attribute_value_ids.name","=",row.get('Processor')],["product_template_attribute_value_ids.name","=",row.get('Memory')],["product_template_attribute_value_ids.name","=",row.get('HDD')],["product_template_attribute_value_ids.name","=",row.get('Graphics')],["product_template_attribute_value_ids.name","=",row.get('Keyboard Options')],["product_template_attribute_value_ids.name","=",row.get('Power')],["product_template_attribute_value_ids.name","=",row.get('Colour')]]

        if product_name == 'mac_mini':
            domain = ["&","&","&","&","&","&","&","&","&",["product_tmpl_id.default_code","=",row.get('Base model code')],["product_template_attribute_value_ids.name","=",row.get('Processor')],["product_template_attribute_value_ids.name","=",row.get('Memory')],["product_template_attribute_value_ids.name","=",row.get('HDD')],["product_template_attribute_value_ids.name","=",row.get('Graphics')],["product_template_attribute_value_ids.name","=",row.get('Mouse and Trackpad')],["product_template_attribute_value_ids.name","=",row.get('Keyboard Options')],["product_template_attribute_value_ids.name","=",row.get('Ethernet')],["product_template_attribute_value_ids.name","=",row.get('Power')],["product_template_attribute_value_ids.name","=",row.get('Colour')]]

        if domain:
            return domain

    # def check_method(self):
    #     import csv
    #     file_path = self.get_module_path()
    #     # ===============================================
    #     # file_location = '/data/MPN/imac_cto_export.csv'
    #     # product_name = 'imac'
    #     # file_location = '/data/MPN/imac_pro_cto_export.csv'
    #     # product_name = 'imac_pro'
    #     # -----------file_location = '/data/MPN/macbook_air_cto_export.csv'
    #     # -----------product_name = 'macbook_air'
    #     # -----------file_location = '/data/MPN/macbook_pro_13_2019_cto_export.csv'
    #     # -----------product_name = 'macbook_pro_13_2019'
    #     # -----------file_location = '/data/MPN/macbook_pro_16_2019_cto_export.csv'
    #     # -----------product_name = 'macbook_pro_16_2019'
    #     file_location = '/data/MPN/mac_mini_cto.csv'
    #     product_name = 'mac_mini'
    #     file_location = file_path + file_location
    #     with open(file_location, 'rU')as file:
    #         data = csv.DictReader(file)
    #         ProductProduct = self.env['product.product'].sudo()
    #
    #         for row in data:
    #             domain = self.get_dynamic_domain_values(product_name=product_name, row=row)
    #             if domain:
    #                 for each_element in domain:
    #                     if len(each_element) > 1:
    #                         if '\xa0' in each_element[2]:
    #                             tmp = each_element[2].replace('\xa0', ' ')
    #                             tmp = " ".join(tmp.split())
    #                             each_element[2] = tmp
    #                 ProdProd = ProductProduct.search(domain)
    #                 print(ProdProd)
    #                 if ProdProd and row.get('Manufacturer part no.') != row.get('Base model code'):
    #                    ProdTmpl_sku = ProdProd.product_tmpl_id.default_code if ProdProd.product_tmpl_id.default_code else ''
    #                    ProdProd.write({'default_code':row.get('Manufacturer part no.')})
    #                    if ProdTmpl_sku:
    #                        ProdProd.product_tmpl_id.write({'default_code' : ProdTmpl_sku})

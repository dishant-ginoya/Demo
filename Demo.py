import csv
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductImport(models.TransientModel):
    _name = 'product.import'
    _description = 'Import Central Products'

    # File to import
    csv_file = fields.Binary('CSV File', required=True)
    file_name = fields.Char('File Name')

    @api.model
    def create_or_get_category(self, category_name):
        """Create or get a category by name."""
        category = self.env['product.category'].search([('name', '=', category_name)], limit=1)
        if not category:
            category = self.env['product.category'].create({'name': category_name})
        return category

    @api.model
    def create_or_get_uom(self, uom_name):
        """Create or get a UOM by name."""
        uom = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
        if not uom:
            uom = self.env['uom.uom'].create({'name': uom_name})
        return uom

    @api.model
    def create_or_get_attribute(self, attribute_name):
        """Create or get an attribute by name."""
        attribute = self.env['product.attribute'].search([('name', '=', attribute_name)], limit=1)
        if not attribute:
            attribute = self.env['product.attribute'].create({'name': attribute_name})
        return attribute

    @api.model
    def create_or_get_attribute_value(self, attribute, value_name):
        """Create or get an attribute value."""
        attribute_value = self.env['product.attribute.value'].search([
            ('name', '=', value_name),
            ('attribute_id', '=', attribute.id)
        ], limit=1)
        if not attribute_value:
            attribute_value = self.env['product.attribute.value'].create({
                'name': value_name,
                'attribute_id': attribute.id
            })
        return attribute_value

    @api.model
    def create_product(self, product_data):
        """Create a product and its variants."""
        # Create or get the category
        category = self.create_or_get_category(product_data['category'])

        # Create the product template (the base product)
        product_template = self.env['product.template'].create({
            'name': product_data['name'],
            'type': 'product',  # 'product' for physical products, 'service' for services
            'categ_id': category.id,
            'uom_id': product_data['uom'].id,
            'uom_po_id': product_data['uom'].id,  # Same UOM for purchase
        })

        # Create the product variant (if applicable)
        if product_data.get('variant_name'):
            self.create_variant(product_template, product_data)

        # Create packaging (if applicable)
        if product_data.get('packaging_name') and product_data.get('packaging_qty'):
            self.create_packaging(product_template, product_data)

        return product_template

    @api.model
    def create_variant(self, product_template, variant_data):
        """Create a variant for the product."""
        product_template.product_variant_ids.create({
            'product_tmpl_id': product_template.id,
            'name': variant_data['variant_name'],
            'default_code': variant_data.get('default_code', False),  # SKU code
            'price': variant_data['price'],
        })

    @api.model
    def create_packaging(self, product_template, packaging_data):
        """Create packaging for the product."""
        self.env['product.packaging'].create({
            'product_tmpl_id': product_template.id,
            'name': packaging_data['packaging_name'],
            'qty': packaging_data['packaging_qty'],
        })

    @api.model
    def create_price_list(self, product_template, price_data):
        """Create a price list for the product."""
        price_list = self.env['product.pricelist.item'].create({
            'product_tmpl_id': product_template.id,
            'fixed_price': price_data['price'],
            'applied_on': '1_product',  # Applies to product
        })
        return price_list

    @api.model
    def create_vendor_price_list(self, product_template, vendor_data):
        """Create a vendor-specific price list for the product."""
        vendor_price_list = self.env['product.supplierinfo'].create({
            'product_tmpl_id': product_template.id,
            'name': vendor_data['vendor'],  # Vendor record should already exist in the system
            'price': vendor_data['vendor_price'],
        })
        return vendor_price_list

    @api.model
    def import_products(self):
        """Main function to import products from a CSV file."""
        import base64
        import io

        # Decode the CSV file
        file_data = base64.b64decode(self.csv_file)
        csv_data = io.StringIO(file_data.decode('utf-8'))
        reader = csv.DictReader(csv_data)

        for row in reader:
            # Retrieve or create UOM
            uom = self.create_or_get_uom(row['uom'])

            # Product Data
            product_data = {
                'name': row['product_name'],
                'category': row['category'],
                'uom': uom,
                'variant_name': row.get('variant_name'),
                'price': float(row.get('price', 0)),
                'packaging_name': row.get('product_packaging_ids.name'),
                'packaging_qty': float(row.get('product_packaging_ids.qty', 1)),
            }

            # Create Product Template and Variant
            product_template = self.create_product(product_data)

            # Create attributes and values if applicable
            if row.get('attributes'):
                attributes = row['attributes'].split(',')  # Assuming comma-separated attributes
                for attribute_name in attributes:
                    attribute = self.create_or_get_attribute(attribute_name.strip())
                    value_name = row.get(f'{attribute_name.strip()}_value')
                    if value_name:
                        self.create_or_get_attribute_value(attribute, value_name.strip())

            # Create Price List
            price_data = {
                'price': float(row.get('price', 0)),
            }
            self.create_price_list(product_template, price_data)

            # Create Vendor Price List
            vendor_data = {
                'vendor': row.get('vendor_name'),
                'vendor_price': float(row.get('vendor_price', 0)),
            }
            self.create_vendor_price_list(product_template, vendor_data)

        return True






from odoo import models, fields, api
import csv
import base64
from io import StringIO

class ProductImport(models.TransientModel):
    _name = 'product.import'
    _description = 'Product Import'

    file_data = fields.Binary('File', required=True)
    file_name = fields.Char('File Name')

    def import_products(self):
        # Decode the file
        file_content = base64.b64decode(self.file_data)
        file_stream = StringIO(file_content.decode('utf-8'))

        # Parse CSV
        csv_reader = csv.DictReader(file_stream)

        for row in csv_reader:
            # Get or create category
            categ = self._get_or_create_category(row['categ_id'])

            # Get or create UOMs
            uom = self._get_or_create_uom(row['uom_id'])
            uom_po = self._get_or_create_uom(row['uom_po_id'])

            # Get or create attributes and attribute values
            attribute_ids = self._create_attributes_and_values(row)

            # Create product template
            template_vals = {
                'name': row['name'],
                'default_code': row['default_code'],
                'categ_id': categ.id,
                'uom_id': uom.id,
                'uom_po_id': uom_po.id,
                'description': row['Description'],
                'weight': float(row['weight']),
                'standard_price': float(row['standard_price']),
                'list_price': float(row['list_price']),
                'attribute_line_ids': [(0, 0, {'attribute_id': att[0], 'value_ids': [(6, 0, att[1])]} ) for att in attribute_ids],
            }
            product_template = self.env['product.template'].create(template_vals)

            # Create product variants (if any)
            self._create_variants(product_template, row)

            # Create price list entries and vendor price list records (if applicable)
            self._create_price_lists(product_template, row)
            self._create_vendor_price_lists(product_template, row)

            # Handle packaging
            self._create_packaging(product_template, row)

        return {'type': 'ir.actions.act_window_close'}

    def _get_or_create_category(self, categ_name):
        category = self.env['product.category'].search([('name', '=', categ_name)], limit=1)
        if not category:
            category = self.env['product.category'].create({'name': categ_name})
        return category

    def _get_or_create_uom(self, uom_name):
        uom = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
        if not uom:
            uom = self.env['uom.uom'].create({'name': uom_name})
        return uom

    def _create_attributes_and_values(self, row):
        attributes = []
        for i in range(1, 5):
            attribute_name = row.get(f'attribute_id{i}')
            if attribute_name:
                # Check if attribute exists, else create it
                attribute = self.env['product.attribute'].search([('name', '=', attribute_name)], limit=1)
                if not attribute:
                    attribute = self.env['product.attribute'].create({'name': attribute_name})

                # Get or create attribute values
                value_name = row.get(f'value_ids{i}')
                if value_name:
                    value = self.env['product.attribute.value'].search([('name', '=', value_name), ('attribute_id', '=', attribute.id)], limit=1)
                    if not value:
                        value = self.env['product.attribute.value'].create({'name': value_name, 'attribute_id': attribute.id})

                    attributes.append((attribute.id, [value.id]))

        return attributes

    def _create_variants(self, product_template, row):
        # If there are attribute lines, create variants
        if product_template.attribute_line_ids:
            product_template._create_variant_ids()

    def _create_price_lists(self, product_template, row):
        price_lists = row['Price list'].split(',')
        for price_list in price_lists:
            pl = self.env['product.pricelist'].search([('name', '=', price_list)], limit=1)
            if pl:
                self.env['product.pricelist.item'].create({
                    'product_tmpl_id': product_template.id,
                    'pricelist_id': pl.id,
                    'fixed_price': float(row['list_price']),
                    'min_quantity': 1,
                })

    def _create_vendor_price_lists(self, product_template, row):
        vendor_name = row['Vendors/Vendor']
        vendor_product_code = row['Vendors/Vendor Product Code']
        vendor_price = row['Vendors/Price']

        vendor = self.env['res.partner'].search([('name', '=', vendor_name)], limit=1)
        if vendor:
            self.env['product.supplierinfo'].create({
                'product_tmpl_id': product_template.id,
                'name': vendor.id,
                'product_code': vendor_product_code,
                'price': float(vendor_price),
            })

    def _create_packaging(self, product_template, row):
        packaging_vals = []
        for i in range(1, 4):
            packaging_name = row.get(f'Packaging{i}')
            packaging_qty = row.get(f'Packaging Contains{i}')
            if packaging_name and packaging_qty:
                packaging_vals.append((0, 0, {'name': packaging_name, 'qty': float(packaging_qty)}))
        if packaging_vals:
            product_template.write({'product_packaging_ids': packaging_vals})
            

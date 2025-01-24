# -*- coding: utf-8; -*-

import datetime
import decimal
from unittest.mock import patch

from wuttjamaican.testing import DataTestCase

from sideshow.batch import neworder as mod


class TestNewOrderBatchHandler(DataTestCase):

    def make_config(self, **kwargs):
        config = super().make_config(**kwargs)
        config.setdefault('wutta.model_spec', 'sideshow.db.model')
        config.setdefault('wutta.enum_spec', 'sideshow.enum')
        return config

    def make_handler(self):
        return mod.NewOrderBatchHandler(self.config)

    def tets_use_local_customers(self):
        handler = self.make_handler()

        # true by default
        self.assertTrue(handler.use_local_customers())

        # config can disable
        config.setdefault('sideshow.orders.use_local_customers', 'false')
        self.assertFalse(handler.use_local_customers())

    def tets_use_local_products(self):
        handler = self.make_handler()

        # true by default
        self.assertTrue(handler.use_local_products())

        # config can disable
        config.setdefault('sideshow.orders.use_local_products', 'false')
        self.assertFalse(handler.use_local_products())

    def tets_allow_unknown_products(self):
        handler = self.make_handler()

        # true by default
        self.assertTrue(handler.allow_unknown_products())

        # config can disable
        config.setdefault('sideshow.orders.allow_unknown_products', 'false')
        self.assertFalse(handler.allow_unknown_products())

    def test_autocomplete_customers_external(self):
        handler = self.make_handler()
        self.assertRaises(NotImplementedError, handler.autocomplete_customers_external,
                          self.session, 'jack')

    def test_autocomplete_cutomers_local(self):
        model = self.app.model
        handler = self.make_handler()

        # empty results by default
        self.assertEqual(handler.autocomplete_customers_local(self.session, 'foo'), [])

        # add a customer
        customer = model.LocalCustomer(full_name="Chuck Norris")
        self.session.add(customer)
        self.session.flush()

        # search for chuck finds chuck
        results = handler.autocomplete_customers_local(self.session, 'chuck')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {
            'value': customer.uuid.hex,
            'label': "Chuck Norris",
        })

        # search for sally finds nothing
        self.assertEqual(handler.autocomplete_customers_local(self.session, 'sally'), [])

    def test_set_customer(self):
        model = self.app.model
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        # customer starts blank
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()
        self.assertIsNone(batch.customer_id)
        self.assertIsNone(batch.local_customer)
        self.assertIsNone(batch.pending_customer)
        self.assertIsNone(batch.customer_name)
        self.assertIsNone(batch.phone_number)
        self.assertIsNone(batch.email_address)

        # pending, typical (nb. full name is automatic)
        handler.set_customer(batch, {
            'first_name': "Fred",
            'last_name': "Flintstone",
            'phone_number': '555-1234',
            'email_address': 'fred@mailinator.com',
        })
        self.assertIsNone(batch.customer_id)
        self.assertIsNone(batch.local_customer)
        self.assertIsInstance(batch.pending_customer, model.PendingCustomer)
        customer = batch.pending_customer
        self.assertEqual(customer.first_name, "Fred")
        self.assertEqual(customer.last_name, "Flintstone")
        self.assertEqual(customer.full_name, "Fred Flintstone")
        self.assertEqual(customer.phone_number, '555-1234')
        self.assertEqual(customer.email_address, 'fred@mailinator.com')
        self.assertEqual(batch.customer_name, "Fred Flintstone")
        self.assertEqual(batch.phone_number, '555-1234')
        self.assertEqual(batch.email_address, 'fred@mailinator.com')

        # pending, minimal
        last_customer = customer # save ref to prev record
        handler.set_customer(batch, {'full_name': "Wilma Flintstone"})
        self.assertIsNone(batch.customer_id)
        self.assertIsNone(batch.local_customer)
        self.assertIsInstance(batch.pending_customer, model.PendingCustomer)
        customer = batch.pending_customer
        self.assertIs(customer, last_customer)
        self.assertEqual(customer.full_name, "Wilma Flintstone")
        self.assertIsNone(customer.first_name)
        self.assertIsNone(customer.last_name)
        self.assertIsNone(customer.phone_number)
        self.assertIsNone(customer.email_address)
        self.assertEqual(batch.customer_name, "Wilma Flintstone")
        self.assertIsNone(batch.phone_number)
        self.assertIsNone(batch.email_address)

        # local customer
        local = model.LocalCustomer(full_name="Bam Bam",
                                    first_name="Bam", last_name="Bam",
                                    phone_number='555-4321')
        self.session.add(local)
        self.session.flush()
        handler.set_customer(batch, local.uuid.hex)
        self.session.flush()
        self.assertIsNone(batch.customer_id)
        # nb. pending customer does not get removed
        self.assertIsInstance(batch.pending_customer, model.PendingCustomer)
        self.assertIsInstance(batch.local_customer, model.LocalCustomer)
        customer = batch.local_customer
        self.assertEqual(customer.full_name, "Bam Bam")
        self.assertEqual(customer.first_name, "Bam")
        self.assertEqual(customer.last_name, "Bam")
        self.assertEqual(customer.phone_number, '555-4321')
        self.assertIsNone(customer.email_address)
        self.assertEqual(batch.customer_name, "Bam Bam")
        self.assertEqual(batch.phone_number, '555-4321')
        self.assertIsNone(batch.email_address)

        # local customer, not found
        mock_uuid = self.app.make_true_uuid()
        self.assertRaises(ValueError, handler.set_customer, batch, mock_uuid.hex)

        # external lookup not implemented
        self.config.setdefault('sideshow.orders.use_local_customers', 'false')
        self.assertRaises(NotImplementedError, handler.set_customer, batch, '42')

        # null
        handler.set_customer(batch, None)
        self.session.flush()
        self.assertIsNone(batch.customer_id)
        # nb. pending customer does not get removed
        self.assertIsInstance(batch.pending_customer, model.PendingCustomer)
        self.assertIsNone(batch.local_customer)
        self.assertIsNone(batch.customer_name)
        self.assertIsNone(batch.phone_number)
        self.assertIsNone(batch.email_address)

    def test_autocomplete_products_external(self):
        handler = self.make_handler()
        self.assertRaises(NotImplementedError, handler.autocomplete_products_external,
                          self.session, 'cheese')

    def test_autocomplete_products_local(self):
        model = self.app.model
        handler = self.make_handler()

        # empty results by default
        self.assertEqual(handler.autocomplete_products_local(self.session, 'foo'), [])

        # add a product
        product = model.LocalProduct(brand_name="Bragg's", description="Vinegar")
        self.session.add(product)
        self.session.flush()

        # search for vinegar finds product
        results = handler.autocomplete_products_local(self.session, 'vinegar')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {
            'value': product.uuid.hex,
            'label': "Bragg's Vinegar",
        })

        # search for brag finds product
        results = handler.autocomplete_products_local(self.session, 'brag')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {
            'value': product.uuid.hex,
            'label': "Bragg's Vinegar",
        })

        # search for juice finds nothing
        self.assertEqual(handler.autocomplete_products_local(self.session, 'juice'), [])

    def test_get_product_info_external(self):
        handler = self.make_handler()
        self.assertRaises(NotImplementedError, handler.get_product_info_external,
                          self.session, '07430500132')

    def test_get_product_info_local(self):
        model = self.app.model
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)
        local = model.LocalProduct(scancode='07430500132',
                                   brand_name='Bragg',
                                   description='Vinegar',
                                   size='32oz',
                                   case_size=12,
                                   unit_price_reg=decimal.Decimal('5.99'))
        self.session.add(local)
        self.session.flush()

        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)

        # typical, for local product
        info = handler.get_product_info_local(self.session, local.uuid.hex)
        self.assertEqual(info['product_id'], local.uuid.hex)
        self.assertEqual(info['scancode'], '07430500132')
        self.assertEqual(info['brand_name'], 'Bragg')
        self.assertEqual(info['description'], 'Vinegar')
        self.assertEqual(info['size'], '32oz')
        self.assertEqual(info['full_description'], 'Bragg Vinegar 32oz')
        self.assertEqual(info['case_size'], 12)
        self.assertEqual(info['unit_price_reg'], decimal.Decimal('5.99'))

        # error if no product_id
        self.assertRaises(ValueError, handler.get_product_info_local, self.session, None)

        # error if product not found
        mock_uuid = self.app.make_true_uuid()
        self.assertRaises(ValueError, handler.get_product_info_local, self.session, mock_uuid.hex)

    def test_add_item(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.assertEqual(len(batch.rows), 0)

        # pending, typical
        kw = dict(
            scancode='07430500001',
            brand_name='Bragg',
            description='Vinegar',
            size='1oz',
            case_size=12,
            unit_cost=decimal.Decimal('1.99'),
            unit_price_reg=decimal.Decimal('2.99'),
        )
        row = handler.add_item(batch, kw, 1, enum.ORDER_UOM_UNIT)
        # nb. this is the first row in batch
        self.assertEqual(len(batch.rows), 1)
        self.assertIs(batch.rows[0], row)
        self.assertIsNone(row.product_id)
        self.assertIsNone(row.local_product)
        product = row.pending_product
        self.assertIsInstance(product, model.PendingProduct)
        self.assertEqual(product.scancode, '07430500001')
        self.assertEqual(product.brand_name, 'Bragg')
        self.assertEqual(product.description, 'Vinegar')
        self.assertEqual(product.size, '1oz')
        self.assertEqual(product.case_size, 12)
        self.assertEqual(product.unit_cost, decimal.Decimal('1.99'))
        self.assertEqual(product.unit_price_reg, decimal.Decimal('2.99'))
        self.assertEqual(row.product_scancode, '07430500001')
        self.assertEqual(row.product_brand, 'Bragg')
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertEqual(row.product_size, '1oz')
        self.assertEqual(row.case_size, 12)
        self.assertEqual(row.unit_cost, decimal.Decimal('1.99'))
        self.assertEqual(row.unit_price_reg, decimal.Decimal('2.99'))
        self.assertEqual(row.unit_price_quoted, decimal.Decimal('2.99'))
        self.assertEqual(row.case_price_quoted, decimal.Decimal('35.88'))
        self.assertEqual(row.total_price, decimal.Decimal('2.99'))

        # pending, minimal
        row = handler.add_item(batch, {'description': "Tangerines"}, 1, enum.ORDER_UOM_UNIT)
        self.assertIsNone(row.product_id)
        self.assertIsNone(row.local_product)
        product = row.pending_product
        self.assertIsInstance(product, model.PendingProduct)
        self.assertIsNone(product.scancode)
        self.assertIsNone(product.brand_name)
        self.assertEqual(product.description, 'Tangerines')
        self.assertIsNone(product.size)
        self.assertIsNone(product.case_size)
        self.assertIsNone(product.unit_cost)
        self.assertIsNone(product.unit_price_reg)
        self.assertIsNone(row.product_scancode)
        self.assertIsNone(row.product_brand)
        self.assertEqual(row.product_description, 'Tangerines')
        self.assertIsNone(row.product_size)
        self.assertIsNone(row.case_size)
        self.assertIsNone(row.unit_cost)
        self.assertIsNone(row.unit_price_reg)
        self.assertIsNone(row.unit_price_quoted)
        self.assertIsNone(row.case_price_quoted)
        self.assertIsNone(row.total_price)

        # error if unknown products not allowed
        self.config.setdefault('sideshow.orders.allow_unknown_products', 'false')
        self.assertRaises(TypeError, handler.add_item, batch, kw, 1, enum.ORDER_UOM_UNIT)

        # local product
        local = model.LocalProduct(scancode='07430500002',
                                   description='Vinegar',
                                   size='2oz',
                                   unit_price_reg=2.99,
                                   case_size=12)
        self.session.add(local)
        self.session.flush()
        row = handler.add_item(batch, local.uuid.hex, 1, enum.ORDER_UOM_CASE)
        self.session.flush()
        self.session.refresh(row)
        self.session.refresh(local)
        self.assertIsNone(row.product_id)
        self.assertIsNone(row.pending_product)
        product = row.local_product
        self.assertIsInstance(product, model.LocalProduct)
        self.assertEqual(product.scancode, '07430500002')
        self.assertIsNone(product.brand_name)
        self.assertEqual(product.description, 'Vinegar')
        self.assertEqual(product.size, '2oz')
        self.assertEqual(product.case_size, 12)
        self.assertIsNone(product.unit_cost)
        self.assertEqual(product.unit_price_reg, decimal.Decimal('2.99'))
        self.assertEqual(row.product_scancode, '07430500002')
        self.assertIsNone(row.product_brand)
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertEqual(row.product_size, '2oz')
        self.assertEqual(row.case_size, 12)
        self.assertIsNone(row.unit_cost)
        self.assertEqual(row.unit_price_reg, decimal.Decimal('2.99'))
        self.assertEqual(row.unit_price_quoted, decimal.Decimal('2.99'))
        self.assertEqual(row.case_price_quoted, decimal.Decimal('35.88'))
        self.assertEqual(row.total_price, decimal.Decimal('35.88'))

        # local product, not found
        mock_uuid = self.app.make_true_uuid()
        self.assertRaises(ValueError, handler.add_item,
                          batch, mock_uuid.hex, 1, enum.ORDER_UOM_CASE)

        # external lookup not implemented
        self.config.setdefault('sideshow.orders.use_local_products', 'false')
        self.assertRaises(NotImplementedError, handler.add_item,
                          batch, '42', 1, enum.ORDER_UOM_CASE)

    def test_update_item(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.assertEqual(len(batch.rows), 0)

        # start with typical pending product
        kw = dict(
            scancode='07430500001',
            brand_name='Bragg',
            description='Vinegar',
            size='1oz',
            case_size=12,
            unit_cost=decimal.Decimal('1.99'),
            unit_price_reg=decimal.Decimal('2.99'),
        )
        row = handler.add_item(batch, kw, 1, enum.ORDER_UOM_CASE)
        self.assertIsNone(row.product_id)
        self.assertIsNone(row.local_product)
        product = row.pending_product
        self.assertIsInstance(product, model.PendingProduct)
        self.assertEqual(product.scancode, '07430500001')
        self.assertEqual(product.brand_name, 'Bragg')
        self.assertEqual(product.description, 'Vinegar')
        self.assertEqual(product.size, '1oz')
        self.assertEqual(product.case_size, 12)
        self.assertEqual(product.unit_cost, decimal.Decimal('1.99'))
        self.assertEqual(product.unit_price_reg, decimal.Decimal('2.99'))
        self.assertEqual(row.product_scancode, '07430500001')
        self.assertEqual(row.product_brand, 'Bragg')
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertEqual(row.product_size, '1oz')
        self.assertEqual(row.case_size, 12)
        self.assertEqual(row.unit_cost, decimal.Decimal('1.99'))
        self.assertEqual(row.unit_price_reg, decimal.Decimal('2.99'))
        self.assertEqual(row.unit_price_quoted, decimal.Decimal('2.99'))
        self.assertEqual(row.case_price_quoted, decimal.Decimal('35.88'))
        self.assertEqual(row.order_qty, 1)
        self.assertEqual(row.order_uom, enum.ORDER_UOM_CASE)
        self.assertEqual(row.total_price, decimal.Decimal('35.88'))

        # set pending, minimal
        handler.update_item(row, {'description': 'Vinegar'}, 1, enum.ORDER_UOM_UNIT)
        # self.session.flush()
        self.assertIsNone(row.product_id)
        self.assertIsNone(row.local_product)
        product = row.pending_product
        self.assertIsInstance(product, model.PendingProduct)
        self.assertIsNone(product.scancode)
        self.assertIsNone(product.brand_name)
        self.assertEqual(product.description, 'Vinegar')
        self.assertIsNone(product.size)
        self.assertIsNone(product.case_size)
        self.assertIsNone(product.unit_cost)
        self.assertIsNone(product.unit_price_reg)
        self.assertIsNone(row.product_scancode)
        self.assertIsNone(row.product_brand)
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertIsNone(row.product_size)
        self.assertIsNone(row.case_size)
        self.assertIsNone(row.unit_cost)
        self.assertIsNone(row.unit_price_reg)
        self.assertIsNone(row.unit_price_quoted)
        self.assertIsNone(row.case_price_quoted)
        self.assertEqual(row.order_qty, 1)
        self.assertEqual(row.order_uom, enum.ORDER_UOM_UNIT)
        self.assertIsNone(row.total_price)

        # start over, new row w/ local product
        local = model.LocalProduct(scancode='07430500002',
                                   description='Vinegar',
                                   size='2oz',
                                   unit_price_reg=3.99,
                                   case_size=12)
        self.session.add(local)
        self.session.flush()
        row = handler.add_item(batch, local.uuid.hex, 1, enum.ORDER_UOM_CASE)
        self.session.flush()
        self.session.refresh(row)
        self.session.refresh(local)
        self.assertIsNone(row.product_id)
        self.assertIsNone(row.pending_product)
        product = row.local_product
        self.assertIsInstance(product, model.LocalProduct)
        self.assertEqual(product.scancode, '07430500002')
        self.assertIsNone(product.brand_name)
        self.assertEqual(product.description, 'Vinegar')
        self.assertEqual(product.size, '2oz')
        self.assertEqual(product.case_size, 12)
        self.assertIsNone(product.unit_cost)
        self.assertEqual(product.unit_price_reg, decimal.Decimal('3.99'))
        self.assertEqual(row.product_scancode, '07430500002')
        self.assertIsNone(row.product_brand)
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertEqual(row.product_size, '2oz')
        self.assertEqual(row.case_size, 12)
        self.assertIsNone(row.unit_cost)
        self.assertEqual(row.unit_price_reg, decimal.Decimal('3.99'))
        self.assertEqual(row.unit_price_quoted, decimal.Decimal('3.99'))
        self.assertEqual(row.case_price_quoted, decimal.Decimal('47.88'))
        self.assertEqual(row.order_qty, 1)
        self.assertEqual(row.order_uom, enum.ORDER_UOM_CASE)
        self.assertEqual(row.total_price, decimal.Decimal('47.88'))

        # update w/ pending product
        handler.update_item(row, kw, 2, enum.ORDER_UOM_CASE)
        self.assertIsNone(row.product_id)
        self.assertIsNone(row.local_product)
        product = row.pending_product
        self.assertIsInstance(product, model.PendingProduct)
        self.assertEqual(product.scancode, '07430500001')
        self.assertEqual(product.brand_name, 'Bragg')
        self.assertEqual(product.description, 'Vinegar')
        self.assertEqual(product.size, '1oz')
        self.assertEqual(product.case_size, 12)
        self.assertEqual(product.unit_cost, decimal.Decimal('1.99'))
        self.assertEqual(product.unit_price_reg, decimal.Decimal('2.99'))
        self.assertEqual(row.product_scancode, '07430500001')
        self.assertEqual(row.product_brand, 'Bragg')
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertEqual(row.product_size, '1oz')
        self.assertEqual(row.case_size, 12)
        self.assertEqual(row.unit_cost, decimal.Decimal('1.99'))
        self.assertEqual(row.unit_price_reg, decimal.Decimal('2.99'))
        self.assertEqual(row.unit_price_quoted, decimal.Decimal('2.99'))
        self.assertEqual(row.case_price_quoted, decimal.Decimal('35.88'))
        self.assertEqual(row.order_qty, 2)
        self.assertEqual(row.order_uom, enum.ORDER_UOM_CASE)
        self.assertEqual(row.total_price, decimal.Decimal('71.76'))

        # update w/ pending, error if not allowed
        self.config.setdefault('sideshow.orders.allow_unknown_products', 'false')
        self.assertRaises(TypeError, handler.update_item, row, kw, 1, enum.ORDER_UOM_UNIT)

        # update w/ local product
        handler.update_item(row, local.uuid.hex, 1, enum.ORDER_UOM_CASE)
        self.assertIsNone(row.product_id)
        # nb. pending remains intact here
        self.assertIsNotNone(row.pending_product)
        product = row.local_product
        self.assertIsInstance(product, model.LocalProduct)
        self.assertEqual(product.scancode, '07430500002')
        self.assertIsNone(product.brand_name)
        self.assertEqual(product.description, 'Vinegar')
        self.assertEqual(product.size, '2oz')
        self.assertEqual(product.case_size, 12)
        self.assertIsNone(product.unit_cost)
        self.assertEqual(product.unit_price_reg, decimal.Decimal('3.99'))
        self.assertEqual(row.product_scancode, '07430500002')
        self.assertIsNone(row.product_brand)
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertEqual(row.product_size, '2oz')
        self.assertEqual(row.case_size, 12)
        self.assertIsNone(row.unit_cost)
        self.assertEqual(row.unit_price_reg, decimal.Decimal('3.99'))
        self.assertEqual(row.unit_price_quoted, decimal.Decimal('3.99'))
        self.assertEqual(row.case_price_quoted, decimal.Decimal('47.88'))
        self.assertEqual(row.order_qty, 1)
        self.assertEqual(row.order_uom, enum.ORDER_UOM_CASE)
        self.assertEqual(row.total_price, decimal.Decimal('47.88'))

        # update w/ local, not found
        mock_uuid = self.app.make_true_uuid()
        self.assertRaises(ValueError, handler.update_item,
                          batch, mock_uuid.hex, 1, enum.ORDER_UOM_CASE)

        # external lookup not implemented
        self.config.setdefault('sideshow.orders.use_local_products', 'false')
        self.assertRaises(NotImplementedError, handler.update_item,
                          row, '42', 1, enum.ORDER_UOM_CASE)

    def test_refresh_row(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.assertEqual(len(batch.rows), 0)

        # missing product
        row = handler.make_row(order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
        self.assertIsNone(row.status_code)
        handler.add_row(batch, row)
        self.assertEqual(row.status_code, row.STATUS_MISSING_PRODUCT)

        # missing order_qty
        row = handler.make_row(product_id=42, order_uom=enum.ORDER_UOM_UNIT)
        self.assertIsNone(row.status_code)
        handler.add_row(batch, row)
        self.assertEqual(row.status_code, row.STATUS_MISSING_ORDER_QTY)

        # refreshed from pending product (null price)
        product = model.PendingProduct(scancode='07430500132',
                                       brand_name='Bragg',
                                       description='Vinegar',
                                       size='32oz',
                                       created_by=user,
                                       status=enum.PendingProductStatus.PENDING)
        row = handler.make_row(pending_product=product, order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
        self.assertIsNone(row.status_code)
        handler.add_row(batch, row)
        self.assertEqual(row.status_code, row.STATUS_OK)
        self.assertIsNone(row.product_id)
        self.assertIs(row.pending_product, product)
        self.assertEqual(row.product_scancode, '07430500132')
        self.assertEqual(row.product_brand, 'Bragg')
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertEqual(row.product_size, '32oz')
        self.assertIsNone(row.case_size)
        self.assertIsNone(row.unit_cost)
        self.assertIsNone(row.unit_price_reg)
        self.assertIsNone(row.unit_price_quoted)
        self.assertIsNone(row.case_price_quoted)
        self.assertIsNone(row.total_price)

        # refreshed from pending product (zero price)
        product = model.PendingProduct(scancode='07430500132',
                                       brand_name='Bragg',
                                       description='Vinegar',
                                       size='32oz',
                                       unit_price_reg=0,
                                       created_by=user,
                                       status=enum.PendingProductStatus.PENDING)
        row = handler.make_row(pending_product=product, order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
        self.assertIsNone(row.status_code)
        handler.add_row(batch, row)
        self.assertEqual(row.status_code, row.STATUS_OK)
        self.assertIsNone(row.product_id)
        self.assertIs(row.pending_product, product)
        self.assertEqual(row.product_scancode, '07430500132')
        self.assertEqual(row.product_brand, 'Bragg')
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertEqual(row.product_size, '32oz')
        self.assertIsNone(row.case_size)
        self.assertIsNone(row.unit_cost)
        self.assertEqual(row.unit_price_reg, 0)
        self.assertEqual(row.unit_price_quoted, 0)
        self.assertIsNone(row.case_price_quoted)
        self.assertEqual(row.total_price, 0)

        # refreshed from pending product (normal, case)
        product = model.PendingProduct(scancode='07430500132',
                                       brand_name='Bragg',
                                       description='Vinegar',
                                       size='32oz',
                                       case_size=12,
                                       unit_cost=decimal.Decimal('3.99'),
                                       unit_price_reg=decimal.Decimal('5.99'),
                                       created_by=user,
                                       status=enum.PendingProductStatus.PENDING)
        row = handler.make_row(pending_product=product, order_qty=2, order_uom=enum.ORDER_UOM_CASE)
        self.assertIsNone(row.status_code)
        handler.add_row(batch, row)
        self.assertEqual(row.status_code, row.STATUS_OK)
        self.assertIsNone(row.product_id)
        self.assertIs(row.pending_product, product)
        self.assertEqual(row.product_scancode, '07430500132')
        self.assertEqual(row.product_brand, 'Bragg')
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertEqual(row.product_size, '32oz')
        self.assertEqual(row.case_size, 12)
        self.assertEqual(row.unit_cost, decimal.Decimal('3.99'))
        self.assertEqual(row.unit_price_reg, decimal.Decimal('5.99'))
        self.assertEqual(row.unit_price_quoted, decimal.Decimal('5.99'))
        self.assertEqual(row.case_price_quoted, decimal.Decimal('71.88'))
        self.assertEqual(row.total_price, decimal.Decimal('143.76'))

        # refreshed from pending product (sale price)
        product = model.PendingProduct(scancode='07430500132',
                                       brand_name='Bragg',
                                       description='Vinegar',
                                       size='32oz',
                                       case_size=12,
                                       unit_cost=decimal.Decimal('3.99'),
                                       unit_price_reg=decimal.Decimal('5.99'),
                                       created_by=user,
                                       status=enum.PendingProductStatus.PENDING)
        row = handler.make_row(pending_product=product, order_qty=2, order_uom=enum.ORDER_UOM_CASE,
                               unit_price_sale=decimal.Decimal('5.19'),
                               sale_ends=datetime.datetime(2099, 1, 1))
        self.assertIsNone(row.status_code)
        handler.add_row(batch, row)
        self.assertEqual(row.status_code, row.STATUS_OK)
        self.assertIsNone(row.product_id)
        self.assertIs(row.pending_product, product)
        self.assertEqual(row.product_scancode, '07430500132')
        self.assertEqual(row.product_brand, 'Bragg')
        self.assertEqual(row.product_description, 'Vinegar')
        self.assertEqual(row.product_size, '32oz')
        self.assertEqual(row.case_size, 12)
        self.assertEqual(row.unit_cost, decimal.Decimal('3.99'))
        self.assertEqual(row.unit_price_reg, decimal.Decimal('5.99'))
        self.assertEqual(row.unit_price_sale, decimal.Decimal('5.19'))
        self.assertEqual(row.sale_ends, datetime.datetime(2099, 1, 1))
        self.assertEqual(row.unit_price_quoted, decimal.Decimal('5.19'))
        self.assertEqual(row.case_price_quoted, decimal.Decimal('62.28'))
        self.assertEqual(row.total_price, decimal.Decimal('124.56'))

    def test_remove_row(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.assertEqual(len(batch.rows), 0)

        kw = dict(
            scancode='07430500132',
            brand_name='Bragg',
            description='Vinegar',
            size='32oz',
            case_size=12,
            unit_cost=decimal.Decimal('3.99'),
            unit_price_reg=decimal.Decimal('5.99'),
            created_by=user,
        )
        row = handler.add_item(batch, kw, 1, enum.ORDER_UOM_CASE)
        self.session.add(row)
        self.session.flush()
        self.assertEqual(batch.row_count, 1)
        self.assertEqual(row.total_price, decimal.Decimal('71.88'))
        self.assertEqual(batch.total_price, decimal.Decimal('71.88'))

        handler.do_remove_row(row)
        self.assertEqual(batch.row_count, 0)
        self.assertEqual(batch.total_price, 0)

    def test_do_delete(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        # make batch w/ pending customer
        customer = model.PendingCustomer(full_name="Fred Flintstone",
                                         status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)
        batch = handler.make_batch(self.session, created_by=user, pending_customer=customer)
        self.session.add(batch)
        self.session.commit()

        # deleting batch will also delete pending customer
        self.assertIn(batch, self.session)
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
        handler.do_delete(batch, user)
        self.session.commit()
        self.assertNotIn(batch, self.session)
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 0)

        # make new pending customer, assigned to batch + order
        customer = model.PendingCustomer(full_name="Wilma Flintstone",
                                         status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)
        batch = handler.make_batch(self.session, created_by=user, pending_customer=customer)
        self.session.add(batch)
        order = model.Order(order_id=77, created_by=user, pending_customer=customer)
        self.session.add(order)
        self.session.flush()

        # deleting batch will *not* delete pending customer
        self.assertIn(batch, self.session)
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
        handler.do_delete(batch, user)
        self.session.commit()
        self.assertNotIn(batch, self.session)
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)

        # make new pending product, associate w/ batch + order
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        handler.set_customer(batch, {'full_name': "Jack Black"})
        row = handler.add_item(batch, dict(
            scancode='07430500132',
            brand_name='Bragg',
            description='Vinegar',
            size='32oz',
            unit_price_reg=5.99,
        ), 1, enum.ORDER_UOM_UNIT)
        product = row.pending_product
        order = model.Order(order_id=33, created_by=user)
        item = model.OrderItem(pending_product=product, order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_INITIATED)
        order.items.append(item)
        self.session.add(order)
        self.session.flush()

        # deleting batch will *not* delete pending product
        self.assertIn(batch, self.session)
        self.assertEqual(self.session.query(model.PendingProduct).count(), 1)
        handler.do_delete(batch, user)
        self.session.commit()
        self.assertNotIn(batch, self.session)
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)

        # make another batch w/ same pending product
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        row = handler.make_row(pending_product=product,
                               order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
        handler.add_row(batch, row)

        # also delete the associated order
        self.session.delete(order)
        self.session.flush()

        # deleting this batch *will* delete pending product
        self.assertIn(batch, self.session)
        self.assertEqual(self.session.query(model.PendingProduct).count(), 1)
        handler.do_delete(batch, user)
        self.session.commit()
        self.assertNotIn(batch, self.session)
        self.assertEqual(self.session.query(model.PendingProduct).count(), 0)

    def test_get_effective_rows(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        # make batch w/ different status rows
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        # STATUS_MISSING_PRODUCT
        row = handler.make_row(order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
        handler.add_row(batch, row)
        self.session.add(row)
        self.session.flush()
        # STATUS_MISSING_ORDER_QTY
        row = handler.make_row(product_id=42, order_qty=0, order_uom=enum.ORDER_UOM_UNIT)
        handler.add_row(batch, row)
        self.session.add(row)
        self.session.flush()
        # STATUS_OK
        row = handler.add_item(batch, {'scancode': '07430500132'}, 1, enum.ORDER_UOM_UNIT)
        self.session.flush()

        # only 1 effective row
        rows = handler.get_effective_rows(batch)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.status_code, row.STATUS_OK)

    def test_why_not_execute(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()

        reason = handler.why_not_execute(batch)
        self.assertEqual(reason, "Must assign the customer")

        batch.customer_id = 42
        batch.customer_name = "Fred Flintstone"

        reason = handler.why_not_execute(batch)
        self.assertEqual(reason, "Customer phone number is required")

        batch.phone_number = '555-1234'

        reason = handler.why_not_execute(batch)
        self.assertEqual(reason, "Must add at least one valid item")

        kw = dict(
            scancode='07430500132',
            brand_name='Bragg',
            description='Vinegar',
            size='32oz',
            case_size=12,
            unit_cost=decimal.Decimal('3.99'),
            unit_price_reg=decimal.Decimal('5.99'),
            created_by=user,
        )
        row = handler.add_item(batch, kw, 1, enum.ORDER_UOM_CASE)
        self.session.add(row)
        self.session.flush()

        reason = handler.why_not_execute(batch)
        self.assertIsNone(reason)

    def test_make_local_customer(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        # make a typical batch
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        handler.set_customer(batch, {'first_name': "John", 'last_name': "Doe",
                                     'phone_number': '555-1234'})
        row = handler.add_item(batch, dict(
            scancode='07430500132',
            brand_name='Bragg',
            description='Vinegar',
            size='32oz',
            unit_price_reg=5.99,
        ), 1, enum.ORDER_UOM_UNIT)
        self.session.flush()

        # making local customer removes pending customer
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
        self.assertEqual(self.session.query(model.LocalCustomer).count(), 0)
        self.assertIsNotNone(batch.pending_customer)
        self.assertIsNone(batch.local_customer)
        handler.make_local_customer(batch)
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 0)
        self.assertEqual(self.session.query(model.LocalCustomer).count(), 1)
        self.assertIsNone(batch.pending_customer)
        local = batch.local_customer
        self.assertIsNotNone(local)
        self.assertEqual(local.first_name, "John")
        self.assertEqual(local.last_name, "Doe")
        self.assertEqual(local.full_name, "John Doe")
        self.assertEqual(local.phone_number, '555-1234')

        # trying again does nothing
        handler.make_local_customer(batch)
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 0)
        self.assertEqual(self.session.query(model.LocalCustomer).count(), 1)
        self.assertIsNone(batch.pending_customer)
        local = batch.local_customer
        self.assertIsNotNone(local)
        self.assertEqual(local.first_name, "John")
        self.assertEqual(local.last_name, "Doe")
        self.assertEqual(local.full_name, "John Doe")
        self.assertEqual(local.phone_number, '555-1234')

        # make another typical batch
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        handler.set_customer(batch, {'first_name': "Chuck", 'last_name': "Norris",
                                     'phone_number': '555-1234'})
        row = handler.add_item(batch, dict(
            scancode='07430500132',
            brand_name='Bragg',
            description='Vinegar',
            size='32oz',
            unit_price_reg=5.99,
        ), 1, enum.ORDER_UOM_UNIT)
        self.session.flush()

        # should do nothing if local customers disabled
        with patch.object(handler, 'use_local_customers', return_value=False):
            self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
            self.assertEqual(self.session.query(model.LocalCustomer).count(), 1)
            self.assertIsNotNone(batch.pending_customer)
            self.assertIsNone(batch.local_customer)
            handler.make_local_customer(batch)
            self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
            self.assertEqual(self.session.query(model.LocalCustomer).count(), 1)
            self.assertIsNotNone(batch.pending_customer)
            self.assertIsNone(batch.local_customer)

        # but things happen by default, since local customers enabled
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
        self.assertEqual(self.session.query(model.LocalCustomer).count(), 1)
        self.assertIsNotNone(batch.pending_customer)
        self.assertIsNone(batch.local_customer)
        handler.make_local_customer(batch)
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 0)
        self.assertEqual(self.session.query(model.LocalCustomer).count(), 2)
        self.assertIsNone(batch.pending_customer)
        local = batch.local_customer
        self.assertIsNotNone(local)
        self.assertEqual(local.first_name, "Chuck")
        self.assertEqual(local.last_name, "Norris")
        self.assertEqual(local.full_name, "Chuck Norris")
        self.assertEqual(local.phone_number, '555-1234')

    def test_make_local_products(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        # make a batch w/ one each local + pending products
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        handler.set_customer(batch, {'full_name': "John Doe"})
        local = model.LocalProduct(scancode='07430500116',
                                   brand_name='Bragg',
                                   description='Vinegar',
                                   size='16oz',
                                   unit_price_reg=3.59)
        self.session.add(local)
        self.session.flush()
        row1 = handler.add_item(batch, local.uuid.hex, 1, enum.ORDER_UOM_UNIT)
        row2 = handler.add_item(batch, dict(
            scancode='07430500132',
            brand_name='Bragg',
            description='Vinegar',
            size='32oz',
            unit_price_reg=5.99,
        ), 1, enum.ORDER_UOM_UNIT)
        self.session.flush()

        # making local product removes pending product
        self.assertEqual(self.session.query(model.PendingProduct).count(), 1)
        self.assertEqual(self.session.query(model.LocalProduct).count(), 1)
        self.assertIsNotNone(row2.pending_product)
        self.assertIsNone(row2.local_product)
        handler.make_local_products(batch, batch.rows)
        self.assertEqual(self.session.query(model.PendingProduct).count(), 0)
        self.assertEqual(self.session.query(model.LocalProduct).count(), 2)
        self.assertIsNone(row2.pending_product)
        local = row2.local_product
        self.assertIsNotNone(local)
        self.assertEqual(local.scancode, '07430500132')
        self.assertEqual(local.brand_name, 'Bragg')
        self.assertEqual(local.description, 'Vinegar')
        self.assertEqual(local.size, '32oz')
        self.assertEqual(local.unit_price_reg, decimal.Decimal('5.99'))

        # trying again does nothing
        handler.make_local_products(batch, batch.rows)
        self.assertEqual(self.session.query(model.PendingProduct).count(), 0)
        self.assertEqual(self.session.query(model.LocalProduct).count(), 2)
        self.assertIsNone(row2.pending_product)
        local = row2.local_product
        self.assertIsNotNone(local)
        self.assertEqual(local.scancode, '07430500132')
        self.assertEqual(local.brand_name, 'Bragg')
        self.assertEqual(local.description, 'Vinegar')
        self.assertEqual(local.size, '32oz')
        self.assertEqual(local.unit_price_reg, decimal.Decimal('5.99'))

        # make another typical batch
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        handler.set_customer(batch, {'full_name': "Chuck Norris"})
        row = handler.add_item(batch, dict(
            scancode='07430500164',
            brand_name='Bragg',
            description='Vinegar',
            size='64oz',
            unit_price_reg=9.99,
        ), 1, enum.ORDER_UOM_UNIT)
        self.session.flush()

        # should do nothing if local products disabled
        with patch.object(handler, 'use_local_products', return_value=False):
            self.assertEqual(self.session.query(model.PendingProduct).count(), 1)
            self.assertEqual(self.session.query(model.LocalProduct).count(), 2)
            self.assertIsNotNone(row.pending_product)
            self.assertIsNone(row.local_product)
            handler.make_local_products(batch, batch.rows)
            self.assertEqual(self.session.query(model.PendingProduct).count(), 1)
            self.assertEqual(self.session.query(model.LocalProduct).count(), 2)
            self.assertIsNotNone(row.pending_product)
            self.assertIsNone(row.local_product)

        # but things happen by default, since local products enabled
        self.assertEqual(self.session.query(model.PendingProduct).count(), 1)
        self.assertEqual(self.session.query(model.LocalProduct).count(), 2)
        self.assertIsNotNone(row.pending_product)
        self.assertIsNone(row.local_product)
        handler.make_local_products(batch, batch.rows)
        self.assertEqual(self.session.query(model.PendingProduct).count(), 0)
        self.assertEqual(self.session.query(model.LocalProduct).count(), 3)
        self.assertIsNone(row.pending_product)
        local = row.local_product
        self.assertIsNotNone(local)
        self.assertEqual(local.scancode, '07430500164')
        self.assertEqual(local.brand_name, 'Bragg')
        self.assertEqual(local.description, 'Vinegar')
        self.assertEqual(local.size, '64oz')
        self.assertEqual(local.unit_price_reg, decimal.Decimal('9.99'))

    def test_make_new_order(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        batch = handler.make_batch(self.session, created_by=user,
                                   customer_id=42, customer_name="John Doe")
        self.session.add(batch)
        kw = dict(
            scancode='07430500132',
            brand_name='Bragg',
            description='Vinegar',
            size='32oz',
            case_size=12,
            unit_cost=decimal.Decimal('3.99'),
            unit_price_reg=decimal.Decimal('5.99'),
            created_by=user,
        )
        row = handler.add_item(batch, kw, 1, enum.ORDER_UOM_CASE)
        self.session.add(row)
        self.session.flush()

        order = handler.make_new_order(batch, [row], user=user)
        self.assertIsInstance(order, model.Order)
        self.assertIs(order.created_by, user)
        self.assertEqual(order.customer_id, 42)
        self.assertEqual(order.customer_name, "John Doe")
        self.assertEqual(len(order.items), 1)
        item = order.items[0]
        self.assertEqual(item.product_scancode, '07430500132')
        self.assertEqual(item.product_brand, 'Bragg')
        self.assertEqual(item.product_description, 'Vinegar')
        self.assertEqual(item.product_size, '32oz')
        self.assertEqual(item.case_size, 12)
        self.assertEqual(item.unit_cost, decimal.Decimal('3.99'))
        self.assertEqual(item.unit_price_reg, decimal.Decimal('5.99'))

    def test_set_initial_item_status(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()
        user = model.User(username='barney')
        item = model.OrderItem()
        self.assertIsNone(item.status_code)
        self.assertEqual(len(item.events), 0)
        handler.set_initial_item_status(item, user)
        self.assertEqual(item.status_code, enum.ORDER_ITEM_STATUS_READY)
        self.assertEqual(len(item.events), 2)
        self.assertEqual(item.events[0].type_code, enum.ORDER_ITEM_EVENT_INITIATED)
        self.assertEqual(item.events[1].type_code, enum.ORDER_ITEM_EVENT_READY)

    def test_execute(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)

        batch = handler.make_batch(self.session, created_by=user,
                                   customer_id=42, customer_name="John Doe")
        self.session.add(batch)
        kw = dict(
            scancode='07430500132',
            brand_name='Bragg',
            description='Vinegar',
            size='32oz',
            case_size=12,
            unit_cost=decimal.Decimal('3.99'),
            unit_price_reg=decimal.Decimal('5.99'),
            created_by=user,
        )
        row = handler.add_item(batch, kw, 1, enum.ORDER_UOM_CASE)
        self.session.add(row)
        self.session.flush()

        order = handler.execute(batch, user=user)
        self.assertIsInstance(order, model.Order)
        self.assertIs(order.created_by, user)
        self.assertEqual(order.customer_id, 42)
        self.assertEqual(order.customer_name, "John Doe")
        self.assertEqual(len(order.items), 1)
        item = order.items[0]
        self.assertEqual(item.product_scancode, '07430500132')
        self.assertEqual(item.product_brand, 'Bragg')
        self.assertEqual(item.product_description, 'Vinegar')
        self.assertEqual(item.product_size, '32oz')
        self.assertEqual(item.case_size, 12)
        self.assertEqual(item.unit_cost, decimal.Decimal('3.99'))
        self.assertEqual(item.unit_price_reg, decimal.Decimal('5.99'))

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, alessandrofmartini@gmail.com

import unittest
import Tkinter as tk
import os
import sys
sys.path.append('../')
from odoo_builder import OdooBuilder, UserError
import mock


class TestOdooBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = OdooBuilder(None)
        f_file = open('foo', 'w')
        f_file.write('foo\nbar\nbaz')
        f_file.close()
        obj_file = open('bar', 'w')
        obj_file.write('foo %s baz')
        obj_file.close()

    @mock.patch('tkMessageBox.showerror')
    def test_UserError(self, mock_showerror):
        UserError('foo')
        self.assertTrue(mock_showerror.called)

    def test_get_format(self):
        foobarbaz = self.builder.get_format('foo')
        self.assertEqual(foobarbaz, 'foo\nbar\nbaz')

    def test_obj_builder(self):
        text = self.builder.obj_builder('bar', 'bar')
        self.assertEqual(text, 'foo bar baz')

    def test_required_fields(self):
        # TEST FOR FAIL
        error = "The following fields crashed:\n"
        error += '* Module Name.\n'
        error += '* User Name.\n'
        error_dict = {'status': False, 'message': error}
        self.assertEqual(self.builder.check_required_fields(), error_dict)
        # TEST FOR SUCCESS
        self.builder.module_name_entry.insert(0, 'foo')
        self.builder.user_name_entry.insert(0, 'bar')
        self.assertTrue(self.builder.check_required_fields()['status'])

    @mock.patch('os.mkdir')
    def test_assure_path_non_existing(self, mock_mkdir):
        path = ['super/hyper/non/existin/path/to/nowhere']
        self.builder.assure_path(path)
        self.assertTrue(mock_mkdir.called)

    @mock.patch('os.mkdir')
    def test_assure_path_exist(self, mock_mkdir):
        path = [os.curdir]
        self.builder.assure_path(path)
        self.assertFalse(mock_mkdir.called)

    def test_create_paths(self):
        cwd = os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))) + '/tests'

        self.builder.module_name_entry.insert(0, 'baz')
        self.builder.user_name_entry.insert(0, 'bar')
        self.builder.path_entry.delete(0, tk.END)
        self.builder.path_entry.insert(0, cwd)
        paths = self.builder.create_paths()
        self.assertTrue(os.path.exists(cwd + '/baz/models'))
        self.assertTrue(os.path.exists(cwd + '/baz/views'))
        self.assertTrue(os.path.exists(cwd + '/baz/static/description'))
        created_paths = {
            'module_root': cwd + '/baz',
            'models': cwd + '/baz/models',
            'views': cwd + '/baz/views',
            'static': cwd + '/baz/static',
            'description': cwd + '/baz/static/description',
        }
        self.assertEqual(paths, created_paths)

    @mock.patch('odoo_builder.UserError')
    def test_create_paths_esle(self, mock_showerror):
        self.builder.module_name_entry.insert(0, 'baz')
        self.builder.user_name_entry.insert(0, 'bar')
        self.builder.path_entry.delete(0, tk.END)
        self.builder.path_entry.insert(0, 'if/this/path/exists/this/will/fail')
        paths_else = self.builder.create_paths()
        self.assertFalse(paths_else)
        self.assertTrue(mock_showerror.called)

    def test_get_module_name(self):
        self.builder.module_name_entry.insert(0, 'nome.do_ modulo')
        names = self.builder.get_module_name()
        right_names = {
            'class': 'NomeDoModulo',
            'object': 'nome.do.modulo',
            'py_file': 'nome_do_modulo',
            'xml': 'nome_do_modulo.xml',
        }
        self.assertEqual(names, right_names)

    def test_get_inherits(self):
        self.builder.inheritance_entry.insert(
            0, 'account.account, models.models, product.product, res.partner')
        right_inherits = {
            'depends': ['models', 'account', 'product'],
            'inherits': ['account.account', 'models.models', 'product.product',
                         'res.partner'],
            'class': ['account_account', 'models_models', 'res_partner',
                      'product_product', ]
        }
        self.assertEqual(self.builder.get_inherits(), right_inherits)

    def test_get_depends(self):
        self.builder.depends_entry.insert(
            0, 'account.invoice, product.template, sale.sale')
        depends = ['account.invoice', 'product.template', 'sale.sale']
        self.assertEqual(self.builder.get_depends(), depends)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

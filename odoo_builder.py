# -*- coding: utf-8 -*-

import os
from os.path import exists
from os.path import isfile
from os.path import join
from shutil import copyfile
import Tkinter as tk
import tkMessageBox
import tkFileDialog
from os import listdir
import re


def UserError(message):
    tkMessageBox.showerror('Erro', message)


class OdooBuilder(tk.Tk):

    # Inicia o app
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def get_format(self, obj_format):
        text = """"""
        f = open(obj_format, 'r')
        for i in f:
                text += (i.rstrip() + '\n')
        return text

    def obj_builder(self, format, *args):
        """Builds the classes based on the file 'class', receives as many parameters
           are specified in that file, on their order"""

        obj_format = self.get_format(format)
        return obj_format % args

    def check_required_fields(self):
        """Checks if the required fields (path, module name, user name) are
           correctly filled, if not it returns a string with the errors"""
        path = str(self.path_entry.get())
        module_name = str(self.module_name_entry.get())
        user = str(self.user_name_entry.get())
        error_upper = "The following fields crashed:\n"
        errors = ''
        if not path or path == '':
            errors += "* Module Path.\n"
        if not exists(path):
            errors += "* This path doesn't exists.\n"
        if not module_name or module_name == '':
            errors += "* Module Name.\n"
        if not user or user == '':
            errors += "* User Name.\n"
        if len(errors) == 0:
            return {'status': True}
        else:
            return {'status': False, 'message': error_upper + errors}

    def assure_path(self, paths):
        for path in paths:
            if not exists(path):
                os.mkdir(path)

    def create_paths(self):
        if self.check_required_fields()['status']:
            name = str(self.module_name_entry.get().lower().
                       replace(' ', '_'))
            path = str(self.path_entry.get())
            if not exists(path):
                os.mkdir(path)
            module_root = path + '/' + name
            models = module_root + '/models'
            views = module_root + '/views'
            static = module_root + '/static'
            description = static + '/description'
            path_list = [module_root, models, views, static, description]
            self.assure_path(path_list)
            return {'module_root': module_root, 'models': models,
                    'views': views, 'static': static,
                    'description': description}
        else:
            UserError(self.check_required_fields()['message'])
            return False

    def build_models(self):
        path = self.path_entry.get() + '/' + self.get_module_name()['py_file']\
            + '/models/'
        user = self.user_name_entry.get().title()
        if not exists(path):
            os.mkdir(path)
        class_new = self.get_module_name()['py_file']
        class_new_file = open(path + '/' + class_new + '.py', 'w')
        class_new_file.write(self.obj_builder(
            'class_name', user, class_new.replace('_', ' ').title().
            replace(' ', ''), class_new.replace('_', '.')))
        class_new_file.close()
        for i in self.get_inherits()['class']:
            class_ = open(path + '/' + i + '.py', 'w')
            class_.write(self.obj_builder(
                'class_inherit', user, i.replace('_', ' ').title().
                replace(' ', ''), i.replace('_', '.')))
            class_.close()

    def build_manifest(self):
        path = self.path_entry.get() + '/' +\
            self.get_module_name()['py_file']
        data_path = self.path_entry.get() + '/' +\
            self.get_module_name()['py_file'] + '/views'
        user = self.user_name_entry.get().title()
        if self.summary_entry.get() != '':
            summary = self.summary_entry.get()
        else:
            summary = ''
        if self.category_entry.get() != '':
            category = self.category_entry.get()
        else:
            category = ''
        module_name = self.get_module_name()['object'].replace('.', ' ').\
            title()
        if self.get_depends() != '' and\
                self.get_inherits()['depends'] != '':
                depends = self.get_depends() +\
                    self.get_inherits()['depends']
        if self.get_depends() != '' and\
                self.get_inherits()['depends'] == '':
                depends = self.get_depends()
        if self.get_depends() == '' and\
                self.get_inherits()['depends'] != '':
                depends = self.get_inherits()['depends']
        depends = list(set(depends))
        data = ['/views/' + f for f in listdir(data_path) if
                isfile(join(data_path, f)) if f.endswith('.xml')]
        if self.wizard.get():
            data += ['/wizard/' + self.get_module_name()['py_file'] +
                     '_wizard.xml']
        manifest = self.obj_builder('manifest', user, module_name, summary,
                                    category, depends, data)
        opnrp_file = open(path + '/__manifest__.py', 'w')
        opnrp_file.write(manifest)
        opnrp_file.close()

    def build_static(self):
        icon = os.path.dirname(os.path.abspath(__file__)) + '/icon.png'
        description = self.path_entry.get() + '/' +\
            self.get_module_name()['py_file'] + '/static/description/'
        copyfile(icon, description + '/icon.png')
        module = self.get_module_name()['object'].replace('.', ' ').title()
        category = self.category_entry.get().title()
        description_entry = self.description_entry.get('0.0', tk.END)
        index = open('index', 'r')
        index = index.read() % (module, category, description_entry)
        index_file = open(description + '/index.html', 'w')
        index_file.write(index)
        index_file.close()

    def built_init_module(self):
        path = self.path_entry.get() + '/' +\
            self.get_module_name()['py_file']
        user = self.user_name_entry.get().title()
        init = open(path + '/__init__.py', 'w')
        init_text = """\
# -*- coding: utf-8 -*-
# © 2016 %s, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from . import models""" % user
        if not self.wizard.get():
            init.write(init_text)
        else:
            init.write(init_text + '\nfrom . import wizard\n')
        init.close()

    def build_views(self):
        path = self.path_entry.get() + '/' + self.get_module_name()['py_file']\
            + '/views/'
        if not exists(path):
            os.mkdir(path)
        new_view = self.get_module_name()['py_file']
        for i in self.get_inherits()['class'] + [new_view]:
            view_id = self.get_module_name()['py_file'] + '_' + i +\
                '_form_view'
            view_name = view_id.replace('_', '.')
            view = open(path + '/' + i + '.xml', 'w')
            view.write(self.obj_builder(
                'view', view_id, view_name))
            view.close()

    def build_init_local(self, local):
        path = self.path_entry.get() + '/' +\
            self.get_module_name()['py_file'] + local
        user = self.user_name_entry.get().title()
        init_head = """\
# -*- coding: utf-8 -*-
# © 2016 %s, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
\n""" % user
        models = [f for f in listdir(path) if
                  isfile(join(path, f)) if f.endswith('.py')]
        for i in models:
            init_head += "from . import %s\n" % i.replace('.py', '')
        init = open(path + '/__init__.py', 'w')
        init.write(init_head)
        init.close()

    def build_wizard_py(self):
        path = self.path_entry.get() + '/' +\
            self.get_module_name()['py_file'] + '/wizard'
        user = self.user_name_entry.get().title()
        wizard_class = self.get_module_name()['class']
        wizard_object = self.get_module_name()['object']
        os.mkdir(path)
        py_wizard = self.obj_builder('wizard_py', user, wizard_class,
                                     wizard_object)
        wizard_py = open(path + '/' + self.get_module_name()['py_file'] +
                         '.py', 'w')
        wizard_py.write(py_wizard)
        wizard_py.close()
        self.build_init_local('/wizard')

    def build_wizard_xml(self):
        path = self.path_entry.get() + '/' +\
            self.get_module_name()['py_file'] + '/wizard'
        if not exists(path):
            os.mkdir(path)
        wizard_xml = path + '/' + self.get_module_name()['py_file'] + '_wizard'
        wizard_id = self.get_module_name()['py_file'] + '_wizard'
        wizard_name = wizard_id.replace('_', '.')
        wizard_model = (self.get_module_name()['py_file'] + '.view').\
            replace('_', '.')
        action_id = (self.get_module_name()['py_file'] + '_action')
        wizard_content = self.obj_builder('wizard_xml', wizard_id, wizard_name,
                                          wizard_model, action_id)
        wizard = open(wizard_xml + '.xml', 'w')
        wizard.write(wizard_content)
        wizard.close()

    def build_wizard(self):
        if self.wizard.get():
            self.build_wizard_py()
            self.build_wizard_xml()

    def create_module(self):
        if self.create_paths():
            self.build_models()
            self.build_views()
            self.build_manifest()
            self.built_init_module()
            self.build_init_local('/models')
            self.build_static()
            self.build_static()
            self.build_wizard()
            if self.check_success():
                tkMessageBox.showinfo('Succes!', 'Module created succesfully.')
                self.destroy()
            else:
                tkMessageBox.showerror('Erro!', 'Problem found during module \
creation. Please, try again.')

    def get_module_name(self):
        module_name = str(self.module_name_entry.get())
        module_class = module_name.replace('.', ' ').title().replace(' ', '')
        module_objetct = module_name.lower().replace(' ', '.')
        module_file_py = module_name.lower().replace(' ', '_')
        module_file_xml = module_name.lower().replace(' ', '_') + '.xml'
        return {
            'class': module_class, 'object': module_objetct,
            'py_file': module_file_py, 'xml': module_file_xml
        }

    def get_inherits(self):
        """Receives a string with the inherits of the module, returns a dict with
            with the inherits objects and the dependences"""
        if self.inheritance_entry.get() != '':
            inherit_entry = self.inheritance_entry.get().split(',')
            inherit_list = [i.strip() for i in inherit_entry]
            depend_list = list(set([i.split('.')[0] for i in inherit_list if
                                   i.split('.')[0] != 'res']))
            class_list = list(set(
                [i.strip().replace('.', '_') for i in inherit_entry]))
            return {'depends': depend_list, 'inherits': inherit_list,
                    'class': class_list}
        else:
            return {'depends': [], 'inherits': [],
                    'class': []}

    def get_depends(self):
        """Receives a string with the dependences and returns
           a list of dependences"""
        # depends = self.dependence_entry.split(',')
        depends = [i.strip() for i in self.depends_entry.get().split(',')]
        return depends

    def show_help_inheritance(self):
        inherit_help_message = """\
Modules that you module will use.
Format: <object1>, <object2>, ...
Eg.: product.template, sale.contact, ..."""
        tkMessageBox.showinfo('Inheritance', inherit_help_message)

    def show_help_depends(self):
        dep_help_message = """Fill this field with the modules that yor module \
will depends, separated by commas.\nEg.: sale, contact, porduct, ..."""
        tkMessageBox.showinfo('Dependence', dep_help_message)

    def show_help_description(self):
            desc_help_message = """Fill this field with your module description \
that will go in the index.html file."""
            tkMessageBox.showinfo('Description', desc_help_message)

    def show_help_category(self):
        desc_help_message = """To what category this module belongs.
Eg.: Sales or Project ..."""
        tkMessageBox.showinfo('Description', desc_help_message)

    def chose_dir(self):
        pathdir = tkFileDialog.askdirectory(title="Chose the dir")
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, pathdir)

    def clear(self):
        """Clear the user entries"""
        self.path_entry.delete(0, tk.END)
        self.module_name_entry.delete(0, tk.END)
        self.user_name_entry.delete(0, tk.END)
        self.depends_entry.delete(0, tk.END)
        self.summary_entry.delete(0, tk.END)
        self.inheritance_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.description_entry.delete('0.0', tk.END)
        self.wizard_create.deselect()
        self.path_entry.focus_set()

    def loop_exists(self, *args):
        """Receives a list of strings, and check to see if the path that they
           represent exists"""
        check = True
        for arg in args:
            check = check and exists(arg)
        return check

    def check_success(self):
        """Checks to assure that the paths were created"""
        success = True
        module_name = self.module_name_entry.get().lower().replace(' ', '_')
        module_name = re.sub('[^A-Za-z0-9-_]', '', module_name)
        path = self.path_entry.get()
        mod_init = path + '/' + module_name + '/models/__init__.py'
        icon = path + '/' + module_name + '/static/description/icon.png'
        xml = path + '/' + module_name + '/views/%s.xml' % module_name
        init = path + '/' + module_name + '/' + '__init__.py'
        manifest = path + '/' + module_name + '/' + '__manifest__.py'
        if self.wizard.get():
            wizard = path + '/' + module_name + '/wizard'
            success = self.loop_exists(path, mod_init, icon, xml, init,
                                       manifest, wizard)
        else:
            success = self.loop_exists(path, mod_init, icon, xml, init,
                                       manifest)
        return success

    def initialize(self):
        """Creates the app window"""
        self.grid()

        self.path_label = tk.Label(self, text="Module Path: ")
        self.path_entry = tk.Entry(self, bd=5, bg='light slate blue')
        self.path_chose_dir = tk.Button(self, text='...', bg='blue',
                                        fg='white',
                                        command=self.chose_dir)
        self.path_label.grid(row=0, column=0)
        self.path_entry.grid(row=0, column=1)
        self.path_chose_dir.grid(row=0, column=2)
        self.path_entry.insert(0, os.path.dirname(os.path.abspath(__file__)))
        # sets the current directory as default

        # Label and entry for the module name
        self.module_name_label = tk.Label(self, text="Module Name: ")
        self.module_name_entry = tk.Entry(self, bd=5, bg='light slate blue')
        self.module_name_label.grid(row=1, column=0)
        self.module_name_entry.grid(row=1, column=1)

        # Label and entry for the user name
        self.user_name_label = tk.Label(self, text="User Name: ")
        self.user_name_entry = tk.Entry(self, bd=5, bg='light slate blue')
        self.user_name_label.grid(row=2, column=0)
        self.user_name_entry.grid(row=2, column=1)

        self.inheritance_label = tk.Label(self, text="Inheritance: ")
        self.inheritance_entry = tk.Entry(self, bd=5)
        self.inheritance_help = tk.Button(self, text='?', bg='blue',
                                          fg='white',
                                          command=self.show_help_inheritance)
        self.inheritance_label.grid(row=3, column=0)
        self.inheritance_entry.grid(row=3, column=1)
        self.inheritance_help.grid(row=3, column=2)

        self.depends_label = tk.Label(self, text="Dependence: ")
        self.depends_entry = tk.Entry(self, bd=5)
        self.depends_help = tk.Button(self, text='?', bg='blue',
                                      fg='white',
                                      command=self.show_help_depends)
        self.depends_label.grid(row=4, column=0)
        self.depends_entry.grid(row=4, column=1)
        self.depends_help.grid(row=4, column=2)

        self.summary_label = tk.Label(self, text="Summary: ")
        self.summary_entry = tk.Entry(self, bd=5)
        self.summary_label.grid(row=5, column=0)
        self.summary_entry.grid(row=5, column=1)

        self.category_label = tk.Label(self, text="Category: ")
        self.category_entry = tk.Entry(self, bd=5)
        self.category_help = tk.Button(self, text='?', bg='blue',
                                       fg='white',
                                       command=self.show_help_category)
        self.category_label.grid(row=6, column=0)
        self.category_entry.grid(row=6, column=1)
        self.category_help.grid(row=6, column=2)

        self.description_label = tk.Label(self, text="Description: ")
        self.description_entry = tk.Text(self, bd=5)
        self.description_entry.config(height=4, width=23)
        self.description_help = tk.Button(self, text='?', bg='blue',
                                          fg='white',
                                          command=self.show_help_description)
        self.description_label.grid(row=0, column=5)
        self.description_entry.grid(row=0, column=6, rowspan=7, sticky='NS')
        self.description_help.grid(row=0, column=7)

        self.create_bt = tk.Button(self, text="Create", bg="red",
                                   command=self.create_module)
        self.create_bt.grid(row=7, column=8)
        self.cancel = tk.Button(self, text="Cancel",
                                command=lambda: self.destroy())
        self.cancel.grid(row=7, column=0)
        self.clear = tk.Button(
            self, text="Clear", command=self.clear)
        self.clear.grid(row=5, column=8)

        self.wizard = tk.IntVar()
        self.wizard_create = tk.Checkbutton(self, text='Create Wizard',
                                            variable=self.wizard)
        self.wizard_create.grid(row=7, column=6)

        self.grid_columnconfigure(0, weight=1)


def center(win):
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center
    This function was taken from stack overflow:
    http://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
    Author: Honest Abe (http://stackoverflow.com/users/1217270/honest-abe)
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

if __name__ == "__main__":

    app = OdooBuilder(None)
    app.title('Odoo Module Builder')
    app.resizable(False, False)
    img = tk.PhotoImage(file='icon.png')
    app.tk.call('wm', 'iconphoto', app._w, img)
    center(app)
    app.mainloop()

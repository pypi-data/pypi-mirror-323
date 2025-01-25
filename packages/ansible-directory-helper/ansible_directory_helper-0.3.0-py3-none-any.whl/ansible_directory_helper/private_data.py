import os
from shutil import rmtree
from .inventory_file import InventoryFile
from .env_directory import EnvDirectory


class PrivateData:

    DEFAULT_INVENTORY_PATH = os.path.join(
        'inventory',
        'hosts'
    )

    DEFAULT_ENV_PATH = os.path.join(
        'env'
    )

    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.init_dir()
        self.init_inventory(PrivateData.DEFAULT_INVENTORY_PATH)
        self.init_env(PrivateData.DEFAULT_ENV_PATH)


    def init_dir(self):
        try:
            os.makedirs(self.dir_path)
        except FileExistsError:
            pass


    def cleanup_dir(self):
        rmtree(self.dir_path)


    def get_dir_path(self):
        return self.dir_path


    def init_inventory(self, inventory_file_path):
        self.inventory_file = InventoryFile(os.path.join(
            self.get_dir_path(),
            inventory_file_path
        ))


    def init_env(self, env_path):
        self.env_directory = EnvDirectory(os.path.join(
            self.get_dir_path(),
            env_path
        ))


    def set_extravar(self, varname, value):
        self.env_directory.set_extravar(varname, value)


    def write_env(self):
        self.env_directory.write()


    def add_inventory_groups(self, groups):
        self.inventory_file.add_groups(groups)


    def add_inventory_host(self, host, group=None, port=None):
        self.inventory_file.add_host(host, group, port)


    def set_inventory_ansible_user(self, host, username):
        self.inventory_file.set_ansible_user(host, username)


    def write_inventory(self):
        self.inventory_file.write()

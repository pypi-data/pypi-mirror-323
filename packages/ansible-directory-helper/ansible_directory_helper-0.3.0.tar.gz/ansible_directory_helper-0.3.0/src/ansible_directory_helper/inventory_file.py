import os
import yaml
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager

class InventoryFile():

    def __init__(self, file_path):
        self.file_path = file_path
        self.inventory_manager = InventoryManager(
            loader=DataLoader(),
            parse=False
        )
        self._init_directory()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self._close_file_handle()


    def _init_directory(self):
        try:
            os.makedirs(os.path.abspath(
                os.path.dirname(self.file_path)
            ))
        except FileExistsError:
            pass


    def _open_file_handle(self):
        self.file_handle = open(self.file_path, 'w')


    def _close_file_handle(self):
        try:
            self.file_handle.close()
        except AttributeError:
            pass


    def get_inventory_dict(self):
        ret_dict = {}
        groups = self.inventory_manager.get_groups_dict()
        for group in groups.keys():
            ret_dict[group] = {'hosts': {}}
            hosts = self.inventory_manager.get_hosts(group)
            for host in hosts:
                ret_dict[group]['hosts'][host.address] = {
                    key: val for key, val in host.vars.items()
                }
                if host.address in ['localhost', '127.0.0.1']:
                    ret_dict[group]['hosts'][host.address][
                        'ansible_connection'
                    ] = 'local'
        return ret_dict


    def write(self):
        self._open_file_handle()
        self.file_handle.write(
            yaml.dump(
                self.get_inventory_dict()
            )
        )
        self._close_file_handle()


    def add_groups(self, groups):
        if isinstance(groups, str):
            groups = [groups]

        for group in groups:
            self.add_group(group)


    def add_group(self, group):
        self.inventory_manager.add_group(group)


    def add_host(self, host, group=None, port=None):
        self.inventory_manager.add_host(host, group, port)


    def set_variable(self, host, varname, value):
        self.inventory_manager._inventory.set_variable(host, varname, value)


    def set_ansible_user(self, host, username):
        self.set_variable(host, 'ansible_user', username)

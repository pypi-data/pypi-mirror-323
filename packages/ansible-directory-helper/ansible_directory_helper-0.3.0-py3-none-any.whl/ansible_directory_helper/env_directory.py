import os
import yaml


class EnvDirectory:

    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.extravars = {}
        self._init_directory()


    def _init_directory(self):
        try:
            os.makedirs(os.path.abspath(
                self.dir_path
            ))
        except FileExistsError:
            pass


    def set_extravar(self, varname, value):
        self.extravars[varname] = value


    def write(self):
        files_to_write = [
            # 'envvars',
            'extravars',
            # 'passwords',
            # 'cmdline',
            # 'settings',
            # 'ssh_key',
        ]
        for f in files_to_write:
            getattr(self, 'write_{}'.format(f))()


    def write_envvars(self):
        pass


    def write_extravars(self):
        with open(
            os.path.join(
                self.dir_path,
                'extravars'
            ),
            'w'
        ) as f:
            f.write(yaml.dump(self.extravars))


    def write_passwords(self):
        pass


    def write_cmdline(self):
        pass


    def write_settings(self):
        pass


    def write_ssh_key(self):
        pass

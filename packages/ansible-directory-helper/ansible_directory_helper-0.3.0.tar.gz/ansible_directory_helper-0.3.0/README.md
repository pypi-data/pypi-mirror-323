### About

This is a small helper library to make it easier to supply different variables to the
Ansible Runner library, specifically its _Input Directory Hierarchy_.

I am building this primarily to help me with [Lampsible](https://github.com/saint-hilaire/lampsible)
and [Docksible](https://github.com/saint-hilaire/docksible), but anyone who is working with
Ansible Runner might find this useful.

### Installing

Install with Pip: `python -m pip install ansible-directory-helper`

### Usage

If you are using Ansible Runner to develop tools to automate server installations, you likely
have many dynamic variables, including but not limited to the system users and host addresses
of your remote servers (_inventory_, in Ansible's parlance), and numerous other variables
that your playbooks might expect during runtime.
Ansible Runner expects these variables to be present in the so called
_Input Directory Hierarchy_, a predefined directory structure on your local file system.
To avoid the hassle of managing these files and directories yourself, you can use this
library, which essentially manages this directory structure for you.

Example:

```python
# my_automation_tool.py

from ansible_runner import Runner, RunnerConfig
from ansible_directory_helper.private_data import PrivateData

private_data_dir = './.my-tool/tmp'
project_dir = './my-tool/src/project'

private_data_obj = PrivateData(private_data_dir)

private_data_obj.add_inventory_groups([
    'group1',
    'group2',
])
private_data_obj.add_inventory_host('host1.example.com', 'group1')
private_data_obj.add_inventory_host('host2.example.com', 'group2')
private_data_obj.set_inventory_ansible_user('host1.example.com', 'user1')
private_data_obj.set_inventory_ansible_user('host2.example.com', 'user2')
private_data_obj.write_inventory()

private_data_obj.set_extravar('some_string', 'Hello, World!')
private_data_obj.set_extravar('some_list', ['Hello', 'World'])
private_data_obj.set_extravar('some_dict', {'Hello': 'World'})
private_data_obj.set_extravar('some_none', None)
private_data_obj.write_env()


# Now the files for inventory and extravars are in the exact location and format in which
# Ansible Runner expects them to be, so you can easily
# configure Runner by simply passing the private_data_dir - all the required
# configuration will work.

rc = RunnerConfig(
    private_data_dir=private_data_dir,
    project_dir=project_dir,
    playbook='my-playbook.yml'
)

rc.prepare()
r = Runner(config=rc)
r.run()

# Do this to delete the private_data_dir from your filesystem.
# This is important because it contains sensitive data.
private_data_obj.cleanup_dir()

```


### Running unit tests

```
python -m unittest
```

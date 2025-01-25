import os
import yaml
import unittest
from ansible_directory_helper.private_data import PrivateData


class TestPrivateData(unittest.TestCase):

    def setUp(self):
        self.TEST_PRIVATE_DATA_DIR = os.path.join(
            'tmp-private-data'
        )
        self.TEST_ENV_DIR = os.path.join(
            self.TEST_PRIVATE_DATA_DIR,
            'env'
        )
        self.TEST_INVENTORY_DIR = os.path.join(
            self.TEST_PRIVATE_DATA_DIR,
            'inventory'
        )
        self.EXPECTED_EXTRAVARS = {
            'test_none': None,
            'test_zero': 0,
            'test_string_0': '',
            'test_string': 'test_val',
            'test_list_0': [],
            'test_list_1': [
                'test_val_1',
                'test_val_2',
            ],
            'test_dict_0': {},
            'test_dict_1': {
                'k1': 'v1',
                'k2': 'v2',
            }
        }
        self.EXPECTED_INVENTORY = {
            'all': {'hosts': {}},
            'ungrouped': {'hosts': {}},
            'group1': {
                'hosts': {
                    'host1.example.com': {
                        'ansible_user': 'user1',
                        'inventory_dir': None,
                        'inventory_file': None,
                    },
                },
            },
            'group2': {
                'hosts': {
                    'host2.example.com': {
                        'ansible_user': 'user2',
                        'inventory_dir': None,
                        'inventory_file': None,
                    },
                },
            },
        }
        self.EXPECTED_LOCAL_INVENTORY = {
            'all': {'hosts': {}},
            'ungrouped': {'hosts': {}},
            'group1': {
                'hosts': {
                    'localhost': {
                        'ansible_user': 'user1',
                        'inventory_dir': None,
                        'inventory_file': None,
                        'ansible_connection': 'local',
                    },
                },
            },
            'group2': {
                'hosts': {
                    '127.0.0.1': {
                        'ansible_user': 'user2',
                        'inventory_dir': None,
                        'inventory_file': None,
                        'ansible_connection': 'local',
                    },
                },
            },
        }
        self.private_data = PrivateData(self.TEST_PRIVATE_DATA_DIR)


    def tearDown(self):
        self.private_data.cleanup_dir()


    def test_extravars(self):
        for k, v in self.EXPECTED_EXTRAVARS.items():
            self.private_data.set_extravar(k, v)

        self.private_data.write_env()

        with open(
            os.path.join(
                self.TEST_ENV_DIR,
                'extravars'
            ),
            'r'
        ) as stream:
            self.assertEqual(
                yaml.safe_load(stream),
                self.EXPECTED_EXTRAVARS
            )


    def test_inventory(self):
        self.private_data.add_inventory_groups([
            'group1',
            'group2',
        ])
        self.private_data.add_inventory_host('host1.example.com', 'group1')
        self.private_data.add_inventory_host('host2.example.com', 'group2')
        self.private_data.set_inventory_ansible_user('host1.example.com', 'user1')
        self.private_data.set_inventory_ansible_user('host2.example.com', 'user2')

        self.private_data.write_inventory()

        with open(
            os.path.join(
                self.TEST_INVENTORY_DIR,
                'hosts'
            ), 'r'
        ) as f:
            self.assertEqual(
                yaml.safe_load(f),
                self.EXPECTED_INVENTORY
            )


    def test_inventory_localhost(self):
        self.private_data.add_inventory_groups([
            'group1',
            'group2',
        ])
        self.private_data.add_inventory_host('localhost', 'group1')
        self.private_data.add_inventory_host('127.0.0.1', 'group2')
        self.private_data.set_inventory_ansible_user('localhost', 'user1')
        self.private_data.set_inventory_ansible_user('127.0.0.1', 'user2')

        self.private_data.write_inventory()

        with open(
            os.path.join(
                self.TEST_INVENTORY_DIR,
                'hosts'
            ), 'r'
        ) as f:
            self.assertEqual(
                yaml.safe_load(f),
                self.EXPECTED_LOCAL_INVENTORY
            )



if __name__ == '__main__':
    unittest.main()

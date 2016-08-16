#!/usr/bin/python3

from nose.tools import *
from amazonia.classes.block_devices import Bdm
from amazonia.classes.block_devices_config import BlockDevicesConfig


def test_block_device_mappings():
    title = 'StackAsg'
    block_devices_config = [
        {'device_name': '/dev/xvda',
         'ebs_volume_size': '15',
         'ebs_volume_type': 'gp2',
         'ebs_encrypted': False,
         'ebs_snapshot_id': '',
         'virtual_name': False},
        {'device_name': '/dev/xvda2',
         'ebs_volume_size': '15',
         'ebs_volume_type': 'gp2',
         'ebs_encrypted': False,
         'ebs_snapshot_id': 'snapshot_123',
         'virtual_name': False},
        {'device_name': '/dev/sda1',
         'ebs_volume_size': '',
         'ebs_volume_type': '',
         'ebs_encrypted': False,
         'ebs_snapshot_id': '',
         'virtual_name': True},
        {'device_name': '/dev/sda2',
         'ebs_volume_size': '15',
         'ebs_volume_type': 'gp2',
         'ebs_encrypted': False,
         'ebs_snapshot_id': '',
         'virtual_name': False}
    ]

    test_bdm = Bdm(title, block_devices_config)
    assert_equals(type(test_bdm), Bdm)

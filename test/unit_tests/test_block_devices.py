#!/usr/bin/python3

from amazonia.classes.block_devices import Bdm
from amazonia.classes.block_devices_config import BlockDevicesConfig
from nose.tools import *


def test_block_device_mappings():
    title = 'StackAsg'
    block_devices_config = [
        BlockDevicesConfig(device_name='/dev/xvda',
                           ebs_volume_size='15',
                           ebs_volume_type='gp2',
                           ebs_encrypted=False,
                           ebs_snapshot_id=None,
                           virtual_name=False),
        BlockDevicesConfig(device_name='/dev/xvda2',
                           ebs_volume_size='15',
                           ebs_volume_type='gp2',
                           ebs_encrypted=False,
                           ebs_snapshot_id='snapshot_123',
                           virtual_name=False),
        BlockDevicesConfig(device_name='/dev/sda1',
                           ebs_volume_size=None,
                           ebs_volume_type=None,
                           ebs_encrypted=False,
                           ebs_snapshot_id=None,
                           virtual_name=True),
        BlockDevicesConfig(device_name='/dev/sda2',
                           ebs_volume_size='15',
                           ebs_volume_type='gp2',
                           ebs_encrypted=False,
                           ebs_snapshot_id=None,
                           virtual_name=False)
    ]

    test_bdm = Bdm(title, block_devices_config)
    assert_equals(type(test_bdm), Bdm)

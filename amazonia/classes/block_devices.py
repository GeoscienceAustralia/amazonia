#!/usr/bin/python3

from troposphere.autoscaling import EBSBlockDevice, BlockDeviceMapping


class Bdm(object):
    def __init__(self, title, block_devices_config):
        """
        Class to add custom block device mappings for multiple disks
        AWS Cloud Formation links:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-launchconfig-blockdev-mapping.html
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-launchconfig-blockdev-template.html
        Troposphere links:
        https://github.com/cloudtools/troposphere/blob/master/troposphere/autoscaling.py
        https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param title: Title to append to device names in template
        :param block_devices_config: List of config for devices to add ot the instance/asg
        :return Block Devices Mapping for ecc instances or autoscaling groups
        """
        self.trop_bdm = []
        self.bdm = self.block_device_mappings(title, block_devices_config)

    def block_device_mappings(self, title, block_devices_config):
        virtual_count = 0
        for n, block_device in enumerate(block_devices_config):
            bdm = BlockDeviceMapping('{0}BlockDevice{1}'.format(title, n),
                                     DeviceName=block_device['device_name'])

            if block_devices_config[n]['virtual_name']:
                bdm.VirtualName = 'ephemeral{0}'.format(virtual_count)
                virtual_count += 1
            else:
                bdm.Ebs = EBSBlockDevice(
                    VolumeSize=block_device['ebs_volume_size'],
                    VolumeType=block_device['ebs_volume_type'])
                if block_devices_config[n]['ebs_encrypted']:
                    bdm.Ebs.Encrypted = block_device['ebs_encrypted']
                if block_devices_config[n]['ebs_snapshot_id']:
                    bdm.Ebs.SnapshotId = block_device['ebs_snapshot_id']
            self.trop_bdm.append(bdm)

        return self.trop_bdm

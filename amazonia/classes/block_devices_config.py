#!/usr/bin/python3


class BlockDevicesConfig(object):
    def __init__(self, device_name, ebs_volume_size, ebs_volume_type, ebs_encrypted, ebs_snapshot_id, virtual_name):
        """
        Simple config class for block device mappings for multiple disks
        AWS Cloud Formation links:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-launchconfig-blockdev-mapping.html
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-launchconfig-blockdev-template.html
        :param device_name: The name of the device within Amazon EC2.
        :param ebs_volume_size: The volume size, in Gigabytes (GiB)This can be a number from 1 – 1024.
          If the volume type is EBS optimized, the minimum value is 10
        :param ebs_volume_type: The EBS volume type. By default, Auto Scaling uses the standard volume type
        :param ebs_encrypted: Indicates whether the volume is encrypted
        :param ebs_snapshot_id: The snapshot ID of the volume to use. If you specify both SnapshotId and VolumeSize,
          VolumeSize must be equal or greater than the size of the snapshot.
        :param virtual_name: The name of the virtual device. The name must be in the form ephemeralX. You can specify
          either VirtualName or Ebs
        """

        self.device_name = device_name
        self.ebs_volume_size = ebs_volume_size
        self.ebs_volume_type = ebs_volume_type
        self.ebs_encrypted = ebs_encrypted
        self.ebs_snapshot_id = ebs_snapshot_id
        self.virtual_name = virtual_name

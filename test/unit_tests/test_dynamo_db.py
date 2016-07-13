from nose.tools import *
from amazonia.classes.dynamo_db import DynamoDB
from troposphere import Template

"""
Tests the functions of the Dynomo DB class
"""


def test_ddb_title():
    """
    Test that the key title is correctly set
    """
    template = Template()
    ddb_titles = ['MyDynamoDB', 'Super22Table', '2020', 'lowercasetable']
    ddb_att_dict = [{'ddb_name': 'Name', 'ddb_atttype': 'S', 'ddb_keytype': 'HASH'},
                    {'ddb_name': 'Version', 'ddb_atttype': 'S', 'ddb_keytype': 'RANGE'}]
    for ddb_title in ddb_titles:
        ddb = DynamoDB(ddb_title=ddb_title,
                       ddb_att_dict=ddb_att_dict,
                       template=template)

        assert_equals(ddb_title, ddb.ddb_table.TableName)

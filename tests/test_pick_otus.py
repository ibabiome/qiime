#!/usr/bin/env python

"""Tests of code for OTU picking"""

__author__ = "Kyle Bittinger, Greg Caporaso"
__copyright__ = "Copyright 2009, the PyCogent Project" 
#remember to add yourself if you make changes
__credits__ = ["Kyle Bittinger", "Greg Caporaso", "Rob Knight"] 
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Kyle Bittinger"
__email__ = "kylebittinger@gmail.com"
__status__ = "Prototype"

from os import remove
from cogent.util.unit_test import TestCase, main
from cogent.app.util import get_tmp_filename
from pipe454.pick_otus import CdHitOtuPicker, DoturOtuPicker, OtuPicker

class OtuPickerTests(TestCase):
    """Tests of the abstract OtuPicker class"""

    def test_init(self):
        """Abstract OtuPicker __init__ should store name, params"""
        p = OtuPicker({})
        self.assertEqual(p.Name, 'OtuPicker')
        self.assertEqual(p.Params, {})

    def test_call(self):
        """Abstract OtuPicker __call__ should raise NotImplementedError"""
        p = OtuPicker({})
        self.assertRaises(NotImplementedError, p, '/path/to/seqs')


class CdHitOtuPickerTests(TestCase):
    """ Tests of the cd-hit-based OTU picker """

    def setUp(self):
        # create the temporary input file
        self.tmp_seq_filepath = get_tmp_filename(\
         prefix='CdHitOtuPickerTest_',\
         suffix='.fasta')
        seq_file = open(self.tmp_seq_filepath,'w')
        seq_file.write(dna_seqs)
        seq_file.close()
        
    def tearDown(self):
        remove(self.tmp_seq_filepath)

    def test_call_default_params(self):
        """CdHitOtuPicker.__call__ returns expected clusters default params"""

        # adapted from test_app.test_cd_hit.test_cdhit_clusters_from_seqs
        
        exp = {0:['cdhit_test_seqs_0'],\
               1:['cdhit_test_seqs_1'],\
               2:['cdhit_test_seqs_2'],\
               3:['cdhit_test_seqs_3'],\
               4:['cdhit_test_seqs_4'],\
               5:['cdhit_test_seqs_5'],\
               6:['cdhit_test_seqs_6'],\
               7:['cdhit_test_seqs_7'],\
               8:['cdhit_test_seqs_8'],\
               9:['cdhit_test_seqs_9']}
        
        app = CdHitOtuPicker(params={})
        obs = app(self.tmp_seq_filepath)
        self.assertEqual(obs, exp)
        
    def test_call_alt_threshold(self):
        """CdHitOtuPicker.__call__ returns expected clusters with alt threshold
        """
        # adapted from test_app.test_cd_hit.test_cdhit_clusters_from_seqs
        
        exp = {0:['cdhit_test_seqs_0'],\
               1:['cdhit_test_seqs_1'],\
               2:['cdhit_test_seqs_2'],\
               3:['cdhit_test_seqs_3'],\
               4:['cdhit_test_seqs_4'],\
               5:['cdhit_test_seqs_5'],\
               6:['cdhit_test_seqs_6','cdhit_test_seqs_8'],\
               7:['cdhit_test_seqs_7'],\
               8:['cdhit_test_seqs_9']}

        app = CdHitOtuPicker(params={'Similarity':0.90})
        obs = app(self.tmp_seq_filepath)
        self.assertEqual(obs, exp)
        
    def test_call_output_to_file(self):
        """CdHitOtuPicker.__call__ output to file functions as expected
        """
        
        tmp_result_filepath = get_tmp_filename(\
         prefix='CdHitOtuPickerTest.test_call_output_to_file_',\
         suffix='.txt')
        
        app = CdHitOtuPicker(params={'Similarity':0.90})
        obs = app(self.tmp_seq_filepath,result_path=tmp_result_filepath)
        
        result_file = open(tmp_result_filepath)
        result_file_str = result_file.read()
        result_file.close()
        # remove the result file before running the test, so in 
        # case it fails the temp file is still cleaned up
        remove(tmp_result_filepath)
        
        # compare data in result file to fake expected file
        self.assertEqual(result_file_str, dna_seqs_result_file_90_exp)
        # confirm that nothing is returned when result_path is specified
        self.assertEqual(obs,None)
        
    def test_call_log_file(self):
        """CdHitOtuPicker.__call__ writes log when expected
        """
        
        tmp_log_filepath = get_tmp_filename(\
         prefix='CdHitOtuPickerTest.test_call_output_to_file_l_',\
         suffix='.txt')
        tmp_result_filepath = get_tmp_filename(\
         prefix='CdHitOtuPickerTest.test_call_output_to_file_r_',\
         suffix='.txt')
        
        app = CdHitOtuPicker(params={'Similarity':0.99})
        obs = app(self.tmp_seq_filepath,\
         result_path=tmp_result_filepath,log_path=tmp_log_filepath)
        
        log_file = open(tmp_log_filepath)
        log_file_str = log_file.read()
        log_file.close()
        # remove the temp files before running the test, so in 
        # case it fails the temp file is still cleaned up
        remove(tmp_log_filepath)
        remove(tmp_result_filepath)
        
        log_file_99_exp = ["CdHitOtuPicker parameters:",\
         "Similarity:0.99","Application:cdhit",\
         'Algorithm:cdhit: "longest-sequence-first list removal algorithm"',\
         "Result path: %s" % tmp_result_filepath,'']
        # compare data in log file to fake expected log file
        # NOTE: Since app.params is a dict, the order of lines is not
        # guaranteed, so testing is performed to make sure that 
        # the equal unordered lists of lines is present in actual and expected
        self.assertEqualItems(log_file_str.split('\n'), log_file_99_exp)
        

class DorurOtuPickerTests(TestCase):
    """Tests for the Dotur-based OTU picker."""

    def setUp(self):
        self.seqs = """>a
UAGGCUCUGAUAUAAUAGCUCUC---------
>c
------------UGACUACGCAU---------
>b
----UAUCGCUUCGACGAUUCUCUGAUAGAGA
"""

        # create the temporary input file
        self.tmp_seq_filepath = get_tmp_filename(prefix='CdHitOtuPickerTest_',
                                                 suffix='.fasta')
        seq_file = open(self.tmp_seq_filepath, 'w')
        seq_file.write(self.seqs)
        seq_file.close()

    def tearDown(self):
        remove(self.tmp_seq_filepath)

    def test_init(self):
        """DoturOtuPicker.__init__ should set default attributes and params"""
        d = DoturOtuPicker({})
        self.assertEqual(d.Name, 'DoturOtuPicker')

    def test_call(self):
        """DoturOtuPicker.__call__ should return correct OTU's"""
        exp = {0: ['a'], 1: ['b'], 2: ['c']}

        params = {}
        d = DoturOtuPicker(params)
        self.assertEquals(d(self.tmp_seq_filepath), exp)

    def test_call_output_to_file(self):
        """DoturOtuPicker.__call__ should write output to file when expected"""
        exp = "0\ta\n1\tb\n2\tc\n"

        tmp_result_filepath = get_tmp_filename(
            prefix='DoturOtuPickerTest.test_call_output_to_file_',
            suffix='.txt')
        
        app = DoturOtuPicker(params={})
        obs = app(self.tmp_seq_filepath, result_path=tmp_result_filepath)
        
        result_file = open(tmp_result_filepath)
        result_file_str = result_file.read()
        result_file.close()
        # remove the result file before running the test, so in 
        # case it fails the temp file is still cleaned up
        remove(tmp_result_filepath)

        # compare data in result file to fake expected file
        self.assertEqual(result_file_str, exp)
        # confirm that nothing is returned when result_path is specified
        self.assertEqual(obs, None)

    def test_call_log_file(self):
        """DoturOtuPicker.__call__ should write log when expected"""
        tmp_log_filepath = get_tmp_filename(
            prefix='DoturOtuPickerTest.test_call_output_to_file_l_',
            suffix='.txt')
        tmp_result_filepath = get_tmp_filename(
            prefix='DoturOtuPickerTest.test_call_output_to_file_r_',
            suffix='.txt')

        app = DoturOtuPicker(params={})
        obs = app(self.tmp_seq_filepath,
                  result_path=tmp_result_filepath,
                  log_path=tmp_log_filepath)

        log_file = open(tmp_log_filepath)
        log_file_str = log_file.read()
        log_file.close()
        # remove the temp files before running the test, so in 
        # case it fails the temp file is still cleaned up
        remove(tmp_log_filepath)
        remove(tmp_result_filepath)

        exp = "%s\nResult path: %s\n" % (str(app), tmp_result_filepath)
        
        # compare data in log file to fake expected log file
        self.assertEqual(log_file_str, exp)


dna_seqs = """>cdhit_test_seqs_0 comment fields, not part of sequence identifiers
AACCCCCACGGTGGATGCCACACGCCCCATACAAAGGGTAGGATGCTTAAGACACATCGCGTCAGGTTTGTGTCAGGCCT
> cdhit_test_seqs_1
ACCCACACGGTGGATGCAACAGATCCCATACACCGAGTTGGATGCTTAAGACGCATCGCGTGAGTTTTGCGTCAAGGCT
>cdhit_test_seqs_2
CCCCCACGGTGGCAGCAACACGTCACATACAACGGGTTGGATTCTAAAGACAAACCGCGTCAAAGTTGTGTCAGAACT
>cdhit_test_seqs_3
CCCCACGGTAGCTGCAACACGTCCCATACCACGGGTAGGATGCTAAAGACACATCGGGTCTGTTTTGTGTCAGGGCT
>cdhit_test_seqs_4
GCCACGGTGGGTACAACACGTCCACTACATCGGCTTGGAAGGTAAAGACACGTCGCGTCAGTATTGCGTCAGGGCT
>cdhit_test_seqs_5
CCGCGGTAGGTGCAACACGTCCCATACAACGGGTTGGAAGGTTAAGACACAACGCGTTAATTTTGTGTCAGGGCA
>cdhit_test_seqs_6
CGCGGTGGCTGCAAGACGTCCCATACAACGGGTTGGATGCTTAAGACACATCGCAACAGTTTTGAGTCAGGGCT
>cdhit_test_seqs_7
ACGGTGGCTACAAGACGTCCCATCCAACGGGTTGGATACTTAAGGCACATCACGTCAGTTTTGTGTCAGAGCT
>cdhit_test_seqs_8
CGGTGGCTGCAACACGTGGCATACAACGGGTTGGATGCTTAAGACACATCGCCTCAGTTTTGTGTCAGGGCT
>cdhit_test_seqs_9
GGTGGCTGAAACACATCCCATACAACGGGTTGGATGCTTAAGACACATCGCATCAGTTTTATGTCAGGGGA"""

dna_seqs_result_file_90_exp = """0\tcdhit_test_seqs_0
1\tcdhit_test_seqs_1
2\tcdhit_test_seqs_2
3\tcdhit_test_seqs_3
4\tcdhit_test_seqs_4
5\tcdhit_test_seqs_5
6\tcdhit_test_seqs_6\tcdhit_test_seqs_8
7\tcdhit_test_seqs_7
8\tcdhit_test_seqs_9
"""



#run unit tests if run from command-line
if __name__ == '__main__':
    main()

import os
from datetime import datetime
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile as UpFile
from django.test import TestCase
import settings
from main.models import *

files_path = os.path.join(settings.MEDIA_ROOT, 'tests')

#Get a file test of perticular extension: sort.[extension]
def get_file(extension):    
    return open('%s/sort.%s' %(files_path, extension))

class Initial:   
    def __init__(self):
        tusr = User.objects.get_or_create(username='test')[0]        
        admn = User.objects.get_or_create(username='admin')[0]
        pgrp = Group.objects.get_or_create(name='public')[0]
        ugrp = Group.objects.get_or_create(name='universal')[0]
        admn.groups.add(ugrp)
        tusr.groups.add(pgrp)
        category = Category.objects.get_or_create(title='test', slug='test', 
                                             description='test')[0]
        error = Error.objects.get_or_create(title='random', 
                                        description='random')[0]
        lang = Language.objects.get_or_create(name='C', ext='c')[0]
        lang.errors.add(error)
        prob = Problem.objects.get_or_create(title='test', slug='test', 
            summary='summary', statement='test contents', level=2, marks=100,
            author=admn, is_public=True, category=category)[0]
        prob.languages.add(lang)
        self.prob = prob
        self.category = category
        self.language = lang
        
    def problem(self):
        return Problem.objects.get(pk=1) 

#Create a testpair
def create_testpair(problem, *args, **kwargs):
    input_file = get_file('in')
    output_file = get_file('out')
    testpair = TestPair(input_file=UpFile(input_file.name,
                                          input_file.read()),
                        output_file=UpFile(output_file.name,
                                           output_file.read()),
                        problem=problem, *args, **kwargs)
    testpair.save()        
    return testpair

#Delete the files created by testpairs on filesystem
def cleanup_testpair_files(testpairs):
    for testpair in testpairs:        
        testpair.delete_files()

class ProblemTests(TestCase):           
    def test_testpair_distribution(self):
        '''
        Testing the problem input output test pairs creation
        '''
        I=Initial()
        ##Create three testcases with weightages 1, 2, 3
        testpairs = []
        for i in range(1, 4):
            testpairs.append(create_testpair(I.problem(), weightage=i))
        #Files are not required in this test
        cleanup_testpair_files(testpairs)

        #Get the updated problem, testpairs due to new testpairs addition
        testpairs = I.problem().testpairs.all()
        self.failUnlessEqual(I.problem().marks_factor,
                             round(I.problem().marks/6, 3))
        
        #Check marks allotment        
        for t in testpairs:
            self.failUnlessEqual(t.marks_alloted,
                                 round(I.problem().marks_factor *
                                       t.weightage, 3))

    def test_marks_obtained(self):
        '''
        Testing the calculation of marks obtained by time taken
        '''
        I=Initial()
        t = create_testpair(I.problem(), weightage=1)
        t.problem = I.problem()
        #Files are not required in this test
        cleanup_testpair_files([t])
        self.failUnlessEqual(t.marks_obtained(0.25), 100)
        self.failUnlessEqual(t.marks_obtained(2.75), 50)
        self.failUnlessEqual(t.marks_obtained(10), 0)

    def test_language(self):
        I=Initial()
        print I.problem().languages.all()

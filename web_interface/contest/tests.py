import os
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile as UpFile
from django.test import TestCase
import settings
from contest.models import *

files_path = os.path.join(settings.MEDIA_ROOT, 'tests')
testuser = User.objects.get_or_create(username='test')[0]        

#Get a file test of perticular extension: sort.[extension]
def get_file(extension):    
    return open('%s/sort.%s' %(files_path, extension))

#Create a new problem or get existing one
def get_problem():
    try:
        problem = Problem.objects.get(pk=1)
        
    except Problem.DoesNotExist:        
        problem = Problem(title='test', slug='test', summary='summary',
                          contents='test contents', level=2, marks=100,
                          publisher=testuser, is_public=True
                          )
        problem.save()

    return problem

#Create a testpair
def create_testpair(*args, **kwargs):
    problem = get_problem()
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

class ModelsTest(TestCase):           
    def test_problem_fields(self):
        '''
        Testing the various coding problem fields
        '''
        problem = get_problem()
        self.failUnlessEqual(problem.pk, 1)
        problem_level_choices = getattr(settings, 'PROBLEM_LEVEL_CHOICES', 
                                     DEFAULT_PROBLEM_LEVEL_CHIOCES)
        self.failUnlessEqual(problem.get_level_display(),
                             problem_level_choices[1])
        problem.delete()

    def test_testpairs(self):
        '''
        Testing the problem input output test pairs creation,
        marks alloted
        '''
        problem = get_problem()
        ##Create three testcases with weightages 1, 2, 3
        testpairs = []
        for i in range(1, 4):
            testpairs.append(create_testpair(weightage=i))
        #Files are not required in this test
        cleanup_testpair_files(testpairs)

        #Get the updated problem, testpairs due to new testpairs addition
        problem = get_problem()
        testpairs = problem.testpairs.all()
        self.failUnlessEqual(problem.marks_factor,
                             round(problem.marks/6, 3))
        
        #Check marks allotment        
        for t in testpairs:
            self.failUnlessEqual(t.marks_alloted,
                                 round(problem.marks_factor *
                                       t.weightage, 3))

    def test_marks_obtained(self):
        '''
        Testing the calculation of marks obtained by time taken
        '''
        problem = get_problem()
        t = create_testpair(weightage=1)
        t.problem = get_problem()
        #Files are not required in this test
        cleanup_testpair_files([t])
        self.failUnlessEqual(t.marks_obtained_by_time(0.25), 100)
        self.failUnlessEqual(t.marks_obtained_by_time(2.75), 50)
        self.failUnlessEqual(t.marks_obtained_by_time(10), 0)
        

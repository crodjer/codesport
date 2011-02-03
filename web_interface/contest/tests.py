import os
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile as UpFile
from django.test import TestCase
import settings
from contest.models import *

class ModelsTest(TestCase):
    testuser = User.objects.get_or_create(username='test')[0]
    files_path = os.path.join(settings.MEDIA_ROOT, 'tests')    
    input_file = open('%s/sort.in' %(files_path))
    output_file = open('%s/sort.out' %(files_path))
    program_file = open('%s/sort.c' %(files_path))
    
    def create_problem(self):        
        problem = Problem(title='test', slug='test', summary='summary',
                          contents='test contents', level=2, marks=100,
                          publisher=self.testuser, is_public=True
                          )
        problem.save()     
        return problem
        
    def test_problem_fields(self):
        '''
        Testing the various coding problem fields
        '''
        problem = self.create_problem()
        self.failUnlessEqual(problem.pk, 1)
        problem_level_choices = getattr(settings, 'PROBLEM_LEVEL_CHOICES', 
                                     DEFAULT_PROBLEM_LEVEL_CHIOCES)
        self.failUnlessEqual(problem.get_level_display(),
                             problem_level_choices[1])
        problem.delete()

    def create_testpair(self, *args, **kwargs):
        testpair = TestPair(input_file=UpFile(self.input_file.name,
                                              self.input_file.read()),
                            output_file=UpFile(self.output_file.name,
                                               self.output_file.read()),
                            problem=self.problem, *args, **kwargs)
        testpair.save()        
        return testpair        

    def test_testpair(self):
        '''
        Testing the problem input output test pairs 
        '''
        self.problem = self.create_problem()
        problem = self.problem
        for i in range(1,5):
            self.create_testpair(weightage=i)

        testpairs = TestPair.objects.filter(problem=problem)
        marks_sum = 0
        for testpair in testpairs:            
            marks_sum += testpair.marks()
            
        self.failUnlessEqual(problem.marks_coefficient, problem.marks/10)    
        testpairs.delete()
##        for testpair in testpairs:                        
##            testpair.delete()
            

import os
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile as UpFile
from django.test import TestCase
import settings
from contest.models import *
files_path = os.path.join(settings.MEDIA_ROOT, 'tests')

class ModelsTest(TestCase):
    testuser = User.objects.get_or_create(username='test')[0]    

    def get_file(self, extension):
        return open('%s/sort.%s' %(files_path, extension))
    
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
        input_file = self.get_file('in')
        output_file = self.get_file('out')
        testpair = TestPair(input_file=UpFile(input_file.name,
                                              input_file.read()),
                            output_file=UpFile(output_file.name,
                                               output_file.read()),
                            problem=self.problem, *args, **kwargs)
        testpair.save()        
        return testpair        

    def test_testpair(self):
        '''
        Testing the problem input output test pairs 
        '''
        self.problem = self.create_problem()
        problem = self.problem        
        testpair1 = self.create_testpair(weightage=2)                    
        self.failUnlessEqual(problem.marks_coefficient, problem.marks/2)
        testpair2 = self.create_testpair(weightage=1)                    
        self.failUnlessEqual(problem.marks_coefficient, problem.marks/3)
        testpair3 = self.create_testpair(weightage=3)                    
        self.failUnlessEqual(problem.marks_coefficient, problem.marks/6)

        #Delete the testpair files
        testpair1.delete_files()
        testpair2.delete_files()
        testpair3.delete_files()

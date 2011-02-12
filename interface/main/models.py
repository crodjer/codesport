from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import settings

'''
TODO: The TestPair file fields don't get deleted from file system on
object deletion.
'''

##The default set of choices for coding problem
DEFAULT_PROBLEM_LEVEL_CHIOCES = (
    'easy', 
    'normal', 
    'hard',
)

##The default set of choices for testpair weightage level
DEFAULT_TESTPAIR_WEIGHTAGE_CHIOCES = (
    'low', 
    'medium', 
    'high',
)

class AbstractModel(models.Model):
    '''
    Abstract model to be imported by all models in the module
    '''
    published_on = models.DateTimeField(_('published on'), auto_now_add=True)
    updated_on = models.DateTimeField(_('updated on'), auto_now=True)
    class Meta:
        abstract=True
        get_latest_by = 'updated_on'

class Contestant(User):
    '''
    A  participant of the coding contest. A proxy model of auth's user.
    '''
    class Meta:
        proxy=True
    
class Problem(AbstractModel):
    '''
    A problem for the coding contest
    '''
    def level_choices():
        '''
        Generates choices tuple for problem level from settings choices 
        set or a default set. 
        '''        
        choices_set = getattr(settings, 'PROBLEM_LEVEL_CHOICES', 
                               DEFAULT_PROBLEM_LEVEL_CHIOCES)
        choices = tuple(enumerate(choices_set, 1))
        return choices
    
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100)
    summary = models.TextField(_('summary'), blank=True)
    contents = models.TextField(_('contents'))
    level = models.IntegerField(_('level'), choices=level_choices())
    marks = models.FloatField(_('total marks'))    
    publisher = models.ForeignKey(User, verbose_name=_('publisher'))   
    is_public = models.BooleanField(_('is_public'))
    marks_factor = models.FloatField(_('marks distribution factor'),
                                          blank=True, default=0,
                                          editable=False)
    
    def __unicode__(self):
        return self.title.title()
        
    def get_absoulte_url(self):
        return reverse('contest:problem',
                       kwargs={'problem_slug':self.slug})

    def set_marks_factor(self):
        '''
        Calculates the factor to be multiplied with test case weight-
        age to obtain case-wise marks such that the total sum would be
        equal to the total marks alloted to the problem.
        '''
        testpairs = self.testpairs
        weightage_sum = testpairs.aggregate(Sum('weightage'))['weightage__sum']        
        if weightage_sum:
            marks_factor = round(self.marks/weightage_sum, 3)
            if not self.marks_factor==marks_factor:
                self.marks_factor = marks_factor
                self.save()
            return self.marks_factor
        elif self.marks_factor:
            self.marks_factor = 0
            self.save()            
        return 0
                
class TestPair(AbstractModel):
    '''
    An input output test pair for a problem.
    '''

    def weightage_choices():
        '''
        Generates choices tuple for testpair weightage from settings
        choices set or a default set. 
        '''        
        choices_set = getattr(settings, 'testpair_WEIGHTAGE_CHOICES', 
                              DEFAULT_TESTPAIR_WEIGHTAGE_CHIOCES)
        choices = tuple(enumerate(choices_set, 1))
        return choices

    problem = models.ForeignKey(Problem, 
                                verbose_name=_('associated problem'), 
                                related_name='testpairs')
    input_file = models.FileField(_('input file'), upload_to='inputs')
    output_file = models.FileField(_('output file'), upload_to='outputs')
    weightage = models.IntegerField(_('weightage'),
                                    choices=weightage_choices())    
    soft_time_limit = models.FloatField(_('soft time limit'), default=0.5)
    hard_time_limit = models.FloatField(_('hard time limit'), default=5)    
    is_mandatory = models.BooleanField(_('is mandatory'))    
    is_public = models.BooleanField(_('is public'))

    def __unicode__(self):
        return 'Test Pair for "%s", Weightage: %s, Marks: %s' \
                %(unicode(self.problem), self.get_weightage_display(),
                  self.marks_alloted)
    
    def delete(self, *args, **kwargs):
        '''
        Delete override.
        Updates the problem marks factor as a testpair is deleted
        '''
        return_obj = super(TestPair, self).delete(*args, **kwargs)
        self.problem.set_marks_factor()
        return return_obj


    def _marks_alloted(self):
        '''
        Calculates the marks alloted to the case through the problem's
        marks_factor
        '''
        return round(self.weightage * self.problem.marks_factor, 3)

    def marks_obtained_by_time(self, time_taken):
        if time_taken <= self.soft_time_limit:
            return self.marks_alloted

        elif time_taken <= self.hard_time_limit:
            exceed_time = time_taken - self.soft_time_limit
            max_exceed_time = self.hard_time_limit - self.soft_time_limit            
            exceed_factor = (max_exceed_time-exceed_time)/max_exceed_time            
            return round(self.marks_alloted * exceed_factor, 3)
        else:
            return 0
        
    def save(self, *args, **kwargs):
        '''
        Save override.
        Updates the problem marks factor as the new testpair is saved        
        '''
        return_obj = super(TestPair, self).save(*args, **kwargs)
        self.problem.set_marks_factor()
        return return_obj

    def delete_files(self):
        '''
        Delete the files from file fields
        '''
        self.input_file.delete(save=False)
        self.output_file.delete(save=False) 

    marks_alloted = property(_marks_alloted)   

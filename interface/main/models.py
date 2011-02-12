from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import settings

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

class Error(models.Model):
    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('error'), max_length=300)

class Language(models.Model):
    name = models.CharField(_('name'), max_length=100)
    ext = models.CharField(_('extension'), max_length=15)
    errors = models.ManyToManyField(Error, related_name='languages', 
                                    verbose_name=_('possible errors'))
    execution_command = models.TextField(_('execution command'))
    is_compiled = models.BooleanField(_('is compiled language'))
    compilation_command = models.TextField(_('compilation command'))

class Tag(models.Model):
    name = models.CharField(_('name'), max_length=100)
    wiki = models.TextField(_('wiki'))

    def __unicode__(self):
        return self.name

class Category(AbstractModel):
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'))
    description = models.TextField(_('description'))
    is_public = models.BooleanField(_('is public'))
    is_timed = models.BooleanField(_('is a timed contest'))
    is_teamed = models.BooleanField(_('is team based'))
    target_groups = models.ManyToManyField(Group, 
                                          verbose_name='target groups')
    start_time = models.DateTimeField(_('start time'), blank=True, 
                                      null=True) 
    end_time = models.DateTimeField(_('end time'), blank=True,
                                    null=True)

    def __unicode__(self):
        return "%s" %(self.title)

    def get_absoulte_url(self):
        return reverse('main:category',
                       kwargs={'category_slug':self.slug})

    def user_can_participate(self, user):
        for group in self.target_groups:
            if user in group.user_set.all():
                return True
        return False

class Team(AbstractModel):
    name = models.CharField(_('name'), max_length=100)
    coders = models.ManyToManyField(User, related_name='teams',
                                    verbose_name=_('coders'))     
    category = models.ForeignKey(Category, verbose_name=_('category'),
                                 related_name='teams')


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
    statement = models.TextField(_('Full Statement'))
    languages = models.ManyToManyField(Language, verbose_name=_('languages'))
    tags = models.ManyToManyField(Tag, verbose_name=_('tags'))
    level = models.IntegerField(_('level'), choices=level_choices())
    marks = models.FloatField(_('total marks'))    
    category = models.ForeignKey(Category, verbose_name = _('category'),
                                related_name='problems')
    author = models.ForeignKey(User, verbose_name=_('author'))
    is_public = models.BooleanField(_('is public'))
    is_open = models.BooleanField(_('is open'))
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
    is_samepls =  models.BooleanField(_('is sample'))

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

    def marks_obtained(self, time_taken):
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

class Submission(AbstractModel):
    problem = models.ForeignKey(Problem, verbose_name=_('problem'),
                                related_name='submissions')
    language = models.ForeignKey(Language, verbose_name=_('language'))
    code = models.FileField(_('code'), upload_to='codes')
    code_filename = models.CharField(_('code filename'), editable=False,
                                    max_length=200)
    coder = models.ForeignKey(User, verbose_name=_('coder'),
                              related_name='submissions')
    is_latest = models.BooleanField(_('is latest'), default=True)
    #process 
    marks = models.FloatField(_('obtained marks'))
    is_correct = models.BooleanField(_('is fully correct'), default=False)
    errors = models.ManyToManyField(Error, verbose_name=('errors'))
    similar = models.ManyToManyField('self', 
                                    verbose_name=_('similar submissions'))


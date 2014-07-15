# Python
import datetime
# Django
from django.db import models
from django.db.models.query import QuerySet
# Third Party
from model_utils.managers import PassThroughManager
from autoslug import AutoSlugField
# Local
from coredata.models import Unit, Person, CourseOffering
from courselib.slugs import make_slug
from courselib.json_fields import JSONField
from grad.models import GradStudent
from ra.models import Account


CONTRACT_STATUS_CHOICES = (
        ("NEW","Draft"),
        ("SGN","Contract Signed"),
        ("CAN","Cancelled"),
)


class ContractFrozen(Exception):
    """
    Once a SGNed contract exists within a Category, that Category
        can never be changed again, except to hide it. 
    Once a contract is in the SGN or CAN state, it can't be edited.
        (Except for the state, which can be moved from SGN to CAN).
    To edit a contract that is SGN, that contract must be CANcelled, 
        then copied, then SiGNed again. 
    Movement between the status options is one-way - 
        a NEW contract can become a SGN contract,
        and a SGN contract can become a CAN contract, 
        but a SGN contract can't be changed to a NEW,
        nor can a CAN contract be changed to NEW or SGN.
    """
    pass


APPOINTMENT_CHOICES = (
        ("INIT","Initial appointment to this position"),
        ("REAP","Reappointment to same position or revision to appointment"),       
)


# These are SIN numbers that we know are probably fake.
DUMMY_SINS = ['999999999', '000000000', '123456789']


class TACategoryQuerySet(QuerySet):
    def visible(self, units):
        return self.filter(account__unit__in=units, hidden=False)

class TAContractQuerySet(QuerySet):
    def contracts(self, units):
        return self.filter(category__account__unit__in=units)\
                    .select_related('category')\
                    .prefetch_related('course')
    def draft(self, units):
        return self.contracts(units).filter(status='NEW')
    def signed(self, units):
        return self.contracts(units).filter(status='SGN')
    def cancelled(self, units):
        return self.contracts(units).filter(status='CAN')


class TACategory(models.Model):
    account = models.ForeignKey(Account)
    # the account already FKs to a Unit, so we don't need one. 
    code = models.CharField(max_length=5, 
                        help_text="Category Choice Code - for example 'GTA2'")
    title = models.CharField(max_length=50,
                        help_text="Category Choice Title - for example 'PhD'")
    pay_per_bu = models.DecimalField(max_digits=8,
                                     decimal_places=2, 
                                     verbose_name="Default pay, "+\
                                                  "per base unit.")
    scholarship_per_bu = models.DecimalField(max_digits=8, 
                                             decimal_places=2, 
                                             verbose_name="Scholarship pay, "+\
                                                          "per base unit.",)
    bu_lab_bonus = models.DecimalField(max_digits=8,
                                       decimal_places=2, 
                                       verbose_name="Bonus BUs awarded to a "+\
                                                    "course with a lab.")

    # ensc-gta2-2014-01-01
    def autoslug(self):
        return make_slug(self.account.unit.label + '-' + unicode(self.code) + \
                         '-' + unicode(self.created.date()))
    slug = AutoSlugField(populate_from=autoslug, 
                         null=False, 
                         editable=False, 
                         unique=True)
    created = models.DateTimeField(default=datetime.datetime.now(), editable=False)
    hidden = models.BooleanField(default=False, editable=False)
    config = JSONField(null=False, blank=False, editable=False, default={})

    objects = PassThroughManager.for_queryset_class(TACategoryQuerySet)()
    
    def __unicode__(self):
        return "%s %s %s" % (self.account.unit.label, unicode(self.code), 
                             unicode(self.created))
    @property
    def contracts(self):
        return TAContract.objects.filter(category=self)
    
    @property
    def frozen(self):
        """
        If any of the contracts in this category are SGN or CAN, this
        category can never be changed, only hidden. 
        """
        bools = [contract.frozen for contract in self.contracts]
        return True in bools

    def save(self, always_allow=False, *args, **kwargs):
        if not always_allow and self.frozen:
            raise ContractFrozen()
        else:
            super(TACategory, self).save(*args, **kwargs)

    def hide(self):
        self.hidden = True
        self.save(always_allow=True)


class TAContract(models.Model):
    """    
    TA Contract, filled in by TA Administrator
    """
    person = models.ForeignKey(Person)
    category = models.ForeignKey(TACategory, 
                                 related_name="contract",
                                 editable=False)
    status = models.CharField(max_length=4,
                              choices=CONTRACT_STATUS_CHOICES,
                              default="NEW",
                              editable=False)
    sin = models.CharField(max_length=30, 
                           verbose_name="SIN",
                           help_text="Social Insurance Number - 000000000 if unknown")
    pay_start = models.DateField()
    pay_end = models.DateField()
    appointment = models.CharField(max_length=4, 
                            choices=APPOINTMENT_CHOICES, 
                            default="INIT")
    conditional_appointment = models.BooleanField(default=False)
    tssu_appointment = models.BooleanField(default=True)
    comments = models.TextField(blank=True)
    # curtis-lassam-2014-09-01 
    def autoslug(self):
        return make_slug(self.person.first_name + '-' + self.person.last_name \
                            + "-" + unicode(self.pay_start))
    slug = AutoSlugField(populate_from=autoslug, 
                         null=False, 
                         editable=False, 
                         unique=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    config = JSONField(null=False, blank=False, editable=False, default={})
    
    objects = PassThroughManager.for_queryset_class(TAContractQuerySet)()
   
    def __unicode__(self):
        return "Contract %s - %s" % (self.person, str(self.pay_start))

    @property
    def frozen(self):
        """
        Returns True when this contract is uneditable. 
        """
        return self.status != 'NEW'

    def save(self, always_allow=False, *args, **kwargs):
        if not always_allow and self.frozen:
            raise ContractFrozen()
        else:
            super(TAContract, self).save(*args, **kwargs)
            self.set_grad_student_sin()

    def sign(self):
        """
        Moves the contract from "Draft" to "Contract Signed"
        """
        self.status = 'SGN'
        self.save(always_allow=True)

    def cancel(self):
        """
        Moves the contract from "Contract Signed" to "Cancelled"
        or
        Moves the contract from "New" to *deleted*
        """
        if self.frozen:
            self.status = 'CAN'
            self.save(always_allow=True)
        else:
            self.delete()

    def delete(self, *args, **kwargs):
        if self.frozen:
            raise ContractFrozen()
        else:
            super(TAContract, self).delete(*args, **kwargs)

    def set_grad_student_sin(self):
        for gs in GradStudent.objects.filter(person=self.person):
            if (('sin' not in gs.config 
                or ('sin' in gs.config and gs.config['sin'] in DUMMY_SINS)) 
                and not self.sin in DUMMY_SINS):
                gs.person.set_sin(self.sin)
                gs.person.save()

    def bu(self):
        return sum( [course.bu for course in self.course_set] )
    
    def prep_bu(self):
        return sum( [course.prep_bu for course in self.course_set] )

    def total_bu(self):
        return sum( [course.total_bu for course in self.course_set] )

    def total_pay(self):
        return decimal.Decimal(self.total_bu()) * self.pay_per_bu


class TACourse(models.Model):
    course = models.ForeignKey(CourseOffering,
                               blank=False, 
                               null=False,
                               related_name="+")
    contract = models.ForeignKey(TAContract, 
                                 blank=False, 
                                 null=False, 
                                 related_name="course")
    bu = models.DecimalField(max_digits=4, decimal_places=2)
    labtut = models.BooleanField(default=False, 
                                 verbose_name="Lab/Tutorial?", 
                                 help_text="Does this course have a lab or tutorial?")
    config = JSONField(null=False, blank=False, default={})
    
    class Meta:
        unique_together = (('contract', 'course'),)
    
    def __unicode__(self):
        return "Course: %s  TA: %s" % (self.course, self.contract)

    @property
    def prep_bu(self):
        """
        Return the prep BUs for this assignment
        """
        if self.labtut:
            return contract.category.bu_lab_bonus 
        else:
            return 0

    @property
    def total_bu(self):
        """
        Return the total BUs for this assignment
        """
        return self.bu + self.prep_bu



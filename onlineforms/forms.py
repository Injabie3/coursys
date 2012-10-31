from django import forms
from django.forms.models import ModelForm
from onlineforms.models import Form, Sheet, Field, FIELD_TYPE_CHOICES, FIELD_TYPE_MODELS, FormGroup, VIEWABLE_CHOICES, NonSFUFormFiller
from django.utils.safestring import mark_safe
from django.utils.html import escape

class DividerFieldWidget(forms.TextInput):
  def render(self, name, value, attrs=None):
    return mark_safe('<hr />')

class ExplanationFieldWidget(forms.Textarea):
  def render(self, name, value, attrs=None):
    return mark_safe('<div>%s</div>' % escape(value))

class GroupForm(ModelForm):
    class Meta:
        model = FormGroup

class FormForm(ModelForm):
    class Meta:
        model = Form
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }
	exclude = ('active', 'original', 'unit') 
        
class SheetForm(forms.Form):
    title = forms.CharField(required=True, max_length=30, label=mark_safe('Title'), help_text='Name of the sheet')
    can_view = forms.ChoiceField(required=True, choices=VIEWABLE_CHOICES, label='Can view')

class EditSheetForm(ModelForm):
    class Meta:
        model = Sheet

class NonSFUFormFillerForm(ModelForm):
    class Meta:
        model = NonSFUFormFiller

class FieldForm(forms.Form):
    type = forms.ChoiceField(required=True, choices=FIELD_TYPE_CHOICES, label='Type')

class AdminAssignForm(forms.Form):
    send_to = forms.ChoiceField(required=True, choices=FormGroup.objects.all(), label='Send to')
    
    def __init__(self, form_group, *args, **kwargs):
        self.form_group = form_group
        super(DynamicForm, self).__init__(*args, **kwargs)
    
class DynamicForm(forms.Form):
    def __init__(self, title, *args, **kwargs):
        self.title = title
        super(DynamicForm, self).__init__(*args, **kwargs)

    def setFields(self, kwargs):
        """
        Sets the fields in a form
        """
        keys = kwargs.keys()

        # Determine order right here
        keys.sort()

        for k in keys:
            self.fields[k] = kwargs[k]

    def fromFields(self, fields):
        """
        Sets the fields from a list of field model objects
        preserving the order they are given in
        """
        fieldargs = {}
        # keep a dictionary of the configured display fields, so we can serialize them with data later
        self.display_fields = {}
        for (counter, field) in enumerate(fields):
            display_field = FIELD_TYPE_MODELS[field.fieldtype](field.config)
            self.fields[counter] = display_field.make_entry_field()
            # keep the display field for later
            self.display_fields[self.fields[counter] ] = display_field


    def fromPostData(self, post_data):
        self.cleaned_data = {}
        for name, field in self.fields.items():
            try:
                if str(name) in post_data:
                    self.cleaned_data[str(name)] = field.clean(post_data[str(name)])
                else:
                    self.cleaned_data[str(name)] = field.clean("")
            except Exception, e:
                self.errors[name] = ", ".join(e.messages)

    def is_valid(self):
        # override because I'm not sure how to bind this form to data (i.e. form.is_bound)
        return not bool(self.errors)

    def validate(self, post):
        """
        Validate the contents of the form
        """
        for name, field in self.fields.items():
            try:
                field.clean(post[str(name)])
            except Exception, e:
                self.errors[name] = e.message

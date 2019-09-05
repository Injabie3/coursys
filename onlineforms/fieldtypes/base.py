from django import forms

# base models for FieldType classes

class FieldConfigForm(forms.Form):
    """
    The base form for field configuration.

    'required', 'label', and 'help_text' are implemented on
    all field objects.
    """

    required = forms.BooleanField(label="Required", required=False, help_text="Should the user be required to complete this field?")
    label = forms.CharField(label="Label", max_length=60, help_text="The label identifying this field, like \"Label\" on this field.")
    help_text = forms.CharField(label="Help Text", required=False, help_text="Help text for the user. This text is help text: what you enter here will appear like this.",
                                widget=forms.TextInput(attrs={'size': 60}))

    def serialize(self):
        """
        Convert entered data into a JSON-friendly object for
        Field.config
        """
        return self.cleaned_data


class FieldBase(object):
    default_config = {'required': False, 'label': '', 'help_text': ''}
    configurable = True
    choices = False
    in_summary = True # this type is included in summary CSV output

    def __init__(self, config=None):
        """
        Given a 'config' dictionary, instantiate this object in such
        a way that it will produce the Field object described by the
        dictionary.
        """
        if not config:
            config = self.default_config.copy()
            if hasattr(self, 'more_default_config'):
                config.update(self.more_default_config)
            self.config = config
        else:
            self.config = config

    def make_config_form(self):
        """
        Returns a Django Form instance that can be used to edit this
        field's details.

        The Form's 'cleaned_data' should match this code's 'config'
        object. 
        
        e.g. user might want to edit the things in the .config field:
        this Form lets them.
        """
        raise NotImplementedError

    def make_entry_field(self, fieldsubmission=None):
        """
        Returns a Django Field for this field, to be filled in by the
        user. If filled is given, it is a FieldSubmission that must be
        used to populate initial data in the field.
        
        e.g. a CharField field.
        """
        raise NotImplementedError

    def serialize_field(self, field):
        """
        Convert filled field (a django.forms.Field, as returned by make_entry_field)
        to a JSON-friendly format. 

        e.g., converting the result of a DateTimeField's 'clean()' method (which is
        itself a datetime) to an ISO standard serialization format
        
        return {'info': unicode(field.clean())}
        """
        raise NotImplementedError

    def to_html(self, fieldsubmission=None):
        """
        Convert FieldSubmission to HTML for display to the user.

        e.g. return mark_safe('<p>'+escape(fieldsubmission.data['info'])+'</p>')
        """
        raise NotImplementedError

    def to_text(self, fieldsubmission):
        """
        Convert FieldSubmission to text for display in CSV summary output. Required only if self.in_summary.

        e.g. escape(fieldsubmission.data['info'])
        """
        raise NotImplementedError

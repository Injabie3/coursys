from .models import Asset, AssetDocumentAttachment, AssetChangeRecord, CATEGORY_CHOICES, assets_from_csv
from django import forms
from coredata.models import Unit
from coredata.widgets import CalendarWidget, DollarInput
from coredata.forms import PersonField
import csv


class AssetForm(forms.ModelForm):
    user = PersonField(required=False)

    def __init__(self, request, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        unit_ids = [unit.id for unit in request.units]
        units = Unit.objects.filter(id__in=unit_ids)
        self.fields['unit'].queryset = units
        self.fields['unit'].empty_label = None
        SORTED_CATEGORIES = sorted(CATEGORY_CHOICES, key=lambda x: x[1])
        self.fields['category'].choices = SORTED_CATEGORIES

    class Meta:
        exclude = []
        model = Asset
        widgets = {
            'notes': forms.Textarea,
            'price': DollarInput,
            'last_order_date': CalendarWidget,
            'vendor': forms.Textarea,
            'service_records': forms.Textarea,
            'calibration_date': CalendarWidget,
            'eol_date': CalendarWidget,
            'date_shipped': CalendarWidget,
        }

    def is_valid(self, *args, **kwargs):
        PersonField.person_data_prep(self)
        return super(AssetForm, self).is_valid(*args, **kwargs)


class AssetAttachmentForm(forms.ModelForm):
    class Meta:
        model = AssetDocumentAttachment
        exclude = ("asset", "created_by")


class AssetChangeForm(forms.ModelForm):
    person = PersonField()

    def __init__(self, request, *args, **kwargs):
        super(AssetChangeForm, self).__init__(*args, **kwargs)
        #  The following two lines look stupid, but they are not.  request.units contains a set of units.
        #  in order to be used this way, we need an actual queryset.
        #
        #  In this case, we also include subunits.  If you manage assets for a parent unit, chances are you may be
        #  adding/removing them for events in your children units.
        unit_ids = [unit.id for unit in Unit.sub_units(request.units)]
        units = Unit.objects.filter(id__in=unit_ids)

    class Meta:
        model = AssetChangeRecord
        widgets = {
            'date': CalendarWidget
        }
        fields = ['person', 'qty', 'date']

    def is_valid(self, *args, **kwargs):
        PersonField.person_data_prep(self)
        return super(AssetChangeForm, self).is_valid(*args, **kwargs)


class InventoryUploadForm(forms.Form):
    file = forms.FileField(required=True)

    def __init__(self, request, *args, **kwargs):
        super(InventoryUploadForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean_file(self):
        file = self.cleaned_data['file']

        if file is not None and (not file.name.endswith('.csv')) and \
                (not file.name.endswith('.CSV')):
            raise forms.ValidationError("Only .csv files are permitted")

        try:
            data = file.read().decode('utf-8-sig').splitlines()
        except UnicodeDecodeError:
            raise forms.ValidationError("Bad UTF-8 data in file.")

        try:
            # Convert the csv reader data to a list, because we need to use it twice.  If we just leave it as a csv
            # reader object, the iterator will be exhausted by the time we call this with save=True
            data = list(csv.reader(data, delimiter=','))
        except csv.Error as e:
            raise forms.ValidationError('CSV decoding error.  Exception was: "' + str(e) + '"')
        # actually parse the input to see if it's valid.  If we make it through this without a ValidationError (in
        # the helper method, it's hopefully safe to call it in the view to actually create the assets.
        assets_from_csv(self.request, data, save=False)
        return data


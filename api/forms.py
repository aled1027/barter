from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from api.models import InvestmentCheck


class InvestmentCheckForm(forms.ModelForm):
    date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))

    class Meta:
        model = InvestmentCheck
        fields = ["instrument", "date", "dry_run"]

    helper = FormHelper()
    helper.add_input(Submit("submit", "Submit", css_class="btn-primary"))

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date is not None and date > timezone.now().date():
            raise ValidationError("The date cannot be in the future")

        return date

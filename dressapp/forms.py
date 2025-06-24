from django import forms
from .models import Review,Product, ProductSize,SizeOption
from django.contrib.auth.forms import AuthenticationForm

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'required': True}),  # ensure it's required in HTML
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].required = True  # required at the form-validation level too


class ProductAdminForm(forms.ModelForm):
    new_sizes = forms.ModelMultipleChoiceField(
        queryset=SizeOption.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Available Sizes"
    )

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        if not instance or not instance.pk:
            # New product: default to M, L, XL
            default_codes = ['M', 'L', 'XL']
            self.initial['new_sizes'] = SizeOption.objects.filter(code__in=default_codes)
        else:
            # Existing product: check only sizes marked available
            available_ids = instance.sizes.filter(is_available=True).values_list('size_id', flat=True)
            self.initial['new_sizes'] = SizeOption.objects.filter(pk__in=available_ids)

        used_ids = []
        if instance and instance.pk:
            used_ids = list(instance.sizes.values_list('size_id', flat=True))

        choices = []
        for size in SizeOption.objects.all():
            label = f"{size.code}" if size.pk in used_ids else size.code
            choices.append((size.pk, label))
        self.fields['new_sizes'].choices = choices

from django import forms
from cars.models import Car

class CarForm(forms.ModelForm):

    class Meta:
        model = Car
        fields = (
            'model',
            'brand',
            'factory_year',
            'model_year',
            'color',
            'transmission',
            'mileage',
            'price',
            'description',
            'is_new',
            'is_available',
            'highlighted',
            'image',
        )

    def clean(self):
        cleaned_data = super().clean()
        factory_year = cleaned_data.get('factory_year')
        model_year = cleaned_data.get('model_year')
        is_new = cleaned_data.get('is_new')
        mileage = cleaned_data.get('mileage')
        highlighted = cleaned_data.get('highlighted')
        is_available = cleaned_data.get('is_available')

        if is_new and mileage > 0:
            error_msg = 'Carros novos não podem ter quilometragem maior que zero.'
            self.add_error('mileage', error_msg)

        if factory_year != model_year: 
            if factory_year < (model_year - 1) or factory_year > (model_year +1):
                error_msg = 'Ano de fabricação e modelo inválidos.'
                self.add_error('factory_year', error_msg)
                self.add_error('model_year', error_msg)
        
        if highlighted and not is_available:
            error_msg = 'Carros destacados devem estar disponíveis.'
            self.add_error('highlighted', error_msg)
            self.add_error('is_available', error_msg)

        return cleaned_data
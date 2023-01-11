from django import forms
from store.models import Product, Variation, Author


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['product_name', 'description', 'price', 'images',
                  'author', 'category', 'stock', 'is_available']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        self.fields['is_available'].widget.attrs['class'] = 'ml-2 mt-1 form-check-input'


class VariationForm(forms.ModelForm):

    class Meta:
        model = Variation
        fields = ['product', 'variation_category',
                  'variation_values', 'is_active']

    def __init__(self, *args, **kwargs):
        super(VariationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        self.fields['is_active'].widget.attrs['class'] = 'ml-2 mt-1 form-check-input'


class AuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ['name', 'is_active']

    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        self.fields['is_active'].widget.attrs['class'] = 'ml-2 mt-1 form-check-input'



from PIL import Image
from django import forms
from django.core.files import File
from store.models import Product
from category.models import Category

class ProductPhotoForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Product
        fields = ('images', 'x', 'y', 'width', 'height', )

    def save(self):
        photo = super(ProductPhotoForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(photo.file)
        cropped_image = image.crop((x, y, w+x, h+y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(photo.file.path)

        return photo

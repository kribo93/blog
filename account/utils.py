from django import forms

class BootstrapMixin(object):
    def __init__(self, *args, **kwargs):
        super(BootstrapMixin, self).__init__(*args, **kwargs)
        meta = getattr(self, 'Meta', object)
        bootstrap_exclude = getattr(meta, 'bootstrap_exclude', [])
        for field in self.fields:
            if field not in bootstrap_exclude:
                if self.fields[field].widget.__class__ not in [forms.CheckboxInput, forms.RadioSelect, forms.FileInput, forms.ClearableFileInput]:
                    cls = self.fields[field].widget.attrs.get('class', '')
                    cls += ' form-control'
                    self.fields[field].widget.attrs['class'] = cls
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label or field.capitalize()
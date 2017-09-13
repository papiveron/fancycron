from django import forms
from models import Schedule

MINUTE_CHOICES = (
	('EveryMinute', 'Every Minute'),
	('Specific Minute', (
            ('1', 'ONE'),
            ('2', 'TWO'),
            ('3', 'THREE'),
            ('4', 'FOUR'),
        )
	),
	('Minute Range', (
            ('1', 'One'),
            ('2', 'TWO'),
        )
	),
	('unknown', 'Unknown'),
)


class ScheduleForm(forms.ModelForm):
    minute = forms.MultipleChoiceField(
        widget = forms.RadioSelect(),
       # choices = MINUTE_CHOICES
	choices =  (
    ('R', 'Red'),
    ('B', 'Yellow'),
    ('G', 'White'),
)

    )

    class Meta:
        model = Schedule

#    def clean_color(self):
 #       color = self.cleaned_data['color']
  #      if not color:
   #         raise forms.ValidationError("...")
#
 #       if len(color) > 2:
  #          raise forms.ValidationError("...")
#
 #       color = ''.join(color)
  #      return color

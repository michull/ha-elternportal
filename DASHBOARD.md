# Dashboard examples


## Helper template sensors
```
{{ state_attr('sensor.elternportal_base_x', 'appointments') | selectattr('start', 'le', now().date() + timedelta(days=6) ) | selectattr('end', 'ge', now().date() ) | list | count }}
{{ state_attr('sensor.elternportal_base_x', 'letters') | selectattr('new') | list | count }}
{{ state_attr('sensor.elternportal_base_x', 'registers') | selectattr('done', 'gt', now().date() ) | list | count }}
{{ state_attr('sensor.elternportal_base_x', 'sicknotes') | selectattr('date_to', 'ge', now().date()) | list | count }}
```


## Appointments (Termine)

This card lists appointments in a markdown card.
The statement in the second line selects only appointments that starts in the next 6 days.
The statement in the third line sorts the dates by start date, with the closest date at the top.

``` yaml
type: markdown
title: Appointments
content: |-
  {% set appointments = state_attr('sensor.elternportal_base_x', 'appointments') %}
  {% set appointments = appointments | selectattr('start', 'le', now().date() + timedelta(days=6) ) | selectattr('end', 'ge', now().date() ) | list | count %}
  {% set letters = letters | sort(attribute='start') %}
  {% for appointment in appointments %}
  {{ appointment.start }}
  {{ appointment.title }}  
  {% endfor %}
```

The result could look like this:
> 2024-10-21  
> Schulaufgabe in Englisch  
>  
> 2024-11-24  
> Schulaufgabe in Deutsch  


## Letters (Elternbriefe)

This card lists `letters` in a markdown card.
The statement in the second line selects only letters that have not yet been acknowledged.
The statement in the third line sorts the letters by sent date with newest letter on top.

``` yaml
type: markdown
title: Letters
content: |-
  {% set letters = state_attr('sensor.elternportal_base_x', 'letters') %}
  {% set letters = letters | selectattr('new') %}
  {% set letters = letters | sort(attribute='sent', reverse=True) %}
  {% for letter in letters %}
  **Subject: {{ letter.subject }}**
  **Sent: {{ letter.sent.strftime("%Y-%m-%d %H:%M") }}**

  {{ letter.description }}
    {% if not loop.last %}---{% endif %}
  {% endfor %}
```

The result could look like this:
> Subject: 1. Elternabend  
> Sent: 2024-09-17 14:30  
>  
> Herzliche Einladung zum ersten Elternabend ...


## Class register (Klassenbuch, Hausaufgaben)

This card lists `registers` in a markdown card.
With the filter in the second line, only registers with upcoming due dates are displayed.

``` yaml
type: markdown
title: Class register
content: |-
  {% set registers = state_attr('sensor.elternportal_base_x', 'registers') %}
  {% set registers = registers | selectattr('done', 'gt', now().date() ) %}
  {% set registers = registers | sort(attribute='start,done') %}
  {% for register in registers %}
  **{{ register.start }} &rarr; {{ register.done }}, {{ register.subject }}, {{ register.teacher }}**
  {{ register.description }}
  {% endfor %}
```

The result could look like this:
> 2024-09-30 &rarr; 2024-10-01, Deutsch, Heinz Mustermann  
> Adjektive: Schulbuch S. 207  
>
> 2024-09-30 &rarr; 2024-10-02, Englisch, Erika Mustermann  
> Arbeitsblatt fertig machen  
> Vokabeln Seite 199 und 200 wiederholen  


## Sick notes (Krankmeldungen)

This card lists `sicknotes` in a markdown card.
The statement in the second line hides previous sick notes.

``` yaml
type: markdown
title: Sick notes
content: |-
  {% set sicknotes = state_attr('sensor.elternportal_base_x', 'sicknotes') %}
  {% set sicknotes = sicknotes | selectattr('date_to', 'ge', now().date()) %}
  {% set sicknotes = sicknotes | sort(attribute='date_from,date_to') %}
  {% for sicknote in sicknotes %}
  **{{ sicknote.date_from }}**: {{ sicknote.comment if sicknote.comment!="" else '[Ohne Kommentar]' }}
  {% endfor %}
```


## Class register II

With the help of [flex-table-card](https://github.com/custom-cards/flex-table-card) and the checked elternportal integration option `sensor_register` you can show the class register in a table.
For a German name of the weekday change the string `en-US` to `de-DE`.

``` yaml
type: custom:flex-table-card
title: Klassenbuch
entities:
  include: sensor.elternportal_register_x
sort_by:
  - x.start+
  - x.done+
columns:
  - name: Tage
    data: list
    modify: >-
      const start = new Date(x.start); const done = new Date(x.done);

      let content = ''; content += start.toLocaleDateString('en-US', { weekday:
      'short' }); content += '&nbsp;&rarr;&nbsp;'; content +=
      done.toLocaleDateString('en-US', { weekday: 'short' }); 

      let title = ''; title += start.toLocaleDateString('en-US', { weekday:
      'long', day: 'numeric', month: 'numeric', year: 'numeric' }); title += '
      &rarr; '; title += done.toLocaleDateString('en-US', { weekday: 'long',
      day: 'numeric', month: 'numeric', year: 'numeric' });

      "<span title='" + title + "'>" + content + "</span>";
    align: center
  - name: Fach
    data: list
    modify: >-
      let content = x.subject_short || x.teacher_short; let title = x.subject +
      " - " + x.teacher; "<span title='" + title + "'>" + content + "</span>";
    align: center
  - name: Beschreibung
    data: list
    modify: x.description
css:
  td: "white-space: pre-line;"
````
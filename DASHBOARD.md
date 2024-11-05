# Dashboard examples

Note:
All sensor names from the following examples must be adapted.
To do this, replace the end `_n` with the appropriate value (e.g. `_1`).


## Helper template sensors

If you want to hide a card, you can create the following helper template sensors. These sensors can be used for [conditional cards](https://www.home-assistant.io/dashboards/conditional) or the [visibility of cards](https://www.home-assistant.io/dashboards/cards/#showing-or-hiding-a-card-or-badge-conditionally).
```
{{ state_attr('sensor.elternportal_base_n', 'appointments') | selectattr('start', 'le', now().date() + timedelta(days=6) ) | selectattr('end', 'ge', now().date() ) | list | count }}
{{ state_attr('sensor.elternportal_base_n', 'letters') | selectattr('new') | list | count }}
{{ state_attr('sensor.elternportal_base_n', 'registers') | selectattr('completion', 'ge', now().date() + timedelta(days=1) ) | list | count }}
{{ state_attr('sensor.elternportal_base_n', 'sicknotes') | selectattr('end', 'ge', now().date()) | list | count }}
```


## Appointments (Termine)

This card lists appointments in a markdown card.
The statement in the second line selects only appointments that starts in the next 6 days.
The statement in the third line sorts the dates by start date, with the closest date at the top.

``` yaml
type: markdown
title: Appointments
content: |-
  {% set appointments = state_attr('sensor.elternportal_base_n', 'appointments') %}
  {% set appointments = appointments | selectattr('start', 'le', now().date() + timedelta(days=6) ) | selectattr('end', 'ge', now().date() ) | list %}
  {% set appointments = appointments | sort(attribute='start') %}
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
  {% set letters = state_attr('sensor.elternportal_base_n', 'letters') %}
  {% set letters = letters | selectattr('new') %}
  {% set letters = letters | sort(attribute='sent', reverse=True) %}
  {% for letter in letters %}
  **Subject: {{ letter.subject }}**
  **Sent: {{ letter.sent.strftime("%Y-%m-%d %H:%M") }}**

  {{ letter.body }}
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
  {% set registers = state_attr('sensor.elternportal_base_n', 'registers') %}
  {% set registers = registers | selectattr('completion', 'gt', now().date() ) %}
  {% set registers = registers | sort(attribute='start,completion') %}
  {% for register in registers %}
  **{{ register.start }} &rarr; {{ register.completion }}, {{ register.subject }}, {{ register.teacher }}**
  {{ register.body }}
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
  {% set sicknotes = state_attr('sensor.elternportal_base_n', 'sicknotes') %}
  {% set sicknotes = sicknotes | selectattr('end', 'ge', now().date()) %}
  {% set sicknotes = sicknotes | sort(attribute='start,end') %}
  {% for sicknote in sicknotes %}
  **{{ sicknote.start }}**: {{ sicknote.comment if sicknote.comment else '[Ohne Kommentar]' }}
  {% endfor %}
```


## Class register II

With the help of [flex-table-card](https://github.com/custom-cards/flex-table-card) and the checked elternportal integration option "Sensor for class register" you can show the class register in a table.
For a German name of the weekday change the string `en-US` to `de-DE`.

``` yaml
type: custom:flex-table-card
title: Class register
entities:
  include: sensor.elternportal_register_x
sort_by:
  - x.start+
  - x.completion+
columns:
  - name: Days
    data: list
    modify: >-
      const start = new Date(x.start);
      const completion = new Date(x.completion);

      let content = '';
      content += start.toLocaleDateString('en-US', { weekday: 'short' });
      content += '&nbsp;&rarr;&nbsp;';
      content += completion.toLocaleDateString('en-US', { weekday: 'short' }); 

      let title = '';
      title += start.toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'numeric', year: 'numeric' });
      title += ' &rarr; ';
      title += completion.toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'numeric', year: 'numeric' });

      "<span title='" + title + "'>" + content + "</span>";
    align: center
  - name: Subject
    data: list
    modify: >-
      let content = x.short || x.subject || x.teacher;
      let title = x.subject + " - " + x.teacher;
      "<span title='" + title + "'>" + content + "</span>";
    align: center
  - name: Description
    data: list
    modify: x.body
css:
  td: "white-space: pre-line;"
````
# Dashboard examples

## Letters (Elternbriefe)

```
type: markdown
content: >-
  ## Letters

  {% for letter in state_attr('sensor.elternportal_vorname', 'letters') %}
  ### #{{ letter.number }}, {{ letter.subject }}
  {{ letter.description }}
      {% if not loop.last %}---{% endif %}
  {% endfor %}
```


## Appointments (Termine)

```
type: markdown
content: >-
  ## Appointments
  {% for appointment in state_attr("sensor.elternportal_vorname", "appointments") %}
  {% if appointment.start.strftime(""%Y%m%d")==appointment.end.strftime("%Y%m%d") %}
  {% set startend = appointment.start.strftime("%d.%m") %}
  {% elif appointment.start.strftime("%Y%m")==appointment.end.strftime("%Y%m") %}
  {% set startend = appointment.start.strftime("%d.") + "-" + appointment.end.strftime("%d.%m") %}
  {% else %}
  {% set startend = appointment.start.strftime("%d.%m") + "-" + appointment.end.strftime("%d.%m") %}
  {% endif %}
  
  {{ startend }}, {{ appointment.title }}  
  {% endfor %}
```


## Conditional

Some cards can be hidden if there are no relevant elements.
```
type: conditional
conditions:
  - condition: numeric_state
    entity: sensor.elternportal_vorname
    attribute: letters_new
    above: 0
card:
  type: markdown
  content: >-
    ## Letters

    {% letters = state_attr('sensor.elternportal_vorname', 'letters') -%}
    {% letters = letters | selectattr('new', 'eq', True) | list -%}
    {% for letter in letters -%}
    ### #{{ letter.number }}, {{ letter.subject }}
    {{ letter.description }}
      {% if not loop.last %}---{% endif %}
    {% endfor %}
```

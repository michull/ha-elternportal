# Dashboard examples

Note:
All sensor names from the following examples must be adapted.
To do this, replace the end `_n` with the appropriate value (e.g. `_1`).


## Appointments (Termine)

This card lists `appointments` in a markdown card.

``` yaml
type: markdown
title: Appointments
content: >-
  {% for appointment in state_attr('sensor.elternportal_appointment_n', 'elements') or [] %}
  {% if appointment.start == appointment.end -%}
  {{ appointment.start.strftime("%m/%d") }}
  {%- else -%}
  {{ appointment.start.strftime("%m/%d") }} to {{
  appointment.end.strftime("%m/%d") }}
  {%- endif -%}
  : {{ appointment.title }}

  {% endfor %}
visibility:
  - condition: numeric_state
    entity: sensor.elternportal_appointment_n
    above: 0
```


## Black board (Schwarzes Brett)

This card lists `blackboards` in a markdown card.

``` yaml
type: markdown
title: Black board
content: >-
  {% for blackboard in state_attr('sensor.elternportal_blackboard_n', 'elements') or [] %}
  **Subject: {{ blackboard.subject }}**
  _Sent: {{ blackboard.sent.strftime("%m/%d") }}_

  {{ blackboard.body }}

  {% if not loop.last %}---{% endif %}
  {% endfor %}
visibility:
  - condition: numeric_state
    entity: sensor.elternportal_blackboard_n
    above: 0
```


## Communication (Mitteilungen)

This card lists `communications` in a markdown card.

``` yaml
type: markdown
title: Communication
content: |-
  {% for message in state_attr('sensor.elternportal_message_n', 'elements') or [] %}
  **Subject: {{ message.subject.strip() }}**
  _Sent: {{ message.sent.strftime("%m/%d %H:%M") }}_

  {{ message.body }}

  {% if not loop.last %}---{% endif %}
  {% endfor %}
visibility:
  - condition: numeric_state
    entity: sensor.elternportal_message_n
    above: 0
```


## Letters (Elternbriefe)

This card lists `letters` in a markdown card.

``` yaml
type: markdown
title: Letters
content: |-
  {% for letter in state_attr('sensor.elternportal_letter_n', 'elements') or [] %}
  **Subject: {{ letter.subject }}**
  _Sent: {{ letter.sent.strftime("%Y-%m-%d %H:%M") }}_

  {{ letter.body }}

  {% if not loop.last %}---{% endif %}
  {% endfor %}
visibility:
  - condition: numeric_state
    entity: sensor.elternportal_letter_n
    above: 0
```


## Class register (Klassenbuch, Hausaufgaben)

This card lists `registers` in a markdown card.

``` yaml
type: markdown
title: Class registers
content: >-
  {% for register in state_attr('sensor.elternportal_register_n', 'elements') or [] %}

  **{{ register.start }} &rarr; {{ register.completion if register.completion
  else register.start }}, {{ register.subject if register.subject else "[no
  subject]" }}, {{ register.teacher }}**

  {{ register.body if register.body else "[no homework entered]" }}

  {% endfor %}
visibility:
  - condition: numeric_state
    entity: sensor.elternportal_register_n
    above: 0
```


## Polls (Umfragen)

This card lists `polls` in a markdown card.

``` yaml
type: markdown
title: Polls
content: >-
  {% for poll in state_attr('sensor.elternportal_poll_n', 'elements') or [] %}
  **{{ poll.title }}{% if poll.attachment %} <ha-icon icon="mdi:attachment"/>{% endif %}**
  *End: {{ poll.end }}, Vote: {{ poll.vote }}*

  {{ poll.detail }}

  {% if not loop.last -%}---{% endif %}
  {% endfor %}
visibility:
  - condition: numeric_state
    entity: sensor.elternportal_poll_n
    above: 0
```


## Sick notes (Krankmeldungen)

This card lists `sicknotes` in a markdown card.

``` yaml
type: markdown
title: Sick notes
content: |-
  {% for sicknote in state_attr('sensor.elternportal_sicknote_n', 'elements') or [] %}
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
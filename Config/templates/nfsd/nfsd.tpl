{%- for dir in dirs -%}
{{dir.path}} {% for cl in dir.clients -%} {{cl.ip_range}}({{cl.options}}) {% endfor %}
{% endfor -%}

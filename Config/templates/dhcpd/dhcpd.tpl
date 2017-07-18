{% if common -%}
{% for option in common.options -%}
option {{option.name}} {{option.value}};
{% endfor -%}

{% if common.default_lease_time -%}
default-lease-time {{common.default_lease_time}};
{% endif -%}
{% if common.max_lease_time -%}
max-lease-time {{common.max_lease_time}};
{% endif -%}

{% if common.ddns_update_style -%}
ddns-update-style {{common.ddns_update_style}};
{% endif -%}

{% if common.authoritative -%}
authoritative;
{% endif -%}

{% if common.log_facility -%}
log-facility {{common.log_facility}};
{% else -%}
log-facility local7;
{% endif -%}
{% endif -%}

{% for subnet in subnets -%}
subnet {{subnet.net}} netmask {{subnet.mask}} {
  {% if subnet.range_start and subnet.range_end -%}
  range {{subnet.range_start}} {{subnet.range_end}};
  {% endif -%}
  {% for option in subnet.options -%}
  option {{option.name}} {{option.value}};
  {% endfor -%}
  {% if subnet.default_lease_time -%}
  default-lease-time {{subnet.default_lease_time}};
  {% endif -%}
  {% if subnet.max_lease_time -%}
  max-lease-time %{subnet.max_lease_time}%;
  {% endif %}
}
{% endfor -%}


{% for host in hosts -%}
host {{host.name}} {
  hardware ethernet {{host.mac}};
  {% if host.filename -%}
  filename {{host.filename}};
  {% endif -%}
  {% if host.fix_ip -%}
  fixed-address {{host.fix_ip}};
  {% endif -%}
  {% if host.server_name -%}
  server-name {{host.server_name}};
  {% endif -%}
}
{% endfor -%}


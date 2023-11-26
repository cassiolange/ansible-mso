#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "community"}

DOCUMENTATION = r"""
---
module: mso_schema_template
short_description: Manage templates in schemas
description:
- Manage templates on Cisco ACI Multi-Site.
author:
- Dag Wieers (@dagwieers)
options:
  tenant:
    description:
    - The tenant used for this template.
    type: str
    required: true
  schema:
    description:
    - The name of the schema.
    type: str
    required: true
  schema_description:
    description:
    - The description of Schema is supported on versions of MSO that are 3.3 or greater.
    type: str
  template_description:
    description:
    - The description of template is supported on versions of MSO that are 3.3 or greater.
    type: str
  template:
    description:
    - The name of the template.
    type: str
    aliases: [ name ]
  display_name:
    description:
    - The name as displayed on the MSO web interface.
    type: str
 template_type:
    description:
     - Deployment Mode. Use stretched-template for Multi-Site or non-stretched-template for Autonomous
     type: str
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ absent, present, query ]
    default: present
notes:
- Due to restrictions of the MSO REST API this module creates schemas when needed, and removes them when the last template has been removed.
seealso:
- module: cisco.mso.mso_schema
- module: cisco.mso.mso_schema_site
extends_documentation_fragment: cisco.mso.modules
"""

EXAMPLES = r"""
- name: Add a new template to a schema
  cisco.mso.mso_schema_template:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    tenant: Tenant 1
    schema: Schema 1
    template: Template 1
    state: present
  delegate_to: localhost

- name: Remove a template from a schema
  cisco.mso.mso_schema_template:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    tenant: Tenant 1
    schema: Schema 1
    template: Template 1
    state: absent
  delegate_to: localhost

- name: Query a template
  cisco.mso.mso_schema_template:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    tenant: Tenant 1
    schema: Schema 1
    template: Template 1
    state: query
  delegate_to: localhost
  register: query_result

- name: Query all templates
  cisco.mso.mso_schema_template:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    tenant: Tenant 1
    schema: Schema 1
    state: query
  delegate_to: localhost
  register: query_result
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.mso.plugins.module_utils.mso import MSOModule, mso_argument_spec, diff_dicts, update_payload


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        l3out_interface_policy=dict(type="str", aliases=["name"], required=True),
        template=dict(type="str", required=True),
        description=dict(type="str", aliases=["descr"]),
        bfd=dict(type="bool", default=False),
        bfd_admin_state=dict(type="str", choices=["enabled", "disabled"], default="enabled"),
        detection_multiplier=dict(type="int", default=3),
        receive_interval=dict(type="int", default=50),
        transmit_interval=dict(type="int", default=50),
        echo_interval=dict(type="int", default=50),
        echo_admin_state=dict(type="str", choices=["enabled", "disabled"], default="enabled"),
        interface_control=dict(type="bool", default=False),
        state = dict(type="str", default="present", choices=["absent", "present", "query"])
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["state", "absent", ["template"]],
            ["state", "present", ["template"]],
        ],
    )

    template = module.params.get("template")
    if template is not None:
        template = template.replace(" ", "")
    state = module.params.get("state")
    l3out_interface_policy =  module.params.get("l3out_interface_policy")
    description = module.params.get("description")
    bfd =  module.params.get("bfd")
    bfd_admin_state = module.params.get("bfd_admin_state")
    detection_multiplier = module.params.get("detection_multiplier")
    receive_interval = module.params.get("receive_interval")
    transmit_interval = module.params.get("transmit_interval")
    echo_interval = module.params.get("echo_interval")
    echo_admin_state = module.params.get("echo_admin_state")
    interface_control = module.params.get("interface_control")



    mso = MSOModule(module)

    template_type = "tenantPolicy"


    templates = mso.request(path="templates/summaries", method="GET", api_version="v1")


    mso.existing = {}

    template_id = ''
    if templates:
        for temp in templates:
            if temp['templateName'] == template and temp['templateType'] == template_type:
                template_id = temp['templateId']

    if not template_id:
        mso.fail_json(msg="Template '{template}' not found".format(template=template))


    
    mso.existing = mso.request(path=f"templates/{template_id}", method="GET", api_version="v1")


    # try to find if the l3out interface policy exist
    l3out_int_pol_exist = False
    try:
        for count, e in enumerate(mso.existing['tenantPolicyTemplate']['template']['l3OutIntfPolGroups']):
            if e['name'] == l3out_interface_policy:
                l3out_int_pol_exist = True
                l3out_int_pol_index = count
    except:
        pass

    if not bfd:
        mso.fail_json("BFD or BFD Multi Hop or OSPF setting need be enabled")

    if state == "query":
        if not mso.existing:
            if template:
                mso.fail_json(msg="Template '{0}' not found".format(template))
            else:
                mso.existing = []
        mso.exit_json()

    template_path = f"templates/{template_id}"

    mso.previous = mso.existing
    if state == "absent":
        mso.proposed = mso.sent = {}
        if l3out_int_pol_exist:
            del mso.existing['tenantPolicyTemplate']['template']['l3OutIntfPolGroups'][l3out_int_pol_index]
            if len(mso.existing['tenantPolicyTemplate']['template']['l3OutIntfPolGroups']) == 0:
                del mso.existing['tenantPolicyTemplate']['template']['l3OutIntfPolGroups']

            if not module.check_mode:
                mso.request(template_path, method="PUT", data=mso.existing)
            mso.existing = {}

    elif state == "present":

        new_l3out_int_pol = {
            "name": l3out_interface_policy,
        }

        if description:
            new_l3out_int_pol['description'] = description

        if bfd:
            new_bfd_entry ={
                "bfdPol":
                    {
                        "adminState": bfd_admin_state,
                        "detectionMultiplier": detection_multiplier,
                        "minRxInterval": receive_interval,
                        "minTxInterval": transmit_interval,
                        "echoAdminState": echo_admin_state,
                        "echoRxInterval": echo_interval,
                        "ifControl": interface_control
                    }
            }
        if not l3out_int_pol_exist:
            if 'l3OutIntfPolGroups' not in mso.existing['tenantPolicyTemplate']['template']:
                mso.existing['tenantPolicyTemplate']['template'].update({'l3OutIntfPolGroups' : []})
            if bfd:
                new_l3out_int_pol.update(new_bfd_entry)

            mso.existing['tenantPolicyTemplate']['template']['l3OutIntfPolGroups'].append(new_l3out_int_pol)
            if not module.check_mode:
                mso.request(template_path, method="PUT", data=mso.existing)
            mso.existing = mso.proposed
        else:
            #interface policy exist, check if need be updated
            current = mso.existing['tenantPolicyTemplate']['template']['l3OutIntfPolGroups'][l3out_int_pol_index].copy()
            if bfd:
                new_l3out_int_pol.update(new_bfd_entry)
                
            diff = diff_dicts(new_l3out_int_pol,current)
            if diff:
                mso.existing['tenantPolicyTemplate']['template']['l3OutIntfPolGroups'][l3out_int_pol_index] = update_payload(diff=diff, payload=current)
                if not module.check_mode:
                    mso.request(template_path, method="PUT", data=mso.existing)
                mso.existing = mso.proposed





    
    

    mso.exit_json()


if __name__ == "__main__":
    main()

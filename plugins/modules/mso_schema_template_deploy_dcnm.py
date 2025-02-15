#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# Copyright: (c) 2022, Cassio Lange (@calange) <calange@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: mso_schema_template_deploy
short_description: Deploy schema templates to sites - DCNM 
description:
- Deploy schema templates to sites.
author:
- Dag Wieers (@dagwieers)
options:
  schema:
    description:
    - The name of the schema.
    type: str
    required: yes
  template:
    description:
    - The name of the template.
    type: str
    required: yes
    aliases: [ name ]
  site:
    description:
    - The name of the site B(to undeploy).
    type: str
  state:
    description:
    - Use C(deploy) to deploy schema template.
    - Use C(status) to get deployment status.
    - Use C(undeploy) to deploy schema template from a site.
    type: str
    choices: [ deploy, status, undeploy ]
    default: deploy
seealso:
- module: cisco.mso.mso_schema_site
- module: cisco.mso.mso_schema_template
extends_documentation_fragment: cisco.mso.modules
'''

EXAMPLES = r'''
- name: Deploy a schema template
  cisco.mso.mso_schema_template_deploy:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    state: deploy
  delegate_to: localhost

- name: Undeploy a schema template
  cisco.mso.mso_schema_template_deploy:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    site: Site 1
    state: undeploy
  delegate_to: localhost

- name: Get deployment status
  cisco.mso.mso_schema:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    state: status
  delegate_to: localhost
  register: status_result
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.mso.plugins.module_utils.mso import MSOModule, mso_argument_spec


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        schema=dict(type='str', required=True),
        template=dict(type='str', required=True, aliases=['name']),
        site=dict(type='str'),
        state=dict(type='str', default='deploy', choices=['deploy', 'status', 'undeploy']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'undeploy', ['site']],
        ],
    )

    schema = module.params.get('schema')
    template = module.params.get('template').replace(' ', '')
    site = module.params.get('site')
    state = module.params.get('state')

    mso = MSOModule(module)

    # Get schema id
    schema_id = mso.lookup_schema(schema)

    payload = dict(
        schemaId=schema_id,
        templateName=template,
    )

    qs = None
    if state == 'deploy':
        # path = 'execute/schema/{0}/template/{1}'.format(schema_id, template)
        path = 'mso/api/v1/task'
    elif state == 'status':
        path = 'status/schema/{0}/template/{1}'.format(schema_id, template)
    elif state == 'undeploy':
        path = 'mso/api/v1/task'
        site_id = mso.lookup_site(site)
        # qs = dict(undeploy=site_id)
        payload.update({'undeploy': []})
        payload['undeploy'].append(site_id)


    if state in ['deploy', 'undeploy']:
        status = mso.request(path, method='POST', data=payload, qs=qs, api_version=None)
        mso.exit_json(**status)
    elif state == 'status':
        status = mso.request(path, method='GET', data=payload, qs=qs, api_version=None)
        mso.exit_json(**status)
    else:
        mso.exit_json()


if __name__ == "__main__":
    main()

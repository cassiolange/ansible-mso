#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "community"}

DOCUMENTATION = r"""
---
module: mso_schema_template_external_epg
short_description: Manage external EPGs in schema templates
description:
- Manage external EPGs in schema templates on Cisco ACI Multi-Site.
author:
- Dag Wieers (@dagwieers)
options:
  schema:
    description:
    - The name of the schema.
    type: str
    required: true
  template:
    description:
    - The name of the template.
    type: str
    required: true
  external_epg:
    description:
    - The name of the external EPG to manage.
    type: str
    aliases: [ name, externalepg ]
  description:
    description:
    - The description of external EPG is supported on versions of MSO that are 3.3 or greater.
    type: str
  type:
    description:
    - The type of external epg.
    - anp needs to be associated with external epg when the type is cloud.
    - l3out can be associated with external epg when the type is on-premise.
    type: str
    choices: [ on-premise, cloud ]
    default: on-premise
  display_name:
    description:
    - The name as displayed on the MSO web interface.
    type: str
  vrf:
    description:
    - The VRF associated with the external epg.
    type: dict
    suboptions:
      name:
        description:
        - The name of the VRF to associate with.
        required: true
        type: str
      schema:
        description:
        - The schema that defines the referenced VRF.
        - If this parameter is unspecified, it defaults to the current schema.
        type: str
      template:
        description:
        - The template that defines the referenced VRF.
        - If this parameter is unspecified, it defaults to the current template.
        type: str
  l3out:
    description:
    - The L3Out associated with the external epg.
    type: dict
    suboptions:
      name:
        description:
        - The name of the L3Out to associate with.
        required: true
        type: str
      schema:
        description:
        - The schema that defines the referenced L3Out.
        - If this parameter is unspecified, it defaults to the current schema.
        type: str
      template:
        description:
        - The template that defines the referenced L3Out.
        - If this parameter is unspecified, it defaults to the current template.
        type: str
  anp:
     description:
     - The anp associated with the external epg.
     type: dict
     suboptions:
       name:
         description:
         - The name of the anp to associate with.
         required: true
         type: str
       schema:
         description:
         - The schema that defines the referenced anp.
         - If this parameter is unspecified, it defaults to the current schema.
         type: str
       template:
         description:
         - The template that defines the referenced anp.
         - If this parameter is unspecified, it defaults to the current template.
         type: str
  preferred_group:
    description:
    - Preferred Group is enabled for this External EPG or not.
    type: bool
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ absent, present, query ]
    default: present
extends_documentation_fragment: cisco.mso.modules
"""

EXAMPLES = r"""
- name: Add a new external EPG
  cisco.mso.mso_schema_template_external_epg:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    external_epg: External EPG 1
    vrf:
      name: VRF
      schema: Schema 1
      template: Template 1
    state: present
  delegate_to: localhost

- name: Add a new external EPG with external epg in cloud
  cisco.mso.mso_schema_template_external_epg:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    external_epg: External EPG 1
    type: cloud
    vrf:
      name: VRF
      schema: Schema 1
      template: Template 1
    anp:
      name: ANP1
      schema: Schema 1
      template: Template 1
    state: present
  delegate_to: localhost

- name: Remove an external EPG
  cisco.mso.mso_schema_template_external_epg:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    external_epg: external EPG1
    state: absent
  delegate_to: localhost

- name: Query a specific external EPGs
  cisco.mso.mso_schema_template_external_epg:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    external_epg: external EPG1
    state: query
  delegate_to: localhost
  register: query_result

- name: Query all external EPGs
  cisco.mso.mso_schema_template_external_epg:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    template: Template 1
    state: query
  delegate_to: localhost
  register: query_result
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.mso.plugins.module_utils.mso import MSOModule, mso_argument_spec, mso_reference_spec, get_template_id, diff_dicts, update_payload


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        schema=dict(type="str", required=True),
        template=dict(type="str", required=True),
        external_epg=dict(type="str", aliases=["name", "externalepg"]),  # This parameter is not required for querying all objects
        description=dict(type="str"),
        display_name=dict(type="str"),
        vrf=dict(type="dict", options=mso_reference_spec(), required=True),
        l3out=dict(type="dict", options=mso_reference_spec(), required=True),
        anp=dict(type="dict", options=mso_reference_spec()),
        preferred_group=dict(type="bool", default=False),
        type=dict(type="str", default="on-premise", choices=["on-premise", "cloud"]),
        site=dict(type="str", required=True),
        qos_level=dict(type="str", default="unspecified", choices=["level1","level2","level3","level4","level5","level6","unspecified"]),
        state=dict(type="str", default="present", choices=["absent", "present", "query"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["state", "absent", ["external_epg"]],
            ["state", "present", ["external_epg", "vrf"]],
            ["type", "cloud", ["anp"]],
        ],
    )

    schema = module.params.get("schema")
    template = module.params.get("template").replace(" ", "")
    external_epg = module.params.get("external_epg")
    description = module.params.get("description")
    display_name = module.params.get("display_name")
    vrf = module.params.get("vrf")
    if vrf is not None and vrf.get("template") is not None:
        vrf["template"] = vrf.get("template").replace(" ", "")
    l3out = module.params.get("l3out")
    if l3out is not None and l3out.get("template") is not None:
        l3out["template"] = l3out.get("template").replace(" ", "")
    anp = module.params.get("anp")
    if anp is not None and anp.get("template") is not None:
        anp["template"] = anp.get("template").replace(" ", "")
    preferred_group = module.params.get("preferred_group")
    type_ext_epg = module.params.get("type")
    state = module.params.get("state")
    site = module.params.get("site")
    qos_level = module.params.get("qos_level")
    
    mso = MSOModule(module)

    # Get schema objects
    schema_id, schema_path, schema_obj = mso.query_schema(schema)
    vrf_schema_id, vrf_schema_path, vrf_schema_obj =  mso.query_schema(vrf['schema'])

    # Get template
    templates = [t.get("name") for t in schema_obj.get("templates")]
    if template not in templates:
        mso.fail_json(msg="Provided template '{0}' does not exist. Existing templates: {1}".format(template, ", ".join(templates)))
    template_idx = templates.index(template)

    # Get external EPGs
    external_epgs = [e.get("name") for e in schema_obj.get("templates")[template_idx]["externalEpgs"]]
    
    external_epg_exist = False
    if external_epg is not None and external_epg in external_epgs:
        external_epg_idx = external_epgs.index(external_epg)
        external_epg_exist = True
        
        # mso.existing = schema_obj.get("templates")[template_idx]["externalEpgs"][external_epg_idx]
        # if "externalEpgRef" in mso.existing:
        #     del mso.existing["externalEpgRef"]
        # if "vrfRef" in mso.existing:
        #     mso.existing["vrfRef"] = mso.dict_from_ref(mso.existing.get("vrfRef"))
        # if "l3outRef" in mso.existing:
        #     mso.existing["l3outRef"] = mso.dict_from_ref(mso.existing.get("l3outRef"))
        # if "anpRef" in mso.existing:
        #     mso.existing["anpRef"] = mso.dict_from_ref(mso.existing.get("anpRef"))

    # Get site
    site_id = mso.lookup_site(site)

    # Get site_idx
    if not schema_obj.get("sites"):
        mso.fail_json(msg="No site associated with template '{0}'. Associate the site with the template using mso_schema_site.".format(template))
    sites = [(s.get("siteId"), s.get("templateName")) for s in schema_obj.get("sites")]
    if (site_id, template) not in sites:
        mso.fail_json(msg="Provided site/template '{0}-{1}' does not exist. Existing sites/templates: {2}".format(site, template, ", ".join(sites)))
        
    # Schema-access uses indexes
    site_idx = sites.index((site_id, template))
    # Path-based access uses site_id-template
    site_template = "{0}-{1}".format(site_id, template)

    all_templates = mso.request(path="templates/summaries", method="GET", api_version="v1")


    l3out_template_id = get_template_id(template_name=l3out['template'], template_type='l3out', template_dict=all_templates)

    if not l3out_template_id:
        mso.fail_json(msg="L3out Template '{template}' not found".format(template=l3out['template']))

    l3out_template = mso.request(path=f"templates/{l3out_template_id}", method="GET", api_version="v1")
    
    # try to find if the l3out exist
    l3out_uuid = ''
    try:
        for count, e in enumerate(l3out_template['l3outTemplate']['l3outs']):
            if e['name'] == l3out['name']:
                l3out_uuid = e['uuid']
    except:
        pass


    if not l3out_uuid:
        mso.fail_json(msg="L3out '{l3out}' not found".format(l3out=l3out['name']))

    mso.existing = mso.request(path=f"schemas/{schema_id}", method="GET", api_version="v1")
    mso.previous = mso.existing

    if state == "query":
        if external_epg is None:
            mso.existing = schema_obj.get("templates")[template_idx]["externalEpgs"]
        elif not mso.existing:
            mso.fail_json(msg="External EPG '{external_epg}' not found".format(external_epg=external_epg))
        mso.exit_json()



    # mso.previous = mso.existing
    if state == "absent":
        mso.proposed = mso.sent = {}
        if external_epg_exist:
            del mso.existing['templates'][template_idx]['externalEpgs'][external_epg_idx]
            del mso.existing['sites'][site_idx]['externalEpgs'][external_epg_idx]

            if not module.check_mode:
                mso.request(schema_path, method="PUT", data=mso.existing)
            mso.existing = {}



    elif state == "present":


        vrf_ref = '/schemas/{0}/templates/{1}/vrfs/{2}'.format(vrf_schema_id,vrf['template'],vrf['name'])
        external_epg_ref = '/schemas/{0}/templates/{1}/externalEpgs/{2}'.format(schema_id,template,external_epg)

        new_ext_epg = {
            "displayName": external_epg,
            "name": external_epg,
            "vrfRef": vrf_ref,
            # "l3outRef": "",
            # "anpRef": "",
            "externalEpgRef": external_epg_ref,
            # "id": external_epg_ref,
            # "type": "externalEpg",
            "preferredGroup": preferred_group,
            "subnets": [],
            "contractRelationships": [],
            "extEpgType": "on-premise",
            "selectors": [],
            # "routeReachabilityInternetType": "internet",
            # "isSrMpls": False,
            "qosPriority": qos_level,
            "description": "",
            "tagAnnotations": []
        }
        if description:
            new_ext_epg['description'] = description

        new_ext_epg_site = {
            "subnets": [],
            "l3outRef": l3out_uuid,
            "routeReachabilityInternetType": "internet",
            "l3outDn": "",
            "externalEpgRef": external_epg_ref
        }


        # mso.sanitize(payload, collate=True)
        if not external_epg_exist:
            #external egp doesn't exist, so create and associate the site.
            if 'externalEpgs' not in mso.existing['templates'][template_idx]:
                mso.existing['templates'][template_idx].update({'externalEpgs' : []})
            mso.existing['templates'][template_idx]['externalEpgs'].append(new_ext_epg)

            if 'externalEpgs' not in mso.existing['sites'][site_idx]:
                mso.existing['sites'][site_idx].update({'externalEpgs': []})
            mso.existing['sites'][site_idx]['externalEpgs'].append(new_ext_epg_site)
            if not module.check_mode:
                mso.request(schema_path, method="PUT", data=mso.existing)
            mso.existing = mso.proposed
        else:
            current = mso.existing['templates'][template_idx]['externalEpgs'][external_epg_idx].copy()
            diff = diff_dicts(new_ext_epg,current,exclude_key="subnets,contractRelationships")
            current_site = mso.existing['sites'][site_idx]['externalEpgs'][external_epg_idx].copy()
            diff_site = diff_dicts(new_ext_epg_site,current_site,exclude_key="subnets,contractRelationships")
            if diff or diff_site:
                if diff:
                    mso.existing['templates'][template_idx]['externalEpgs'][external_epg_idx] = update_payload(diff=diff, payload=current)
                if diff_site:
                    mso.existing['sites'][site_idx]['externalEpgs'][external_epg_idx] = update_payload(diff=diff_site, payload=current_site)
                if not module.check_mode:
                    mso.request(schema_path, method="PUT", data=mso.existing)
                mso.existing = mso.proposed
        



    
    mso.exit_json()


if __name__ == "__main__":
    main()

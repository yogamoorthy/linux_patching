#!/usr/bin/env python3
from ansible.module_utils.basic import AnsibleModule
import requests
import time
import json
import re

DOCUMENTATION = """
---
module: fixpackinfo
author:
    - "William Vanderlip-Mclean <wmclean@hy-vee.com>"
short_description: Get info about Manhattan Patches
description:
    - Call the Central MMC server to query to FixpackManagmentService. This can
      pull information about any cluster that is fedderated.
"""

EXAMPLES = """
- name: Report the Full Fixpack
  fixpack:
    conduct: report
    username: awesomeuser
    password: awesomepassword
    cluster: DM_OM-Fill
    hostname: dlwdmomfapp1
    folder: /manh/apps/scope/wm
    mmc: https://mmc2017-v.hy-vee.net:3443

- name: Check if Fixpack in installed for Java
  fixpack:
    conduct: check_version
    version: 0044
    language: java
    username: awesomeuser
    password: awesomepassword
    cluster: DM_OM-Fill
    hostname: dlwdmomfapp1
    folder: /manh/apps/scope/wm
    mmc: https://mmc2017-v.hy-vee.net:3443
"""

RETURN = """
java:
    description: List of java fixpacks that are installed
    type: str
    returned: always
cpp:
    description: List of cpp fixpacks that are installed
    type: str
    retuned: somtimes
"""


class FixPack:
    def __init__(self, module, result):
        self.module = module
        self.username = module.params["username"]
        self.password = module.params["password"]
        self.cluster = module.params["cluster"]
        self.hostname = module.params["hostname"]
        self.folder = module.params["folder"]
        self.conduct = module.params["conduct"]
        self.incoming_version = module.params["version"]
        self.language = module.params["language"]
        self.mmc = module.params["mmc"]
        self.application = self.folder.split("/")[-1]
        self.changed = False
        self.epoch_now = int(time.time())
        self.results = result
        self.session = requests.session()

    def run(self):
        self._login()
        self._appCheck()
        self._gather()
        if self.conduct == "check_version":
            self._versionCheck()
        return self.results

    def _login(self):
        login_url = "{}/j_spring_security_check".format(self.mmc)
        payload = {"j_username": self.username, "j_password": self.password}

        try:
            self.session.post(login_url, verify=False, data=payload)
        except requests.exceptions.ConnectionError:
            self.module.fail_json(msg="Unable to login")

    def _appCheck(self):
        applist_url = "{}/webaccess/smcService/applications/list".format(self.mmc)
        applist_params = (
            ("cid", self.cluster),
            ("_dc", self.epoch_now),
            ("apps", "1"),
        )

        applist_request = self.session.get(
            applist_url, params=applist_params, verify=False
        )

        app_list = []
        for i in applist_request.json():
            if self.hostname in i["host"]:
                app_list.append("{}".format(i["app"]))

        if self.application not in app_list:
            msg = "{} not found in {} for {}".format(
                self.application, self.cluster, self.hostname
            )
            self.module.fail_json(msg=msg)

    def _versionCheck(self):
        if self.results["{}".format(self.language)] is None:
            self.results["can_update"] = False
        elif int(self.incoming_version) > int(
            re.search(r"\d+", self.results["{}".format(self.language)][0].split()[-1])[
                0
            ]
        ):
            self.results["can_update"] = True
        else:
            self.results["can_update"] = False

        if self.results["{}".format(self.language)] is None:
            self.results["can_remove"] = False
        elif int(self.incoming_version) == int(
            re.search(r"\d+", self.results["{}".format(self.language)][0].split()[-1])[
                0
            ]
        ):
            self.results["can_remove"] = True
        else:
            self.results["can_remove"] = False

    def _gather(self):
        fixpack_url = "{}/webaccess/FixpackMgmtViewService".format(self.mmc)
        params = (
            ("cid", self.cluster),
            ("hostName", self.hostname),
            ("folder", self.folder),
            ("_dc", self.epoch_now),
        )

        try:
            fixpack_request = self.session.get(fixpack_url, params=params, verify=False)
            fixpack_content = fixpack_request.json()
        except json.decoder.JSONDecodeError:
            self.module.fail_json(
                msg="Error: Unxepected.... This was due to the inability to read the json."
            )

        try:
            java_patches = []
            for patch in fixpack_content["JAVA"]:
                java_patches.append("{} {}".format(patch["timestamp"], patch["name"]))
            self.results["java"] = java_patches
            self.results["changed"] = True
        except KeyError:
            self.results["java"] = None

        try:
            tao_patches = []
            for patch in fixpack_content["TAO"]:
                tao_patches.append("{} {}".format(patch["timestamp"], patch["name"]))
            self.results["cpp"] = tao_patches
            self.results["changed"] = True
        except KeyError:
            self.results["cpp"] = None

        if self.module.check_mode:
            self.module.exit_json(changed=self.changed)


def main():
    argument_spec = dict(
        username=dict(type="str", required=True),
        password=dict(type="str", required=True),
        cluster=dict(type="str", required=True),
        hostname=dict(type="str", required=True),
        folder=dict(type="str", required=True),
        mmc=dict(type="str", required=True),
        conduct=dict(type="str", required=True),
        version=dict(type="str", required=False),
        language=dict(type="str", required=False),
    )

    result = dict()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    obj_Fixpack = FixPack(module, result)
    response = obj_Fixpack.run()
    module.exit_json(**response)


if __name__ == "__main__":
    main()

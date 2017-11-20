#!/usr/bin/env python3
#
# Copyright (c) 2017 Katerina Koutlia, Roberto Riggio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

"""Application tracking pool-wide power consumption."""

import time

from empower.core.app import EmpowerApp
from empower.core.app import DEFAULT_PERIOD
from empower.lvapp.lvappconnection import LVAPPConnection
from empower.main import RUNTIME


class RANSlicing(EmpowerApp):
    """Application to ask for the transmission times of eacj tenant
    and (soon) to apply the weight algorithm and change the weights for the WADRR.

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default,  5000ms)

    Example:

        ./empower-runtime.py apps.ranslicing.ranslicing --tenant_id=48c7d783-cbc1-4d45-981e-8ace7d870031
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.weights_default = 100
        self.weights = []
        self.times = {}
        self.time = 0

    def loop(self):
        """ Periodic job. """

        print("------- entered loop to call wadrr request --------")

        for wtp in RUNTIME.wtps:
            #print(wtp)
            LVAPPConnection.send_wadrr_request(self, wtp, self.tenant_id)
            print("took times")

            self.get_time()

    def get_time(self):

     for wtp in RUNTIME.wtps:    
        for tenant_id in RUNTIME.tenants:
            tenant = RUNTIME.tenants[tenant_id]
            if(self.tenant_id == tenant_id):
                print("tenants equal")
                print(tenant.tenant_name)
                self.time = RUNTIME.wtps[wtp].response[tenant.tenant_name]
                print(self.time)




def launch(tenant_id, every=5000):
    return RANSlicing(tenant_id=tenant_id, every=every)

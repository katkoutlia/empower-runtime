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
from empower.main import RUNTIME


class WeightApp(EmpowerApp):
    """Application to apply the weight algorithm based on the tenant trasnmission
    times and traffic.
    Before executing it, the apps.wadrrdata.wadrrdata is needed to be executed previously
    in each tenant.

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default,  7000ms)

    Example:

        ./empower-runtime.py apps.weightapp.weightapp --tenant_id=48c7d783-cbc1-4d45-981e-8ace7d870031
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_ssid = RUNTIME.tenants[self.tenant_id].tenant_name

        self.times = {}
        self.tenant_traffic = {}

        self.weights_default = 100
        self.weights = {}

        
    def loop(self):
        """ Periodic job. """

        print("------- WEIGHT APP --------")

        for wtp in RUNTIME.wtps:
            
            """ Get data received from the wtp (tenant transmission times and traffic) """
            for tenant_id in RUNTIME.tenants:
                tenant = RUNTIME.tenants[tenant_id]
                if tenant.tenant_name in RUNTIME.wtps[wtp].response:
                    self.times[tenant.tenant_name] = RUNTIME.wtps[wtp].response[tenant.tenant_name]
                    self.log.info("Transmission time of tenant %s %u", tenant.tenant_name, self.times[tenant.tenant_name])


                self.tenant_traffic[tenant.tenant_name] = 0

                for lvap in RUNTIME.tenants[tenant_id].lvaps:
                    if lvap in RUNTIME.wtps[wtp].rx_packets_response:
                        self.tenant_traffic[tenant.tenant_name] += RUNTIME.wtps[wtp].rx_packets_response[lvap][0]

                self.log.info("Traffic of tenant %s %d", tenant.tenant_name, self.tenant_traffic[tenant.tenant_name])


def launch(tenant_id, every=7000):
    return WeightApp(tenant_id=tenant_id, every=every)

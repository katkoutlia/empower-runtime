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
    """Application to request each tenants transmission times and received traffic
    and (soon) to apply the weight algorithm and change the weights for the WADRR.

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default,  5000ms)

    Example:

        ./empower-runtime.py apps.ranslicing.ranslicing --tenant_id=48c7d783-cbc1-4d45-981e-8ace7d870031
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_ssid = RUNTIME.tenants[self.tenant_id].tenant_name
        
        self.times = {}
        self.rx_packets = {}

        self.tenant_traffic = {}

        self.weights_default = 100
        self.weights = []

        
    def loop(self):
        """ Periodic job. """

        print("------- entered loop to call wadrr request --------")

        for wtp in RUNTIME.wtps:
            
            """ Request transmission times from the wtp """
            LVAPPConnection.send_wadrr_request(self, wtp, self.tenant_id)

            """ Get transmission times for each tenant """
            self.get_time(wtp)

            """ Get traffic for each lvap """
            self.wtp_bin_counter(every=self.every,
                                 wtp=wtp,
                                 callback=self.counters_callback)

            """ Store traffic for each tenant """
            self.store_traffic(wtp)

            """ Execute the weight algorithm only for the first tenant of the list """
            for tenant_id in RUNTIME.tenants:
                tenant = RUNTIME.tenants[tenant_id]
                #print(tenant.tenant_name)
                break

            if(self.tenant_id == tenant_id):
                self.weight_algorithm(wtp, tenant_id)


    def get_time(self, wtp):
      
        if self.current_ssid in RUNTIME.wtps[wtp].response:
            self.times[self.current_ssid] = RUNTIME.wtps[wtp].response[self.current_ssid]
            print(self.times[self.current_ssid])


    def store_traffic(self, wtp):
        #sum traffic of lvaps of this tenant 

        #In every loop I add all the traffic of the LVAPs of this tenant
        self.tenant_traffic[self.current_ssid] = 0

        for lvap in RUNTIME.tenants[self.tenant_id].lvaps:
            if lvap in RUNTIME.wtps[wtp].rx_packets_response:
                for packets in RUNTIME.wtps[wtp].rx_packets_response[lvap]:
                    self.rx_packets[lvap] = packets
                    self.tenant_traffic[self.current_ssid] += packets

        print(self.tenant_traffic[self.current_ssid])


    def weight_algorithm(self, wtp, tenant_id):

        tenant = RUNTIME.tenants[tenant_id]
        print("Calculate weights only for tenant:", tenant.tenant_name)


    def counters_callback(self, stats):
        """ New stats available. """

        self.log.info("New counters received from %s" % stats.wtp)

def launch(tenant_id, every=5000):
    return RANSlicing(tenant_id=tenant_id, every=every)

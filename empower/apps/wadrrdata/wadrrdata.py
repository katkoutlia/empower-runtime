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


class CollectData(EmpowerApp):
    """Application to request each tenants transmission times and traffic.
    Data will be processed by apps.weightapp.weightapp

    Command Line Parameters:

        tenant_id: tenant id
        every: loop period in ms (optional, default,  5000ms)

    Example:

        ./empower-runtime.py apps.wadrrdata.wadrrdata --tenant_id=48c7d783-cbc1-4d45-981e-8ace7d870031
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        self.current_ssid = RUNTIME.tenants[self.tenant_id].tenant_name
        
        self.times = {}
        self.tenant_traffic = {}

        self.wtpup(callback=self.wtp_up_callback)

        
    def loop(self):
        """ Periodic job. """

        for wtp in RUNTIME.wtps:
            
            """ Request transmission times from the wtp """
            LVAPPConnection.send_wadrr_request(self, wtp, self.tenant_id)


    def wtp_up_callback(self, wtp):
        """ New LVAP. """

        self.wtp_bin_counter(every=self.every,
                             wtp=wtp.addr,
                             callback=self.counters_callback)


    def counters_callback(self, stats):
        """ New stats available. """

        self.log.info("New counters received from %s" % stats.wtp)


def launch(tenant_id, every=5000):
    return CollectData(tenant_id=tenant_id, every=every)

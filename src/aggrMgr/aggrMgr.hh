/* Copyright 2008, 2009 (C) Nicira, Inc.
 *
 * This file is part of NOX.
 *
 * NOX is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * NOX is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NOX.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef ROUTING_HH
#define ROUTING_HH 1

#include <boost/shared_ptr.hpp>
#include <boost/shared_array.hpp>
#include <list>
#include <queue>
#include <sstream>
#include <vector>

#include "linkInfo.hh"
#include "port.hh"
#include "component.hh"
#include "event.hh"
#include "flow.hh"
#include "hash_map.hh"
#include "hash_set.hh"
#include "discovery/link-event.hh"
#include "netinet++/ethernetaddr.hh"
#include "openflow/openflow.h"
#include "topology/topology.hh"
#include "coreapps/messenger/messenger.hh"

 /*
 * All integer values are stored in host byte order and should be passed in as
 * such as well.
 *
 */

namespace vigil {
namespace applications {

class AggrMgr
    : public container::Component {

public:
    LinkInfoList links;

    AggrMgr(const container::Context*,
                   const xercesc::DOMNode*);
    // for python
    AggrMgr();
    ~AggrMgr() { }

    static void getInstance(const container::Context*, AggrMgr*&);

    void configure(const container::Configuration*);
    void install();

private:
    /* Not essential now
    Topology *topology;
    */

    Disposition handle_link_event(const Event&);
    Disposition handle_msg_event(const Event&);
};

}
}

#endif

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
#include "aggrMgr.hh"

#include <boost/bind.hpp>
#include <inttypes.h>

#include "assert.hh"
#include "openflow/nicira-ext.h"
#include "vlog.hh"

namespace vigil {
namespace applications {

static Vlog_module lg("aggrMgr");

// Constructor - initializes openflow packet memory used to setup route

AggrMgr::AggrMgr(const container::Context* c,
                               const xercesc::DOMNode* d)
    : container::Component(c), topology(0), nat(0), len_flow_actions(0),
      num_actions(0), ofm(0)
{
    max_output_action_len = get_max_action_len();
}

void
AggrMgr::getInstance(const container::Context* ctxt,
                            AggrMgr*& r)
{
    r = dynamic_cast<AggrMgr*>
        (ctxt->get_by_interface(container::Interface_description
                                (typeid(AggrMgr).name())));
}


void
AggrMgr::configure(const container::Configuration*)
{
    resolve(topology);
    resolve(nat);
    register_handler<Link_event>
        (boost::bind(&AggrMgr::handle_link_change, this, _1));
    register_handler<CH_msg_event>
        (boost::bind(&AggrMgr::handle_CH_msg, this, _1));
}

void
AggrMgr::install()
{}

Disposition
AggrMgr::handle_link_change(const Event& e)
{
    const Link_event& le = assert_cast<const Link_event&>(e);

    RouteQueue new_candidates;
    RoutePtr route(new Route());
    Link tmp = { le.dpdst, le.sport, le.dport };
    route->id.src = le.dpsrc;
    route->id.dst = le.dpdst;
    route->path.push_back(tmp);
    if (le.action == Link_event::REMOVE) {
        cleanup(route, true);
        fixup(new_candidates, true);
    } else if (le.action == Link_event::ADD) {
        RoutePtr left_subpath(new Route());
        RoutePtr right_subpath(new Route());
        left_subpath->id.src = left_subpath->id.dst = le.dpsrc;
        right_subpath->id.src = right_subpath->id.dst = le.dpdst;
        add(local_routes, route);
        add(left_local, route, right_subpath);
        add(right_local, route, left_subpath);
        new_candidates.push(route);
        fixup(new_candidates, false);
    } else {
        VLOG_ERR(lg, "Unknown link event action %u", le.action);
    }

    return CONTINUE;
}

Disposition
AggrMgr::handle_CH_msg(const Event& e)
{
    const CH_event& smsg = assert_cast<const CH_event&>(e);
    return STOP;
}

}
}

REGISTER_COMPONENT(vigil::container::Simple_component_factory
                   <vigil::applications::AggrMgr>,
                   vigil::applications::AggrMgr);

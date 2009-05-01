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
    : container::Component(c)
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
    /* Commented for now. It seems possible to just use the
     * link_event messages to maintain topology information
     * 
    resolve(topology);
     */
    register_handler<Link_event>
        (boost::bind(&AggrMgr::handle_link_event, this, _1));
    register_handler<Msg_event>
        (boost::bind(&AggrMgr::handle_msg_event, this, _1));
}

void
AggrMgr::install()
{}

Disposition
AggrMgr::handle_link_event(const Event& e)
{
    const Link_event& le = assert_cast<const Link_event&>(e);

    LIL_iterator itr;
    LinkInfo li = {le.dpsrc, le.dpdst, le.sport;, le.dport};
    for (itr = links.begin(); itr != links.end(); itr++) 
        if ((*itr) == li)
            break;

    if (le.action == Link_event::ADD) {
        if (itr == links.end())
            li.insert(li);

    } else if (le.action == Link_event::REMOVE) {
        erase(itr);

    } else {
        VLOG_ERR(lg, "Unknown link event action %u", le.action);
    }

    return CONTINUE;
}

Disposition
AggrMgr::handle_msg_event(const Event& e)
{
    const Msg_event& me = assert_cast<const Msg_event&>(e);

    switch (me.msg->type)
    {
        case SFA_START_SLICE:
            char slice_name[ntohs(me.msg->length)-2];
            memcpy(slice_name, me.msg->body, ntohs(me.msg->length)-3);
            slice_name[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Start_slice %s", slice_name);

            return STOP;

        case SFA_STOP_SLICE:
            char slice_name[ntohs(me.msg->length)-2];
            memcpy(slice_name, me.msg->body, ntohs(me.msg->length)-3);
            slice_name[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Stop_slice %s", slice_name);

            return STOP;

        case SFA_CREATE_SLICE:
            char slice_name[ntohs(me.msg->length)-2];
            memcpy(slice_name, me.msg->body, ntohs(me.msg->length)-3);
            slice_name[ntohs(me.msg->length)-3] = '\0';

            /* After the first null, we have the RSpec string */
            char *rspec_str = slice_name[strlen(slice_name)];
            
            VLOG_DBG(lg, "Create_slice %s with rspec_str %s", slice_name, rspec_str);

            return STOP;

        case SFA_DELETE_SLICE:
            char slice_name[ntohs(me.msg->length)-2];
            memcpy(slice_name, me.msg->body, ntohs(me.msg->length)-3);
            slice_name[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Delete_slice %s", slice_name);

            return STOP;

        case SFA_LIST_SLICES:
            VLOG_DBG(lg, "List_slices");

            return STOP;

        case SFA_LIST_COMPONENTS:
            VLOG_DBG(lg, "List_components");

            return STOP;

        case SFA_REGISTER:
            char record_info[ntohs(me.msg->length)-2];
            memcpy(record_info, me.msg->body, ntohs(me.msg->length)-3);
            record_info[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Register_record %s", record_info);

            return STOP;

        case SFA_REBOOT_COMPONENT:
            char component_name[ntohs(me.msg->length)-2];
            memcpy(component_name, me.msg->body, ntohs(me.msg->length)-3);
            component_name[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Reboot_component %s", component_name);

            return STOP;

    }

    return CONTINUE;
}

}
}

REGISTER_COMPONENT(vigil::container::Simple_component_factory
                   <vigil::applications::AggrMgr>,
                   vigil::applications::AggrMgr);

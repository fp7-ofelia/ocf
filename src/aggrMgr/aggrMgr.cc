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
#include "message.h"

#include <boost/bind.hpp>
#include <inttypes.h>

#include "assert.hh"
#include "openflow/nicira-ext.h"
#include "vlog.hh"

using namespace std;

namespace vigil {
namespace applications {

static Vlog_module lg("aggrMgr");

// Constructor - initializes openflow packet memory used to setup route

AggrMgr::AggrMgr(const container::Context* c,
                               const xercesc::DOMNode* d)
    : container::Component(c)
{
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

    LinkInfoList_iterator itr;
    LinkInfo li = {le.dpsrc, le.dpdst, le.sport, le.dport};
    for (itr = links.begin(); itr != links.end(); itr++) 
        if ((*itr) == li)
            break;

    if (le.action == Link_event::ADD) {
        if (itr == links.end())
            links.push_back(li);

    } else if (le.action == Link_event::REMOVE) {
        links.erase(itr);

    } else {
        VLOG_ERR(lg, "Unknown link event action %u", le.action);
    }

    return CONTINUE;
}

Disposition
AggrMgr::handle_msg_event(const Event& e)
{
    const Msg_event& me = assert_cast<const Msg_event&>(e);
    char *rspec_str = NULL, *slice_id = NULL;
    Array_buffer *buf = NULL;

    switch (me.msg->type)
    {
        case SFA_START_SLICE:
            slice_id = (char *)malloc(ntohs(me.msg->length)-2);
            memcpy(slice_id, me.msg->body, ntohs(me.msg->length)-3);
            slice_id[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Start_slice %s", slice_id);

            free(slice_id);
            return STOP;

        case SFA_STOP_SLICE:
            slice_id = (char *)malloc(ntohs(me.msg->length)-2);
            memcpy(slice_id, me.msg->body, ntohs(me.msg->length)-3);
            slice_id[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Stop_slice %s", slice_id);

            free(slice_id);
            return STOP;

        case SFA_CREATE_SLICE:
            slice_id = (char *)malloc(ntohs(me.msg->length)-2);
            memcpy(slice_id, me.msg->body, ntohs(me.msg->length)-3);
            slice_id[ntohs(me.msg->length)-3] = '\0';

            /* After the first null, we have the RSpec string */
            rspec_str = slice_id + strlen(slice_id);
            
            VLOG_DBG(lg, "Create_slice %s with rspec_str %s", slice_id, rspec_str);

            free(slice_id);
            return STOP;

        case SFA_DELETE_SLICE:
            slice_id = (char *)malloc(ntohs(me.msg->length)-2);
            memcpy(slice_id, me.msg->body, ntohs(me.msg->length)-3);
            slice_id[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Delete_slice %s", slice_id);

            free(slice_id);
            return STOP;

        case SFA_LIST_SLICES:
            VLOG_DBG(lg, "List_slices");

            return STOP;

        case SFA_LIST_COMPONENTS:
            VLOG_DBG(lg, "List_components");

            rspec_str = (char *) malloc(MESSENGER_BUFFER_SIZE);
            memset(rspec_str, 0, MESSENGER_BUFFER_SIZE);
            strcat(rspec_str, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
            strcat(rspec_str, "<RSpec>\n");

            for (LinkInfoList_iterator itr = links.begin(); itr != links.end(); itr++) {
                strcat(rspec_str, "<linkInfo>\n");
		        sprintf(rspec_str + strlen(rspec_str), "<srcPoint><dataPathId>%lx</dataPathId><port>%d</port></srcPoint>\n", (*itr).dpsrc.as_host(), (*itr).sport);
		        sprintf(rspec_str + strlen(rspec_str), "<dstPoint><dataPathId>%lx</dataPathId><port>%d</port></dstPoint>\n", (*itr).dpdst.as_host(), (*itr).dport);
                strcat(rspec_str, "</linkInfo>\n");
            }
            strcat(rspec_str, "</RSpec>\n");
            
            buf = new Array_buffer((uint8_t*)rspec_str, strlen(rspec_str));
            printf("Writing buffer of size %d\n", strlen(rspec_str));
            me.sock->write(*buf, false);
            me.sock->write_wait();

            free(rspec_str);

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

        default:
            return CONTINUE;
    }

    return CONTINUE;
}

REGISTER_COMPONENT(vigil::container::Simple_component_factory
                   <vigil::applications::AggrMgr>,
                   vigil::applications::AggrMgr);

} // applications
} // vigil

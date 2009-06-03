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

#include <memory>   // std::auto_ptr
#include <iostream>
#include <fstream>
#include <sstream>

#include "rspec.hxx" //CodeSynthesis generated
#define RSPEC_XSD_CURRENT_VERSION  "1.0"
#define RSPEC_XSD_NAMESPACE "http://yuba.stanford.edu/geniLight/rspec";
#define RSPEC_XSD_LOCATION "http://yuba.stanford.edu/geniLight/rspec.xsd";
#define FLOWVISOR_CONFIG_DIRECTORY "/tmp"

using namespace std;
using namespace ::geniLight::rspec;

namespace vigil {
namespace applications {

using namespace ::geniLight::rspec;

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
    register_handler<Datapath_join_event>
        (boost::bind(&AggrMgr::handle_datapath_join, this, _1));
    register_handler<Datapath_leave_event>
        (boost::bind(&AggrMgr::handle_datapath_leave, this, _1));
    register_handler<Msg_event>
        (boost::bind(&AggrMgr::handle_msg_event, this, _1));
}

void
AggrMgr::install()
{}

Disposition
AggrMgr::handle_datapath_join(const Event& e)
{
    const Datapath_join_event& dj = assert_cast<const Datapath_join_event&>(e);
    //uint64_t dpint = dj.datapath_id.as_host();

    switches.push_back(dj.datapath_id);
    list<uint16_t> ports;
    for (std::vector<Port>::const_iterator iter = dj.ports.begin();
            iter != dj.ports.end(); ++iter)
    {
        //Ignoring iter->name;
        ports.push_back(iter->port_no);
    }
    switch_ports[dj.datapath_id] = ports;
    return CONTINUE;
}

Disposition
AggrMgr::handle_datapath_leave(const Event& e)
{
    const Datapath_leave_event& dl = assert_cast<const Datapath_leave_event&>(e);
    switches.remove(dl.datapath_id);
    switch_ports.erase(dl.datapath_id);

    return CONTINUE;
}

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
    int count_written;

    switch (me.msg->type)
    {
        case SFA_START_SLICE: {
            slice_id = (char *)malloc(ntohs(me.msg->length)-2);
            memcpy(slice_id, me.msg->body, ntohs(me.msg->length)-3);
            slice_id[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Start_slice %s", slice_id);

            free(slice_id);
            break;}

        case SFA_STOP_SLICE:
            slice_id = (char *)malloc(ntohs(me.msg->length)-2);
            memcpy(slice_id, me.msg->body, ntohs(me.msg->length)-3);
            slice_id[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Stop_slice %s", slice_id);

            free(slice_id);
            break;

        case SFA_CREATE_SLICE:{
            slice_id = (char *)malloc(ntohs(me.msg->length)-2);
            memcpy(slice_id, me.msg->body, ntohs(me.msg->length)-3);
            slice_id[ntohs(me.msg->length)-3] = '\0';

            /* After the first null, we have the RSpec string */
            rspec_str = slice_id + strlen(slice_id) + 1;
            
            VLOG_DBG(lg, "Create_slice %s (len=%d) with rspec_str %s (len=%d)", slice_id, strlen(slice_id), rspec_str, strlen(rspec_str));
            convert_rspec_str_to_flowvisor_config(slice_id, rspec_str);

            free(slice_id);
            break;}

        case SFA_DELETE_SLICE:{
            slice_id = (char *)malloc(ntohs(me.msg->length)-2);
            memcpy(slice_id, me.msg->body, ntohs(me.msg->length)-3);
            slice_id[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Delete_slice %s", slice_id);

            free(slice_id);
            break;}

        case SFA_LIST_SLICES:{
            VLOG_DBG(lg, "List_slices");

            break;}

        case SFA_LIST_COMPONENTS:{
            VLOG_DBG(lg, "List_components");

            rspec_str = (char *)malloc(MESSENGER_BUFFER_SIZE);
            memset(rspec_str, 0, MESSENGER_BUFFER_SIZE);
            generate_rspec_of_components(rspec_str, MESSENGER_BUFFER_SIZE);

            //printf("Writing buffer of size %d\n", strlen(rspec_str));
            Nonowning_buffer buf((uint8_t*)rspec_str, strlen(rspec_str));
            count_written = me.sock->stream->write(buf, 0);
            VLOG_DBG(lg, "Done writing %d bytes", count_written);

            free(rspec_str);

            break;}

        case SFA_REGISTER: {
            char record_info[ntohs(me.msg->length)-2];
            memcpy(record_info, me.msg->body, ntohs(me.msg->length)-3);
            record_info[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Register_record %s", record_info);

            break;}

        case SFA_REBOOT_COMPONENT: {
            char component_name[ntohs(me.msg->length)-2];
            memcpy(component_name, me.msg->body, ntohs(me.msg->length)-3);
            component_name[ntohs(me.msg->length)-3] = '\0';
            VLOG_DBG(lg, "Reboot_component %s", component_name);

            break;}

        default:
            return CONTINUE;
    }

    return STOP;
}

struct membuf:streambuf {
    membuf(char *begin, char *end) {
        this->setp(begin, end);
    }
};

int
AggrMgr::generate_rspec_of_components(char *rspec_str, int length)
{

    auto_ptr<rspec> root(new rspec(RSPEC_XSD_CURRENT_VERSION));
    rspec::switches_sequence switchList;

    for (list<datapathid>::const_iterator itr1 = switches.begin(); itr1 != switches.end(); itr1++) {
        // Insert individual switches to root->switches()
        char switch_id[50];
        sprintf(switch_id, "%lx", itr1->as_host());
        nodeInfo node((xml_schema::string)string(switch_id));
        nodeInfo::interfaceList_sequence interfaceList;

        list<uint16_t>& ports = switch_ports[*itr1];
        for (list<uint16_t>::const_iterator itr2 = ports.begin(); itr2 != ports.end(); itr2++) {
            interface i((*itr2));
            interfaceList.push_back(i);
        }

        //for (LinkInfoList_iterator itr2 = links.begin(); itr2 != links.end(); itr2++) {
        //        i != sw->node().interfaceList().end ();
        //    if ((*itr2).dpsrc == (*itr1))

        node.interfaceList(interfaceList);
        switchInfo sw(node);
        switchList.push_back(sw);
    }
    root->switches(switchList);

    try
    {
        //Write RSpec to buffer
        xml_schema::namespace_infomap map;
        map["tns"].schema = RSPEC_XSD_LOCATION;
        map["tns"].name = RSPEC_XSD_NAMESPACE;

        // Using following class to write directly into buffer
        membuf strbuf(rspec_str, rspec_str+length-1);
        ostream out(&strbuf);
        RSpec (out, *root, map);
    }
    catch (const xml_schema::exception& e) {
        cerr << e << endl;
        VLOG_DBG(lg, "XML Parsing expection");
        return 0; //failure
    }

    return 1; //success
}

int 
AggrMgr::convert_rspec_str_to_flowvisor_config (char *slice_id, char *rspec_str)
{
    //Use following code if we need a dummy file
    //ofstream outfile("rspec.xml");
    //outfile << rspec_str << endl;
    //outfile.close();

    char guestfilename[50];
    sprintf(guestfilename, "%s/slice_%s.guest", FLOWVISOR_CONFIG_DIRECTORY, slice_id);
    ofstream guestfile(guestfilename);

    try
    {
        // Using following class to avoid making copies of RSpec
        membuf strbuf(rspec_str, rspec_str + strlen(rspec_str));
        istream in(&strbuf);
        auto_ptr<rspec> root(RSpec (in));

        //Use following two lines if we use dummy file
        //auto_ptr<rspec> root(RSpec ("rspec.xml"));
        //remove("rspec.xml"); //clean up

        if (root->version() == RSPEC_XSD_CURRENT_VERSION) {
            VLOG_DBG(lg, "Mismatching RSpec version");
            return 0; //failure
        }
        if (root->switches().size() != 1) {
            VLOG_DBG(lg, "Incorrect size of switches");
            return 0; //failure
        }
        //Currently FlowSpace is common for all switches. So extract
        //only first value
        switchInfo sw = root->switches().front();
        string controller = (string &)sw.node().controllerUrl();

        guestfile << "Id: " << slice_id << endl;
        guestfile << "Host: " << controller << endl;

        //For each flowspace entry in the RSpec
        for (nodeInfo::flowSpace_const_iterator f (sw.node().flowSpace().begin ());
                f != sw.node().flowSpace().end ();
                ++f)
        {
            guestfile << "FlowSpace: ";
            guestfile << f->policy() << ": ";
            guestfile << "port: " << f->port() << ": ";
            guestfile << "dl_src: " << f->dl_src() << ": ";
            guestfile << "dl_dst: " << f->dl_dst() << ": ";
            guestfile << "dl_type: " << f->dl_type() << ": ";
            guestfile << "vlan_id: " << f->vlan_id() << ": ";
            guestfile << "ip_src: " << f->ip_src() << ": ";
            guestfile << "ip_dst: " << f->ip_dst() << ": ";
            guestfile << "ip_proto: " << f->ip_proto() << ": ";
            guestfile << "tp_src: " << f->tp_src() << ": ";
            guestfile << "tp_dst: " << f->tp_dst() << endl;
        }

        for (rspec::switches_const_iterator sw (root->switches().begin ());
                sw != root->switches ().end ();
                ++sw) {
            guestfile << "AllowedPorts: " << endl;
            for (nodeInfo::interfaceList_const_iterator i (sw->node().interfaceList().begin ());
                    i != sw->node().interfaceList().end ();
                    ++i)
            {
                if (i!=sw->node().interfaceList().begin())
                    cout << ",";
                cout << i->port();
            }
            cout << "\t" << sw->node().nodeId() <<endl;
        }

        guestfile.close();
        if (system("killall -HUP flowvisor")) {
            VLOG_DBG(lg, "Unable to send HUP to flowvisor");
            return 0;
        }
    }
    catch (const xml_schema::exception& e) {
        cerr << e << endl;
        VLOG_DBG(lg, "XML Parsing expection");
        return 0; //failure
    }

    return 1; //success
}

REGISTER_COMPONENT(vigil::container::Simple_component_factory
                   <vigil::applications::AggrMgr>,
                   vigil::applications::AggrMgr);

} // applications
} // vigil
// Process XML files using stubs generated by CodeSynthesis


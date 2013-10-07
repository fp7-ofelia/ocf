#
# BOWL expedient plugin for the Berlin Open Wireless Lab
# based on the sample plugin
#
# Authors: Theresa Enghardt (tenghardt@inet.tu-berlin.de)
#          Robin Kuck (rkuck@net.t-labs.tu-berlin.de)
#          Julius Schulz-Zander (julius@net.t-labs.tu-berlin.de)
#          Tobias Steinicke (tsteinicke@net.t-labs.tu-berlin.de)
#
# Copyright (C) 2013 TU Berlin (FG INET)
# All rights reserved.
#
"""
Manages BOwl Nodes

@date: Sep 11, 2013
@author: Theresa Enghardt
"""
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import simple
from expedient.clearinghouse.utils import post_message_to_current_user
from expedient.common.messaging.models import DatedMessage
from bowl_plugin.models.BowlResource import BowlResource as BowlResourceModel
from bowl_plugin.models.BowlResourceAggregate import BowlResourceAggregate as BowlResourceAggregateModel

from bowl_plugin.utils.validators import validate_resource_name
import decimal, random
import jsonrpclib
import logging
import datetime

def resource_allocate(request, slice_id, agg_id, node_id=None):
    '''
    Add node to the topology, allocating them for 3 hours
    '''
    
    logger = logging.getLogger(__name__)
    logger.info("Called %s resource_allocate of node %s, slice %s on aggregate %s" % (str(request.method), str(node_id), str(agg_id), str(slice_id)))
    if agg_id != None and slice_id != None and node_id != None:
        try:
            aggregate = get_object_or_404(BowlResourceAggregateModel, pk=agg_id)
            s = jsonrpclib.Server(aggregate.client.url)
            end_time = datetime.datetime.now() + datetime.timedelta(hours=13) 
            username = request.user.first_name + " " + request.user.last_name
            if username in [None, " "]:
                username = "Unknown User"
            nodes = [ int(node_id) ]
            logger.debug("Allocating slice %s nodes %s , end_time %s, for user %s (%s) at server %s" % (str(slice_id), str(nodes), end_time.isoformat(), username, request.user.email, str(s)))
            res = s.Allocate(slice_id, nodes, end_time.isoformat(), username, str(request.user.email))
            if res == 0:
                DatedMessage.objects.post_message_to_user( "Added Node %d of slice %s on aggregate %s" % (int(node_id), str(slice_id), str(aggregate)), user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,)
            else:
                DatedMessage.objects.post_message_to_user( "%s Aggregate Manager error on Allocate" % str(aggregate), user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
        except Exception, e:
            logger.error("%s" % str(e))
            DatedMessage.objects.post_message_to_user( "Error adding node: %s " % str(e), user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
    else:
        logger.error("No aggregate ID, slice ID or node ID given")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def resource_provision(request, agg_id, slice_id):
    '''
    Reserve Nodes for 1 week
    '''
    
    logger = logging.getLogger(__name__)
    logger.info("Called %s resource_provision of slice %s on aggregate %s" % (str(request.method), str(agg_id), str(slice_id)))

    if agg_id != None and slice_id != None:
        try:
            aggregate = get_object_or_404(BowlResourceAggregateModel, pk=agg_id)
            s = jsonrpclib.Server(aggregate.client.url)
            end_time = datetime.datetime.now() + datetime.timedelta(days=7) 
            username = request.user.first_name + " " + request.user.last_name
            if username in [None, " "]:
                username = "Unknown User"
            logger.debug("Provisioning slice %s , end_time %s, for user %s (%s) at server %s" % (str(slice_id), end_time.isoformat(), username, request.user.email, str(s)))
            res = s.Provision(slice_id, end_time.isoformat(), username, username, str(request.user.email))
            if res == 0:
                DatedMessage.objects.post_message_to_user( "Provisioned slice %s on aggregate %s until %s" % (str(slice_id), str(aggregate), str(end_time)), user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,)
            elif res == -2:
                DatedMessage.objects.post_message_to_user( "Provisioned slice %s on aggregate %s until %s, but notifying BOWL admins failed. Please send mail to bowl-admins@lists.net.t-labs.tu-berlin.de" % (str(slice_id), str(aggregate), str(end_time)), user=request.user, msg_type=DatedMessage.TYPE_WARNING,)
            else:
                DatedMessage.objects.post_message_to_user( "%s Aggregate Manager error on Provision for 1 week " % str(aggregate), user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
        except Exception, e:
            logger.error("%s" % str(e))
            DatedMessage.objects.post_message_to_user( "Error adding node: %s " % str(e), user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
    else:
        logger.error("No aggregate ID or slice ID given")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def resource_extend(request, agg_id, slice_id):
    '''
    Extend Nodes for 4 weeks
    '''
    
    logger = logging.getLogger(__name__)
    logger.info("Called %s resource_extend of slice %s on aggregate %s" % (str(request.method), str(agg_id), str(slice_id)))

    if agg_id != None and slice_id != None:
        try:
            aggregate = get_object_or_404(BowlResourceAggregateModel, pk=agg_id)
            s = jsonrpclib.Server(aggregate.client.url)
            end_time = datetime.datetime.now() + datetime.timedelta(weeks=4) 
            username = request.user.first_name + " " + request.user.last_name
            if username in [None, " "]:
                username = "Unknown User"
            logger.debug("Provisioning slice %s , end_time %s, for user %s (%s) at server %s" % (str(slice_id), end_time.isoformat(), username, request.user.email, str(s)))
            res = s.Provision(slice_id, end_time.isoformat(), username, username, str(request.user.email))
            if res == 0:
                DatedMessage.objects.post_message_to_user( "Reserved slice %s on aggregate %s until %s" % (str(slice_id), str(aggregate), str(end_time)), user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,)
            elif res == -2:
                DatedMessage.objects.post_message_to_user( "Reserved slice %s on aggregate %s until %s, but notifying BOWL admins failed. Please send mail to bowl-admins@lists.net.t-labs.tu-berlin.de" % (str(slice_id), str(aggregate), str(end_time)), user=request.user, msg_type=DatedMessage.TYPE_WARNING,)
            else:
                DatedMessage.objects.post_message_to_user( "%s Aggregate Manager error on Provision for 4 weeks" % str(aggregate), user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
        except Exception, e:
            logger.error("%s" % str(e))
            DatedMessage.objects.post_message_to_user( "Error adding node: %s " % str(e), user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
    else:
        logger.error("No aggregate ID or slice ID given")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def resource_delete(request, agg_id, slice_id):
    '''
    Delete reservations
    '''
    
    logger = logging.getLogger(__name__)
    logger.info("Called %s resource_delete of slice %s on aggregate %s" % (str(request.method), str(agg_id), str(slice_id)))

    if agg_id != None and slice_id != None:
        try:
            aggregate = get_object_or_404(BowlResourceAggregateModel, pk=agg_id)
            s = jsonrpclib.Server(aggregate.client.url)
            username = request.user.first_name + " " + request.user.last_name
            if username in [None, " "]:
                username = "Unknown User"
            slices = [ slice_id ]
            logger.debug("Deleting nodes of slice %s, for user %s (%s) ID %s at server %s" % (str(slices), username, request.user.email, str(request.user), str(s)))
            res = s.Delete(slices, username, str(request.user.email), str(request.user))
            if res == 0:
                DatedMessage.objects.post_message_to_user( "Deleted slice %s on aggregate %s" % (str(slice_id), str(aggregate)), user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,)
            elif res == -2:
                DatedMessage.objects.post_message_to_user( "Deleted slice %s on aggregate %s, but notifying BOWL admins failed. Please send mail to bowl-admins@lists.net.t-labs.tu-berlin.de" % (str(slice_id), str(aggregate)), user=request.user, msg_type=DatedMessage.TYPE_WARNING,)
            else:
                DatedMessage.objects.post_message_to_user( "%s Aggregate Manager error on Delete " % str(aggregate), user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
        except Exception, e:
            logger.error("%s" % str(e))
            DatedMessage.objects.post_message_to_user( "Error deleting slice: %s " % str(e), user=request.user, msg_type=DatedMessage.TYPE_ERROR,)
    else:
        logger.error("No aggregate ID, slice ID or node ID given")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class BowlResource():
    """
    Manages creation/edition of BowlResources from the input of a given form.
    """
    
    @staticmethod
    def create(instance, aggregate_id, slice=None):
        try:
            if all(x in instance.__dict__ for x in ["name"]):
                br = BowlResourceModel()
                br.aggregate_id = aggregate_id
                br.set_label(instance.__dict__['name'])
                br.set_name(instance.__dict__['name'])
                if slice:
                    sr.set_project_id(slice.project.id)
                    sr.set_project_name(slice.project.name)
                    sr.set_slice_id(slice.id)
                    sr.set_slice_name(slice.name)
                sr.save()
        except Exception as e:
            if "Duplicate entry" in str(e):
                raise Exception("BowlResource with name '%s' already exists." % str(instance.name))
            else:
                raise e

    @staticmethod
    def fill(instance, slice, aggregate_id, resource_id = None):
        # resource_id = False => create. Check that no other resource exists with this name
        if not resource_id:
            if BowlResourceModel.objects.filter(name = instance.name):
                # Every exception will be risen to the upper level
                raise Exception("BowlResource with name '%s' already exists." % str(instance.name))

            instance.aggregate_id = aggregate_id
            instance.project_id = slice.project.id
            instance.project_name = slice.project.name
            instance.slice_id = slice.id
            instance.slice_name = slice.name
        # resource_id = True => edit. Change name/label
        instance.label = instance.name
        return instance

    @staticmethod
    def delete(resource_id):
        try:
            BowlResourceModel.objects.get(id = resource_id).delete()
        except:
            pass




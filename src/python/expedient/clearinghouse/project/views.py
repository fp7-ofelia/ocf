'''
@author: jnaous
'''

from django.views.generic import list_detail, create_update, simple
from models import Project
from forms import ProjectCreateForm
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from expedient.clearinghouse.aggregate.forms import AggregateTypeForm
from expedient.clearinghouse.aggregate.models import Aggregate
from django.core.exceptions import PermissionDenied
import logging
from expedient.common.utils.views import generic_crud
from expedient.common.messaging.models import DatedMessage
from django.db.models import Q
logger = logging.getLogger("Project Views")

TEMPLATE_PATH = "expedient/clearinghouse/project"

def list(request):
    '''Show list of projects'''
    
    qs = Project.objects.filter(Q(members=request.user)|Q(owner=request.user))
    return list_detail.object_list(
        request,
        queryset=qs,
        template_name=TEMPLATE_PATH+"/list.html",
        template_object_name="project",
    )

def delete(request, proj_id):
    '''Delete the project'''
    project = get_object_or_404(Project, id=proj_id)
    req = create_update.delete_object(
        request,
        model=Project,
        post_delete_redirect=reverse('home'),
        object_id=proj_id,
        template_name=TEMPLATE_PATH+"/confirm_delete.html",
    )
    if req.status_code == HttpResponseRedirect.status_code:
        DatedMessage.objects.post_message_to_user(
            "Successfully deleted project %s" % project.name,
            request.user, msg_type=DatedMessage.TYPE_SUCCESS)
    return req

def detail(request, proj_id):
    '''Show information about the project'''
    project = get_object_or_404(Project, id=proj_id)
    return list_detail.object_detail(
        request,
        Project.objects.all(),
        object_id=proj_id,
        template_name=TEMPLATE_PATH+"/detail.html",
        template_object_name="project",
        extra_context={
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % project.name, reverse("project_detail", args=[project.id])),
            )
        }
    )

def create(request):
    '''Create a new project'''
    
    def pre_save(instance, created):
        instance.owner = request.user
        logger.debug("called pre_save for creating project")
    
    def post_save(instance, created):
        instance.members.add(request.user)
        
    def redirect(instance):
        return reverse("project_detail", args=[instance.id])
    
    return generic_crud(
        request, None,
        model=Project,
        form_class=ProjectCreateForm,
        template=TEMPLATE_PATH+"/create_update.html",
        pre_save=pre_save,
        post_save=post_save,
        redirect=redirect,
        extra_context={
            "iframe": True,
            "base": "iframebase.html",
            "cancel_url": reverse("project_list"),
        },
        success_msg = lambda instance: "Successfully created project %s." % instance.name,
    )
    
def update(request, proj_id, iframe=False):
    '''Update information about a project'''
    
    def redirect(instance):
        if iframe:
            return reverse("project_list")
        else:
            return reverse("project_detail", args=[instance.id])
    
    return generic_crud(
        request, proj_id,
        model=Project,
        form_class=ProjectCreateForm,
        template=TEMPLATE_PATH+"/create_update.html",
        redirect=redirect,
        template_object_name="project",
        extra_context={
            "iframe": iframe,
            "base": "iframebase.html" if iframe else "base.html",
            "cancel_url": reverse("project_list") if iframe else reverse("project_detail", args=[proj_id]),
        },
        success_msg = lambda instance: "Successfully updated project %s." % instance.name,
    )

def update_iframe(request, proj_id):
    return update(request, proj_id, True)

def add_aggregate(request, proj_id):
    '''Add/remove aggregates to/from a project'''
    
    project = get_object_or_404(Project, id=proj_id)
    aggregate_list = Aggregate.objects.exclude(
        id__in=project.aggregates.all().values_list("id", flat=True))
    
    if request.method == "GET":
        return simple.direct_to_template(
            request, template=TEMPLATE_PATH+"/add_aggregates.html",
            extra_context={
                "aggregate_list": aggregate_list,
                "project": project,
                "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % project.name, reverse("project_detail", args=[project.id])),
                    ("Add Project Aggregates", request.path),
                ),
            }
        )
    
    elif request.method == "POST":
        # check which submit button was pressed
        items = request.POST.items()
        agg_id = -1
        for i in items:
            if i[1] == "Select":
                try:
                    agg_id = int(i[0]) # there should be only one item
                except:
                    raise Http404
        if agg_id not in aggregate_list.values_list("id", flat=True):
            raise Http404
        aggregate = get_object_or_404(Aggregate, id=agg_id).as_leaf_class()
        return HttpResponseRedirect(aggregate.add_to_project(
            project, reverse("project_add_agg", args=[proj_id])))
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
def update_aggregate(request, proj_id, agg_id):
    '''Update any info stored at the aggregate'''
    # TODO: This function might actually change the DB. So change to post
    project = get_object_or_404(Project, id=proj_id)
    aggregate = get_object_or_404(
        Aggregate, id=agg_id, id__in=project.aggregates.values_list(
            "id", flat=True)).as_leaf_class()
    return HttpResponseRedirect(aggregate.add_to_project(
        project, reverse("project_detail", args=[proj_id])))

def remove_aggregate(request, proj_id, agg_id):
    # TODO: This function might actually change the DB. So change to post
    project = get_object_or_404(Project, id=proj_id)
    aggregate = get_object_or_404(
        Aggregate, id=agg_id, id__in=project.aggregates.values_list(
            "id", flat=True)).as_leaf_class()
    return HttpResponseRedirect(aggregate.remove_from_project(
        project, reverse("project_detail", args=[proj_id])))

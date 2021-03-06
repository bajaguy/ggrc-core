# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""TaskGroup model related tests."""

from mock import patch

import ddt

from ggrc.models import all_models
from ggrc_workflows import ac_roles
from integration.ggrc import generator
from integration.ggrc.models import factories
from integration.ggrc_workflows.helpers import rbac_helper
from integration.ggrc_workflows.helpers import workflow_api
from integration.ggrc_workflows.helpers import workflow_test_case
from integration.ggrc_workflows.models import factories as wf_factories


@ddt.ddt
class TestTaskGroupApiCalls(workflow_test_case.WorkflowTestCase):
  """Tests related to TaskGroup REST API calls."""

  @ddt.data(
      rbac_helper.GA_RNAME,
      rbac_helper.GE_RNAME,
      rbac_helper.GR_RNAME,
      rbac_helper.GC_RNAME,
  )
  def test_post_tg_g_role_admin(self, g_rname):
    """POST TaskGroup logged in as {} & WF Admin."""
    with factories.single_commit():
      self.setup_helper.setup_workflow((g_rname,))

    g_person = self.setup_helper.get_person(g_rname,
                                            ac_roles.workflow.ADMIN_NAME)
    self.api_helper.set_user(g_person)

    workflow = all_models.Workflow.query.one()

    data = workflow_api.get_task_group_post_dict(workflow, g_person)
    response = self.api_helper.post(all_models.TaskGroup, data)
    self.assertEqual(response.status_code, 201)

  def test_get_tg_g_reader_no_role(self):
    """GET TaskGroup collection logged in as GlobalReader & No Role."""
    with factories.single_commit():
      wf_factories.TaskGroupFactory()
      self.setup_helper.setup_person(rbac_helper.GR_RNAME, "No Role")

    g_reader = self.setup_helper.get_person(rbac_helper.GR_RNAME, "No Role")
    self.api_helper.set_user(g_reader)

    task_group = all_models.TaskGroup.query.one()
    response = self.api_helper.get_collection(task_group, (task_group.id, ))
    self.assertTrue(response.json["task_groups_collection"]["task_groups"])

  @ddt.data(
      rbac_helper.GA_RNAME,
      rbac_helper.GE_RNAME,
      rbac_helper.GR_RNAME,
      rbac_helper.GC_RNAME,
  )
  def test_clone_tg_g_role_admin(self, g_rname):
    """Clone TaskGroup logged in as {} & WF Admin."""
    with factories.single_commit():
      workflow = self.setup_helper.setup_workflow((g_rname,))
      wf_factories.TaskGroupFactory(workflow=workflow)

    g_person = self.setup_helper.get_person(g_rname,
                                            ac_roles.workflow.ADMIN_NAME)
    self.api_helper.set_user(g_person)

    task_group = all_models.TaskGroup.query.one()

    data = workflow_api.get_task_group_clone_dict(task_group)
    response = self.api_helper.post(all_models.TaskGroup, data)
    self.assertEqual(response.status_code, 201)


class TestCloneTaskGroup(workflow_test_case.WorkflowTestCase):
  """Test clone TaskGroup operation."""

  def setUp(self):
    super(TestCloneTaskGroup, self).setUp()
    self.object_generator = generator.ObjectGenerator()

  @patch("ggrc_workflows.get_copy_title")
  def test_clone_task_group(self, get_copy_title_patch):
    """Check clone tg and if proper copy title set."""
    expected_title = 'Copy Title'
    get_copy_title_patch.return_value = expected_title

    with factories.single_commit():
      workflow = self.setup_helper.setup_workflow((rbac_helper.GC_RNAME,))
      task_group = wf_factories.TaskGroupFactory(workflow=workflow)
      cloned_task_group = wf_factories.TaskGroupFactory(
          parent_id=task_group.id, workflow=workflow)

    cloned_title = cloned_task_group.title

    _, clone_tg = self.object_generator.generate_object(
        all_models.TaskGroup, {"title": "TG - copy 1", "clone": task_group.id})
    get_copy_title_patch.assert_called_once_with(
        task_group.title, [cloned_title])
    self.assertEqual(clone_tg.title, expected_title)
    self.assertEqual(clone_tg.parent_id, task_group.id)

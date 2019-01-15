# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for control model."""
from datetime import datetime
import unittest

import mock

from ggrc import db, settings
from ggrc.models import all_models
from integration.ggrc import TestCase
from integration.ggrc.models import factories
from integration.ggrc import api_helper


class TestControl(TestCase):
  """Tests for control model."""

  def setUp(self):
    """setUp, nothing else to add."""
    super(TestControl, self).setUp()
    self.api = api_helper.Api()

  def test_simple_categorization(self):
    """Check append category append to control."""
    category = factories.ControlCategoryFactory()
    control = factories.ControlFactory()
    control.categories.append(category)
    db.session.commit()
    self.assertIn(category, control.categories)
    # be really really sure
    control = db.session.query(all_models.Control).get(control.id)
    self.assertIn(category, control.categories)

  def test_has_test_plan(self):
    """Check test plan setup to control."""
    control = factories.ControlFactory(test_plan="This is a test text")
    control = db.session.query(all_models.Control).get(control.id)
    self.assertEqual(control.test_plan, "This is a test text")

  def test_set_end_date(self):
    """End_date can't to be updated."""
    control = factories.ControlFactory()
    self.api.put(control, {"end_date": "2015-10-10"})
    control = db.session.query(all_models.Control).get(control.id)
    self.assertIsNone(control.end_date)

  def test_set_deprecated_status(self):
    """Deprecated status setup end_date."""
    control = factories.ControlFactory()
    self.assertIsNone(control.end_date)
    self.api.put(control, {"status": all_models.Control.DEPRECATED})
    control = db.session.query(all_models.Control).get(control.id)
    self.assertIsNotNone(control.end_date)

  def test_create_commentable(self):
    """Test if commentable fields are set on creation"""
    recipients = "Admin,Control Operators,Control Owners"
    send_by_default = 0
    response = self.api.post(all_models.Control, {
        "control": {
            "title": "Control title",
            "context": None,
            "recipients": recipients,
            "send_by_default": send_by_default,
        },
    })
    self.assertEqual(response.status_code, 201)
    control_id = response.json.get("control").get("id")
    control = db.session.query(all_models.Control).get(control_id)
    self.assertEqual(control.recipients, recipients)
    self.assertEqual(control.send_by_default, send_by_default)

  def test_update_commentable(self):
    """Test update of commentable fields"""
    control = factories.ControlFactory()
    self.assertEqual(control.recipients, "")
    self.assertIs(control.send_by_default, True)

    recipients = "Admin,Control Operators,Control Owners"
    send_by_default = 0
    self.api.put(control, {
        "recipients": recipients,
        "send_by_default": send_by_default,
    })
    control = db.session.query(all_models.Control).get(control.id)
    self.assertEqual(control.recipients, recipients)
    self.assertEqual(control.send_by_default, send_by_default)

  @unittest.skip("Skipped until control not Reviewable")
  def test_review_get(self):
    """Test that review data is present in control get response"""
    with factories.single_commit():
      control = factories.ControlFactory()
      review = factories.ReviewFactory(reviewable=control)
      review_id = review.id

    resp = self.api.get(all_models.Control, control.id)
    self.assert200(resp)
    resp_control = resp.json["control"]
    self.assertIn("review", resp_control)
    self.assertEquals(review_id, resp_control["review"]["id"])


class TestSyncServiceControl(TestCase):
  """Tests for control model using sync service."""

  def setUp(self):
    """setUp, nothing else to add."""
    super(TestSyncServiceControl, self).setUp()
    self.api = api_helper.Api()

    self.app_user_email = "external_app@example.com"
    self.ext_user_email = 'external@example.com'

    settings.EXTERNAL_APP_USER = self.app_user_email

    custom_headers = {
        'X-GGRC-user': '{"email": "%s"}' % self.app_user_email,
        'X-external-user': '{"email": "%s"}' % self.ext_user_email
    }

    self.api.headers.update(custom_headers)
    self.api.client.get("/login", headers=self.api.headers)

  @mock.patch("ggrc.settings.INTEGRATION_SERVICE_URL", "mock")
  def test_control_create(self):
    """Test control creation using sync service."""
    control_body = self.prepare_control_request_body()

    response = self.api.post(all_models.Control, {
        "control": control_body
    })

    self.assertEqual(response.status_code, 201)

    id_ = response.json.get("control").get("id")
    self.assertEqual(control_body["id"], id_)

    control = db.session.query(all_models.Control).get(id_)
    app_user = db.session.query(all_models.Person).filter(
        all_models.Person.email == self.app_user_email).one()
    ext_user = db.session.query(all_models.Person).filter(
        all_models.Person.email == self.ext_user_email).one()

    self.assertEqual(ext_user.modified_by_id, app_user.id)
    self.assertEqual(control.modified_by_id, ext_user.id)

    self.assertEqual(control.title, control_body["title"])
    self.assertEqual(control.slug, control_body["slug"])
    self.assertEqual(control.created_at, control_body["created_at"])
    self.assertEqual(control.updated_at, control_body["updated_at"])

    expected_categories = {
        category["id"] for category in control_body["categories"]
    }
    mapped_categories = {category.id for category in control.categories}
    self.assertEqual(mapped_categories, expected_categories)

  @staticmethod
  def prepare_control_request_body():
    """Create payload for control creation."""
    created_at = datetime(2018, 1, 1)
    updated_at = datetime(2018, 1, 2)
    category = factories.ControlCategoryFactory()

    return {
        "id": 123,
        "title": "new_control",
        "context": None,
        "created_at": created_at,
        "updated_at": updated_at,
        "slug": "CONTROL-01",
        "categories": [
            {
                "id": category.id,
                "type": "ControlCategory"
            }
        ]
    }

  @mock.patch("ggrc.settings.INTEGRATION_SERVICE_URL", "mock")
  def test_control_update(self):
    """Test control update using sync service."""
    control = factories.ControlFactory()

    response = self.api.get(control, control.id)

    api_link = response.json["control"]["selfLink"]

    control_body = response.json["control"]
    control_body["title"] = "updated_title"
    control_body["created_at"] = "2018-01-04"
    control_body["updated_at"] = "2018-01-05"

    response = self.api.send_request(self.api.client.put,
                                     control,
                                     response.json,
                                     api_link=api_link)

    self.assertEqual("updated_title", response.json["control"]["title"])
    self.assertEqual("2018-01-04", response.json["control"]["created_at"])
    self.assertEqual("2018-01-05", response.json["control"]["updated_at"])

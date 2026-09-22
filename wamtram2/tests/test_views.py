from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from wamtram2.views import TrtDataEntryFormView


class TrtDataEntryFormViewTests(SimpleTestCase):
    """Regression tests for WAMTRAM2 data-entry form context."""

    def test_bound_form_uses_submitted_entered_by_name_and_id(self):
        """
        A bound form must use the Entered by value submitted with the current
        request rather than a previously remembered session value.
        """
        view = TrtDataEntryFormView()
        view.request = RequestFactory().post(
            "/new-data-entry/1/",
            data={
                "entered_by_id": "2002",
            },
        )
        view.kwargs = {
            "batch_id": 1,
        }

        form = SimpleNamespace(
            is_bound=True,
            data={
                "entered_by_id": "2002",
                "recorded_by_id": "",
                "measured_by_id": "",
                "tagged_by_id": "",
                "place_code": "",
            },
        )

        batch = SimpleNamespace(
            entry_batch_id=1,
            template=None,
        )

        with (
            patch.object(
                TrtDataEntryFormView,
                "get_person_name",
                side_effect=lambda person_id: (
                    "Person B" if person_id == "2002" else ""
                ),
            ),
            patch.object(
                TrtDataEntryFormView,
                "get_place_name",
                return_value="",
            ),
            patch(
                "django.views.generic.edit.FormMixin.get_context_data",
                return_value={"form": form},
            ),
            patch(
                "wamtram2.views.TrtEntryBatches.objects.get",
                return_value=batch,
            ),
        ):
            context = view.get_context_data(form=form)

        self.assertEqual(context["entered_by_id"], "2002")
        self.assertEqual(context["entered_by_name"], "Person B")
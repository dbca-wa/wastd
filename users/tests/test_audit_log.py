from django.test import TestCase
from datetime import timedelta
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.test import RequestFactory, TestCase
from users.middleware import ModuleAccessMiddleware
from users.models import AuditLog, Organisation, User
from users.admin import AuditLogAdmin
from django.contrib import admin
from marine_mammal_incidents.models import Incident, Species, Uploaded_file

class AuditLogCreationTests(TestCase):
    # Verify that deleting a normal Django model instance creates an audit log
    # containing the expected deletion action and object information.
    def test_audit_log_created_after_record_deleted(self):
        organisation = Organisation.objects.create(
            code="audit-delete-test",
            label="Audit Delete Test",
        )
        organisation_pk = organisation.pk

        organisation.delete()

        log = AuditLog.objects.get(
            app_label="users",
            model_name="organisation",
            object_pk=str(organisation_pk),
        )

        self.assertEqual(log.action, AuditLog.ACTION_DELETE)
        self.assertEqual(log.object_repr, "Audit Delete Test")
    
    # Verify that Django session deletions are excluded from audit logging,
    # as sessions are short-lived framework records rather than business data.
    def test_session_deletion_is_not_logged(self):
        session = Session.objects.create(
            session_key="audit-test-session",
            session_data="",
            expire_date=timezone.now() + timedelta(days=1),
        )
        session_pk = session.pk

        session.delete()

        self.assertFalse(
            AuditLog.objects.filter(
                app_label="sessions",
                model_name="session",
                object_pk=str(session_pk),
            ).exists()
        )

    # Verify that a deletion performed within a request records the authenticated
    # actor together with the request path, HTTP method, and remote IP address.
    def test_audit_log_captures_actor_and_request_metadata(self):
        user = User.objects.create_user(
            username="audit-test-user",
            password="test-password",
        )

        organisation = Organisation.objects.create(
            code="audit-metadata-test",
            label="Audit Metadata Test",
        )
        organisation_pk = organisation.pk

        factory = RequestFactory()
        request = factory.delete(
            "/admin/users/organisation/1/delete/?next=test",
            REMOTE_ADDR="127.0.0.1",
        )
        request.user = user

    # Verify that a deletion performed within a request records the authenticated
    # actor together with the request path, HTTP method, and remote IP address.
    def delete_organisation(request):
        organisation.delete()
        return None

        middleware = ModuleAccessMiddleware(delete_organisation)
        middleware(request)

        log = AuditLog.objects.get(
            app_label="users",
            model_name="organisation",
            object_pk=str(organisation_pk),
        )

        self.assertEqual(log.actor, user)
        self.assertEqual(
            log.path,
            "/admin/users/organisation/1/delete/?next=test",
        )
        self.assertEqual(log.method, "DELETE")
        self.assertEqual(log.remote_addr, "127.0.0.1")

class AuditLogRetentionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = User.objects.create_superuser(
            username="audit-retention-superuser",
            email="audit-retention@example.com",
            password="test-password",
        )
        self.model_admin = AuditLogAdmin(AuditLog, admin.site)
        self.request = self.factory.get("/admin/users/auditlog/")
        self.request.user = self.superuser

    # Verify that an audit log less than one year old is protected from
    # deletion, even when the deletion is requested by a superuser.
    def test_log_less_than_one_year_old_cannot_be_deleted(self):
        log = AuditLog.objects.create(
            action=AuditLog.ACTION_DELETE,
            app_label="users",
            model_name="organisation",
            object_pk="1",
            object_repr="Recent retention test",
            created_at=timezone.now() - timedelta(days=364),
        )

        self.assertFalse(
            self.model_admin.has_delete_permission(
                self.request,
                log,
            )
        )

    # Verify that an audit log more than one year old becomes eligible
    # for deletion when the deletion is requested by a superuser.
    def test_log_more_than_one_year_old_can_be_deleted(self):
        log = AuditLog.objects.create(
            action=AuditLog.ACTION_DELETE,
            app_label="users",
            model_name="organisation",
            object_pk="2",
            object_repr="Old retention test",
            created_at=timezone.now() - timedelta(days=366),
        )

        self.assertTrue(
            self.model_admin.has_delete_permission(
                self.request,
                log,
            )
        )

class AuditLogPermissionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.model_admin = AuditLogAdmin(AuditLog, admin.site)

        self.staff_user = User.objects.create_user(
            username="audit-staff-user",
            password="test-password",
            is_staff=True,
        )

        self.superuser = User.objects.create_superuser(
            username="audit-permission-superuser",
            email="audit-permission@example.com",
            password="test-password",
        )

        self.old_log = AuditLog.objects.create(
            action=AuditLog.ACTION_DELETE,
            app_label="users",
            model_name="organisation",
            object_pk="1",
            object_repr="Permission test",
            created_at=timezone.now() - timedelta(days=366),
        )

    # Verify that a normal staff user cannot delete an audit log,
    # even when the log is older than the one-year retention period.
    def test_non_superuser_cannot_delete_audit_log(self):
        request = self.factory.get("/admin/users/auditlog/")
        request.user = self.staff_user

        self.assertFalse(
            self.model_admin.has_delete_permission(
                request,
                self.old_log,
            )
        )

    # Verify that a superuser can delete an audit log once the
    # log is older than the one-year retention period.
    def test_superuser_can_delete_old_audit_log(self):
        request = self.factory.get("/admin/users/auditlog/")
        request.user = self.superuser

        self.assertTrue(
            self.model_admin.has_delete_permission(
                request,
                self.old_log,
            )
        )

class AuditLogBulkDeletionTests(TestCase):
    # Verify that deleting multiple records through QuerySet.delete()
    # creates a separate audit log for every deleted object.
    def test_bulk_deletion_creates_audit_log_for_each_object(self):
        organisation_one = Organisation.objects.create(
            code="audit-bulk-one",
            label="Audit Bulk One",
        )
        organisation_two = Organisation.objects.create(
            code="audit-bulk-two",
            label="Audit Bulk Two",
        )

        organisation_pks = {
            str(organisation_one.pk),
            str(organisation_two.pk),
        }

        Organisation.objects.filter(
            pk__in=[
                organisation_one.pk,
                organisation_two.pk,
            ]
        ).delete()

        logs = AuditLog.objects.filter(
            app_label="users",
            model_name="organisation",
            object_pk__in=organisation_pks,
        )

        self.assertEqual(logs.count(), 2)
        self.assertSetEqual(
            set(logs.values_list("object_pk", flat=True)),
            organisation_pks,
        )

class AuditLogCascadeDeletionTests(TestCase):
    # Verify that deleting a parent Incident also creates an audit log
    # for an Uploaded_file automatically deleted through CASCADE.
    def test_cascade_deletion_creates_audit_logs_for_related_objects(self):
        species = Species.objects.create(
            common_name="Audit Test Species",
            scientific_name="Audit test species",
        )

        incident = Incident.objects.create(
            incident_date=timezone.now().date(),
            species=species,
            number_of_animals=1,
            incident_type=Incident.STRANDING,
            sex=Incident.UNKNOWN,
            age_class=Incident.UNKNOWN,
            condition_when_found="Unknown",
            outcome="Unknown",
        )

        uploaded_file = Uploaded_file.objects.create(
            incident=incident,
            title="Audit Cascade Test",
        )

        incident_pk = incident.pk
        uploaded_file_pk = uploaded_file.pk

        incident.delete()

        self.assertFalse(
            Uploaded_file.objects.filter(
                pk=uploaded_file_pk,
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                app_label="marine_mammal_incidents",
                model_name="incident",
                object_pk=str(incident_pk),
            ).exists()
        )

        self.assertTrue(
            AuditLog.objects.filter(
                app_label="marine_mammal_incidents",
                model_name="uploaded_file",
                object_pk=str(uploaded_file_pk),
            ).exists()
        )
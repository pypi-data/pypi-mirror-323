import datetime as dt
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from edc_consent.site_consents import site_consents
from edc_constants.constants import NOT_APPLICABLE, PATIENT
from edc_facility import import_holidays
from edc_facility.models import HealthFacility, HealthFacilityTypes
from edc_utils import get_utcnow
from edc_visit_schedule.models import VisitSchedule
from edc_visit_schedule.post_migrate_signals import populate_visit_schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.utils import get_related_visit_model_cls

from edc_appointment.constants import SKIPPED_APPT
from edc_appointment.models import Appointment, InfoSources
from edc_appointment_app.consents import consent_v1
from edc_appointment_app.forms import NextAppointmentCrfForm
from edc_appointment_app.models import NextAppointmentCrf, SubjectConsent
from edc_appointment_app.visit_schedule import get_visit_schedule6

utc = ZoneInfo("UTC")
tz = ZoneInfo("Africa/Dar_es_Salaam")


@override_settings(SITE_ID=10)
class TestNextAppointmentCrf(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc))
    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule6())
        site_consents.registry = {}
        site_consents.register(consent_v1)
        populate_visit_schedule()

        self.subject_identifier = "101-40990029-4"
        identity = "123456789"
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(days=10),
            identity=identity,
            confirm_identity=identity,
            dob=get_utcnow() - relativedelta(years=25),
        )

        # put subject on schedule
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_appointment_app.onschedulesix"
        )
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.nextappointmentcrf": ("appt_date", "visitschedule")
        }
    )
    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc))
    def test_ok(self):
        self.assertEqual(5, Appointment.objects.all().count())
        appointment = Appointment.objects.get(timepoint=0)
        subject_visit_model_cls = get_related_visit_model_cls()
        subject_visit_model_cls.objects.create(
            report_datetime=appointment.appt_datetime,
            appointment=appointment,
            reason=SCHEDULED,
        )

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.nextappointmentcrf": ("appt_date", "visitschedule")
        }
    )
    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc))
    def test_next_appt_ok(self):
        self.assertEqual(5, Appointment.objects.all().count())
        appointment = Appointment.objects.get(timepoint=0)
        subject_visit = get_related_visit_model_cls().objects.create(
            appointment=appointment,
            reason=SCHEDULED,
            report_datetime=appointment.report_datetime,
        )
        # start with a next appt date three months from now, which will be 1030
        # incorrectly link this to visit code 1000
        data = dict(
            report_datetime=subject_visit.report_datetime,
            appt_date=(appointment.appt_datetime + relativedelta(months=3)).date(),
            visitschedule=VisitSchedule.objects.get(visit_code="1000"),
            info_source=InfoSources.objects.get(name=PATIENT),
        )
        obj = NextAppointmentCrf(subject_visit=subject_visit)
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()

        self.assertIn("visitschedule", form._errors)
        self.assertIn("1030", str(form._errors.get("visitschedule")))

        # incorrectly link this to visit code 1010
        data.update(visitschedule=VisitSchedule.objects.get(visit_code="1010"))
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("1030", str(form._errors.get("visitschedule")))

        # incorrectly link this to visit code 1020
        data.update(visitschedule=VisitSchedule.objects.get(visit_code="1020"))
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("1030", str(form._errors.get("visitschedule")))

        # correctly link this to visit code 1030
        data.update(visitschedule=VisitSchedule.objects.get(visit_code="1030"))
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        self.assertNotIn("1030", str(form._errors.get("visitschedule")))

        # create model instance
        NextAppointmentCrf.objects.create(subject_visit=subject_visit, **data)
        # assert skipped over 1010, 1020
        apppointment = Appointment.objects.get(visit_code="1010")
        self.assertEqual(apppointment.appt_status, SKIPPED_APPT)
        self.assertEqual(apppointment.appt_timing, NOT_APPLICABLE)
        apppointment = Appointment.objects.get(visit_code="1020")
        self.assertEqual(apppointment.appt_status, SKIPPED_APPT)
        self.assertEqual(apppointment.appt_timing, NOT_APPLICABLE)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.nextappointmentcrf": ("appt_date", "visitschedule")
        }
    )
    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc))
    def test_next_appt_with_health_facility(self):
        self.assertEqual(get_utcnow().weekday(), 1)  # tues
        health_facility_type = HealthFacilityTypes.objects.create(
            name="Integrated", display_name="Integrated"
        )
        health_facility = HealthFacility.objects.create(
            name="integrated_facility",
            health_facility_type=health_facility_type,
            mon=False,
            tue=True,
            wed=False,
            thu=True,
            fri=False,
            sat=False,
            sun=False,
        )
        self.assertEqual(5, Appointment.objects.all().count())
        appointment = Appointment.objects.get(timepoint=0)
        subject_visit_model_cls = get_related_visit_model_cls()
        subject_visit = subject_visit_model_cls.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
            report_datetime=appointment.report_datetime,
        )

        data = dict(
            report_datetime=subject_visit.report_datetime,
            appt_date=(
                appointment.appt_datetime + relativedelta(months=3) + relativedelta(days=3)
            ).date(),
            info_source=InfoSources.objects.get(name=PATIENT),
            visitschedule=VisitSchedule.objects.get(visit_code="1030"),
            health_facility=health_facility.id,
        )
        self.assertEqual(data.get("appt_date").weekday(), 4)
        obj = NextAppointmentCrf(subject_visit=subject_visit)
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("appt_date", form._errors)
        self.assertIn("Invalid clinic day", str(form._errors.get("appt_date")))

        data.update(appt_date=data.get("appt_date") + relativedelta(days=1))
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("appt_date", form._errors)
        self.assertIn("Expected Mon-Fri", str(form._errors.get("appt_date")))

        data.update(appt_date=data.get("appt_date") - relativedelta(days=2))
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        self.assertNotIn("appt_date", form._errors)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.nextappointmentcrf": ("appt_date", "visitschedule")
        },
        LANGUAGE_CODE="sw",
    )
    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=tz))
    def test_next_appt_with_health_facility_tz(self):
        self.assertEqual(get_utcnow().weekday(), 1)  # tues
        health_facility_type = HealthFacilityTypes.objects.create(
            name="Integrated", display_name="Integrated"
        )
        health_facility = HealthFacility.objects.create(
            name="integrated_facility",
            health_facility_type=health_facility_type,
            mon=False,
            tue=True,
            wed=False,
            thu=True,
            fri=False,
            sat=False,
            sun=False,
        )
        appointment = Appointment.objects.get(timepoint=0)
        subject_visit_model_cls = get_related_visit_model_cls()
        subject_visit = subject_visit_model_cls.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
            report_datetime=appointment.report_datetime,
        )
        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=(
                appointment.appt_datetime + relativedelta(months=3) + relativedelta(days=2)
            ).date(),
            info_source=InfoSources.objects.get(name=PATIENT),
            visitschedule=VisitSchedule.objects.get(visit_code="1030"),
            health_facility=health_facility.id,
        )
        self.assertEqual(data.get("appt_date").weekday(), 3)

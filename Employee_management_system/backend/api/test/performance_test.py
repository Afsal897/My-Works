from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now

from api.models import (
    User, Role, UserRole,
    Department, Designation, EmployeeProfile,
    Project, ProjectAssignment,
    PerformanceRating
)

class SubmitPerformanceRatingTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('performance_rating')

        # Create or get roles
        self.manager_role, _ = Role.objects.get_or_create(name='Manager')
        self.employee_role, _ = Role.objects.get_or_create(name='Employee')

        # Create users
        self.manager_user, _ = User.objects.get_or_create(username='manager', email='manager@example.com')
        self.manager_user.set_password('pass')
        self.manager_user.save()

        self.employee_user, _ = User.objects.get_or_create(username='employee', email='employee@example.com')
        self.employee_user.set_password('pass')
        self.employee_user.save()

        # Assign roles
        UserRole.objects.get_or_create(user=self.manager_user, role=self.manager_role)
        UserRole.objects.get_or_create(user=self.employee_user, role=self.employee_role)

        # Create or get department and designation
        self.department, _ = Department.objects.get_or_create(name='Engineering')
        self.designation, _ = Designation.objects.get_or_create(title='Developer')

        # Create profiles
        self.manager_profile, _ = EmployeeProfile.objects.get_or_create(
            user=self.manager_user,
            defaults={
                "department": self.department,
                "designation": self.designation,
                "join_date": "2023-01-01",
                "phone_number": "123"
            }
        )

        self.employee_profile, _ = EmployeeProfile.objects.get_or_create(
            user=self.employee_user,
            defaults={
                "department": self.department,
                "designation": self.designation,
                "join_date": "2023-01-01",
                "phone_number": "456"
            }
        )

        # Create a completed project managed by manager
        self.project, _ = Project.objects.get_or_create(
            name="Completed Project",
            manager=self.manager_profile,
            defaults={
                "description": "Done",
                "start_date": "2023-01-01",
                "status": "completed",
                "created_by": self.manager_user
            }
        )

        # Assign employee to project
        ProjectAssignment.objects.get_or_create(
            employee=self.employee_profile,
            project=self.project,
            defaults={
                "assignment_status": "completed",
                "assigned_by": self.manager_user
            }
        )

        self.valid_payload = {
            "employee": self.employee_profile.id,
            "project": self.project.id,
            "rating": 4,
            "review_comment": "Great work",
            "review_date": now().date()
        }

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_manager_can_submit_performance_rating(self):
        headers = self.get_auth_header(self.manager_user)
        response = self.client.post(self.url, self.valid_payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PerformanceRating.objects.filter(employee=self.employee_profile, project=self.project).exists())

    def test_non_manager_cannot_submit_rating(self):
        headers = self.get_auth_header(self.employee_user)
        response = self.client.post(self.url, self.valid_payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], "Only managers can submit performance ratings.")

    def test_invalid_project_manager_relation(self):
        # Create another project not managed by manager
        other_project = Project.objects.create(
            name="Other Project",
            description="Invalid",
            start_date='2023-01-01',
            status='completed',
            created_by=self.manager_user,
            manager=self.manager_profile
        )

        payload = self.valid_payload.copy()
        payload['project'] = other_project.id

        headers = self.get_auth_header(self.manager_user)
        response = self.client.post(self.url, payload, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_not_assigned_to_project(self):
        # Create a new employee not assigned to the project
        unassigned_user = User.objects.create_user(username='other', email='other@example.com', password='pass')
        unassigned_profile = EmployeeProfile.objects.create(
            user=unassigned_user,
            department=self.department,
            designation=self.designation,
            join_date='2023-01-01',
            phone_number='789'
        )

        payload = self.valid_payload.copy()
        payload['employee'] = unassigned_profile.id

        headers = self.get_auth_header(self.manager_user)
        response = self.client.post(self.url, payload, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], "Employee is not assigned to this project.")




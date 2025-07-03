from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import (
    Department, 
    Role, 
    UserRole, 
    EmployeeProfile, 
    Designation, 
    Project,
    ProjectAssignment
    )
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

class CreateDepartmentTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('create_department')
        self.admin_role, _ = Role.objects.get_or_create(name='Admin')
        self.employee_role, _ = Role.objects.get_or_create(name='Employee')

        # Create users
        self.admin_user = User.objects.create_user(username='admin', 
                                                   email='admin@gmail.com',
                                                   password='adminpass')
        self.employee_user = User.objects.create_user(username='employee', 
                                                      email='employee@gmail.com',
                                                      password='employeepass')

        # Assign roles
        UserRole.objects.get_or_create(user=self.admin_user, role=self.admin_role)
        UserRole.objects.get_or_create(user=self.employee_user, role=self.employee_role)

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_admin_can_create_department(self):
        data = {'name': 'Engineering'}
        headers = self.get_auth_header(self.admin_user)
        response = self.client.post(self.url, data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Engineering')
        self.assertTrue(Department.objects.filter(name='Engineering').exists())

    def test_employee_cannot_create_department(self):
        data = {'name': 'HR'}
        headers = self.get_auth_header(self.employee_user)
        response = self.client.post(self.url, data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Only Admins are allowed to perform this action.')

    def test_duplicate_department(self):
        Department.objects.get_or_create(name='Finance')
        data = {'name': 'finance'} 
        headers = self.get_auth_header(self.admin_user)
        response = self.client.post(self.url, data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already exists', response.data['error'])


class CreateEmployeeProfileTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('create_profile')

        # Create roles
        self.admin_role, _ = Role.objects.get_or_create(name='Admin')
        self.employee_role, _ = Role.objects.get_or_create(name='Employee')

        # Create admin and target user
        self.admin_user = User.objects.create_user(username='admin', 
                                                   email='admin@gmail.com',
                                                   password='adminpass')
        self.target_user = User.objects.create_user(username='employee1', 
                                                    email='employee1@gmail.com',
                                                    password='emppass')

        # Assign roles
        UserRole.objects.get_or_create(user=self.admin_user, role=self.admin_role)

        # Create department and designation
        self.department = Department.objects.create(name='Engineering')
        self.designation = Designation.objects.create(title='Software Engineer')

        self.valid_payload = {
            'user': self.target_user.id,
            'phone_number': '1234567890',
            'date_of_birth': '1995-01-01',
            'join_date': '2024-01-01',
            'department': self.department.id,
            'designation': self.designation.id,
        }

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_admin_can_create_employee_profile(self):
        headers = self.get_auth_header(self.admin_user)
        response = self.client.post(self.url, self.valid_payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user_username'], 'employee1')
        self.assertEqual(response.data['department_name'], 'Engineering')
        self.assertEqual(response.data['designation_title'], 'Software Engineer')
        self.assertTrue(EmployeeProfile.objects.filter(user=self.target_user).exists())

    def test_non_admin_cannot_create_employee_profile(self):
        # Regular employee (no admin role)
        non_admin_user = User.objects.create_user(username='normal', password='normalpass')
        UserRole.objects.get_or_create(user=non_admin_user, role=self.employee_role)

        headers = self.get_auth_header(non_admin_user)
        response = self.client.post(self.url, self.valid_payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Only Admins are allowed to perform this action.')


class CreateDesignationTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('create_designation')
        
        # Create roles
        self.admin_role, _ = Role.objects.get_or_create(name='Admin')
        self.employee_role, _ = Role.objects.get_or_create(name='Employee')

        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin', 
            email='admin@example.com',
            password='adminpass123'
        )

        # Create non-admin user 
        self.employee_user = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='emppass123'
        )

        # Assign roles
        UserRole.objects.get_or_create(user=self.admin_user, role=self.admin_role)
        UserRole.objects.get_or_create(user=self.employee_user, role=self.employee_role)

        self.valid_payload = {
            "title": "Team Lead",
            "description": "Leads a small engineering team"
        }

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_admin_can_create_designation(self):
        headers = self.get_auth_header(self.admin_user)
        response = self.client.post(self.url, self.valid_payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Designation created successfully.')
        self.assertTrue(Designation.objects.filter(title='Team Lead').exists())

    def test_non_admin_cannot_create_designation(self):
        headers = self.get_auth_header(self.employee_user)
        response = self.client.post(self.url, self.valid_payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Only Admins can create designations.')


class EditDepartmentTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('edit_department')

        # Create roles
        self.admin_role, _ = Role.objects.get_or_create(name='Admin')
        self.employee_role, _ = Role.objects.get_or_create(name='Employee')

        # Users
        self.admin_user = User.objects.create_user(username='admin', 
                                                   email='admin@example.com', 
                                                   password='adminpass')
        self.employee_user = User.objects.create_user(username='user', 
                                                      email='user@example.com', 
                                                      password='userpass')

        # Assign roles
        UserRole.objects.get_or_create(user=self.admin_user, role=self.admin_role)
        UserRole.objects.get_or_create(user=self.employee_user, role=self.employee_role)

        # Create a department
        self.department = Department.objects.create(name='Finance', description='Handles money')

        self.valid_payload = {
            "department_id": self.department.id,
            "name": "Updated Finance",
            "description": "Handles all financial operations"
        }

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_admin_can_edit_department(self):
        headers = self.get_auth_header(self.admin_user)
        response = self.client.patch(self.url, self.valid_payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Department updated successfully.")
        self.department.refresh_from_db()
        self.assertEqual(self.department.name, "Updated Finance")

    def test_non_admin_cannot_edit_department(self):
        headers = self.get_auth_header(self.employee_user)
        response = self.client.patch(self.url, self.valid_payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], "User does not have permission.")

    def test_missing_department_id(self):
        headers = self.get_auth_header(self.admin_user)
        invalid_payload = {"name": "No ID Provided"}
        response = self.client.patch(self.url, invalid_payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Department ID is required.")

    def test_invalid_department_id(self):
        headers = self.get_auth_header(self.admin_user)
        response = self.client.patch(self.url, {"department_id": 9999}, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Department does not exist.")


class DeleteDepartmentTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('delete_department')

        # Roles
        self.admin_role, _ = Role.objects.get_or_create(name='Admin')
        self.employee_role, _ = Role.objects.get_or_create(name='Employee')

        # Users
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='adminpass')
        self.employee_user = User.objects.create_user(username='emp', email='emp@example.com', password='emppass')

        # Assign roles
        UserRole.objects.get_or_create(user=self.admin_user, role=self.admin_role)
        UserRole.objects.get_or_create(user=self.employee_user, role=self.employee_role)

        # Create a department
        self.department = Department.objects.create(name='HR', description='Human Resources')

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_admin_can_soft_delete_department(self):
        payload = {"department_id": self.department.id}
        headers = self.get_auth_header(self.admin_user)
        response = self.client.delete(self.url, payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Department soft-deleted successfully.')

        self.department.refresh_from_db()
        self.assertIsNotNone(self.department.deleted_at)

    def test_non_admin_cannot_delete_department(self):
        payload = {"department_id": self.department.id}
        headers = self.get_auth_header(self.employee_user)
        response = self.client.delete(self.url, payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Only Admins can delete departments.')

    def test_deleting_nonexistent_or_already_deleted_department(self):
        # Soft-delete manually
        self.department.deleted_at = now()
        self.department.save()

        payload = {"department_id": self.department.id}
        headers = self.get_auth_header(self.admin_user)
        response = self.client.delete(self.url, payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Department not found or already deleted.', response.data['department_id'])

    def test_missing_department_id(self):
        headers = self.get_auth_header(self.admin_user)
        response = self.client.delete(self.url, {}, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('department_id', response.data)


class EditEmployeeProfileTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('edit_employee_profile')

        # Create roles
        self.admin_role, _ = Role.objects.get_or_create(name="Admin")
        self.employee_role, _ = Role.objects.get_or_create(name="Employee")

        # Create users
        self.admin_user = User.objects.create_user(username="admin", email="admin@example.com", password="adminpass")
        self.employee_user = User.objects.create_user(username="emp1", email="emp1@example.com", password="emppass")

        # Assign roles
        UserRole.objects.create(user=self.admin_user, role=self.admin_role)
        UserRole.objects.create(user=self.employee_user, role=self.employee_role)

        # Department and Designation
        self.department = Department.objects.create(name="Engineering")
        self.designation = Designation.objects.create(title="Developer")

        # Create profile
        self.profile = EmployeeProfile.objects.create(
            user=self.employee_user,
            phone_number="1234567890",
            date_of_birth="1990-01-01",
            join_date="2022-01-01",
            department=self.department,
            designation=self.designation
        )

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_admin_can_edit_employee_profile(self):
        payload = {
            "employee_id": self.profile.id,
            "phone_number": "9998887777"
        }
        headers = self.get_auth_header(self.admin_user)
        response = self.client.patch(self.url, payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Employee profile updated successfully.")
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number, "9998887777")

    def test_non_admin_cannot_edit_employee_profile(self):
        payload = {
            "employee_id": self.profile.id,
            "phone_number": "1112223333"
        }
        headers = self.get_auth_header(self.employee_user)
        response = self.client.patch(self.url, payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], "Only Admins can edit employee profiles.")

    def test_edit_with_invalid_employee_id(self):
        payload = {
            "employee_id": 9999,
            "phone_number": "1111111111"
        }
        headers = self.get_auth_header(self.admin_user)
        response = self.client.patch(self.url, payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Employee profile not found.")

    def test_edit_with_invalid_field(self):
        payload = {
            "employee_id": self.profile.id,
            "invalid_field": "unexpected"
        }
        headers = self.get_auth_header(self.admin_user)
        response = self.client.patch(self.url, payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid field(s) in request.", response.data['error'])
        self.assertIn("invalid_field", response.data['invalid_fields'])

    def test_edit_without_employee_id(self):
        payload = {
            "phone_number": "1231231234"
        }
        headers = self.get_auth_header(self.admin_user)
        response = self.client.patch(self.url, payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Employee ID is required.")


class ListDepartmentsTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('list_departments')

        # Create user
        self.user = User.objects.create_user(username="john", email="john@example.com", password="johnpass")
        self.admin_role, _ = Role.objects.get_or_create(name='Admin')
        UserRole.objects.create(user=self.user, role=self.admin_role)

        # Create departments
        self.active_department = Department.objects.create(name="Engineering", description="Core tech team")
        self.deleted_department = Department.objects.create(name="HR", description="Soft-deleted dept", deleted_at=now())

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_authenticated_user_can_view_departments(self):
        headers = self.get_auth_header(self.user)
        response = self.client.get(self.url, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Engineering')

    def test_unauthenticated_user_cannot_view_departments(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ListDesignationsTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('list_designations')

        # Create user
        self.user = User.objects.create_user(
            username='testuser', 
            email='testuser@example.com', 
            password='testpass'
        )

        # Assign any role (not required, but keeping your pattern)
        role, _ = Role.objects.get_or_create(name="Employee")
        UserRole.objects.get_or_create(user=self.user, role=role)

        # Create designations
        Designation.objects.create(title='Developer', description='Writes code')
        Designation.objects.create(title='Manager', description='Manages team')
        Designation.objects.create(title='Tester', description='Tests applications', deleted_at=now())  # Soft-deleted

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_authenticated_user_can_list_designations(self):
        headers = self.get_auth_header(self.user)
        response = self.client.get(self.url, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only non-deleted ones

        # Ensure sorted order by title
        self.assertEqual(response.data[0]['title'], 'Developer')
        self.assertEqual(response.data[1]['title'], 'Manager')

    def test_unauthenticated_user_cannot_list_designations(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ListEmployeesTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('list_employees')

        # Create roles
        self.role, _ = Role.objects.get_or_create(name='Employee')

        # Users
        self.user1 = User.objects.create_user(username='john', email='john@example.com', password='johnpass')
        self.user2 = User.objects.create_user(username='doe', email='doe@example.com', password='doepass')
        self.deleted_user = User.objects.create_user(username='ghost', email='ghost@example.com', password='ghostpass')

        # Assign roles
        UserRole.objects.get_or_create(user=self.user1, role=self.role)
        UserRole.objects.get_or_create(user=self.user2, role=self.role)
        UserRole.objects.get_or_create(user=self.deleted_user, role=self.role)

        # Department and Designation
        self.department = Department.objects.create(name='Engineering')
        self.designation = Designation.objects.create(title='Developer')

        # Employee profiles
        EmployeeProfile.objects.create(
            user=self.user1,
            phone_number='1234567890',
            date_of_birth='1995-01-01',
            join_date='2023-01-01',
            department=self.department,
            designation=self.designation
        )

        EmployeeProfile.objects.create(
            user=self.user2,
            phone_number='1112223333',
            date_of_birth='1994-02-02',
            join_date='2022-02-02',
            department=self.department,
            designation=self.designation
        )

        EmployeeProfile.objects.create(
            user=self.deleted_user,
            phone_number='9999999999',
            date_of_birth='1990-03-03',
            join_date='2020-03-03',
            department=self.department,
            designation=self.designation,
            deleted_at=now()  # Soft-deleted
        )

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_authenticated_user_can_list_employees(self):
        headers = self.get_auth_header(self.user1)
        response = self.client.get(self.url, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only non-deleted profiles

        # Check keys in response
        for emp in response.data:
            self.assertIn('user_username', emp)
            self.assertIn('designation_title', emp)
            self.assertIn('department_name', emp)

    def test_unauthenticated_user_cannot_list_employees(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ListUnassignedEmployeesTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('list_unassigned_employees')

        # Create roles
        self.admin_role, _ = Role.objects.get_or_create(name='Admin')
        self.manager_role, _ = Role.objects.get_or_create(name='Manager')
        self.employee_role, _ = Role.objects.get_or_create(name='Employee')

        # Create users
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='adminpass')
        self.manager_user = User.objects.create_user(username='manager', email='manager@example.com', password='managerpass')
        self.employee_user = User.objects.create_user(username='employee', email='employee@example.com', password='emppass')
        self.extra_user1 = User.objects.create_user(username='free1', email='free1@example.com', password='pass')
        self.extra_user2 = User.objects.create_user(username='free2', email='free2@example.com', password='pass')

        # Assign roles
        UserRole.objects.create(user=self.admin_user, role=self.admin_role)
        UserRole.objects.create(user=self.manager_user, role=self.manager_role)
        UserRole.objects.create(user=self.employee_user, role=self.employee_role)
        UserRole.objects.create(user=self.extra_user1, role=self.employee_role)


        # Create department and designation
        self.department = Department.objects.create(name='Engineering')
        self.designation = Designation.objects.create(title='Developer')

        # Manager profile (required for Project manager_id)
        self.manager_profile = EmployeeProfile.objects.create(
            user=self.manager_user,
            phone_number='000',
            department=self.department,
            designation=self.designation,
            join_date='2023-01-01'
        )

        # Employee Profiles
        self.emp1 = EmployeeProfile.objects.create(
            user=self.employee_user,
            phone_number='111',
            department=self.department,
            designation=self.designation,
            join_date='2023-01-01'
        )
        self.emp2 = EmployeeProfile.objects.create(
            user=self.extra_user1,
            phone_number='222',
            department=self.department,
            designation=self.designation,
            join_date='2023-01-01'
        )
        self.emp3 = EmployeeProfile.objects.create(
            user=self.extra_user2,
            phone_number='333',
            department=self.department,
            designation=self.designation,
            join_date='2023-01-01',
            deleted_at=now()
        )

        # ✅ Create project with manager
        self.project = Project.objects.create(
            name="Test Project",
            description="Project for test",
            start_date='2023-01-01',
            created_by=self.admin_user,
            manager=self.manager_profile  # FIXED
        )

        # Assign emp1 to project
        ProjectAssignment.objects.create(
            project=self.project,
            employee=self.emp1,
            assignment_status='active',
            assigned_by=self.admin_user
        )

    def get_auth_header(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}

    def test_admin_can_view_unassigned_employees(self):
        headers = self.get_auth_header(self.admin_user)
        response = self.client.get(self.url, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # emp2 only
        self.assertEqual(response.data[0]['name'], 'free1')

    def test_manager_can_view_unassigned_employees(self):
        headers = self.get_auth_header(self.manager_user)
        response = self.client.get(self.url, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'free1')

    def test_employee_cannot_view_unassigned_employees(self):
        headers = self.get_auth_header(self.employee_user)
        response = self.client.get(self.url, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Only Admins and Managers can view this list.')

    def test_unauthenticated_user_cannot_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)      




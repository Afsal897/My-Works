from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Role, UserRole 
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now

User = get_user_model()

class RegisterAdminTest(APITestCase):

    def setUp(self):
        self.url = reverse('register_admin')

        self.valid_payload = {
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "adminpass123",
            "confirm_password": "adminpass123"
        }

        self.invalid_payload = {
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "adminpass123",
            "confirm_password": "wrongpass"
        }

    def test_register_admin_successfully(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Admin user registered successfully.")
        self.assertTrue(User.objects.filter(username="adminuser").exists())
        self.assertTrue(Role.objects.filter(name="Admin").exists())
        self.assertTrue(UserRole.objects.filter(user__username="adminuser", role__name="Admin").exists())

    def test_register_admin_with_mismatched_passwords(self):
        response = self.client.post(self.url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_admin_when_admin_already_exists(self):
        # Create a user and assign 'Admin' role
        user = User.objects.create_user(username="existing_admin", password="pass123")
        admin_role, _ = Role.objects.get_or_create(name="Admin")
        UserRole.objects.create(user=user, role=admin_role)

        # Try to create another admin
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], "Admin user already exists.")


class RegisterEmployeeOrManagerTest(APITestCase):

    def setUp(self):
        # Create admin user and assign Admin role
        self.admin_user = User.objects.create_user(username="admin", email="admin@example.com", password="admin123")
        self.employee_user = User.objects.create_user(username="emp", email="emp@example.com", password="emp123")

        admin_role, _ = Role.objects.get_or_create(name="Admin")
        Role.objects.get_or_create(name="Manager")
        Role.objects.get_or_create(name="Employee")
        UserRole.objects.create(user=self.admin_user, role=admin_role)

        # Token for admin and non-admin
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.employee_token = str(RefreshToken.for_user(self.employee_user).access_token)

        # Endpoint 
        self.url = reverse('register_employee_or_manager')

        self.valid_payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "test1234",
            "confirm_password": "test1234",
            "role": "Employee"
        }

    def test_admin_can_register_employee(self):
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Employee user registered successfully.")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_admin_can_register_manager(self):
        payload = self.valid_payload.copy()
        payload["username"] = "manageruser"
        payload["role"] = "Manager"

        response = self.client.post(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Manager user registered successfully.")

    def test_non_admin_cannot_register_user(self):
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "Only Admins are allowed to perform this action.")

    def test_invalid_role_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["role"] = "InvalidRole"

        response = self.client.post(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Role must be either 'Employee' or 'Manager'.")

    def test_password_mismatch_is_rejected(self):
        payload = self.valid_payload.copy()
        payload["confirm_password"] = "wrongpass"

        response = self.client.post(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)


class LoginUserTest(APITestCase):

    def setUp(self):
        self.url = reverse('login_user')

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        self.role,_ = Role.objects.get_or_create(name="Employee")
        UserRole.objects.create(user=self.user, role=self.role)

    def test_login_with_username(self):
        response = self.client.post(self.url, {
            "identifier": "testuser",
            "password": "testpassword"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["role"], "Employee")

    def test_login_with_email(self):
        response = self.client.post(self.url, {
            "identifier": "test@example.com",
            "password": "testpassword"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["role"], "Employee")

    def test_login_invalid_password(self):
        response = self.client.post(self.url, {
            "identifier": "testuser",
            "password": "wrongpassword"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Invalid login credentials.")

    def test_login_nonexistent_user(self):
        response = self.client.post(self.url, {
            "identifier": "doesnotexist",
            "password": "any"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Invalid login credentials.")

    def test_login_disabled_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.url, {
            "identifier": "testuser",
            "password": "testpassword"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "User is disabled.")


class ChangePasswordTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpassword123"
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.url = reverse('changepassword')

        self.headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.access_token}"
        }

    def test_change_password_successfully(self):
        payload = {
            "old_password": "oldpassword123",
            "new_password": "newpassword456",
            "confirm_password": "newpassword456"
        }
        response = self.client.put(self.url, data=payload, format="json", **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password changed successfully.")

        # Check if password actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword456"))

    def test_change_password_wrong_old_password(self):
        payload = {
            "old_password": "wrongold",
            "new_password": "newpassword456",
            "confirm_password": "newpassword456"
        }
        response = self.client.put(self.url, data=payload, format="json", **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["old_password"], "Incorrect old password.")

    def test_change_password_mismatch(self):
        payload = {
            "old_password": "oldpassword123",
            "new_password": "newpassword456",
            "confirm_password": "doesnotmatch"
        }
        response = self.client.put(self.url, data=payload, format="json", **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("New passwords do not match.", response.data["confirm_password"])

    def test_change_password_missing_fields(self):
        payload = {
            "old_password": "oldpassword123",
            # missing new_password and confirm_password
        }
        response = self.client.put(self.url, data=payload, format="json", **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertIn("confirm_password", response.data)


class ChangeUserRoleTest(APITestCase):

    def setUp(self):
        # Create roles
        self.admin_role, _ = Role.objects.get_or_create(name="Admin")
        self.manager_role, _ = Role.objects.get_or_create(name="Manager")
        self.employee_role, _ = Role.objects.get_or_create(name="Employee")

        # Create users
        self.admin_user = User.objects.create_user(
            username="admin", 
            email="admin@example.com",
            password="pass123"
        )
        self.target_user = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="pass123"
        )
        self.other_user = User.objects.create_user(
            username="other", 
            email="other@example.com",
            password="pass123"
        )

        # Assign roles
        UserRole.objects.create(user=self.admin_user, role=self.admin_role)
        UserRole.objects.create(user=self.target_user, role=self.employee_role)
        UserRole.objects.create(user=self.other_user, role=self.manager_role)

        # Get tokens
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.other_token = str(RefreshToken.for_user(self.other_user).access_token)

        self.url = reverse('changerole')

    def test_admin_can_change_role(self):
        payload = {
            "user_id": self.target_user.id,
            "role_id": self.manager_role.id
        }
        response = self.client.put(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Role changed successfully")

        updated_role = UserRole.objects.get(user=self.target_user).role
        self.assertEqual(updated_role.name, "Manager")

    def test_non_admin_cannot_change_role(self):
        payload = {
            "user_id": self.target_user.id,
            "role_id": self.manager_role.id
        }
        response = self.client.put(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.other_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "Only Admins are allowed to perform this action.")

    def test_change_to_nonexistent_user(self):
        payload = {
            "user_id": 9999,
            "role_id": self.manager_role.id
        }
        response = self.client.put(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("User does not exist", str(response.data))

    def test_change_to_nonexistent_role(self):
        payload = {
            "user_id": self.target_user.id,
            "role_id": 9999
        }
        response = self.client.put(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Role does not exist", str(response.data))

    def test_cannot_assign_admin_role(self):
        payload = {
            "user_id": self.target_user.id,
            "role_id": self.admin_role.id
        }
        response = self.client.put(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot assign admin role", str(response.data))

    def test_cannot_change_role_of_admin_user(self):
        payload = {
            "user_id": self.admin_user.id,
            "role_id": self.manager_role.id
        }
        response = self.client.put(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot change role of an Admin user.", str(response.data))


class DeleteUserTest(APITestCase):

    def setUp(self):
        # Create roles
        self.admin_role,_ = Role.objects.get_or_create(name="Admin")
        self.employee_role,_ = Role.objects.get_or_create(name="Employee")

        # Create users
        self.admin = User.objects.create_user(username="admin",
                                              email="admin@example.com", 
                                              password="admin123")
        self.target_user = User.objects.create_user(username="target", 
                                                    email="target@example.com", 
                                                    password="target123")
        self.other_user = User.objects.create_user(username="nonadmin", 
                                                   email="nonadmin@example.com", 
                                                   password="pass123")
        self.deleted_user = User.objects.create_user(username="deleted", 
                                                     email="deleted@example.com", 
                                                     password="pass123", is_active=False, deleted_at=now())

        # Assign roles
        UserRole.objects.create(user=self.admin, role=self.admin_role)
        UserRole.objects.create(user=self.target_user, role=self.employee_role)
        UserRole.objects.create(user=self.other_user, role=self.employee_role)
        UserRole.objects.create(user=self.deleted_user, role=self.employee_role)

        # Tokens
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)
        self.non_admin_token = str(RefreshToken.for_user(self.other_user).access_token)

        self.url = reverse('delete_user')

    def test_admin_can_soft_delete_user(self):
        payload = {"user_id": self.target_user.id}
        response = self.client.delete(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User deleted (soft delete).")

        self.target_user.refresh_from_db()
        self.assertFalse(self.target_user.is_active)
        self.assertIsNotNone(self.target_user.deleted_at)

    def test_non_admin_cannot_delete_user(self):
        payload = {"user_id": self.target_user.id}
        response = self.client.delete(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.non_admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "only admins can delete accounts")

    def test_cannot_delete_nonexistent_or_already_deleted_user(self):
        payload = {"user_id": self.deleted_user.id}
        response = self.client.delete(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user does not exist or is already deleted", str(response.data))

    def test_cannot_delete_admin_user(self):
        payload = {"user_id": self.admin.id}
        response = self.client.delete(
            self.url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Admin accounts cannot be deleted", str(response.data))


class ListUsersWithRolesTest(APITestCase):

    def setUp(self):
        self.url = reverse('list_user')

        # Create roles
        self.employee_role,_ = Role.objects.get_or_create(name="Employee")
        self.manager_role,_ = Role.objects.get_or_create(name="Manager")

        # Create users
        self.user1 = User.objects.create_user(username="user1", email="u1@example.com", password="pass123")
        self.user2 = User.objects.create_user(username="user2", email="u2@example.com", password="pass123")
        self.deleted_user = User.objects.create_user(username="deleted", email="deleted@example.com", password="pass123", deleted_at=now())

        # Assign roles
        UserRole.objects.create(user=self.user1, role=self.employee_role)
        UserRole.objects.create(user=self.user2, role=self.manager_role)

        # Token for authenticated access
        self.token = str(RefreshToken.for_user(self.user1).access_token)
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

    def test_list_users_excludes_deleted_users(self):
        response = self.client.get(self.url, format="json", **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user["username"] for user in response.data]
        self.assertIn("user1", usernames)
        self.assertIn("user2", usernames)
        self.assertNotIn("deleted", usernames)

    def test_users_have_role_info(self):
        response = self.client.get(self.url, format="json", **self.headers)
        roles = [user["role"]["name"] for user in response.data if user["role"]]
        self.assertIn("Employee", roles)
        self.assertIn("Manager", roles)

    def test_requires_authentication(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


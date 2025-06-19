from .auth_url import urlpatterns as auth_urls
from .employee_url import urlpatterns as employee_urls
from .skill_url import urlpatterns as skill_urls
from .project_url import urlpatterns as project_urls


urlpatterns = auth_urls + employee_urls + skill_urls + project_urls

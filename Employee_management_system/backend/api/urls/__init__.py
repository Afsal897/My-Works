from .auth_url import urlpatterns as auth_urls
from .employee_url import urlpatterns as employee_urls
from .skill_url import urlpatterns as skill_urls
from .project_url import urlpatterns as project_urls
from .leave_url import urlpatterns as leave_urls
from .timepay_url import urlpatterns as timepay_urls


urlpatterns = auth_urls + employee_urls + skill_urls + project_urls + leave_urls + timepay_urls

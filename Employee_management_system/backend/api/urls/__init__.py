from .auth_url import urlpatterns as auth_urls
from .employee_url import urlpatterns as employee_urls
from .skill_url import urlpatterns as skill_urls
from .project_url import urlpatterns as project_urls
from .leave_url import urlpatterns as leave_urls
from .timepay_url import urlpatterns as timepay_urls
from .support_url import urlpatterns as support_urls
from .performance_url import urlpatterns as perfomance_urls


url_1 = auth_urls + employee_urls + skill_urls + leave_urls
url_2 = project_urls + timepay_urls + support_urls + perfomance_urls


#final
urlpatterns = url_1 + url_2

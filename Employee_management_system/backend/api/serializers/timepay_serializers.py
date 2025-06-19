from rest_framework import serializers
from api.models import Timesheet, Payroll

class TimesheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timesheet
        fields = '__all__'

class PayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = '__all__'

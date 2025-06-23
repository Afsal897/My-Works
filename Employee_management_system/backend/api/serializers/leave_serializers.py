from rest_framework import serializers
from api.models import Leave, LeaveBalance
from django.utils.timezone import now

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'


class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = '__all__'


class LeaveActionSerializer(serializers.Serializer):
    leave_id = serializers.IntegerField()

    def validate_leave_id(self, value):
        try:
            leave = Leave.objects.get(id=value, deleted_at__isnull=True)
        except Leave.DoesNotExist:
            raise serializers.ValidationError("Leave request not found or already deleted.")

        if leave.status != "pending":
            raise serializers.ValidationError("Only pending leaves can be approved or rejected.")
        return value

    def approve(self, user):
        leave = Leave.objects.get(id=self.validated_data['leave_id'])
        employee = leave.employee
        leave_days = (leave.end_date - leave.start_date).days + 1

        try:
            balance_record = LeaveBalance.objects.get(
                employee=employee,
                leave_type=leave.leave_type,
                deleted_at__isnull=True
            )
        except LeaveBalance.DoesNotExist:
            # No balance → all days become LOP
            leave.is_lop = True
            lop_days = leave_days
        else:
            if balance_record.balance >= leave_days:
                # Full paid leave
                balance_record.balance -= leave_days
                balance_record.save()
                leave.is_lop = False
                lop_days = 0
            else:
                # Partial LOP
                lop_days = leave_days - balance_record.balance
                balance_record.lop_count += lop_days
                balance_record.balance = 0  # Use up remaining balance
                balance_record.save()
                leave.is_lop = True

        leave.status = 'approved'
        leave.approved_by = user
        leave.approved_on = now()
        leave.save()
        return leave

    def reject(self, user):
        leave = Leave.objects.get(id=self.validated_data['leave_id'])
        leave.status = 'rejected'
        leave.approved_by = user
        leave.approved_on = now()
        leave.save()
        return leave
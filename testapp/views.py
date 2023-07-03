from django.shortcuts import render
from django.views.generic import View
from testapp.models import Employee
from django.http import HttpResponse
# from django.core.serializers import serialize
from testapp.mixin import SerializeMixin, HttpResponseMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from testapp.utils import is_json
from testapp.forms import EmployeeForm
import json

# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class EmployeeDetailCBV(SerializeMixin, HttpResponseMixin, View):
    def get_object_by_id(self, id):
        try:
            emp = Employee.objects.get(id=id)
        except Employee.DoesNotExist:
            emp = None

        return emp

    def get(self, request, id, *args, **kwargs):
        try:
            emp = Employee.objects.get(id=id)  # emp is not list
        except Employee.DoesNotExist:
            json_data = json.dumps({'message': 'The requested resource not availabe'})
            # return HttpResponse(json_data, content_type='application/json', status=404)
            return self.render_to_http_response(json_data, 404)
        else:
            json_data = self.serialize([emp])
            # return HttpResponse(json_data, content_type='application/json', status=200)
            return self.render_to_http_response(json_data)
        # print(emp)
        # Method 1
        # emp_data = {
        #     "eno": emp.eno,
        #     "ename": emp.ename,
        #     "esal": emp.esal,
        #     "eaddr": emp.eaddr,
        # }
        #
        # json_data = json.dumps(emp_data)

        # Method 2
        # json_data = serialize('json', [emp], fields=('eno', 'ename', 'eaddr'))

        # return HttpResponse(json_data, content_type="application/json")

    def put(self, request, id, *args, **kwargs):
        emp = self.get_object_by_id(id)

        if emp is None:
            json_data = json.dumps({'message': 'Then matched resource found, no update'})
            return self.render_to_http_response(json_data, 404)

        data = request.body
        valid_json = is_json(data)
        if not valid_json:
            json_data = json.dumps({'msg': 'please send valid json data only'})
            return self.render_to_http_response(json_data, 400)

        provided_data = json.loads(data)
        original_data = {
            'eno': emp.eno,
            'ename': emp.ename,
            'esal': emp.esal,
            'eaddr': emp.eaddr
        }
        original_data.update(provided_data)
        form = EmployeeForm(original_data, instance=emp)

        if form.is_valid():
            form.save(commit=True)
            json_data = json.dumps({'message': 'Resource updated successfully'})
            return self.render_to_http_response(json_data)
        if form.errors:
            json_data = json.dumps(form.errors)
            return self.render_to_http_response(json_data, 400)

    def delete(self, request, id, *args, **kwargs):
        emp = Employee.objects.get(id=id)
        if emp is None:
            json_data = json.dumps({'message': 'Then matched resource found, no delete'})
            return self.render_to_http_response(json_data, 404)

        status, deleted_item = emp.delete()
        if status == 1:
            json_data = json.dumps({'message': 'Resource deleted successfully'})
            return self.render_to_http_response(json_data)
        json_data = json.dumps({'msg': 'unable to delete, please try again'})
        return self.render_to_http_response(json_data)


@method_decorator(csrf_exempt, name='dispatch')
class EmployeeListCBV(SerializeMixin, HttpResponseMixin, View):
    def get(self, request, *args, **kwargs):
        empList = Employee.objects.all()   # empList is list
        json_data = self.serialize(empList)

        # return HttpResponse(json_data, content_type="application/json")
        return self.render_to_http_response(json_data)

    def post(self, request, *args, **kwargs):
        data = request.body
        valid_json = is_json(data)

        if not valid_json:
            json_data = json.dumps({'msg': 'please send valid json data only'})
            return self.render_to_http_response(json_data, 400)

        emp_data = json.loads(data)
        form = EmployeeForm(emp_data)

        if form.is_valid():
            form.save(commit=True)
            json_data = json.dumps({'message': 'Resource created successfully'})
            return self.render_to_http_response(json_data)
        if form.errors:
            json_data = json.dumps(form.errors)
            return self.render_to_http_response(json_data, 400)

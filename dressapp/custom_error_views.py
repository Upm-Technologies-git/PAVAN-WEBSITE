from django.shortcuts import render

def custom_error_view(request, exception=None, status_code=500):
    return render(request, 'error.html', {'status_code': status_code}, status=status_code)

def custom_404_view(request, exception):
    return custom_error_view(request, exception, status_code=404)

def custom_500_view(request):
    return custom_error_view(request, status_code=500)

def custom_403_view(request, exception):
    return custom_error_view(request, exception, status_code=403)

def custom_400_view(request, exception):
    return custom_error_view(request, exception, status_code=400)

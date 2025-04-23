from django.http import JsonResponse
from .models import Customer

def format_cnic(raw_cnic: str) -> str:
    if len(raw_cnic) == 13:
        return f"{raw_cnic[:5]}-{raw_cnic[5:12]}-{raw_cnic[12]}"
    return raw_cnic 

def customer_search(request):
    """
    API endpoint to search for a customer by CNIC
    """
    cnic = request.GET.get('cnic', '').replace('-', '')
    
    if not cnic:
        return JsonResponse({'found': False, 'error': 'No CNIC provided'})
    
    try:
        customer = Customer.objects.get(cnic=cnic)
        return JsonResponse({
            'found': True,
            'customer': {
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'phone_number': customer.phone_number,
                'address': customer.address,
                'cnic': format_cnic(str(customer.cnic)),
            }
        })
    except Customer.DoesNotExist:
        return JsonResponse({'found': False})
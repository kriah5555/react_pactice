from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect # redirect to direct url redirect(to)
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from .forms import ContactForm, DeviseForm
from .models import ContactDetails, Devise, DeviseApis, APICountThreshold

from . import UserFuncrtions
from django.views.generic import UpdateView, TemplateView
from django.urls import reverse
from django.contrib import messages #import messages
from datetime import datetime
from django.views.generic import CreateView, UpdateView
from map.views import get_marker_color
from django.contrib.auth.models import User

# Create your views here.

def user_login_access(request):
    user = request.user
    if not user.is_staff and user.is_authenticated:
        devise    = Devise.objects.filter(devise_id=user.username).first()
        apis      = DeviseApis.objects.filter(device=devise)
        used      = 0
        remaining = 0
        if (len(apis)):
            api_thresholds = APICountThreshold.objects.filter(devise=devise).first()
            if api_thresholds:
                val       = api_thresholds.red - len(apis)
                used      = len(apis)
                remaining = 0 if (val < 0) else api_thresholds.red - len(apis)

        request.session['pk']             = devise.pk
        request.session['name']           = devise.name
        request.session['setial_no']      = devise.setial_no
        request.session['devise_id']      = devise.devise_id
        request.session['chipset_no']     = devise.chipset_no
        request.session['email']          = devise.email
        request.session['phone']          = devise.phone
        request.session['address1']       = devise.address1
        request.session['address2']       = devise.address2
        request.session['purchase_date']  = str(devise.purchase_date)
        request.session['time_of_sale']   = str(devise.time_of_sale)
        request.session['warrenty']       = str(devise.warrenty)
        request.session['amount_paid']    = devise.amount_paid
        request.session['balance_amount'] = devise.balance_amount
        request.session['api_usage']      = len(apis)
        request.session['api_threshold']  = True if (api_thresholds) else False
        request.session['used']           = used
        request.session['color']          = get_marker_color(devise)
        request.session['remaining']      = remaining

        print(used, remaining, api_thresholds,'------------')

        return redirect('/devise_user_details/')

def home(request):
    if request.method == 'GET':
        template_name = 'home1.html'
        return render(request, template_name)
    elif request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Contact details added successfully")
        else:
            return render(request, 'home1.html', {'errors': form.errors})
        
        template_name = 'home1.html'
        return render(request, template_name, {'message' : 'Contact details has been added successfully'})

def login(request):
    context = dict()
    if request.method == 'GET':
        template_name = 'login1.html'
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username = username, password = password)
        if user is not None:
            auth.login(request,user)
            resp = user_login_access(request)
            if  resp:
                return resp
            return redirect('/dashboard/')
        else:
            template_name = 'login1.html'
            context       =  {'error' : 'Invalid username or password'}
    return render(request, template_name, context = context)
    
def logout(request):
    auth.logout(request)
    return redirect('/')

def users(request):
    resp = user_login_access(request)
    if  resp:
        return resp
    template_name = "users.html"
    return render(request, template_name)

def add_devise(request):
    resp = user_login_access(request)
    if  resp:
        return resp
    context = {'message' : ''}
    if request.method == 'GET':
        template_name = "add_devise.html"
    elif request.method == 'POST':
        form = DeviseForm(request.POST)
        if form.is_valid():
            form.save()
            UserFuncrtions.create_user(request.POST['devise_id'], request.POST['email'])
            template_name = 'device_list.html'
            messages.success(request,"Devise added successfully")
            return redirect("/device-list/")
        else:
            errors  = form.errors
            field_errors = dict()
            for error in errors:
                field_errors[error] = errors[error]

            default_values = {
                'name'           : request.POST['name'],
                'devise_id'      : request.POST['devise_id'],
                'setial_no'      : request.POST['setial_no'],
                'chipset_no'     : request.POST['chipset_no'],
                'email'          : request.POST['email'],
                'address1'       : request.POST['address1'],
                'address2'       : request.POST['address2'],
                'purchase_date'  : request.POST['purchase_date'],
                'time_of_sale'   : request.POST['time_of_sale'],
                'warrenty'       : request.POST['warrenty'],
                'amount_paid'    : request.POST['amount_paid'],
                'balance_amount' : request.POST['balance_amount'],
                'phone'          : request.POST['phone'],
            }
            return render(request, 'add_devise.html', {'devise' : default_values, 'field_errors' : field_errors})
    return render(request, template_name = template_name, context=context)

def edit_devise(request, **kwargs):
    resp = user_login_access(request)
    if  resp:
        return resp
    context = {'message' : ''}
    devise  = Devise.objects.get(pk = kwargs['pk'])
    devise.purchase_date = datetime.strptime(str(devise.purchase_date), '%Y-%m-%d')
    devise.warrenty = datetime.strptime(str(devise.warrenty), '%Y-%m-%d')
    if request.method == 'GET':
        template_name = "add_devise.html"
        context       = {
            'devise' : devise,
        }
    elif request.method == 'POST':
        form = DeviseForm(request.POST or None, instance=devise)
        if form.is_valid():
            form.save()
            messages.success(request,"Devise updated successfully")
            return redirect("/device-list/")
        else:
            return render(request, 'add_devise.html', {'errors': form.errors, 'devise' : devise, })
    return render(request, template_name = template_name, context=context)

def notifications(request, **kwargs):
    resp = user_login_access(request)
    if  resp:
        return resp
    if (kwargs):
       data = ContactDetails.objects.get(pk = kwargs['pk'])
       data.status = False
       data.save()
    
    notifications_all = ContactDetails.objects.all()
    template_name     = 'notifications.html'
    context = {
        'notification_active'   : notifications_all.filter(status=True),
        'notification_inactive' : notifications_all.filter(status=False),
    }
    return render(request, template_name = template_name, context = context)

def devise_list(request, **kwargs):
    resp = user_login_access(request)
    if  resp:
        return resp
    if request.method == 'POST':
        pk = request.POST['pk']
        if pk:
            devises = Devise.objects.filter(pk=request.POST['pk'])
        else :
            devises = Devise.objects.all()
    else:
        devises = Devise.objects.all()

    devices = Devise.objects.all()
    template_name     = 'device_list.html'
    
    context = {
        'devise_count' :len(devises),
        'devises'      : devises,
        'devices'      : devices,
    }
    return render(request, template_name = template_name, context = context)

def api_list(request, **kwargs):
    resp = user_login_access(request)
    if  resp:
        return resp
    n, p, k, name = '', '', '', ''
    if request.method == 'POST':
        # n = request.POST['n']
        # p = request.POST['p']
        # k = request.POST['k']
        name = request.POST['area_name']
        
    devise = Devise.objects.get(pk = kwargs['pk'])
    apis = DeviseApis.objects.filter(device__pk=kwargs['pk'], area_name__contains=name)
    template_name     = 'api_list.html'
    context = {
        'api_count'   : len(apis),
        'apis'        : apis,
        'devise' : devise,
    }
    return render(request, template_name = template_name, context = context)

def devise_details(request, **kwargs):
    resp = user_login_access(request)
    if  resp:
        return resp
    devise  = Devise.objects.get(pk = kwargs['pk'])

    # for i in range(56):
    #     DeviseApis.objects.create(
    #         device=devise,
    #         area_name='bond'+str(i),
    #         devise_id=70099+i,
    #         serial_no=1208827+i,
    #         electrical_conduction=89,
    #         nitrogen=13,
    #         phosphorous=45,
    #         potassium=98,
    #         calcium=43,
    #         magnesium=23,
    #         zinc=55,
    #         manganese=78,
    #         iron=89,
    #         copper=65,
    #         boron=12,
    #         molybdenum=49,
    #         chlorine=23,
    #         nickel=44,
    #         organic_carboa=12,
    #         )


    apis          = DeviseApis.objects.filter(device=devise)
    template_name = "devise_details1.html"
    used          = 0
    remaining     = 0
    if (len(apis)):
        api_thresholds = APICountThreshold.objects.filter(devise=devise).first()
        if api_thresholds:
            val       = api_thresholds.red - len(apis)
            used      = len(apis)
            remaining = 0 if (val < 0) else api_thresholds.red - len(apis)

    context       = {
        'devise'        : devise,
        'api_usage'     : len(apis),
        'api_threshold' : APICountThreshold.objects.filter(devise=devise).first(),
        'used'          : used,
        'color'         : get_marker_color(devise),
        'remaining'     : remaining,
    }
    return render(request, template_name = template_name, context=context)

def api_overview(request, **kwargs):
    resp = user_login_access(request)
    if  resp:
        return resp
    api = DeviseApis.objects.get(pk=kwargs['pk'])
    template_name = "api_details.html"
    context = {
        'api' : api,
        'devise_name' : api.device.name,
    }
    return render(request, template_name = template_name, context=context)

class UpdateApi(UpdateView):
    model = DeviseApis
    fields = '__all__'
    template_name = 'updaet-api.html'
    
    def get_context_data(self, **kwargs):
        context = super(UpdateApi, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        messages.success(self.request, "API updated successfully")
        return context

    def get_success_url(self):
        return reverse('api-overview', kwargs={'pk': self.kwargs['pk']})

class APIThresholdForm(CreateView):
    template_name = 'api_threshold_form.html'
    model         = APICountThreshold
    fields        = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        return context
    def get_success_url(self):
        return reverse('device-details', kwargs={'pk': self.kwargs['pk']})
    
    def get_initial(self):
        devise = Devise.objects.get(pk = self.kwargs['pk'])
        return {'devise' : devise}

class APIThresholdFormUpdate(UpdateView):
    template_name = 'api_threshold_form.html'
    model         = APICountThreshold
    fields        = '__all__'   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['devise_pk']
        return context

    def get_success_url(self):
        return reverse('device-details', kwargs={'pk': self.kwargs['devise_pk']})

def change_password(request, **kwargs):
    resp = user_login_access(request)
    if  resp:
        return resp
    template_name = 'change_password.html'
    context       = dict()
    devise        = Devise.objects.filter(pk=kwargs['pk']).first()
    if request.method == 'GET':
        context = {
            'devise' : devise
        }
    elif request.method == 'POST':
        UserFuncrtions.change_password(devise.devise_id, request.POST['password'])
        messages.success(request, "password changes successfully")
        return redirect('/device-list/')
    return render(request, template_name = template_name, context=context)

def get_dashboard_chart_data(id):
    return_array = []
    if (id):
        apis = DeviseApis.objects.filter(device__pk=id).order_by('created_at').values()
        date_list = []
        for api in apis:
            date1 = api['created_at']
            date_list.append(date1.date())
        if date_list:
            date_list = [*set(date_list)]
            for i in date_list:
                return_array.append((f'{str(i.year)},{str(int(i.month) -1)},{str(i.day)}',len(apis.filter(created_at__date=i))))
    return return_array, Devise.objects.get(pk = id) if id else ''


def dashboard(request):
    resp = user_login_access(request)
    if  resp:
        return resp
    return redirect('/welcome/')

class Dashboard(TemplateView):

    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        devise_name =''
        if len(self.request.GET):
            pk = self.request.GET['pk']
            chart_date, devise_name = get_dashboard_chart_data(pk)
        context = super().get_context_data(**kwargs)
        devises = Devise.objects.all()
        context = {
            'devises' : devises,
            'chart_data' : chart_date,
            'devise_name' : devise_name
        }

        # apis = DeviseApis.objects.filter(created_at__year =. '2022').filter(created_at__month = '2022')
        # apis.filter()
        # if apis:
        #     for api in apis:      
        #         print (api.created_at.date())
                # get all the data
                # convert them to date and month
                # apply count function on it
        return context


    
    
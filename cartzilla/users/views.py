from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, CustomerProfileForm, SellerProfileForm, UserUpdateForm
from .models import Customer, Seller, Role


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            account_type = form.cleaned_data.get('account_type')
            user = form.save(commit=False)

            if account_type == 'seller':
                user.is_seller = True
                user.is_customer = False
            else:
                user.is_customer = True
                user.is_seller = False

            user.save()

            # Create role
            Role.objects.create(user=user, role=account_type)

            # Create profile based on account type
            if account_type == 'seller':
                Seller.objects.create(user=user)
            else:
                Customer.objects.create(user=user)

            messages.success(request, f'Account created! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if request.user.is_seller:
            seller = Seller.objects.get(user=request.user)
            p_form = SellerProfileForm(request.POST, instance=seller)
        else:
            customer = Customer.objects.get(user=request.user)
            p_form = CustomerProfileForm(request.POST, instance=customer)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

        if request.user.is_seller:
            seller = Seller.objects.get(user=request.user)
            p_form = SellerProfileForm(instance=seller)
        else:
            customer = Customer.objects.get(user=request.user)
            p_form = CustomerProfileForm(instance=customer)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)
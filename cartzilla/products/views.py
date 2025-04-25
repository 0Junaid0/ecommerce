from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Product, Category, Review, BargainRequest
from .forms import ProductForm, ReviewForm, CategoryForm, BargainRequestForm, CounterOfferForm
from users.models import Seller


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get('category')
    search_query = request.GET.get('search')

    if category_id:
        products = products.filter(category_id=category_id)

    if search_query:
        products = products.filter(name__icontains=search_query)

    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = Review.objects.filter(product=product)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        bargain_form = BargainRequestForm(request.POST)

        if 'review_submit' in request.POST and review_form.is_valid():
            if request.user.is_authenticated:
                review = review_form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                messages.success(request, 'Review submitted successfully!')
                return redirect('product_detail', pk=product.pk)
            else:
                messages.warning(request, 'Please login to submit a review.')

        if 'bargain_submit' in request.POST and bargain_form.is_valid():
            if request.user.is_authenticated:
                if product.allow_bargain:
                    offered_price = bargain_form.cleaned_data.get('offered_price')
                    if product.min_price and offered_price < product.min_price:
                        messages.warning(request, f'Your offer must be at least ${product.min_price}.')
                    else:
                        bargain = bargain_form.save(commit=False)
                        bargain.user = request.user
                        bargain.product = product
                        bargain.save()
                        messages.success(request, 'Bargain request sent to seller!')
                else:
                    messages.warning(request, 'This product does not allow bargaining.')
            else:
                messages.warning(request, 'Please login to make a bargain offer.')
    else:
        review_form = ReviewForm()
        bargain_form = BargainRequestForm()

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'bargain_form': bargain_form if product.allow_bargain else None
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def seller_products(request):
    if not request.user.is_seller:
        messages.warning(request, 'You do not have seller privileges.')
        return redirect('home')

    seller = get_object_or_404(Seller, user=request.user)
    products = Product.objects.filter(seller=seller)

    context = {
        'products': products
    }
    return render(request, 'products/seller_products.html', context)


@login_required
def add_product(request):
    if not request.user.is_seller:
        messages.warning(request, 'You do not have seller privileges.')
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            seller = get_object_or_404(Seller, user=request.user)
            product.seller = seller
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('seller_products')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})


@login_required
def edit_product(request, pk):
    if not request.user.is_seller:
        messages.warning(request, 'You do not have seller privileges.')
        return redirect('home')

    product = get_object_or_404(Product, pk=pk)

    # Verify that the current user is the owner of this product
    if product.seller.user != request.user:
        messages.warning(request, 'You can only edit your own products.')
        return redirect('seller_products')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('seller_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, pk):
    if not request.user.is_seller:
        messages.warning(request, 'You do not have seller privileges.')
        return redirect('home')

    product = get_object_or_404(Product, pk=pk)

    # Verify that the current user is the owner of this product
    if product.seller.user != request.user:
        messages.warning(request, 'You can only delete your own products.')
        return redirect('seller_products')

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('seller_products')

    return render(request, 'products/delete_product.html', {'product': product})


@login_required
def bargain_requests(request):
    if not request.user.is_seller:
        messages.warning(request, 'You do not have seller privileges.')
        return redirect('home')

    seller = get_object_or_404(Seller, user=request.user)
    bargain_requests = BargainRequest.objects.filter(product__seller=seller)

    context = {
        'bargain_requests': bargain_requests
    }
    return render(request, 'products/bargain_requests.html', context)


@login_required
def handle_bargain(request, pk):
    if not request.user.is_seller:
        messages.warning(request, 'You do not have seller privileges.')
        return redirect('home')

    bargain = get_object_or_404(BargainRequest, pk=pk)

    # Verify that the current user is the seller of the product
    if bargain.product.seller.user != request.user:
        messages.warning(request, 'You can only handle bargains for your own products.')
        return redirect('bargain_requests')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept':
            bargain.status = 'accepted'
            bargain.save()
            messages.success(request, 'Bargain offer accepted!')

        elif action == 'reject':
            bargain.status = 'rejected'
            bargain.save()
            messages.success(request, 'Bargain offer rejected.')

        elif action == 'counter':
            form = CounterOfferForm(request.POST, instance=bargain)
            if form.is_valid():
                bargain = form.save(commit=False)
                bargain.status = 'counter'
                bargain.save()
                messages.success(request, 'Counter offer sent!')
            else:
                messages.warning(request, 'Invalid counter offer.')

    return redirect('bargain_requests')


@login_required
def user_bargains(request):
    bargains = BargainRequest.objects.filter(user=request.user)

    context = {
        'bargains': bargains
    }
    return render(request, 'products/user_bargains.html', context)


@login_required
def handle_counter_offer(request, pk):
    bargain = get_object_or_404(BargainRequest, pk=pk)

    # Verify that the current user is the one who initiated the bargain
    if bargain.user != request.user:
        messages.warning(request, 'You can only respond to your own bargain requests.')
        return redirect('user_bargains')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept':
            bargain.status = 'accepted'
            bargain.save()
            messages.success(request, 'You accepted the counter offer!')

        elif action == 'reject':
            bargain.status = 'rejected'
            bargain.save()
            messages.success(request, 'You rejected the counter offer.')

    return redirect('user_bargains')
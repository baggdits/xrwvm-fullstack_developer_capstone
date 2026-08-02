# Uncomment the required imports before adding the code
# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

import json
import logging

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .restapis import (
    analyze_review_sentiments,
    get_request,
    post_review,
)

# from .populate import initiate


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def get_cars(request):
    count = CarMake.objects.count()
    print(count)

    car_models = CarModel.objects.select_related("car_make")

    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })

    return JsonResponse({"CarModels": cars})


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]

    # Try to check if provided credentials can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}

    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {
            "userName": username,
            "status": "Authenticated"
        }

    return JsonResponse(data)


# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...


# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...


# Update get_dealerships to render all dealerships by default,
# or a particular state if state is passed.
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state

    dealerships = get_request(endpoint)

    return JsonResponse({
        "status": 200,
        "dealers": dealerships
    })


# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)

        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail["review"])
            print(response)

            if response and "sentiment" in response:
                review_detail["sentiment"] = response["sentiment"]
            else:
                review_detail["sentiment"] = "neutral"

        return JsonResponse({
            "status": 200,
            "reviews": reviews
        })

    return JsonResponse({
        "status": 400,
        "message": "Bad Request"
    })


# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)

        return JsonResponse({
            "status": 200,
            "dealer": dealership
        })

    return JsonResponse({
        "status": 400,
        "message": "Bad Request"
    })


# Create an `add_review` view to submit a review
def add_review(request):
    if not request.user.is_anonymous:
        data = json.loads(request.body)

        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception:
            return JsonResponse({
                "status": 401,
                "message": "Error in posting review"
            })

    return JsonResponse({
        "status": 403,
        "message": "Unauthorized"
    })


# def add_review(request):
# ...

import rest_framework as rf
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.viewsets import GenericViewSet

from api import models, serializers

from .forms import InvestmentCheckForm

# Create your views here.


class InstrumentViewSet(
    rf.mixins.CreateModelMixin,
    rf.mixins.RetrieveModelMixin,
    rf.mixins.ListModelMixin,
    rf.mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = models.Instrument.objects.all()
    serializer_class = serializers.InstrumentSerializer
    permission_classes = [rf.permissions.IsAdminUser]


@staff_member_required
def investment_check(request):
    if request.method == "POST":
        form = InvestmentCheckForm(request.POST)
        if form.is_valid():
            # TODO: pull logic out so this doesn't do anything right now
            invest_check = form.save()
            invest_check.save()

            change_page_url = reverse(
                "admin:api_investmentcheck_change", args=(invest_check.id,)
            )

            # Redirect to the change page URL
            return redirect(change_page_url)

    form = InvestmentCheckForm()
    return render(request, "check.html", {"form": form})

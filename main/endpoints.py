from rest_framework import serializers,viewsets
from . import models

class OrderLineSerializer(serializers.HyperlinkedModelSerializer):
    book = serializers.StringRelatedField()
    class Meta:
        model = models.OrderLine
        fields = ('id', 'order', 'book', 'status')
        read_only_fields = ('id', 'order', 'product')

class PaidOrderLineViewSet(viewsets.ModelViewSet):
    queryset = models.OrderLine.objects.filter(order__status=models.Order.PAID).order_by("-order__date_added")
    serializer_class = OrderLineSerializer
    filter_fields = ('order', 'status')

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Order
        fields = ('shipping_name','shipping_address','shipping_town',
                  'shipping_county','date_updated','date_added')
class PaidOrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.filter(status=models.Order.PAID).order_by("-date_added")
    serializer_class = OrderSerializer
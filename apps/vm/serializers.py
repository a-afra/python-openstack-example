from rest_framework import serializers
from apps.vm.models import Server


class ServerCreateSerializer(serializers.ModelSerializer):
    disk = serializers.IntegerField()

    class Meta:
        model = Server
        fields = [
            "name",
            "flavor",
            "image",
            "network",
            "disk",
        ]


class ServerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Server
        fields = "__all__"



from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from apps.vm.models import Server
from django.core.exceptions import ObjectDoesNotExist
from utils.openstack_utils import list_flavors, list_images, list_networks, create_server, get_ids
from apps.vm.serializers import ServerListSerializer, ServerCreateSerializer
from requests.exceptions import ConnectionError
from core.settings import env


class FlavorListView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        try:
            flavors = list_flavors()
        except Exception as e:
            return Response(
                {"message": "bad request.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(flavors, status=status.HTTP_200_OK)


class ImageListView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        try:
            images = list_images()
        except Exception as e:
            return Response(
                {"message": "bad request.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(images, status=status.HTTP_200_OK)


class NetworkListView(generics.ListAPIView):
    """
    A view that retrieves a list of networks.
    """

    def list(self, request, *args, **kwargs):
        try:
            networks = list_networks()
        except Exception as e:
            return Response(
                {"message": "bad request.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(networks, status=status.HTTP_200_OK)


class ServerListCreateView(generics.ListCreateAPIView):
    def list(self, request, *args, **kwargs):
        user_servers = Server.objects.all()
        serializer = ServerListSerializer(user_servers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = ServerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        server_name = validated_data["name"]
        flavor_name = validated_data["flavor"]
        image_name = validated_data["image"]
        network_name = validated_data["network"]

        try:
            vm_config = get_ids(
                image_name=image_name,
                flavor_name=flavor_name,
                network_name=network_name
            )
        except Exception as e:
            return Response(
                {
                    "message": "Bad request.",
                    "detail": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        server_instance = Server.objects.create(
            name=server_name,
            image=image_name,
            flavor=flavor_name,
            state="PENDING",
        )
        try:
            create_server.delay(
                server_name=server_name,
                config=vm_config,
                size=validated_data["disk"],
                server_instance_id=server_instance.id,
            )
        except Exception as e:
            server_instance.state = "FAILED"
            server_instance.save()
            return Response(
                {
                    "message": "Server creation failed.",
                    "detail": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        return Response({"detail": "Server created."}, status=status.HTTP_201_CREATED)
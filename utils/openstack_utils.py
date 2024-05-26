import openstack
from core.settings import env
from celery import shared_task
from apps.vm.models import Server
import time

#openstack.enable_logging(debug=True)

def create_connection():
    return openstack.connect(
        auth_url=env("AUTH_URL"),
        username=env("USER_NAME"),
        password=env("PASSWORD"),
        project_id= env("PROJECT_ID"),
        project_name=env("PROJECT_NAME"),
        user_domain_name="Default",
        region_name=env("REGION_NAME"),
        identity_api_version=3,
        load_yaml_config=False,
    )

conn = create_connection()


def list_images(conn=conn):
    return conn.compute.images()

def list_flavors(conn=conn):
    return conn.compute.flavors()

def list_networks(conn=conn):
    return conn.network.networks()

def get_ids(image_name, flavor_name, network_name):
    image = conn.image.find_image(image_name)
    if image == None:
        raise Exception("Image not found.")
    flavor = conn.compute.find_flavor(flavor_name)
    if flavor == None:
        raise Exception("Flavor not found.")
    network = conn.network.find_network(network_name)
    if network == None:
        raise Exception("Network not found.")

    return {"image": image.id, "flavor": flavor.id, "network": network.id}

def create_volume(volume_size, image_id):
    volume = conn.block_storage.create_volume(
        image_id=image_id,
        volume_type="economy_class",
        size=volume_size,
        is_bootable=True
    )
    return volume.id

def update_server_state(server_instance_id):
    server_instance = Server.objects.get(id=server_instance_id)
    status = ""
    while status == "ACTIVE":
        time.sleep(5)
        server = conn.compute.get_server(server_instance.uid)
        status = server.status

@shared_task
def create_server(server_name, config, size, server_instance_id):
    try:
        server_instance = Server.objects.get(id=server_instance_id)
        server = conn.compute.create_server(
            name=server_name,
            flavor_id=config["flavor"],
            networks=[{"uuid": config["network"]}],
            create_volume_default= True,
            hide_create_volume= False,
            block_device_mapping_v2= [
                {
                "source_type": "image",
                "destination_type": "volume",
                "delete_on_termination": False,
                "uuid": config["image"],
                "boot_index": "0",
                "volume_size": size
                }
            ],
            # block_device_mapping_v2= [
            #     {
            #     "source_type": "volume",
            #     "destination_type": "volume",
            #     "delete_on_termination": False,
            #     "uuid": create_volume(size, config["image"]),
            #     "boot_index": "0"
            #     }
            # ],
        )
    except Exception as e:
        server_instance.state = "FAILED"
        server_instance.save()
        print(str(e))

    server = conn.compute.wait_for_server(server)
    server_instance.ip_address = server.access_ipv4
    server_instance.uid = server.id
    server_instance.state = server.status
    server_instance.save()


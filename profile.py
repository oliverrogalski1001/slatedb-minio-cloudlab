"""Two-node CloudLab profile for benchmarking SlateDB with MinIO as the object store.

Sets up a MinIO server node and a SlateDB client node connected via a dedicated link.
The SlateDB node automatically configures credentials and creates a bucket on the MinIO node.
"""

import geni.portal as portal
import geni.rspec.pg as rspec

MINIO_IP = "10.10.1.1"
SLATEDB_IP = "10.10.1.2"
NETMASK = "255.255.255.0"

pc = portal.Context()

pc.defineParameter(
    "raw_node_type_slatedb_client",
    "Hardware Type",
    portal.ParameterType.NODETYPE,
    "",
)
pc.defineParameter(
    "slatedb_repo",
    "SlateDB Repository URL",
    portal.ParameterType.STRING,
    "https://github.com/slatedb/slatedb.git",
)
pc.defineParameter(
    "raw_node_type_minio_server",
    "Hardware Type",
    portal.ParameterType.NODETYPE,
    "",
)
pc.defineParameter(
    "minio_license", "Minio License Key", portal.ParameterType.STRING, ""
)
pc.defineParameter(
    "minio_root_user", "Root Username", portal.ParameterType.STRING, "minioadmin"
)
pc.defineParameter(
    "minio_root_password", "Root Password", portal.ParameterType.STRING, "minioadmin"
)
pc.defineParameter(
    "minio_bucket", "MinIO Bucket Name", portal.ParameterType.STRING, "slatedb"
)

params = pc.bindParameters()
request = pc.makeRequestRSpec()

node_minio = request.RawPC("minio-node")
node_minio.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU24-64-STD"
node_slatedb = request.RawPC("slatedb-node")
node_slatedb.disk_image = (
    "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU24-64-STD"
)

if params.raw_node_type_minio_server != "":
    node_minio.hardware_type = params.raw_node_type_minio_server
if params.raw_node_type_slatedb_client != "":
    node_slatedb.hardware_type = params.raw_node_type_slatedb_client

# Create a link between the two nodes
iface_minio = node_minio.addInterface("if1")
iface_minio.addAddress(rspec.IPv4Address(MINIO_IP, NETMASK))

iface_slatedb = node_slatedb.addInterface("if1")
iface_slatedb.addAddress(rspec.IPv4Address(SLATEDB_IP, NETMASK))

link = request.Link("link-0")
link.addInterface(iface_minio)
link.addInterface(iface_slatedb)

node_minio.addService(
    rspec.Execute(
        shell="sh",
        command="/local/repository/setup-minio.sh '{}' '{}' '{}'".format(
            params.minio_license, params.minio_root_user, params.minio_root_password
        ),
    )
)

node_slatedb.addService(
    rspec.Execute(
        shell="sh",
        command="/local/repository/setup-slatedb.sh '{}' '{}' '{}' '{}' '{}'".format(
            params.slatedb_repo,
            params.minio_root_user,
            params.minio_root_password,
            MINIO_IP,
            params.minio_bucket,
        ),
    )
)

pc.printRequestRSpec()

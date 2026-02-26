import geni.portal as portal
import geni.rspec.pg as rspec

pc = portal.Context()

pc.defineParameter(
    "raw_node_type",
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

params = pc.bindParameters()
request = pc.makeRequestRSpec()

node = request.RawPC("minio-node")
node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU24-64-STD"

if params.raw_node_type != "":
    node.hardware_type = params.raw_node_type

node.addService(
    rspec.Execute(
        shell="bash",
        command="/local/repository/setup-minio.sh '{}' '{}' '{}'".format(
            params.minio_license, params.minio_root_user, params.minio_root_password
        ),
    )
)

pc.printRequestRSpec()

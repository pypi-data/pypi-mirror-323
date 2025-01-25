from enum import Enum
from uuid import UUID
from pydantic import BaseModel

class Environment(str, Enum):
    lab = "lab"
    prod = "prod"

class Type(str, Enum):
    baremetal = "baremetal"

class Version(str, Enum):
    v4_14_16 = "4.14.14"
    v4_16_07 = "4.16.07"

class Profile(str, Enum):
    standard = "standard"

class VlanType(str, Enum):
    baremetal = "bm"

class ClusterCreateResponseSuccess(BaseModel):
    id: UUID
    name: str
    environment: Environment
    type: Type
    version: Version
    project: str
    pod: str
    servers: list[str]
    access: str

class ClusterCreateResponseFailure(BaseModel):
    id: UUID

class L2VNLogical(BaseModel):
    virtual_network_name: str
    servers: list[str]
    uplink_connection_type: str
    downlink_connection_type: str
    vlan_type: VlanType = VlanType.baremetal

class L2VNCreateRequest(BaseModel):
    id: UUID
    pod: str
    tenant_name: str
    profile: Profile = Profile.standard
    logical: list[L2VNLogical]

class L2VNCreateResponseSuccess(BaseModel):
    id: UUID
    vlan_id: int

class L2VNCreateResponseFailure(BaseModel):
    id: UUID

class Community(str, Enum):
    standard = "NFV-OCP-CO-LAN"

class L3VNCreateRequest(BaseModel):
    id: UUID
    pod_name: str
    vlan_id: int
    cidr_v4: str
    community: Community = Community.standard
    virtual_network_name: str
    imports: list[str]
    exports: list[str]

class L3VNCreateResponseSuccess(BaseModel):
    id: UUID
    cidr_v4: str

class L3VNCreateResponseFailure(BaseModel):
    id: UUID

class E2ECreateRequest(BaseModel):
    id: UUID
    name: str
    environment: Environment
    type: Type
    version: Version
    project: str
    pod: str
    servers: list[str]
    machine_network_cidr: str
    machine_network_vlan: int

class E2ECreateResponseSuccess(BaseModel):
    id: UUID
    name: str
    access: str

class E2ECreateResponseFailure(BaseModel):
    id: UUID
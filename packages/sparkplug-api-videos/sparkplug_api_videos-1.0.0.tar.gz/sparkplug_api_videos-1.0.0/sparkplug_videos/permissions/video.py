# sparkplug
from sparkplug_core.permissions import (
    ActionPermission,
    IsCreator,
    IsAuthenticated,
)


class Video(
    ActionPermission,
):
    # user permissions
    create_perms = IsAuthenticated

    # object permissions
    read_perms = IsAuthenticated
    write_perms = IsCreator

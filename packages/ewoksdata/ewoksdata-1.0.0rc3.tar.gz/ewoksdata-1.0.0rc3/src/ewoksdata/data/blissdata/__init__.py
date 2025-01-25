from importlib.metadata import version
from packaging.specifiers import SpecifierSet


def _not_supported_by_blissdata_version(*_, **kw):
    raise RuntimeError(f"Not supported by blissdata {_BLISSDATA_VERSION}")


from blissdata.h5api import dynamic_hdf5  # noqa F401

_BLISSDATA_VERSION = version("blissdata")

if _BLISSDATA_VERSION in SpecifierSet("<1", prereleases=True):
    from .blissdatav0 import iter_bliss_scan_data_from_memory  # noqa F401
    from .blissdatav0 import last_lima_image  # noqa F401

    iter_bliss_scan_data_from_memory_slice = _not_supported_by_blissdata_version
elif _BLISSDATA_VERSION in SpecifierSet("<2", prereleases=True):
    from .blissdatav1 import iter_bliss_scan_data_from_memory  # noqa F401
    from .blissdatav1 import iter_bliss_scan_data_from_memory_slice  # noqa F401
    from .blissdatav1 import last_lima_image  # noqa F401
else:
    from .blissdatav2 import iter_bliss_scan_data_from_memory  # noqa F401
    from .blissdatav2 import iter_bliss_scan_data_from_memory_slice  # noqa F401
    from .blissdatav2 import last_lima_image  # noqa F401

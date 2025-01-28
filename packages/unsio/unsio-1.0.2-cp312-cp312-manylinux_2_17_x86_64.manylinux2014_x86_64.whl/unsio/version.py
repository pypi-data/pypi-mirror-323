import importlib.metadata

package="unsio"
try:
    version = importlib.metadata.version(package)
except:
    print(f"Unable to detect version for [{package}]")
    version ="undef"

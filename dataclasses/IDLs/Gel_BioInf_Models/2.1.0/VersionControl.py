from dataclasses import dataclass

@dataclass
class VersionControl:
    """This is the version for the entire set of data models as referred to the Git release tag"""
    GitVersionControl: str = "2.1.0"


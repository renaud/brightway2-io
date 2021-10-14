__all__ = [
    "activity_hash",
    "add_ecoinvent_33_biosphere_flows",
    "add_ecoinvent_34_biosphere_flows",
    "add_ecoinvent_35_biosphere_flows",
    "add_ecoinvent_36_biosphere_flows",
    "add_ecoinvent_37_biosphere_flows",
    "add_ecoinvent_38_biosphere_flows",
    "add_example_database",
    "backup_data_directory",
    "backup_project_directory",
    "BW2Package",
    "bw2setup",
    "create_core_migrations",
    "create_default_biosphere3",
    "create_default_lcia_methods",
    "CSVImporter",
    "CSVLCIAImporter",
    "DatabaseSelectionToGEXF",
    "DatabaseToGEXF",
    "Ecospold1LCIAImporter",
    "es2_activity_hash",
    "ExcelImporter",
    "ExcelLCIAImporter",
    "get_csv_example_filepath",
    "get_xlsx_example_filepath",
    "lci_matrices_to_excel",
    "lci_matrices_to_matlab",
    "load_json_data_file",
    "Migration",
    "migrations",
    "MultiOutputEcospold1Importer",
    "normalize_units",
    "restore_project_directory",
    "SimaProCSVImporter",
    "SimaProLCIACSVImporter",
    "SingleOutputEcospold1Importer",
    "SingleOutputEcospold2Importer",
    "useeio11",
    "unlinked_data",
    "UnlinkedData",
]

from .version import version as __version__

from .package import BW2Package
from .export import (
    DatabaseToGEXF,
    DatabaseSelectionToGEXF,
    keyword_to_gephi_graph,
    lci_matrices_to_excel,
    lci_matrices_to_matlab,
)
from .backup import (
    backup_data_directory,
    backup_project_directory,
    restore_project_directory,
)
from .data import (
    add_ecoinvent_33_biosphere_flows,
    add_ecoinvent_34_biosphere_flows,
    add_ecoinvent_35_biosphere_flows,
    add_ecoinvent_36_biosphere_flows,
    add_ecoinvent_37_biosphere_flows,
    add_ecoinvent_38_biosphere_flows,
    add_example_database,
    get_csv_example_filepath,
    get_xlsx_example_filepath,
)
from .migrations import migrations, Migration, create_core_migrations
from .importers import (
    CSVImporter,
    CSVLCIAImporter,
    Ecospold1LCIAImporter,
    ExcelImporter,
    ExcelLCIAImporter,
    MultiOutputEcospold1Importer,
    SimaProCSVImporter,
    SimaProLCIACSVImporter,
    SingleOutputEcospold1Importer,
    SingleOutputEcospold2Importer,
    Exiobase3MonetaryImporter,
    Exiobase3HybridImporter,
)
from .units import normalize_units
from .unlinked_data import unlinked_data, UnlinkedData
from .utils import activity_hash, es2_activity_hash, load_json_data_file

from bw2data import config, databases

config.metadata.extend(
    [migrations, unlinked_data,]
)


def create_default_biosphere3(overwrite=False):
    from .importers import Ecospold2BiosphereImporter

    eb = Ecospold2BiosphereImporter()
    eb.apply_strategies()
    eb.write_database(overwrite=overwrite)


def create_default_lcia_methods(overwrite=False, rationalize_method_names=False):
    from .importers import EcoinventLCIAImporter

    ei = EcoinventLCIAImporter()
    if rationalize_method_names:
        ei.add_rationalize_method_names_strategy()
    ei.apply_strategies()
    ei.write_methods(overwrite=overwrite)


def bw2setup():
    if "biosphere3" in databases:
        print("Biosphere database already present!!! No setup is needed")
        return
    print("Creating default biosphere\n")
    create_default_biosphere3()
    print("Creating default LCIA methods\n")
    create_default_lcia_methods()
    print("Creating core data migrations\n")
    create_core_migrations()


def useeio11(name='US EEIO 1.1'):
    URL = "https://www.lcacommons.gov/lca-collaboration/ws/public/download/json/repository_US_Environmental_Protection_Agency@USEEIO"

    if "US EEIO 1.1" in databases:
        print("US EEIO 1.1 already present")
        return

    from .importers.json_ld import JSONLDImporter
    from .importers.json_ld_lcia import JSONLDLCIAImporter
    from pathlib import Path
    import tempfile
    import urllib
    import zipfile

    with tempfile.TemporaryDirectory() as td:
        dp = Path(td)
        print("Downloading US EEIO 1.1")
        urllib.request.urlretrieve(URL, dp / "USEEIO11.zip")

        print("Unzipping file")
        with zipfile.ZipFile(dp / "USEEIO11.zip", 'r') as zip_ref:
            zip_ref.extractall(dp)

        (dp / "USEEIO11.zip").unlink()

        print("Importing data")
        j = JSONLDImporter(dp, name)
        j.apply_strategies(no_warning=True)
        j.merge_biosphere_flows()
        assert j.all_linked
        j.write_database()

        l = JSONLDLCIAImporter(dp)
        l.apply_strategies()
        l.match_biosphere_by_id(name)
        assert l.all_linked
        l.write_methods()

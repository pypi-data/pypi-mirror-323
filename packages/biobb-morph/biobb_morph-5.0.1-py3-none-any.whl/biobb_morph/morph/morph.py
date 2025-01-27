#!/usr/bin/env python3

# Module from BioBB basics
import argparse
from pathlib import Path
from typing import Optional

from biobb_common.configuration import settings
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger

# Modules for BioBB Morph
from biobb_morph.morph import common


class Morph(BiobbObject):
    """
    | biobb_morph Morph
    | The Morph class is designed for the production of 3DSpine meshes, from a template IVD mesh to a target, patient-personalized model.
    | The Morph class is designed for the production of 3DSpine meshes, from a template IVD mesh to a target, patient-personalized model. It supports various non-rigid registration modes and morphing operations to achieve optimal mesh alignment and transformation.

    Args:
        input_AF_stl_path (str): Path to the AF stl input file path. File type: input. `Sample file <https://github.com/bioexcel/biobb_morph/blob/baac08889094d194f898c619ae661510f8cbd498/biobb_morph/test/data/morph/IVD_L2L3_AF_NC0031.stl>`_. Accepted formats: stl (edam:format_3993).
        input_NP_stl_path (str): Path to the NP stl input file path. File type: input. `Sample file <https://github.com/bioexcel/biobb_morph/blob/baac08889094d194f898c619ae661510f8cbd498/biobb_morph/test/data/morph/IVD_L2L3_NP_NC0031.stl>`_. Accepted formats: stl (edam:format_3993).
        input_lambdaBeta_csv_path (str) (Optional): Path to the csv lambdaBeta input file path. File type: input. `Sample file <https://raw.githubusercontent.com/bioexcel/biobb_morph/refs/heads/master/biobb_morph/sources/lambdaBeta.csv>`_. Accepted formats: csv (edam:format_3752).
        output_morphed_zip_path (str): Path to the output morphed zip file path. File type: output. `Sample file <https://urlto.sample>`_. Accepted formats: zip (edam:format_3752).
        properties (dict - Python dictionary object containing the tool parameters, not input/output files):
            * **morph** (*int*) - (5) Non-Rigid registration mode. Options: 1: AF, 2: NP, 3: NoBEP, 4: CEPmorph, 5: All, 0: NONE.
            * **toINP** (*int*) - (4) Create the .inp file for specific components. Options: 1: AF, 2: NP, 3: NoBEP, 4: All, 0: NONE.
            * **abaqusCommand** (*str*) - ("gmsh") Command used to call ABAQUS. If '-a gmsh', the Gmsh tool is used.
            * **bcpdCommand** (*str*) - ("bcpd") Command used to call BCPD++.
            * **checkFElem** (*int*) - (2) Check failed elements of the resulting .inp file (Abaqus required). Options: 1: YES, 2: Iterate value of lambda, 0: NO.
            * **rigid** (*int*) - (1) Perform rigid registration at the beginning of the process. Options: 1: YES, 0: NO.
            * **WCEP** (*int*) - (0) Perform morphing with CEP. Options: 1: YES, 0: NO.
            * **interpo** (*int*) - (1) Use interpolated files. Options: 1: YES, 0: NO.
            * **fusion** (*int*) - (1) Fuse the AF and NP for the final morph. Options: 1: YES, 0: NO.
            * **surfRegCEP** (*int*) - (1) Morph external surfaces of AF and NP (including CEP). Options: 1: YES, 0: NO.
            * **checkHaus** (*int*) - (1) Check Hausdorff distance between 3D grids (Euclidean distance). Options: 1: YES, 0: NO.
            * **CEP** (*int*) - (0) Perform non-rigid registration of the CEP. Options: 1: YES, 0: NO.
            * **TZ** (*int*) - (1) Create a Transition Zone. Options: 1: YES, 0: NO.
            * **movement** (*list*) - ([0, 0, 0.05]) Enter a list of floats separated by spaces to represent desired movement. Positive: positive direction, Negative: negative direction, 0: no movement.
            * **nodeDistance** (*float*) - (0.3) Distance between two nodes of the mesh.
            * **moveTo** (*list*) - ([0.0, 24.1397991, 2.94929004]) Translation of the AF and NP.
            * **plane** (*list*) - ([1, 1, 0]) Plane to orthogonally project the nodes of the NP to create the spline line of the perimeter.
            * **reduce_param** (*float*) - (0.8) Parameter to reduce the size of the contour of the NP.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_morph.morph.morph import morph

            prop = {
                'morph: 5
            }
            morph(input_AF_stl_path='/path/to/AF.stl',
                  input_NP_stl_path='/path/to/NP.stl',
                  output_morphd_zip_path='/path/to/morphed.zip',
                  properties=prop)

    Info:
        * wrapped_software:
            * name: Morph
            * version: >=1.0.0
            * license: BSD 3-Clause
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl
    """

    def __init__(
        self,
        input_AF_stl_path: str,
        input_NP_stl_path: str,
        output_morphed_zip_path: str,
        input_lambdaBeta_csv_path: Optional[str] = None,
        properties: Optional[dict] = None,
        **kwargs,
    ) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        self.sources_path = str(Path(__file__).resolve().parents[1].joinpath("sources"))
        input_lambdaBeta_csv_path = input_lambdaBeta_csv_path or str(
            Path(self.sources_path).joinpath("lambdaBeta.csv")
        )

        # Input/Output files
        self.io_dict = {
            "in": {
                "input_AF_stl_path": input_AF_stl_path,
                "input_NP_stl_path": input_NP_stl_path,
                "input_lambdaBeta_csv_path": input_lambdaBeta_csv_path,
            },
            "out": {
                "output_morphed_zip_path": output_morphed_zip_path,
            },
        }

        # Properties
        # WARNING: Not a property but a file it should be in the input
        # self.files = self.io_dict["in"]["input_file_path1"]
        self.morph = properties.get("morph", 5)
        self.toINP = properties.get("toINP", 4)
        self.abaqusCommand = properties.get("abaqusCommand", "gmsh")
        self.bcpdCommand = properties.get("bcpdCommand", "bcpd")
        self.checkFElem = properties.get("checkFElem", 2)
        self.rigid = properties.get("rigid", 1)
        self.WCEP = properties.get("WCEP", 0)
        self.interpo = properties.get("interpo", 1)
        self.fusion = properties.get("fusion", 1)
        self.surfRegCEP = properties.get("surfRegCEP", 1)
        self.checkHaus = properties.get("checkHaus", 1)
        self.CEP = properties.get("CEP", 0)
        # WARNING: Not a property but a file it should be in the input
        # self.lambdaBeta = properties.get("lambdaBeta", "lambdaBeta.csv")
        self.TZ = properties.get("TZ", 1)
        self.movement = properties.get("movement", [0, 0, 0.05])
        self.nodeDistance = properties.get("nodeDistance", 0.3)
        self.moveTo = properties.get("moveTo", [0.0, 24.1397991, 2.94929004])
        self.plane = properties.get("plane", [1, 1, 0])
        self.reduce_param = properties.get("reduce_param", 0.8)

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Morph <biobb_morph.biobb_morph.Morph>` object."""

        if self.check_restart():
            return 0

        self.stage_files()

        fu.log(
            f"input_AF_stl_path: {self.stage_io_dict['in']['input_AF_stl_path']}",
            self.out_log,
        )
        fu.log(
            f"input_NP_stl_path: {self.stage_io_dict['in']['input_NP_stl_path']}",
            self.out_log,
        )
        # Create input_stl_path
        input_stl_path = Path(
            self.stage_io_dict["in"]["input_AF_stl_path"]
        ).parent.joinpath("input.stl")
        with open(input_stl_path, "w") as f:
            f.write(f"{Path(self.stage_io_dict['in']['input_AF_stl_path']).name}\n")
            f.write(f"{Path(self.stage_io_dict['in']['input_NP_stl_path']).name}")
        fu.log(
            f"input.stl: {input_stl_path}",
            self.out_log,
        )
        # Create results directory
        results_path = Path(
            self.stage_io_dict["out"]["output_morphed_zip_path"]
        ).parent.joinpath("results")
        fu.log(
            f"results_path: {results_path}",
            self.out_log,
        )

        # Adding specific morphing properties
        morph_args = [
            str(input_stl_path),
            str(self.sources_path),
            str(results_path),
            self.morph,
            self.WCEP,
            self.toINP,
            self.interpo,
            self.fusion,
            self.rigid,
            self.surfRegCEP,
            self.checkFElem,
            self.checkHaus,
            self.CEP,
            self.nodeDistance,
            self.moveTo,
            self.movement,
            self.plane,
            self.reduce_param,
            self.TZ,
            self.stage_io_dict["in"]["input_lambdaBeta_csv_path"],
            self.bcpdCommand,
            self.abaqusCommand,
        ]

        # Executing the command line as a list of items (elements order will be maintained)
        fu.log("Executing the morph function with specified arguments", self.out_log)
        common.morph(*morph_args)

        # Create results zip file
        fu.log(
            f"results zip file: {self.stage_io_dict['out']['output_morphed_zip_path']}",
            self.out_log,
        )
        fu.zip_list(
            self.stage_io_dict["out"]["output_morphed_zip_path"], [results_path]
        )

        # Copy files to host
        self.copy_to_host()

        # Remove temporal files
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)
        return 0


def morph(
    input_AF_stl_path: str,
    input_NP_stl_path: str,
    output_morphed_zip_path: str,
    input_lambdaBeta_csv_path: Optional[str] = None,
    properties: Optional[dict] = None,
    **kwargs,
) -> int:
    """Create :class:`Morph <biobb_morph.biobb_morph.Morph>` class and
    execute the :meth:`launch() <biobb_morph.biobb_morph.Morph.launch>` method."""

    return Morph(
        input_AF_stl_path=input_AF_stl_path,
        input_NP_stl_path=input_NP_stl_path,
        output_morphed_zip_path=output_morphed_zip_path,
        input_lambdaBeta_csv_path=input_lambdaBeta_csv_path,
        properties=properties,
        **kwargs,
    ).launch()


def main():
    parser = argparse.ArgumentParser(
        description="Wrapper of the  Morph module.",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
    )
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        help="This file can be a YAML file, JSON file or JSON string",
    )

    # Specific args
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument(
        "--input_AF_stl_path",
        required=True,
        help="Input AF stl file path",
    )
    required_args.add_argument(
        "--input_NP_stl_path",
        required=True,
        help="Input NP stl file path",
    )
    required_args.add_argument(
        "--output_morphed_zip_path",
        required=True,
        help="Output morphed zip file path",
    )
    parser.add_argument(
        "--input_lambdaBeta_csv_path",
        required=False,
        help="Input lambdaBeta csv file path",
    )

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    morph(
        input_AF_stl_path=args.input_AF_stl_path,
        input_NP_stl_path=args.input_NP_stl_path,
        output_morphed_zip_path=args.output_morphed_zip_path,
        input_lambdaBeta_csv_path=args.input_lambdaBeta_csv_path,
        properties=properties,
    )


if __name__ == "__main__":
    main()

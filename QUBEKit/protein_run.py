#!/usr/bin/env python

from QUBEKit.ligand import Protein
from QUBEKit.parametrisation import XMLProtein
from QUBEKit.lennard_jones import LennardJones
from QUBEKit.proteinTools import qube_general, pdb_reformat, get_water
from os import remove
import argparse


def main():
    """This script is used to prepare proteins with the QUBE FF
    1) prepare the protein for onetep using --setup which prints an xyz of the system
    2) after the onetep calculation bring back the ddec.onetep file and parametrise the system with --build
     this must be the same pdb used in setup as the atom order must be retained."""

    # Setup the action classes
    class SetupAction(argparse.Action):
        """This class is called when we setup a new protein."""

        def __call__(self, pars, namespace, values, option_string=None):
            """This function is executed when setup is called."""

            print('starting protein prep, reading pdb file...')
            pro = Protein(values)
            print(f'{len(protein.Residues)} residues found!')
            # TODO find the magic numbers for the box for onetep
            pro.write_xyz(name='protein')
            print(f'protein.xyz file made for ONETEP\n Run this file')
            exit()

    class BuildAction(argparse.Action):
        """This class handles the building of the protein xml and pdb files."""

        def __call__(self, pars, namespace, values, option_string=None):
            """This function is executed when build is called."""

            pro = Protein(values)
            # print the qube general FF to use in the parameterization
            qube_general()
            # now we want to add the connections and parametrise the protein
            XMLProtein(pro)
            # this updates the bonded info that is now in the object

            # finally we need the non-bonded parameters from onetep
            # fake configs as this will always be true
            # TODO should we also have the ability to get DDEC6 charges from the cube file?
            configs = [{'charge': 0}, {'charges_engine': 'onetep', 'density_engine': 'onetep' }, {}, {}]
            lj = LennardJones(pro, config_dict=configs)
            pro.NonbondedForce = lj.calculate_non_bonded_force()

            # now we write out the final parameters
            # we should also calculate the charges and lj at this point!
            print('Writing pdb file with conections...')
            pro.write_pdb(name='QUBE_pro')
            print('Writing XML file for the system...')
            pro.write_parameters(name='QUBE_pro', protein=True)
            # now remove the qube general file
            remove('QUBE_general_pi.xml')
            print('Done')
            exit()

    class WaterAction(argparse.Action):
        """This class builds the water models requested"""

        def __call__(self, pars, namespace, values, option_string=None):
            """This function is executed when water is called."""
            get_water(values)
            exit()

    class ConvertAction(argparse.Action):
        """This class converts the names in a qube taj file to match the reference."""

        def __call__(self, pars, namespace, values, option_string=None):
            """This function is executed when water is called."""
            refernece, target = values[0], values[1]
            print(refernece, target)
            print(f'Rewriting input:{target} to match:{refernece}...')
            pdb_reformat(refernece, target)
            print('Done output made: QUBE_traj.pdb')
            exit()

    # Set up the argument parser
    parser = argparse.ArgumentParser(prog='QUBEKit-pro', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='QUBEKit-pro is an extension to QUBEKit that allows the preparation'
                                                 'of amber prepared proteins with the QUBE force field and creates force'
                                                 ' field xml files for OpenMM simulation.')
    parser.add_argument('-setup', '--setup', action=SetupAction,
                        help='Enter the name of the amber prepared protein file to convert to xyz for onetep.')

    parser.add_argument('-build', '--build_simulation_files', action=BuildAction,
                        help='Enter the name of the amber prepared protein file to generate QUBE pdb and xml files.')

    parser.add_argument('-water', '--water', nargs='?', default='help', action=WaterAction,
                        choices=['help', 'tip3p', 'spce', 'tip4p', 'tip4pew', 'tip5p', 'tip3pfb', 'tip4pfb', 'tip4p-d',
                                 'opc'],
                        help='Enter the name of the water model you would like to use.')

    parser.add_argument('-convert', '--convert', nargs=2, action=ConvertAction,
                        help='Enter the reference followed by the qube traj file you want to re format.')

    parser.parse_args()



if __name__ == '__main__':
    main()
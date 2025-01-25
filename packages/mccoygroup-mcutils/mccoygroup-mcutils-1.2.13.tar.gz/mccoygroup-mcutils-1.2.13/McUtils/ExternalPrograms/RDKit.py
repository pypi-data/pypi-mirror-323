

__all__ = [
    "RDMolecule"
]

import numpy as np, io, os
from .. import Numputils as nput

from .ChemToolkits import RDKitInterface

class RDMolecule:
    """
    A simple interchange format for RDKit molecules
    """

    def __init__(self, rdconf, charge=None):
        #atoms, coords, bonds):
        self.conf = rdconf
        self.charge = charge

    @property
    def rdmol(self):
        return self.conf.GetOwningMol()
    @property
    def atoms(self):
        mol = self.rdmol
        return [atom.GetSymbol() for atom in mol.GetAtoms()]
    @property
    def bonds(self):
        mol = self.rdmol
        return [
            [b.GetBeginAtomIdx(), b.GetEndAtomIdx(), b.GetBondTypeAsDouble()]
            for b in mol.GetBonds()
        ]
    @property
    def coords(self):
        return self.conf.GetPositions()
    @property
    def rings(self):
        return self.rdmol.GetRingInfo().AtomRings()
    @property
    def meta(self):
        return self.rdmol.GetPropsAsDict()

    @classmethod
    def chem_api(cls):
        return RDKitInterface.submodule("Chem")
    @classmethod
    def from_rdmol(cls, rdmol, conf_id=0, charge=None, guess_bonds=False, sanitize=True, sanitize_ops=None):
        if guess_bonds:
            Chem = cls.chem_api() # to get nice errors
            rdDetermineBonds = RDKitInterface.submodule("Chem.rdDetermineBonds")
            rdmol = Chem.Mol(rdmol)
            if charge is None:
                charge = 0
            rdDetermineBonds.DetermineConnectivity(rdmol, charge=charge)
            # return cls.from_rdmol(rdmol, conf_id=conf_id, guess_bonds=False, charge=charge)
        if sanitize:
            Chem = cls.chem_api() # to get nice errors
            rdmolops = RDKitInterface.submodule("Chem.rdmolops")
            if sanitize_ops is None:
                sanitize_ops = (
                        rdmolops.SANITIZE_ALL
                        ^rdmolops.SANITIZE_PROPERTIES
                        # ^rdmolops.SANITIZE_ADJUSTHS
                        # ^rdmolops.SANITIZE_CLEANUP
                        ^rdmolops.SANITIZE_CLEANUP_ORGANOMETALLICS
                )
            rdmol = Chem.Mol(rdmol)
            Chem.SanitizeMol(rdmol, sanitize_ops)
        conf = rdmol.GetConformer(conf_id)
        return cls(conf, charge=charge)

    @classmethod
    def from_coords(cls, atoms, coords, bonds=None, charge=None, guess_bonds=None):
        Chem = cls.chem_api()
        mol = Chem.EditableMol(Chem.Mol())
        mol.BeginBatchEdit()
        for a in atoms:
            a = Chem.Atom(a)
            mol.AddAtom(a)
        if bonds is not None:
            for b in bonds:
                if len(b) == 2:
                    i,j = b
                    t = 1
                else:
                    i,j,t = b
                if nput.is_numeric(t):
                    t = Chem.BondType.values[int(t)]
                else:
                    t = Chem.BondType.names[t]
                mol.AddBond(i, j, t)
        mol.CommitBatchEdit()

        mol = mol.GetMol()
        conf = Chem.Conformer(len(atoms))
        conf.SetPositions(np.asanyarray(coords))
        conf.SetId(0)
        mol.AddConformer(conf)

        if guess_bonds is None:
            guess_bonds = bonds is None

        return cls.from_rdmol(mol, charge=charge, guess_bonds=guess_bonds)

    @classmethod
    def from_mol(cls, mol, coord_unit="Angstroms", guess_bonds=None):
        from ..Data import UnitsData

        return cls.from_coords(
            mol.atoms,
            mol.coords * UnitsData.convert(coord_unit, "Angstroms"),
            bonds=mol.bonds,
            charge=mol.charge,
            guess_bonds=guess_bonds
        )

    @classmethod
    def _load_sdf_conf(cls, stream, which=0):
        Chem = cls.chem_api()
        mol = None
        for i in range(which+1):
            mol = next(Chem.ForwardSDMolSupplier(stream, sanitize=False, removeHs=False))
        return mol
    @classmethod
    def from_sdf(cls, sdf_string, which=0):
        if os.path.isfile(sdf_string):
            with open(sdf_string, 'rb') as stream:
                mol = cls._load_sdf_conf(stream, which=which)
        else:
            mol = cls._load_sdf_conf(io.BytesIO(sdf_string.encode()), which=which)
        return cls.from_rdmol(mol)

    @classmethod
    def get_confgen_opts(cls):
        return {}
    @classmethod
    def from_smiles(cls, smiles, num_confs=1, add_implicit_hydrogens=False):

        if os.path.isfile(smiles):
            with open(smiles) as f:
                smiles = f.read()
        Chem = cls.chem_api()
        params = Chem.SmilesParserParams()
        params.removeHs = False
        rdkit_mol = Chem.MolFromSmiles(smiles, params)
        mol = Chem.AddHs(rdkit_mol, explicitOnly=not add_implicit_hydrogens)
        rdDistGeom = RDKitInterface.submodule("Chem.rdDistGeom")
        rdDistGeom.EmbedMolecule(mol, num_confs, **cls.get_confgen_opts())

        return cls.from_rdmol(mol)
    @classmethod
    def from_molblock(cls, molblock):
        Chem = cls.chem_api()
        if os.path.isfile(molblock):
            mol = Chem.MolFromMolFile(molblock, sanitize=False, removeHs=False)
        else:
            mol = Chem.MolFromMolBlock(molblock, sanitize=False, removeHs=False)
        return cls.from_rdmol(mol)



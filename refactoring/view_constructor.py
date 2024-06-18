import json
from enum import Enum
from display import MOLSTAR_PREFIX, MOLSTARSUFFIX, PocketSurfaceColors


class PocketColors(Enum):
    YELLOW = 'yellow',
    MAGENTA = 'magenta',
    RED = 'red',
    BLUE = 'blue',
    GREEN = 'green'


class ViewConstructor:
    @classmethod
    def construct_ligand_view(cls, config_file="./ligand_config.json"):
        pass

    @classmethod
    def construct_protein_view(cls, config_file="./protein_config.json"):
        protein = Protein.from_config(config_file)
        return protein.construct_view() if protein else None


class Pocket:
    def __init__(self, color, path):
        self.color = color
        self.path = path

    def construct_view(self):
        with open(self.path, "r") as e:
            pocket = e.read()

            pocket = pocket.replace('\n', '\\n').replace('\t', '\\t')
            pocket_data = "{ data: `" + pocket + "`.trim(), color: { name: 'uniform', value: '" + \
                          PocketSurfaceColors[self.color.value][1] + "' }, label: '" + PocketSurfaceColors[self.color.value][
                              0] + " Pocket' },\n"
            return pocket_data


class Protein:
    def __init__(self, protein_path, protein_style_type, protein_surface_alpha, pocket_surface_alpha, pocket_style_type, pockets):
        self.path = protein_path
        self.protein_style_type = protein_style_type
        self.protein_surface_alpha = protein_surface_alpha
        self.pocket_style_type = pocket_style_type
        self.pocket_surface_alpha = pocket_surface_alpha
        self.pockets = pockets

    @classmethod
    def from_config(cls, config_file):
        with open(config_file, 'r') as cfg:
            config = json.load(cfg)

            if (not config.get('protein_path') or not config.get('protein_style_type')
                    or not config.get('pocket_style_type') or not config.get('pocket_surface_alpha')):
                return None

            protein_path = config['protein_path']
            protein_style_type = config['protein_style_type']
            protein_surface_alpha = config['protein_surface_alpha']

            if protein_style_type == 'surface':
                protein_surface_alpha = 1

            pocket_surface_alpha = config['pocket_surface_alpha']
            pocket_style_type = config['pocket_style_type']
            pocket_strs = config.get('pockets', [])
            pockets = []
            for pocket_str, path in pocket_strs.items():
                try:
                    pockets.append(Pocket(PocketColors(pocket_str).name, path))
                except ValueError:
                    pass

            return Protein(protein_path, protein_style_type, protein_surface_alpha, pocket_style_type, pocket_surface_alpha, pockets)

    def construct_view(self):
        with open(self.path, "r") as e:
            protein = e.read()
            protein = protein.replace('\n', '\\n')

            protein_data = 'var structureData = `' + protein + '`.trim();'

            loading_protein = "loadStructureExplicitly(viewer, structureData, structureFormat, dataLabel='protein', protein_style_type='" + self.protein_style_type + "', protein_surface_alpha=" + str(
                self.protein_surface_alpha) + ");"

            updated_html = MOLSTAR_PREFIX + "\n" + protein_data + "\n" + loading_protein + "\n"
            if self.pockets:
                loading_pockets = "loadStructureAndPockets(viewer, pocketDataList, pocketFormat, pocket_style_type='" + self.pocket_style_type + "', pocket_surface_alpha=" + str(
                    self.pocket_surface_alpha) + ");"
                pocket_surface_msg = 'var pocket_surface_alpha = ' + str(self.pocket_surface_alpha) + ';'

                updated_html += "const pocketDataList = [" + "\n"

                for p in self.pockets:
                    pocket_view = p.construct_view()
                    if pocket_view:
                        updated_html += pocket_view

                updated_html += "];" + "\n" + pocket_surface_msg + "\n" + loading_pockets + MOLSTARSUFFIX
            else:
                updated_html += "\n" + MOLSTARSUFFIX

            return updated_html


class Ligand:
    def __init__(self, ligand_path):
        self.path = ligand_path

    @classmethod
    def from_config(cls, config_file):
        with open(config_file, 'r') as cfg:
            config = json.load(cfg)

            if not config.get('ligand_path'):
                return None

            ligand_path = config['ligand_path']

            return Ligand(ligand_path)

    def construct_view(self):
        pass

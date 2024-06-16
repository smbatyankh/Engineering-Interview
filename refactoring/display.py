MOLSTAR_PREFIX = '''
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
            <link rel="icon" href="./favicon.ico" type="image/x-icon">
            <title>Embedded Mol* Viewer</title>
            <style>
                #app {
                    position: relative;
                    width: 100%;
                    height: 100vh;
                }
            </style>
            <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/molstar@latest/build/viewer/molstar.css" />
        </head>
        <body>
            <div id="app"></div>
            <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/molstar@latest/build/viewer/molstar.js"></script>
            <script type="text/javascript">
                molstar.Viewer.create('app', {
                    layoutIsExpanded: false,
                    layoutShowControls: false,
                    layoutShowRemoteState: false,
                    layoutShowSequence: true,
                    layoutShowLog: false,
                    layoutShowLeftPanel: false,

                    viewportShowExpand: false,
                    viewportShowSelectionMode: true,
                    viewportShowAnimation: true,

                    pdbProvider: 'rcsb',
                    emdbProvider: 'rcsb',
                }).then(viewer => {
                viewer.plugin.canvas3d?.setProps({
                    renderer: {
                        backgroundColor: 0xFFFFFF,
                    },
                    camera: {
                        mode: 'orthographic',
                        helper: { axes: { name: 'off', params: {} } },
                    },
                    cameraFog: { name: 'off', params: {} },
                    hiZ: { enabled: true }
                });

    
    async function loadLigand(viewer, data, format, dataLabel = 'ligand', ligand_type = 'ball-and-stick') {
        const _data = await viewer.plugin.builders.data.rawData({ data: data, label: dataLabel });
        const trajectory = await viewer.plugin.builders.structure.parseTrajectory(_data, format);
        const model = await viewer.plugin.builders.structure.createModel(trajectory);
        const structure = await viewer.plugin.builders.structure.createStructure(model);

        const components = {
            ligand: await viewer.plugin.builders.structure.tryCreateComponentStatic(structure, 'ligand'),
        };

        const builder = viewer.plugin.builders.structure.representation;
        const update = viewer.plugin.build();

        if (components.ligand) {
            builder.buildRepresentation(update, components.ligand, { type: ligand_type }, { tag: 'ligand' });
        }
        
        await update.commit();
    }

    async function loadStructureExplicitly(viewer, data, format, dataLabel = 'protein', style_type = 'cartoon', surface_alpha = 0) {
        const _data = await viewer.plugin.builders.data.rawData({ data: data, label: dataLabel });
        const trajectory = await viewer.plugin.builders.structure.parseTrajectory(_data, format);
        const model = await viewer.plugin.builders.structure.createModel(trajectory);
        const structure = await viewer.plugin.builders.structure.createStructure(model);

        const components = {
            polymer: await viewer.plugin.builders.structure.tryCreateComponentStatic(structure, 'polymer'),
            ligand: await viewer.plugin.builders.structure.tryCreateComponentStatic(structure, 'ligand'),
            water: await viewer.plugin.builders.structure.tryCreateComponentStatic(structure, 'water'),
        };

        const builder = viewer.plugin.builders.structure.representation;
        const update = viewer.plugin.build();
        if (components.polymer) {
            builder.buildRepresentation(update, components.polymer, {
                type: style_type,
                typeParams: {
                    alpha: 1,
                    quality: 'high'
                }
            }, { tag: 'polymer-${style_type}' });

            builder.buildRepresentation(update, components.polymer, {
                type: 'molecular-surface',
                typeParams: {
                    alpha: surface_alpha,
                    quality: 'high',
                    smoothness: 1
                },
                colorTheme: { name: 'hydrophobicity' }
            }, { tag: 'polymer-surface' });
        }
        if (components.ligand) builder.buildRepresentation(update, components.ligand, { type: 'ball-and-stick' }, { tag: 'ligand' });
        if (components.water) builder.buildRepresentation(update, components.water, { type: 'ball-and-stick', typeParams: { alpha: 0.6 } }, { tag: 'water' });
        
        await update.commit();
    }

    async function loadStructureAndPockets(viewer, pocketDataList, pocketFormat, pocket_style_type='gaussian-surface', pocket_surface_alpha = 1) {
        async function visualizePocket(data, format, color, label) {
            const _data = await viewer.plugin.builders.data.rawData({ data: data, label: label });
            const trajectory = await viewer.plugin.builders.structure.parseTrajectory(_data, format);
            const model = await viewer.plugin.builders.structure.createModel(trajectory);
            const structure = await viewer.plugin.builders.structure.createStructure(model);

            const pocketComponent = await viewer.plugin.builders.structure.tryCreateComponentStatic(structure, 'all');
            if (pocketComponent) {
                const builder = viewer.plugin.builders.structure.representation;
                const update = viewer.plugin.build();
                builder.buildRepresentation(update, pocketComponent, {
                    type: pocket_style_type,
                    typeParams: { alpha: pocket_surface_alpha },
                    color: color.name, colorParams: { value: color.value }
                }, { tag: label });
                await update.commit();
            }
        }

        for (let pocket of pocketDataList) {
            await visualizePocket(pocket.data, pocketFormat, pocket.color, pocket.label);
        }
    }

    var pocketFormat = 'pdb'.trim();
    var structureFormat = 'pdb'.trim();
    var ligandFormat = 'pdb'.trim();
'''

MOLSTARSUFFIX = '''
                });
            </script>
        </body>
    </html>
'''


PocketSurfaceColors = {
    'red': ('Red', "0xFF0000"),
    'green': ('Green', "0x008000"),
    'blue': ('Blue', "0x0403FF"),
    'yellow': ('Yellow', "0xFFFF00"),
    'magenta': ('Magenta', "0xFF00FF"),
    'cyan': ('Cyan', "0x00FFFF"),
    'orange': ('Orange', "0xFFA500"),
    'celeste': ('Celeste', "0xb2FFFF"),
    'purple': ('Purple', "0x800080"),
    'brown': ('Brown', "0xA52A2A")
}


def bad_design_construct_view(is_ligand):
    if is_ligand:
        ligand_path = "./files/molecules/BEB.pdb"
        e = open(ligand_path, "r")
        ligand = e.read()
        ligand = ligand.replace('\n', '\\n')

        style = 'ball-and-stick'
        # style = 'molecular-surface'
        ligand_data = f'var structureData = `{ligand}`.trim();'
        ligand_type = f'var ligand_type = `{style}`'
        loading = f"loadLigand(viewer, structureData, structureFormat, 'ligand', ligand_type);"

        updated_html = MOLSTAR_PREFIX + "\n" + ligand_data + "\n" + ligand_type + "\n" + loading + MOLSTARSUFFIX
    else:
        protein_path = "./files/proteins/5HOB.pdb"
        pocket_paths = [
            "./files/pockets/5HOB_yellow_pocket.pdb",
            "./files/pockets/5HOB_magenta_pocket.pdb",
            "./files/pockets/5HOB_red_pocket.pdb",
            "./files/pockets/5HOB_blue_pocket.pdb",
            "./files/pockets/5HOB_green_pocket.pdb",
        ]
        # pocket_paths = []
        pocket_style_type = 'gaussian-surface'
        protein_style_type = 'cartoon'
        protein_surface_alpha = 0.4
        # protein_surface_alpha = 0
        pocket_surface_alpha = 1

        e = open(protein_path, "r")
        protein = e.read()
        protein = protein.replace('\n', '\\n')
        
        colors = list(PocketSurfaceColors.keys())

        if protein_style_type == 'surface':
            protein_surface_alpha = 1

        protein_data = 'var structureData = `' + protein + '`.trim();'
        pocket_surface_msg = 'var pocket_surface_alpha = ' + str(pocket_surface_alpha) + ';'

        loading_protein = "loadStructureExplicitly(viewer, structureData, structureFormat, dataLabel='protein', protein_style_type='" + protein_style_type + "', protein_surface_alpha=" + str(protein_surface_alpha) + ");"
        
        updated_html = MOLSTAR_PREFIX + "\n" + protein_data +  "\n"+ loading_protein + "\n"
        if pocket_paths:
            loading_pockets = "loadStructureAndPockets(viewer, pocketDataList, pocketFormat, pocket_style_type='" + pocket_style_type + "', pocket_surface_alpha=" + str(pocket_surface_alpha) + ");"
            updated_html += "const pocketDataList = [" + "\n"
            colors = list(PocketSurfaceColors.keys())
            for j in range(len(pocket_paths)):
                e = open(pocket_paths[j], "r")
                pocket = e.read()

                pocket = pocket.replace('\n', '\\n').replace('\t', '\\t')
                pocket_data = "{ data: `" + pocket + "`.trim(), color: { name: 'uniform', value: '" + PocketSurfaceColors[colors[j]][1] + "' }, label: '" + PocketSurfaceColors[colors[j]][0] + " Pocket' },\n"
                updated_html += pocket_data

            updated_html += "];" + "\n" +  pocket_surface_msg + "\n" + loading_pockets + MOLSTARSUFFIX
        else:
            updated_html += "\n" + MOLSTARSUFFIX

    return updated_html


# result = bad_design_construct_view(True)
result = bad_design_construct_view(False)

with open("result.html", "w") as e:
    e.write(result)

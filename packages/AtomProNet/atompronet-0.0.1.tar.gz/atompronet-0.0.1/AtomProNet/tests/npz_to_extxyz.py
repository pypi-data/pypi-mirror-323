def npz_to_extxyz(input_file):

    import numpy as np
    import os
    from ase import Atoms
    from ase.io import write
    from ase.calculators.singlepoint import SinglePointCalculator

    # Read in npz file
    #in_filename = 'F:/Research/ML/package/VASP_GNN_dataset_converter/trial/alumina_pure.npz'
    #out_filename = 'F:/Research/ML/package/VASP_GNN_dataset_converter/trial/nequip_data_alumina_pure.extxyz'
    #data = np.load(in_filename)

   # Get the absolute path of the input file
    in_filename = os.path.join(input_file, 'Converted.npz')
    input_dir = os.path.dirname(in_filename)                    # Extract the directory path from in_filename
    out_filename = os.path.join(input_dir, 'Converted.extxyz')  # Create output filename in the same directory

    data = np.load(in_filename)

    # Get data
    positions = data['positions']
    lattice_params = data['lattice']  # Replace with the actual path to your lattice.npy file
    symbols = data['symbols']
    energies = data['energies']
    forces = data['forces']
    pressures = data['pressures']

    # Reshape the data to have 190 structures with 288 atoms each
    num_structures, num_atoms_per_structure, num_coords = positions.shape
    positions = positions.reshape(num_structures * num_atoms_per_structure, num_coords)
    symbols = np.tile(symbols, num_atoms_per_structure)
    forces = forces.reshape(num_structures, num_atoms_per_structure, num_coords)
    forces = forces.reshape(num_structures * num_atoms_per_structure, num_coords)
    pressures = np.repeat(pressures, num_atoms_per_structure, axis=0)  # Repeat pressures for each atom in the structure

    # Reshape lattice_params to have shape (num_structures, 3, 3)
    lattice_params = lattice_params.reshape(-1, 3, 3)

    # List to store all structures
    all_atoms = []

    # Iterate over structures
    for idx in range(num_structures):
        # Extract positions, forces, and pressure for the current structure
        start_idx = idx * num_atoms_per_structure
        end_idx = (idx + 1) * num_atoms_per_structure
        structure_positions = positions[start_idx:end_idx]
        structure_forces = forces[start_idx:end_idx]
        structure_pressure = pressures[start_idx:end_idx]

        # Ensure that positions, forces, and pressures have the same length
        assert len(structure_positions) == len(structure_forces) == len(structure_pressure), f"Positions, forces, and pressures have different lengths for structure {idx + 1}"

        # Create an empty Atoms object
        curr_atoms = Atoms()

        # Set global periodic boundary conditions for the entire structure
        curr_atoms.set_pbc([True, True, True])

        try:
            # Debug print statements
            print(f"Lattice params shape: {lattice_params.shape}")
            print(f"Lattice params for structure {idx + 1}: {lattice_params[idx]}")

            # Iterate through atoms and append to the structure
            for atom_idx in range(len(structure_positions)):
                atom_position = structure_positions[atom_idx]
                atom_symbol = str(symbols[atom_idx])

                # Attempt to create an atom with explicit lattice information
                atom = Atoms(
                    positions=[atom_position],
                    cell=lattice_params[idx],  # Use the lattice parameters corresponding to the current structure
                    symbols=[atom_symbol]
                )

                # Append the atom to the current structure
                curr_atoms += atom

            # Set the energy information for the current structure
            structure_energy = energies[idx][0]
            curr_atoms.info["energy"] = structure_energy

            # Create a SinglePointCalculator for the entire structure
            calculator = SinglePointCalculator(curr_atoms, energy=structure_energy, forces=structure_forces.tolist())
            curr_atoms.set_calculator(calculator)

            # Append the current structure to the list
            all_atoms.append(curr_atoms)
            print(f"Structure {idx + 1} successfully created and added to the list.")

        except Exception as e:
            print(f"Error creating atoms in structure {idx + 1}: {e}")

    # Write all structures to the output file with lattice information, properties line, and pressure information
    with open(out_filename, 'w') as f:
        for idx, curr_atoms in enumerate(all_atoms):
            structure_energy = energies[idx][0]
            structure_pressure = pressures[idx * num_atoms_per_structure]  # Get pressure for the current structure

            # Check the length of structure_pressure and adjust indexing
            if len(structure_pressure) == 6:
                rearranged_pressure = [
                    structure_pressure[0],  # XX
                    structure_pressure[3],  # XY 
                    structure_pressure[5],  # XZ 
                    structure_pressure[3],  # YX 
                    structure_pressure[1],  # YY
                    structure_pressure[4],  # YZ 
                    structure_pressure[5],  # ZX 
                    structure_pressure[4],  # ZY 
                    structure_pressure[2]   # ZZ
                ]

            # Format the comment line with rearranged pressure information
            comment_line = f"virial=\"{' '.join(map(str, rearranged_pressure))}\" " \
                        f"Lattice=\"{lattice_params[idx, 0, 0]} 0.0 0.0 0.0 {lattice_params[idx, 1, 1]} 0.0 0.0 0.0 {lattice_params[idx, 2, 2]}\" " \
                        f"Properties=species:S:1:pos:R:3:forces:R:3 energy={structure_energy} pbc=\"T T T\""

            # Write the structure to the output file
            write(f, curr_atoms, format='extxyz', comment=comment_line)
            print(f"Structure {idx + 1} successfully written to the file.")

            print(f"Output file saved to: {out_filename}")

    return input_file

#cat nequip_data_alumina_pure.extxyz nequip_data_alumina_Al.extxyz nequip_data_alumina_O.extxyz nequip_data_alumina_AlO.extxyz > nequip_data.extxyz
#salloc --time=6:0:0 --gres=gpu:1 --ntasks=1 --cpus-per-task=8 --mem=32G --account=def-mponga --mail-type=ALL  srun $VIRTUAL_ENV/bin/jupyterlab.sh        
import os
from mp_api.client import MPRester
from pymatgen.core.structure import Structure
from pymatgen.core.lattice import Lattice

def construct_poscar_from_structure(structure, input_folder, filename="POSCAR"):
    # Construct the path to the VASP_files directory within the input folder
    directory = os.path.join(input_folder, "VASP_files")
    
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    # Full file path to save the POSCAR file
    filepath = os.path.join(directory, filename)
    print(f"Saving POSCAR file to: {filepath}")  # Debugging statement
    
    # Constructs a POSCAR file from a given structure object
    with open(filepath, 'w') as f:
        f.write("Generated using mp-api\n")
        f.write("1.0\n")
        for vec in structure.lattice.matrix:
            f.write(f"{' '.join(map(str, vec))}\n")
        species = [site.specie.symbol for site in structure.sites]
        unique_species = sorted(set(species), key=species.index)
        f.write(" ".join(unique_species) + "\n")
        f.write(" ".join([str(species.count(s)) for s in unique_species]) + "\n")
        f.write("Direct\n")
        for site in structure.sites:
            f.write(f"{' '.join(map(str, site.frac_coords))}\n")

def create_supercell(structure, supercell_size):
    pymatgen_structure = Structure(
        lattice=Lattice(structure.lattice.matrix),
        species=[site.specie for site in structure.sites],
        coords=[site.frac_coords for site in structure.sites],
        coords_are_cartesian=False
    )
    supercell = pymatgen_structure.make_supercell(supercell_size)
    return supercell


import os

def fetch_data_for_ML_training(mpr, material_id, input_folder):
    """
    Fetches energy data for a given material ID and writes it to an energy file in the desired format.
    """
    # Ensure the input folder exists
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)

    energy_file = os.path.join(input_folder, "energy.txt")
    lattice_file = os.path.join(input_folder, "lattice.txt")
    positions_file = os.path.join(input_folder, "positions.txt")  

    try:
        # Retrieve entries for the material ID
        entries = mpr.get_entry_by_material_id(material_id)

        # Check if entries exist
        if entries:
            # Check if the energy file exists; if not, add a header
            if not os.path.exists(energy_file):
                with open(energy_file, 'w') as ef:
                    ef.write("")  # Just ensuring the file is created
                    print(f"Created energy file at: {energy_file}")

            # Check if the lattice file exists; if not, add a header
            if not os.path.exists(lattice_file):
                with open(lattice_file, 'w') as lf:
                    lf.write("")
                    print(f"Created lattice file at: {lattice_file}")

            # Check if the positions file exists; if not, add a header
            if not os.path.exists(positions_file):
                with open(positions_file, 'w') as pf:
                    pf.write("")  # Just ensuring the file is created
                    print(f"Created positions file at: {positions_file}")

            # Process each entry in the list
            for entry in entries:
                # Retrieve energy values
                total_energy = entry.energy
                energy_per_atom = entry.energy_per_atom
                energy_without_entropy = entry.uncorrected_energy
                # Handle missing phase information by setting a default value
                phase = getattr(entry, 'phase', 'Unknown')  # Default to 'Unknown' if 'phase' is not found
                correction_method = getattr(entry, 'correction_method', 'Unknown')  # Default to 'Unknown' if 'correction_method' is not found

                # Extract lattice parameters
                lattice = entry.structure.lattice
                lattice_params = f"{lattice.a:.3f} {lattice.b:.3f} {lattice.c:.3f}"

                # Append the energy data to the energy file in the requested format
                with open(energy_file, 'a') as ef:
                    ef.write(f"{material_id} Phase {phase}:\n")
                    ef.write(f"  Energy without entropy = {energy_without_entropy:.8f} Energy per atom = {energy_per_atom:.8f} Correction method = {correction_method}\n")
                    print(f"Energy data for {material_id} Phase {phase} has been written to {energy_file}.")

                # Append the lattice parameters to the lattice file
                with open(lattice_file, 'a') as lf:
                    lf.write(f"{material_id}\n")
                    lf.write(f"{lattice.a:.6f} 0.000 0.000 0.000 {lattice.b:.3f} 0.000 0.000 0.000 {lattice.c:.3f}\n")
                    print(f"Lattice parameters for {material_id} have been written to {lattice_file}.")

                # Write positions to the positions file
                with open(positions_file, 'a') as pf:
                    pf.write(f"{material_id}\n")
                    pf.write("POSITION\n")
                    pf.write("-----------------------------------------\n")
                    for site in entry.structure:
                        coords = site.coords
                        pf.write(f"{coords[0]:.6f} {coords[1]:.6f} {coords[2]:.6f}\n")
                    pf.write("\n")
                    print(f"Atomic positions for {material_id} have been written to {positions_file}.")
        else:
            print(f"No energy data found for material ID {material_id}.")
    except Exception as e:
        print(f"Error fetching energy data for {material_id}: {e}")





def fetch_and_write_poscar(api_key, query, input_folder, create_supercell_option, supercell_size=None):

    #print(f"Called with: api_key={api_key}, query={query}, input_folder={input_folder}, create_supercell_option={create_supercell_option}, supercell_size={supercell_size}")    
  
    download_energy = input("Do you want to download energy+lattice data for the materials? (yes/no): ").lower() == "yes"
    
    with MPRester(api_key) as mpr:
        if query.startswith("mp-"):
            # Querying by material ID
            material_id = query
            structure = mpr.get_structure_by_material_id(material_id)
            if structure:
                print(f"Structure for material ID {material_id} fetched successfully.")
                construct_poscar_from_structure(structure, input_folder, f"{material_id}_POSCAR")
                print(f"POSCAR file for {material_id} has been generated.")

                # Download energy data if requested
                if download_energy:
                    fetch_data_for_ML_training(mpr, material_id, input_folder)
                
                # Create supercell if option is enabled
                if create_supercell_option and supercell_size:
                    supercell = create_supercell(structure, supercell_size)
                    supercell_size_str = "_".join(map(str, supercell_size))
                    supercell_filename = f"{material_id}_{supercell_size_str}_supercell_POSCAR"
                    construct_poscar_from_structure(supercell, input_folder, supercell_filename)
                    print(f"Supercell POSCAR file for {material_id} has been generated and saved as {supercell_filename}.")
        
        elif "," in query:
            # Querying by a comma-separated list of elements
            elements = [elem.strip().capitalize() for elem in query.split(',')]
            try:
                summaries = mpr.materials.summary.search(elements=elements)
                for summary in summaries:
                    material_id = summary.material_id
                    structure = mpr.get_structure_by_material_id(material_id)
                    if structure:
                        construct_poscar_from_structure(structure, input_folder, f"{material_id}_POSCAR")
                        print(f"POSCAR file for {material_id} has been generated.")

                        # Download energy data if requested
                        if download_energy:
                            fetch_data_for_ML_training(mpr, material_id, input_folder)
                        
                        # Create supercell if option is enabled
                        if create_supercell_option and supercell_size:
                            supercell = create_supercell(structure, supercell_size)
                            supercell_size_str = "_".join(map(str, supercell_size))
                            supercell_filename = f"{material_id}_{supercell_size_str}_supercell_POSCAR"
                            construct_poscar_from_structure(supercell, input_folder, supercell_filename)
                            print(f"Supercell POSCAR file for {material_id} has been generated and saved as {supercell_filename}.")
            except Exception as e:
                print(f"Error during bulk search: {e}")
        
        else:
            # Querying by compound formula
            formula = query
            try:
                summaries = mpr.materials.summary.search(formula=formula)
                for summary in summaries:
                    material_id = summary.material_id
                    structure = mpr.get_structure_by_material_id(material_id)
                    if structure:
                        construct_poscar_from_structure(structure, input_folder, f"{material_id}_POSCAR")
                        print(f"POSCAR file for {material_id} has been generated.")

                        # Download energy data if requested
                        if download_energy:
                            fetch_data_for_ML_training(mpr, material_id, input_folder)
                        
                        # Create supercell if option is enabled
                        if create_supercell_option and supercell_size:
                            supercell = create_supercell(structure, supercell_size)
                            supercell_size_str = "_".join(map(str, supercell_size))
                            supercell_filename = f"{material_id}_{supercell_size_str}_supercell_POSCAR"
                            construct_poscar_from_structure(supercell, input_folder, supercell_filename)
                            print(f"Supercell POSCAR file for {material_id} has been generated and saved as {supercell_filename}.")
            except Exception as e:
                print(f"Error during formula-based search: {e}")

if __name__ == "__main__":
    input_folder = input("Please enter the full path to the folder where the operations should be performed: ").strip()
    default_api_key = "H5zmHxuvPs9LKyABNRQmUsj0ROBYs5C4"
    user_api_key = input("Enter your Materials Project API key (press Enter to use default): ")
    api_key = user_api_key if user_api_key.strip() != "" else default_api_key
    query = input("Enter the material ID (e.g., mp-1234), compound formula (e.g., Al2O3), or elements (e.g., Li, O, Mn) for bulk download: ")
    
    # Ask once if supercells should be created for all structures
    create_supercell_option = input("Do you want to create supercells for all structures? (yes/no): ").lower() == 'yes'
    supercell_size = None
    if create_supercell_option:
        sizes = input("Enter the supercell size (e.g., 2 2 2): ")
        supercell_size = [int(x) for x in sizes.split()]
    
    # Call the function
    if create_supercell_option:
        fetch_and_write_poscar(api_key, query, input_folder, create_supercell_option, supercell_size)
    else:
        fetch_and_write_poscar(api_key, query, input_folder, create_supercell_option)
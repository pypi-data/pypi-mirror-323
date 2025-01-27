import os
import random
import ase.io

def read_datasets(file_path):
    """Read all datasets from the extxyz file using ASE."""
    datasets = []
    for frame in ase.io.iread(file_path, format='extxyz'):
        datasets.append(frame)
    return datasets

def split(input_folder):

    use_default = input("Do you want to split the Data files? (yes/no): ").strip().lower()

    if use_default.startswith('y'):
        file_choice = input("Do you want to split '1.Converted.extxyz' or '2.Other files'? (1 or 2): ").strip()

        if file_choice == '1':
            input_file_name = 'Converted.extxyz'
            print(f"Splitting file: {input_file_name}")
        elif file_choice == '2':
            input_file_name = input("Please enter the name of the file to split (including extension): ").strip()
            print(f"Splitting file: {input_file_name}")
        else:
            print("Invalid choice. Returning to main script.")
            return None
        
    else:
        print("Dataset splitting skipped. Returning control to the main script.")
        return None
    
    # Define the path to the selected file only if input_file_name is set
    if 'input_file_name' not in locals():
        print("No valid file selected for splitting. Returning to main script.")
        return None

    # Define the path to the selected file
    input_file = os.path.join(input_folder, input_file_name)
    
    # Check if the input file exists
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"'{input_file_name}' not found in the specified folder: {input_folder}")
    
    # Read all datasets
    datasets = read_datasets(input_file)
    total_datasets = len(datasets)
    
    print(f"The dataset contains {total_datasets} structures.")
    
    # Ask if the user wants to split the dataset
    split_decision = input("Do you want to split the dataset into train, test, and validation sets? (yes/no): ").strip().lower()
    
    if split_decision.startswith('y'):
        # Get the number of structures for each split
        num_train = int(input(f"Enter the number of structures for train.extxyz (max {total_datasets}): "))
        num_validation = int(input(f"Enter the number of structures for validation.extxyz (max {total_datasets - num_train}): "))
        
        # Validate input
        if num_train + num_validation > total_datasets:
            raise ValueError("The sum of train and validation datasets exceeds the total number of structures.")
        
        # Shuffle and split the datasets
        random.shuffle(datasets)
        train_datasets = datasets[:num_train]
        validation_datasets = datasets[num_train:num_train + num_validation]
        test_datasets = datasets[num_train + num_validation:]
        
        # Define file paths
        train_file = os.path.join(input_folder, 'train.extxyz')
        validation_file = os.path.join(input_folder, 'validation.extxyz')
        test_file = os.path.join(input_folder, 'test.extxyz')
        
        # Save the datasets
        ase.io.write(train_file, train_datasets, format='extxyz')
        ase.io.write(validation_file, validation_datasets, format='extxyz')
        ase.io.write(test_file, test_datasets, format='extxyz')
        
        # Print the results
        print(f"Train dataset saved to {train_file} with {len(train_datasets)} structures.")
        print(f"Validation dataset saved to {validation_file} with {len(validation_datasets)} structures.")
        print(f"Test dataset saved to {test_file} with {len(test_datasets)} structures.")
        return input_folder
    else:
        print("Dataset splitting skipped.")

# If the script is run directly, ask for input_folder and call split
if __name__ == "__main__":
    input_folder = input("Please enter the path to the input folder: ").strip()
    split(input_folder)

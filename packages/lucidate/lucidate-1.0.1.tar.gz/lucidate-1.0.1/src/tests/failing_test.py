import pandas as pd

class DataProcessor:
    def __init__(self, file_path):
        self.data = pd.read_csv(file_path)
        
def main():
    processor = DataProcessor('non_existent_file.csv') # not a real file!
    
if __name__ == "__main__":
    main()
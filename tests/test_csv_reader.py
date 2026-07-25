from pathlib import Path

from importer.csv_reader import CSVReader
from importer.csv_validator import CSVValidator
from importer.data_transformer import DataTransformer


def main():

    project_root = Path(__file__).resolve().parent.parent
    csv_file = project_root / "sample_data" / "reliance.csv"

    reader = CSVReader()
    validator = CSVValidator()
    transformer = DataTransformer()

    df = reader.read(csv_file)

    validator.validate(df)

    df = transformer.transform(df)

    print("=" * 70)
    print("CSV IMPORT TEST")
    print("=" * 70)

    print(df.head())

    print()

    print("Rows    :", df.height)
    print("Columns :", df.width)
    print()

    print("Schema")
    print(df.schema)


if __name__ == "__main__":
    main()
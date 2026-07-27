from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from data_engine import downloader
from services.service_factory import ServiceFactory


def main():

    downloader = ServiceFactory.symbol_download_service()
    loader = ServiceFactory.symbol_csv_loader()
    validator = ServiceFactory.symbol_validator()
    transformer = ServiceFactory.symbol_transformer()

    download = downloader.download_symbol_master() 

    df = loader.load(download.file_path)

    df = validator.validate(df)

    transformed = transformer.transform(df)

    print("\nCanonical Columns\n")
    print(list(transformed.columns))

    print("\nPreview\n")
    print(transformed.head())
    print("\nData Types\n")
    print(transformed.dtypes)

    print("\nNull Values\n")
    print(transformed.isna().sum())


if __name__ == "__main__":
    main()
    
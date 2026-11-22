# AI-TOS File-by-File Analysis

This inventory covers the project source/config/test files in the uploaded archive after excluding generated `.git`, `.venv`, `__pycache__`, and `.pytest_cache` artifacts from the production package. Each retained file is reviewed and assigned a role.

| File | Lines | Role | Main definitions |
|---|---:|---|---|
| `.env` | 0 | package marker / empty |  |
| `.env.example` | 7 | application / core |  |
| `.gitignore` | 8 | application / core |  |
| `README.md` | 7 | configuration / documentation |  |
| `ai/__init__.py` | 0 | package marker / empty |  |
| `alembic.ini` | 149 | configuration / documentation |  |
| `analytics/__init__.py` | 0 | package marker / empty |  |
| `app/__init__.py` | 0 | package marker / empty |  |
| `app/application.py` | 5 | application / core | Application |
| `common/__init__.py` | 0 | package marker / empty |  |
| `common/enums/import_status.py` | 24 | domain support | ImportStatus |
| `config/__init__.py` | 0 | package marker / empty |  |
| `config/application.yaml` | 34 | configuration / documentation |  |
| `config/constants.py` | 15 | application / core |  |
| `config/database.yaml` | 12 | configuration / documentation |  |
| `config/logging.yaml` | 4 | configuration / documentation |  |
| `config/market.yaml` | 3 | configuration / documentation |  |
| `config/risk.yaml` | 6 | configuration / documentation |  |
| `config/settings.py` | 57 | application / core | Settings |
| `core/__init__.py` | 0 | package marker / empty |  |
| `core/bootstrap.py` | 30 | application / core | Bootstrap |
| `core/constants.py` | 77 | application / core |  |
| `core/exceptions.py` | 70 | application / core | AITradingError, ConfigurationError, DatabaseError, DatabaseConnectionError, MarketDataError, ScannerError, StrategyError, RiskManagementError, PortfolioError |
| `core/kernel.py` | 38 | application / core | ApplicationKernel |
| `core/logger.py` | 29 | application / core | get_logger |
| `core/settings.py` | 74 | application / core | Settings, get_settings |
| `dashboard/__init__.py` | 0 | package marker / empty |  |
| `dashboard/app.py` | 23 | dashboard |  |
| `data/__init__.py` | 0 | package marker / empty |  |
| `data_engine/__init__.py` | 0 | package marker / empty |  |
| `data_engine/constants.py` | 77 | data ingestion / ETL |  |
| `data_engine/database/__init__.py` | 0 | package marker / empty |  |
| `data_engine/database/base_loader.py` | 20 | data ingestion / ETL | BaseLoader |
| `data_engine/database/market_data_loader.py` | 32 | data ingestion / ETL | MarketDataLoader |
| `data_engine/downloader/__init__.py` | 0 | package marker / empty |  |
| `data_engine/downloader/base_downloader.py` | 96 | data ingestion / ETL | BaseDownloader |
| `data_engine/downloader/download_manager.py` | 198 | data ingestion / ETL | DownloadResult, DownloadManager |
| `data_engine/downloader/downloader_config.py` | 211 | data ingestion / ETL | DatasetConfig, get_dataset, get_download_path, get_archive_path, ensure_dataset_directories |
| `data_engine/downloader/file_verifier.py` | 169 | data ingestion / ETL | VerificationResult, FileVerifier |
| `data_engine/downloader/nse_downloader.py` | 505 | data ingestion / ETL | NSEDownloader |
| `data_engine/exceptions.py` | 141 | data ingestion / ETL | DataEngineException, DownloadException, SessionException, NetworkException, ValidationException, ResponseValidationException, CsvValidationException, SchemaValidationException, StorageException, LoaderException, PipelineException, AuditException |
| `data_engine/loader/__init__.py` | 9 | data ingestion / ETL |  |
| `data_engine/loader/csv_loader.py` | 320 | data ingestion / ETL | CSVLoader |
| `data_engine/loader/symbol_csv_loader.py` | 101 | data ingestion / ETL | SymbolCSVLoader |
| `data_engine/market_data.py` | 38 | data ingestion / ETL | _norm, read_market_csv |
| `data_engine/pipeline/__init__.py` | 9 | data ingestion / ETL |  |
| `data_engine/pipeline/download_pipeline.py` | 252 | data ingestion / ETL | DownloadPipeline |
| `data_engine/pipeline/market_data_pipeline.py` | 500 | data ingestion / ETL | MarketDataPipeline |
| `data_engine/storage/__init__.py` | 0 | package marker / empty |  |
| `data_engine/storage/file_manager.py` | 254 | data ingestion / ETL | FileManager |
| `data_engine/transformer/__init__.py` | 3 | data ingestion / ETL |  |
| `data_engine/transformer/data_transformer.py` | 512 | data ingestion / ETL | DataTransformer |
| `data_engine/transformer/symbol_transformer.py` | 293 | data ingestion / ETL | SymbolTransformer |
| `data_engine/validator/__init__.py` | 10 | data ingestion / ETL |  |
| `data_engine/validator/csv_validator.py` | 394 | data ingestion / ETL | CSVValidationException, CSVValidator |
| `data_engine/validator/response_validator.py` | 150 | data ingestion / ETL | ResponseValidator |
| `data_engine/validator/symbol_validator.py` | 193 | data ingestion / ETL | SymbolValidator |
| `database/__init__.py` | 0 | package marker / empty |  |
| `database/base.py` | 4 | database layer | Base |
| `database/base_model.py` | 44 | database layer | BaseModel |
| `database/connection.py` | 43 | database layer | DatabaseManager |
| `database/db.py` | 0 | package marker / empty |  |
| `database/models/__init__.py` | 25 | database layer |  |
| `database/models/download_history.py` | 131 | database layer | DownloadStatus, DownloadHistory |
| `database/models/import_batch.py` | 202 | database layer | ImportBatch |
| `database/models/import_execution.py` | 217 | database layer | ImportExecution |
| `database/models/indicator_data.py` | 144 | database layer | IndicatorData |
| `database/models/indicator_definition.py` | 22 | database layer | IndicatorDefinition |
| `database/models/indicator_run_history.py` | 61 | database layer | IndicatorRunHistory |
| `database/models/market_data.py` | 173 | database layer | MarketData |
| `database/models/symbol.py` | 119 | database layer | Symbol |
| `database/repositories/__init__.py` | 7 | database layer |  |
| `database/repositories/base_repository.py` | 137 | database layer | BaseRepository |
| `database/repositories/download_history_repository.py` | 179 | database layer | DownloadHistoryRepository |
| `database/repositories/import_batch_repository.py` | 142 | database layer | ImportBatchRepository |
| `database/repositories/indicator_repository.py` | 148 | database layer | IndicatorRepository |
| `database/repositories/market_data_repository.py` | 293 | database layer | MarketDataRepository |
| `database/repositories/symbol_repository.py` | 198 | database layer | SymbolRepository |
| `database/session.py` | 21 | database layer | new_session, get_session |
| `database/unit_of_work.py` | 92 | database layer | UnitOfWork |
| `docs/Architecture.md` | 0 | package marker / empty |  |
| `docs/ChangeLog.md` | 0 | package marker / empty |  |
| `docs/Database.md` | 0 | package marker / empty |  |
| `docs/Development.md` | 0 | package marker / empty |  |
| `docs/Production.md` | 31 | configuration / documentation |  |
| `downloads/raw/bhavcopy/bhavcopy_20260726.csv` | 3260 | application / core |  |
| `downloads/raw/symbols/symbol_master_20260726.csv` | 2388 | application / core |  |
| `downloads/raw/symbols/symbol_master_20260727.csv` | 2407 | application / core |  |
| `dto/__init__.py` | 7 | domain support |  |
| `dto/import_result.py` | 133 | domain support | ImportResult |
| `dto/import_statistics.py` | 23 | domain support | ImportStatistics |
| `dto/indicator_dto.py` | 15 | domain support | IndicatorDTO |
| `dto/market_data_dto.py` | 32 | domain support | MarketDataCreateDTO |
| `dto/symbol_dto.py` | 25 | domain support | SymbolCreateDTO |
| `exceptions/__init__.py` | 0 | package marker / empty |  |
| `exceptions/download_exception.py` | 9 | application / core | DownloadException |
| `importer/__init__.py` | 0 | package marker / empty |  |
| `importer/csv_reader.py` | 36 | application / core | CSVReader |
| `importer/csv_validator.py` | 33 | application / core | CSVValidator |
| `importer/data_transformer.py` | 32 | application / core | DataTransformer |
| `indicator/calculator.py` | 53 | indicator engine | IndicatorCalculator |
| `indicator/engine.py` | 17 | indicator engine | IndicatorEngine |
| `indicator/loader.py` | 16 | indicator engine | IndicatorLoader |
| `indicator/saver.py` | 56 | indicator engine | IndicatorSaver |
| `indicator/supertrend.py` | 102 | indicator engine | calculate_supertrend |
| `journal/__init__.py` | 0 | package marker / empty |  |
| `logs/application.log` | 1361 | application / core |  |
| `main.py` | 19 | application / core | main |
| `migrations/README` | 1 | database migration |  |
| `migrations/env.py` | 80 | database migration | run_migrations_offline, run_migrations_online |
| `migrations/script.py.mako` | 28 | database migration |  |
| `migrations/versions/0bc36e062681_create_symbol_table.py` | 53 | database migration | upgrade, downgrade |
| `migrations/versions/80ecd7831bab_create_market_data_table.py` | 59 | database migration | upgrade, downgrade |
| `migrations/versions/b066194363c3_create_import_batch_tables.py` | 99 | database migration | upgrade, downgrade |
| `migrations/versions/d23ce694d352_create_download_history_table.py` | 173 | database migration | upgrade, downgrade |
| `migrations/versions/e6f8a1dab74a_create_indicator_tables.py` | 105 | database migration | upgrade, downgrade |
| `models/__init__.py` | 0 | package marker / empty |  |
| `models/download_result.py` | 31 | domain support | DownloadResult |
| `models/transformation_result.py` | 81 | domain support | TransformationResult |
| `models/validation_result.py` | 34 | domain support | ValidationResult |
| `portfolio/__init__.py` | 0 | package marker / empty |  |
| `portfolio/backtester.py` | 40 | portfolio / backtest | BacktestResult, PositionalBacktester |
| `project.txt` | 110100 | configuration / documentation |  |
| `project_clean.txt` | 60715 | configuration / documentation |  |
| `project_files.txt` | 351 | configuration / documentation |  |
| `project_folders.txt` | 109 | configuration / documentation |  |
| `project_structure.txt` | 85143 | configuration / documentation |  |
| `pyproject.toml` | 4 | configuration / documentation |  |
| `reports/__init__.py` | 0 | package marker / empty |  |
| `reports/exporter.py` | 11 | reporting | export_scan, export_backtest |
| `requirements.txt` | 12 | configuration / documentation |  |
| `risk/__init__.py` | 0 | package marker / empty |  |
| `risk/manager.py` | 24 | risk | PositionPlan, RiskManager |
| `sample_data/reliance.csv` | 980 | application / core |  |
| `scanner/__init__.py` | 0 | package marker / empty |  |
| `scanner/engine.py` | 15 | scanner | Scanner |
| `scripts/__init__.py` | 0 | package marker / empty |  |
| `scripts/test_download.py` | 75 | test / diagnostic script | main |
| `scripts/test_download_service.py` | 52 | test / diagnostic script | print_result, main |
| `scripts/test_symbol_download.py` | 50 | test / diagnostic script | main |
| `scripts/test_symbol_loader.py` | 73 | test / diagnostic script | main |
| `scripts/test_symbol_transformer.py` | 41 | test / diagnostic script | main |
| `scripts/test_symbol_validator.py` | 97 | test / diagnostic script | main |
| `scripts/test_synchronization.py` | 58 | test / diagnostic script | print_result, main |
| `services/__init__.py` | 3 | service layer |  |
| `services/base_service.py` | 71 | service layer | BaseService |
| `services/download_service.py` | 186 | service layer | DownloadStatus, DownloadService |
| `services/import/__init__.py` | 0 | package marker / empty |  |
| `services/import/import_manager.py` | 0 | package marker / empty |  |
| `services/import_batch_service.py` | 179 | service layer | ImportBatchService |
| `services/import_service.py` | 202 | service layer | ImportService |
| `services/indicator_service.py` | 179 | service layer | IndicatorService |
| `services/market_data_mapper.py` | 83 | service layer | MarketDataMapper |
| `services/market_data_service.py` | 286 | service layer | MarketDataService |
| `services/service_factory.py` | 50 | service layer | ServiceFactory |
| `services/symbol_download_service.py` | 206 | service layer | SymbolDownloadService |
| `services/symbol_service.py` | 165 | service layer | SymbolService |
| `services/synchronization_service.py` | 215 | service layer | SynchronizationResult, SynchronizationService |
| `strategy/__init__.py` | 0 | package marker / empty |  |
| `strategy/positional.py` | 27 | strategy | Signal, PositionalStrategy |
| `test_base.py` | 23 | test / diagnostic script | main |
| `test_base_model.py` | 33 | test / diagnostic script | main |
| `test_session.py` | 38 | test / diagnostic script | main |
| `test_symbol.py` | 27 | test / diagnostic script | main |
| `test_symbol_repository.py` | 15 | test / diagnostic script | main |
| `tests/__init__.py` | 0 | package marker / empty |  |
| `tests/conftest.py` | 88 | test / diagnostic script | setup_database, db_session, cleanup_session |
| `tests/integration/__init__.py` | 0 | package marker / empty |  |
| `tests/repositories/__init__.py` | 0 | package marker / empty |  |
| `tests/repositories/test_base_repository.py` | 236 | test / diagnostic script | repository, sample_symbol, test_add_entity, test_get_by_id, test_exists_true, test_exists_false, test_get_all, test_count, test_add_many, test_delete, test_delete_many, test_refresh |
| `tests/repositories/test_indicator_repository.py` | 196 | test / diagnostic script | repository, sample_indicator_data, test_get_by_symbol, test_get_latest, test_get_by_symbol_and_date, test_exists_for_symbol_and_date, test_exists_for_symbol_and_date_false, test_count_by_symbol, test_delete_by_symbol |
| `tests/repositories/test_market_data_repository.py` | 190 | test / diagnostic script | repository, sample_market_data, test_get_latest_price, test_get_price_history, test_get_price_history_by_symbol, test_get_by_symbol_and_date, test_exists_for_symbol_and_date, test_count_by_symbol, test_get_latest_trading_date, test_get_earliest_trading_date, test_get_all_symbol_ids |
| `tests/repositories/test_symbol_repository.py` | 171 | test / diagnostic script | repository, sample_symbols, test_get_by_symbol_code, test_get_by_symbol_code_not_found, test_exists_by_symbol_code_true, test_exists_by_symbol_code_false, test_get_all_symbol_codes, test_get_active_symbols, test_get_by_exchange, test_count_by_exchange, test_search_by_symbol_code, test_search_by_symbol_name |
| `tests/services/test_base_service.py` | 69 | test / diagnostic script | test_base_service_creation, test_require_not_none_success, test_require_not_none_failure, test_require_success, test_require_failure, test_logging_methods_exist, test_logging_methods_execute |
| `tests/services/test_import_service.py` | 274 | test / diagnostic script | mock_loader, mock_validator, mock_transformer, mock_market_data_service, import_service, test_import_service_initialization, test_import_statistics_creation, test_import_file_success, test_import_file_validation_failure, test_import_directory_missing_directory, test_import_directory_empty, test_import_directory_multiple_files |
| `tests/services/test_indicator_service.py` | 254 | test / diagnostic script | symbol_service, indicator_service, symbol, create_indicator_dto, test_create_indicator, test_duplicate_indicator, test_get_indicator, test_get_latest, test_get_by_symbol, test_get_by_symbol_and_date, test_count_by_symbol, test_delete_indicator |
| `tests/services/test_market_data_service.py` | 226 | test / diagnostic script | symbol_service, market_service, symbol, create_market_dto, test_create_market_data, test_duplicate_market_data, test_get_market_data, test_get_latest_price, test_get_by_symbol_and_date, test_price_history, test_count_by_symbol, test_delete_market_data |
| `tests/services/test_symbol_service.py` | 131 | test / diagnostic script | service, create_dto, test_create_symbol, test_duplicate_symbol, test_get_symbol, test_get_by_symbol_code, test_activate_deactivate, test_delete_symbol, test_search |
| `tests/test_csv_reader.py` | 40 | test / diagnostic script | main |
| `tests/test_csv_validator.py` | 149 | test / diagnostic script | validator, valid_dataframe, test_validate_success, test_empty_dataframe, test_missing_required_column, test_duplicate_columns, test_null_values, test_minimum_rows, test_column_count |
| `tests/test_data_transformer.py` | 932 | test / diagnostic script | TestDataTransformer |
| `tests/test_file_manager.py` | 47 | test / diagnostic script | test_build_filename, test_save_and_read, test_delete |
| `tests/test_indicator_calculator.py` | 92 | test / diagnostic script | main |
| `tests/test_indicator_validation.py` | 271 | test / diagnostic script | Validator, main |
| `tests/test_market_data_crud.py` | 117 | test / diagnostic script | main |
| `tests/test_market_repository.py` | 26 | test / diagnostic script | main |
| `tests/test_repository.py` | 22 | test / diagnostic script | main |
| `tests/test_response_validator.py` | 136 | test / diagnostic script | make_response, test_valid_response, test_invalid_status, test_empty_response, test_html_response, test_missing_header |
| `tests/test_supertrend.py` | 129 | test / diagnostic script | main |
| `tests/test_symbol_crud.py` | 90 | test / diagnostic script | main |
| `tests/test_symbol_service.py` | 40 | test / diagnostic script | main |
| `tests/test_unit_of_work.py` | 62 | test / diagnostic script | main |
| `tests/unit/test_csv_market_data.py` | 10 | test / diagnostic script | test_simple_csv |
| `tests/unit/test_indicators_strategy.py` | 25 | test / diagnostic script | sample, test_indicator_columns_and_no_talib_dependency, test_strategy_is_deterministic, test_risk_sizing |
| `validators/__init__.py` | 16 | domain support |  |
| `validators/base_validator.py` | 20 | domain support | ValidationError, BaseValidator |
| `validators/indicator_validator.py` | 15 | domain support | IndicatorValidator |
| `validators/market_data_validator.py` | 52 | domain support | MarketDataValidator |
| `validators/symbol_validator.py` | 42 | domain support | SymbolValidator |

## Production changes

- Removed the accidental concatenation of a second loader module from `data_engine/database/base_loader.py`; created `data_engine/database/market_data_loader.py`.
- Removed the hard-coded database password from configuration and added `.env.example` / `DATABASE_URL` support.
- Replaced the TA-Lib dependency with a pandas/numpy indicator implementation so deployment does not depend on a native TA-Lib wheel.
- Implemented the previously empty indicator engine and added SuperTrend persistence fields.
- Added deterministic positional strategy, scanner, risk sizing, and no-lookahead paper backtester.
- Added Streamlit command-center dashboard and CLI scan entry point.
- Added focused unit tests and a production setup/operations document.
- Existing database-heavy integration tests are retained but require the configured PostgreSQL/driver environment; they are not falsely reported as passed in this isolated build environment.

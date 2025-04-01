# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=broad-exception-caught
# pylint: disable=line-too-long
# pylint: disable=unused-variable
# pylint: disable=broad-exception-raised
import logging
import uuid
import datetime
import inspect
from typing import List, Dict, Any, Union, Optional, Tuple
from google.api_core.exceptions import NotFound
from google.cloud import  bigquery
from ipulse_shared_base_ftredge import (DataResource,
                                        LogLevel,
                                        Action ,
                                        Alert,
                                        ProgressStatus,
                                        StructLog ,
                                        log_info,
                                        log_warning,
                                        log_by_lvl)

from ..pipelines import FunctionResult, Pipelinemon, handle_pipeline_operation_exception

###########################################################################################
#################################### BIGQUERY SCHEMA/TYPES Helpers ############################
###########################################################################################

def _convert_python_type_to_bigquery(value: Any) -> str:
    """
    Determine BigQuery column type from Python value.        
    Returns:
        str: BigQuery data type
    """
    if value is None:
        raise ValueError("Cannot determine BigQuery type from None value")
    if isinstance(value, datetime.datetime):
        return "TIMESTAMP"
    if isinstance(value, datetime.date):
        return "DATE"
    if isinstance(value, str):
        if not value.strip():
            raise ValueError("Cannot determine BigQuery type from empty string")
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d')
            return "DATE"
        except ValueError:
            return "STRING"
            
     # Handle boolean before int!
    if isinstance(value, bool):
        return "BOOLEAN"
    # Handle numeric types
    if isinstance(value, int):
        return "INTEGER"
    if isinstance(value, float):
        return "FLOAT"
        
    return "STRING"

def create_bigquery_schema_from_json_schema(json_schema: list) -> List[bigquery.SchemaField]:
    schema = []
    for field in json_schema:
        if "max_length" in field:
            schema.append(bigquery.SchemaField(field["name"], field["type"], mode=field["mode"], max_length=field["max_length"]))
        else:
            schema.append(bigquery.SchemaField(field["name"], field["type"], mode=field["mode"]))
    return schema


def _convert_cerberus_type_to_bigquery(field_rules: dict) -> str:
    """Maps a Cerberus type to a BigQuery data type, handling custom rules."""

    if 'check_with' in field_rules:
        if field_rules['check_with'] == 'standard_str_date':
            return 'DATE'
        if field_rules['check_with'] == 'iso_str_timestamp':
            return 'TIMESTAMP'
        if field_rules['check_with'] == 'standard_str_time':
            return 'TIME'

    # Default type mapping if no custom rule is found
    type_mapping = {
        'string': 'STRING',
        'integer': 'INT64',
        'float': 'FLOAT64',
        'boolean': 'BOOL',
        'datetime': 'TIMESTAMP',
        'date': 'DATE',
        'time': 'TIME'
    }
    # Handle the case where 'type' is a list
    field_type = field_rules.get('type', 'string')
    if isinstance(field_type, list):
        # Choose the first valid type from the list or default to 'STRING'
        for ft in field_type:
            if ft in type_mapping:
                return type_mapping[ft]
        return 'STRING'  # Default if no valid type found
    else:
        return type_mapping.get(field_type, 'STRING')


def create_bigquery_schema_from_cerberus_schema(cerberus_schema: dict) -> List[bigquery.SchemaField]:
    """Converts a Cerberus validation schema to a BigQuery schema.
        Handles 'custom_date' and 'custom_timestamp' rules as DATE and TIMESTAMP.
    """
    bq_schema = []
    for field_name, field_rules in cerberus_schema.items():
        field_type = _convert_cerberus_type_to_bigquery(field_rules)  # Pass field_name for rule checks
        mode = 'REQUIRED' if field_rules.get('required') else 'NULLABLE'
        max_length = field_rules.get('maxlength')
        
        if max_length and field_type == 'STRING':
            field = bigquery.SchemaField(field_name, field_type, mode=mode, max_length=max_length)
        else:
            field = bigquery.SchemaField(field_name, field_type, mode=mode)
        
        bq_schema.append(field)

    return bq_schema


###########################################################################################
#################################### BIGQUERY JOBS HELPER FUNCTIONS ###############################
###########################################################################################

def _get_bigquery_job_details(job: Union[bigquery.LoadJob, bigquery.QueryJob, bigquery.CopyJob, bigquery.ExtractJob]) -> Dict[str, Any]:

    """
    Get BigQuery job status while preserving existing values through appending.
    Returns a status dict with appended values instead of overwriting.
    """
    details ={} # shortcut
    details["execution_errors_count"]= len(job.errors or [])
    details["bigquery_job_id"] = job.job_id or ""
    details["job_user_email"] = job.user_email or ""

    if isinstance(job, bigquery.QueryJob):
        details["total_bytes_billed"] = job.total_bytes_billed
        details["total_bytes_processed"] = job.total_bytes_processed
        details["cache_hit"] = job.cache_hit
        details["slot_millis"] = job.slot_millis
        details["num_dml_affected_rows"] = job.num_dml_affected_rows
        if job.started and job.ended:
            details["duration_ms"] = (job.ended - job.started).total_seconds() * 1000
    elif isinstance(job, bigquery.LoadJob): # Add LoadJob specifics
        if job.started and job.ended:
            details["job_duration_ms"] = (job.ended - job.started).total_seconds() * 1000
        details["job_output_bytes"] = job.output_bytes or 0
        details["job_output_rows"] = job.output_rows or 0    
    elif isinstance(job, (bigquery.CopyJob, bigquery.ExtractJob)): # Add any required fields for other job types
        pass # for now we will keep this empty, you might need to add specific fields

    return {job.job_id: details}

def _summarize_bigquery_job_errors(job: Union[bigquery.LoadJob, bigquery.QueryJob, bigquery.CopyJob, bigquery.ExtractJob], max_errors_to_log: int = 7) -> str:
    """Summarizes job errors for logging."""
    if job.errors:
        limited_errors = " >> ERRORS DURING JOB:\n"
        for error in job.errors[:max_errors_to_log]:
            if isinstance(error, dict) and "message" in error:
                limited_errors += error["message"] + "\n"
            else:
                limited_errors += str(error) + "\n"
        if len(job.errors) > max_errors_to_log:
            limited_errors += f"\n...and {len(job.errors) - max_errors_to_log} more errors."
        return limited_errors
    return ""

def _handle_query_job_result(query_job: Union[bigquery.LoadJob, bigquery.QueryJob, bigquery.CopyJob, bigquery.ExtractJob],
                             result: FunctionResult,
                             action: Action,
                             max_job_issues_to_log: int = 7,
                             rows: Optional[List[bigquery.Row]] = None,
                             pipelinemon: Optional[Pipelinemon] = None,
                             logger: Optional[logging.Logger] = None,
                             single_column: bool = False) -> None:
    """Helper to standardize query job result handling"""
    # Add job details and errors if any
    result.add_metadata(**_get_bigquery_job_details(job=query_job))

    if query_job.state == "DONE":
        # Initialize data and records_fetched for read operations
        if rows is not None:  # Explicitly check if rows were provided (even if empty)
            if single_column:
                result.data = [row[0] for row in rows]  # Extract single column values
            else:
                result.data = [dict(row) for row in rows]
            result.add_metadata(records_fetched=len(result.data))
            result.add_state(f"FETCHED_{len(result.data)}_RECORDS")
        
        if query_job.errors:
            result.add_issue(f"{action}_JOB_COMPLETED_WITH_ERRORS")
            result.add_issue(_summarize_bigquery_job_errors(job=query_job, max_errors_to_log=max_job_issues_to_log), update_state=False)
            result.final(issues_allowed=True)
        else:
            result.add_state(f"{action}_COMPLETED")
    else:
        result.add_issue(f"{action} failed with state {query_job.state}")
        result.add_issue(_summarize_bigquery_job_errors(job=query_job, max_errors_to_log=max_job_issues_to_log), update_state=False)
    result.final()
    log_by_lvl(
        info_msg=f"{action} job completed with state {query_job.state}.",
        debug_msg=result.get_final_report(),
        logger=logger
    )
    if pipelinemon:
        pipelinemon.add_log(StructLog(
            level=LogLevel.INFO if result.is_success else LogLevel.ERROR,
            action=action,
            resource=DataResource.DB_BIGQUERY,
            progress_status=result.progress_status,
            q=len(result.data) if result.data else 0,
            description=result.get_final_report()
        ))


###########################################################################################
#################################### BIGQUERY CREATE TABLE and LOAD FROM JSON ###############################
###########################################################################################


def create_or_replace_bigquery_table_extended(
    table_full_path: str,
    schema: List[bigquery.SchemaField],
    project_id: Optional[str] = None,
    replace_if_exists: bool = False,
    temp: bool = False,
    bigquery_client: Optional[bigquery.Client] = None,
    pipelinemon: Optional[Pipelinemon] = None,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    raise_e: bool = False
) -> FunctionResult:
    """Creates a BigQuery table with the specified schema.

    Args:
        table_full_path: Full table path (project.dataset.table)
        schema: Table schema as list of SchemaField objects
        project_id: Optional GCP Project ID (if not included in table_full_path)
        replace_if_exists: If True, replace existing table
        temp: Whether this is a temporary table
        bigquery_client: Optional pre-initialized BigQuery client
        pipelinemon: Optional pipeline monitoring object
        logger: Optional logger instance
        print_out: Whether to print output
        raise_e: Whether to raise exceptions
        
    Returns:
        FunctionResult with creation status
    """
    function_name = inspect.currentframe().f_code.co_name
    result = FunctionResult(function_name)

    try:
        # Parse table path
        path_parts = table_full_path.split('.')
        if len(path_parts) == 3:
            path_project_id, dataset_name, table_name = path_parts
            if project_id and project_id != path_project_id:
                raise ValueError(f"Conflicting project IDs: {project_id} vs {path_project_id} in path")
            project_id = path_project_id
        elif len(path_parts) == 2:
            if not project_id:
                raise ValueError("project_id is required when not included in table_full_path")
            dataset_name, table_name = path_parts
        else:
            raise ValueError(f"Invalid table_full_path format: {table_full_path}")

        result.add_metadata(
            project_id=project_id,
            dataset_name=dataset_name,
            table_name=table_name,
            table_full_path=table_full_path,
            replace_if_exists=replace_if_exists,
            temp=temp
        )

        # Initialize client if needed
        if not bigquery_client:
            bigquery_client = bigquery.Client(project=project_id)

        # Check if dataset exists
        dataset_ref = bigquery_client.dataset(dataset_name)
        try:
            bigquery_client.get_dataset(dataset_ref)
        except NotFound as e:
            raise ValueError(f"Dataset {dataset_name} does not exist. Please create it first via Terraform") from e

        # Check if table exists
        table_ref = dataset_ref.table(table_name)
        table_exists = False
        try:
            bigquery_client.get_table(table_ref)
            table_exists = True
            if pipelinemon:
                pipelinemon.add_log(StructLog(
                    level=LogLevel.NOTICE, 
                    alert=Alert.ALREADY_EXISTS,
                    resource=DataResource.DB_TABLE,
                    description=f"Table {table_name} already existed in {dataset_name}."
                ))
        except NotFound:
            table_exists = False

        # Handle existing table

        if temp:
            del_action=Action.PERSIST_DELETE_TABLE_TEMP
            cr_action=Action.PERSIST_CREATE_OR_REPLACE_TABLE_TEMP
        else:
            del_action=Action.PERSIST_DELETE_TABLE
            cr_action=Action.PERSIST_CREATE_OR_REPLACE_TABLE
        if table_exists:
            if replace_if_exists:
                bigquery_client.delete_table(table_ref)
                result.add_metadata(existing_table_deleted=True)
                result.add_state("TABLE_DELETED")
                msg = f"Table {table_name} in dataset {dataset_name} was deleted."
                log_by_lvl(debug_msg=result.get_final_report(), info_msg=msg, logger=logger, print_out=print_out)
                
                if pipelinemon:
                    pipelinemon.add_system_impacted(f"bigquery_delete_table: {table_name}")
                    pipelinemon.add_log(StructLog(
                        level=LogLevel.INFO,
                        action=del_action,
                        resource=DataResource.DB_BIGQUERY,
                        progress_status=ProgressStatus.DONE,
                        description=result.get_final_report()
                    ))
            else:
            
                notice_msg = "CREATION_SKIPPED as Table exists and replace_if_exists=False"
                result.add_notice(notice_msg)
                result.final()
                
                if pipelinemon:
                    pipelinemon.add_log(StructLog(
                        level=LogLevel.NOTICE,
                        action=cr_action,
                        resource=DataResource.DB_BIGQUERY,
                        alert=Alert.ALREADY_EXISTS,
                        progress_status=result.progress_status,
                        description=notice_msg
                    ))
                
                log_warning(
                    msg=notice_msg,
                    logger=logger,
                    print_out=print_out
                )
                return result

        # Create table
        table = bigquery.Table(table_ref, schema=schema)
        table = bigquery_client.create_table(table)
        result.add_state("TABLE_CREATED")
        result.final()

        msg = f"Table {table_name} created in dataset {dataset_name}."
        log_by_lvl(debug_msg=result.get_final_report(), info_msg=msg, logger=logger, print_out=print_out)

        if pipelinemon:
            pipelinemon.add_system_impacted(f"bigquery_create_table: {table_name}")
            pipelinemon.add_log(StructLog(
                level=LogLevel.INFO,
                action=Action.PERSIST_CREATE_OR_REPLACE_TABLE,
                resource=DataResource.DB_BIGQUERY,
                progress_status=result.progress_status,
                description=result.get_final_report()
            ))

    except Exception as e:
        handle_pipeline_operation_exception(
            e=e,
            result=result,
            action=Action.PERSIST_CREATE_OR_REPLACE_TABLE,
            resource=DataResource.DB_BIGQUERY,
            logger=logger,
            pipelinemon=pipelinemon,
            print_out=print_out,
            raise_e=raise_e
        )
    finally:
        result.final()
    return result

def load_from_json_bigquery_table_extended(
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
    table_full_path: str,
    project_id: Optional[str] = None,
    schema: Optional[List[bigquery.SchemaField]] = None,
    create_table_if_not_exists: bool = False,
    truncate_table_if_exists: bool = False,
    temp: bool = False,
    bigquery_client: Optional[bigquery.Client] = None,
    max_job_errors_to_log: int = 7,
    pipelinemon: Optional[Pipelinemon] = None,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    raise_e: bool = False
) -> FunctionResult:
    """Creates or appends to a BigQuery table from JSON data.

    Args:
        data: Data to load as dict or list of dicts
        table_full_path: Full table path (project.dataset.table)
        project_id: Optional GCP Project ID (if not in table_full_path)
        schema: Optional schema for table creation
        create_if_not_exists: Whether to create table if missing
        truncate_table_if_exists: Whether to truncate table if it exosts, otherwise it will append (False to error)
        temp: Whether this is a temporary table
        bigquery_client: Optional pre-initialized BigQuery client
        max_job_errors_to_log: Max number of job errors to log
        pipelinemon: Optional pipeline monitoring object
        logger: Optional logger instance
        print_out: Whether to print output
        raise_e: Whether to raise exceptions

    Returns:
        FunctionResult with operation status
    """
    function_name = inspect.currentframe().f_code.co_name
    result = FunctionResult(function_name)
    
    try:
        # Parse table path
        path_parts = table_full_path.split('.')
        if len(path_parts) == 3:
            path_project_id, dataset_name, table_name = path_parts
            if project_id and project_id != path_project_id:
                raise ValueError(f"Conflicting project IDs: {project_id} vs {path_project_id} in path")
            project_id = path_project_id
        elif len(path_parts) == 2:
            if not project_id:
                raise ValueError("project_id is required when not included in table_full_path")
            dataset_name, table_name = path_parts
        else:
            raise ValueError(f"Invalid table_full_path format: {table_full_path}")

        result.add_metadata(
            project_id=project_id,
            table_full_path=table_full_path,
            create_if_not_exists=create_table_if_not_exists,
            overwrite_data_if_exists=truncate_table_if_exists,
            temp=temp
        )

        # Initialize client
        if not bigquery_client:
            bigquery_client = bigquery.Client(project=project_id)

        # Handle single record case
        if isinstance(data, dict):
            data = [data]

        # Check if dataset exists
        dataset_ref = bigquery_client.dataset(dataset_name)
        try:
            bigquery_client.get_dataset(dataset_ref)
        except NotFound as e:
            raise ValueError(f"Dataset {dataset_name} does not exist. Please create it first via Terraform") from e

        # Configure job
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        )

        # Check table existence and set dispositions
        table_ref = dataset_ref.table(table_name)
        table_exists = False
        action = Action.PERSIST_CREATE_OR_LOAD_TABLE_FROM_JSON_TEMP if temp else Action.PERSIST_CREATE_OR_LOAD_TABLE_FROM_JSON
        try:
            bigquery_client.get_table(table_ref)
            table_exists = True
        except NotFound:
            table_exists = False

        if table_exists:
            if truncate_table_if_exists:
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
                result.add_state("TRUNCATING_EXISTING_TABLE")
            else:
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
                result.add_state("APPENDING_TO_EXISTING_TABLE")
                
        else:
            if create_table_if_not_exists:
                job_config.create_disposition = bigquery.CreateDisposition.CREATE_IF_NEEDED
                result.add_state("CREATING_NEW_TABLE")
            else:
                # New handling for non-existent table
                warning_msg = "CREATION_SKIPPED as Table does not exist and create_if_not_exists=False"
                result.add_warning(warning_msg)
                result.final()
                
                if pipelinemon:
                    pipelinemon.add_log(StructLog(
                        level=LogLevel.WARNING,
                        action=action,
                        resource=DataResource.DB_BIGQUERY,
                        alert=Alert.TABLE_NOT_FOUND,
                        progress_status=result.progress_status,
                        description=warning_msg
                    ))
                
                log_warning(
                    msg=warning_msg,
                    logger=logger,
                    print_out=print_out
                )
                return result

        # Load data
        result.add_state(f"{action}_LOAD_STARTED")
        
        load_job = bigquery_client.load_table_from_json(
            data,
            table_full_path,
            job_config=job_config,
            project=project_id
        )
        load_job.result()  # Wait for completion

        _handle_query_job_result(
            query_job=load_job,
            result=result,
            action=action,
            max_job_issues_to_log=max_job_errors_to_log,
            pipelinemon=pipelinemon,
            logger=logger
        )

    except Exception as e:
        handle_pipeline_operation_exception(
            e=e,
            result=result,
            action=Action.PERSIST_WRITE if truncate_table_if_exists else action,
            resource=DataResource.DB_BIGQUERY,
            logger=logger,
            pipelinemon=pipelinemon,
            raise_e=raise_e,
            print_out=print_out
        )
    finally:
        result.final()
        
    return result


###########################################################################################
#################################### BIGQUERY MERGE and WRITE QUERY ###############################
###########################################################################################


def merge_into_bigquery_table_extended(
    project_id: str,
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
    table_full_path: str,
    merge_key_columns: Union[str, List[str]], # Columns to use for identifying duplicates
    max_job_errors_to_log: int = 7,
    bigquery_client: Optional[bigquery.Client] = None,
    schema: Optional[List[bigquery.SchemaField]] = None,
    pipelinemon: Optional[Pipelinemon]=None,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    raise_e: bool = False,
) -> FunctionResult:
    """
    Merges data into a BigQuery table, avoiding duplicates based on the provided merge key columns.
    Returns:
        Dict[str, Any]: Status information about the merge operation.
    """
    function_name = inspect.currentframe().f_code.co_name
    result = FunctionResult(function_name)
    result.add_metadata(
        project_id=project_id,
        table_full_path=table_full_path,
        merge_key_columns=merge_key_columns
    )
    temp_table_name = None

    try:
        # Input validation
        if not project_id or not table_full_path:
            raise ValueError("project_id and table_full_path are required")
        if not merge_key_columns:
            raise ValueError("merge_key_columns cannot be empty")

        # Setup
        bigquery_client = bigquery_client or bigquery.Client(project=project_id)
        dataset_name, table_name = table_full_path.split('.')[1:3]
        temp_table_name = f"{table_name}_temp_{datetime.datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
        temp_table_full_path = f"{project_id}.{dataset_name}.{temp_table_name}"
        
        result.add_metadata(
            temp_table_full_path=temp_table_full_path,
            dataset_name=dataset_name,
            table_name=table_name
        )

        # Create temp table
        result.add_state("CREATING_TEMP_TABLE")
        create_result:FunctionResult = load_from_json_bigquery_table_extended(
            bigquery_client=bigquery_client,
            data=data,
            project_id=project_id,
            table_full_path=temp_table_full_path,
            create_table_if_not_exists=True,
            truncate_table_if_exists=True,
            max_job_errors_to_log=max_job_errors_to_log,
            schema=schema,
            pipelinemon=pipelinemon,
            logger=logger,
            print_out=print_out,
        )
        result.integrate_result(create_result)
        
        if not create_result.is_success:
            result.add_state("TEMP_TABLE_CREATION_FAILED")
            result.add_issue(f"Failed to create temp table: {create_result.get_final_report()}")
            result.final()
            return result

        # Merge tables
        result.add_state("MERGING_TABLES")
        merge_func_result:FunctionResult = merge_two_bigquery_tables_extended(
            bigquery_client=bigquery_client,
            project_id=project_id,
            target_table_full_path=table_full_path,
            source_table_full_path=temp_table_full_path,
            merge_key_columns=merge_key_columns,
            pipelinemon=pipelinemon,
            logger=logger,
            raise_e=raise_e,
            print_out=print_out
        )
        result.integrate_result(merge_func_result)

        # Final status based on merge result
        if merge_func_result.is_success:
            result.add_state("MERGE_COMPLETED")
        else:
            result.add_issue("MERGE_FAILED")
        result.final()

        # Log after finalizing
        log_by_lvl(
            info_msg=f"Merge operation completed for table {table_full_path}.",
            debug_msg=result.get_final_report(),
            logger=logger,
            print_out=print_out
        )
        if pipelinemon:
            pipelinemon.add_system_impacted(f"bigquery_merge: {table_full_path}")
            pipelinemon.add_log(StructLog(
                level=LogLevel.INFO,
                action=Action.PERSIST_MERGE_QUERY,
                resource=DataResource.DB_BIGQUERY,
                progress_status=result.progress_status,
                description=result.get_final_report()
            ))

    except Exception as e:
        handle_pipeline_operation_exception(
            e=e,
            result=result,
            action=Action.PERSIST_MERGE_QUERY,
            resource=DataResource.DB_BIGQUERY,
            logger=logger,
            pipelinemon=pipelinemon,
            print_out=print_out,
            raise_e=raise_e
        )
    finally:
        if temp_table_name:
            try:
                bigquery_client.delete_table(temp_table_full_path, not_found_ok=True)
                result.add_state("TEMP_TABLE_DELETED")
                msg=f"Temp table {temp_table_full_path} deleted."
                log_info(msg=msg, logger=logger, print_out=print_out)
                if pipelinemon:
                    pipelinemon.add_system_impacted(f"bigquery_delete_table: {temp_table_full_path}")
                    pipelinemon.add_log(StructLog(level=LogLevel.INFO, action=Action.PERSIST_DELETE_TABLE_TEMP, resource=DataResource.DB_BIGQUERY, progress_status=ProgressStatus.DONE, description=result.get_final_report()))
            except Exception as cleanup_e:

                result.add_warning(f"Failed to cleanup temp table: {cleanup_e}")
                log_warning(msg=f"Failed to cleanup temp table {temp_table_full_path}.", logger=logger, print_out=print_out)
                if pipelinemon:
                    pipelinemon.add_log(StructLog(level=LogLevel.WARNING, action=Action.PERSIST_DELETE_TABLE_TEMP, resource=DataResource.DB_BIGQUERY, progress_status=ProgressStatus.FAILED, description=result.get_final_report()))
        result.final()
    return result



def merge_two_bigquery_tables_extended(
    target_table_full_path: str,
    source_table_full_path: str,
    merge_key_columns: Union[str, List[str]],
    project_id: str,
    bigquery_client: Optional[bigquery.Client] = None,
    max_job_errors_to_log: int = 7,
    pipelinemon: Optional[Pipelinemon] = None,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    raise_e: bool = False
) -> FunctionResult:
    """Merges two BigQuery tables using a merge query.

    Args:
        target_table_full_path: Full path of target table
        source_table_full_path: Full path of source table
        merge_key_columns: Column(s) to use as merge keys
        project_id: GCP Project ID
        bigquery_client: Optional pre-initialized BigQuery client
        max_job_errors_to_log: Max number of job errors to include in logs
        pipelinemon: Optional pipeline monitoring object
        logger: Optional logger instance
        print_out: Whether to print output
        raise_e: Whether to raise exceptions

    Returns:
        FunctionResult with merge operation status
    """
    function_name = inspect.currentframe().f_code.co_name
    result = FunctionResult(function_name)
    result.add_metadata(
        project_id=project_id,
        target_table=target_table_full_path,
        source_table=source_table_full_path
    )
    try:
        if not bigquery_client:
            if not project_id:
                raise ValueError("project_id is required when bigquery_client is not provided.")
            bigquery_client = bigquery.Client(project=project_id)

        if isinstance(merge_key_columns, str):
            merge_key_columns = [merge_key_columns]
        merge_condition = " AND ".join([f"table1.{col} = table2.{col}" for col in merge_key_columns])
        merge_query = f"""
        MERGE `{target_table_full_path}` AS table1
        USING `{source_table_full_path}` AS table2
        ON {merge_condition}
        WHEN NOT MATCHED THEN
            INSERT ROW
        """
        result.add_state("MERGE_QUERY_STARTED")
        query_merge_job = bigquery_client.query(merge_query)
        query_merge_job.result()  # Wait for the merge to complete
        _handle_query_job_result(query_job=query_merge_job,
                                 result=result,
                                 action= Action.PERSIST_MERGE_QUERY,
                                 max_job_issues_to_log=max_job_errors_to_log, pipelinemon=pipelinemon, logger=logger)

            
    except Exception as e:
        handle_pipeline_operation_exception(
            e=e,
            result=result,
            action=Action.PERSIST_MERGE_QUERY,
            resource=DataResource.DB_BIGQUERY,
            logger=logger,
            pipelinemon=pipelinemon,
            print_out=print_out,
            raise_e=raise_e
        )
    finally:
        result.final()       
    return result


###########################################################################################
#################################### BIGQUERY WRITE QUERY FUNCTIONS ###############################
###########################################################################################




def write_query_to_bigquery_table_extended(
    project_id: str,
    query: str,
    bigquery_client: Optional[bigquery.Client] = None,
    pipelinemon: Optional[Pipelinemon] = None,
    max_job_errors_to_log: int = 7,
    print_out: bool = False,
    logger: Optional[logging.Logger] = None,
    raise_e: bool = False
) -> FunctionResult:
    """Executes a BigQuery SQL query that modifies data.

    Args:
        project_id: GCP Project ID
        query: SQL query string
        bigquery_client: Optional pre-initialized BigQuery client  
        pipelinemon: Optional pipeline monitoring object
        max_job_errors_to_log: Max number of job errors to include in logs
        print_out: Whether to print output
        logger: Optional logger instance
        raise_e: Whether to raise exceptions

    Returns:
        FunctionResult with query execution status
    """
    function_name = inspect.currentframe().f_code.co_name
    result = FunctionResult(function_name)
    result.add_metadata(project_id=project_id, query=query)
    try:
        # Validate inputs
        if not project_id:
            raise ValueError("project_id is required")
        if not query:
            raise ValueError("query cannot be empty")
            
        # Get or create client
        bigquery_client = bigquery_client or bigquery.Client(project=project_id)

        # Execute query
        result.add_state("QUERY_WRITE_STARTED")
        query_job = bigquery_client.query(query, project=project_id)
        query_job.result()
        
        _handle_query_job_result(query_job=query_job, result=result,
                                 action=Action.PERSIST_WRITE_QUERY,
                                 max_job_issues_to_log=max_job_errors_to_log,
                                 pipelinemon=pipelinemon,
                                 logger=logger)



    except Exception as e:
        handle_pipeline_operation_exception(
            e=e,
            result=result,
            action=Action.PERSIST_WRITE_QUERY,
            resource=DataResource.DB_BIGQUERY,
            logger=logger,
            pipelinemon=pipelinemon,
            raise_e=raise_e,
            print_out=print_out
        )
    finally:
        result.final()     
    return result


###########################################################################################
#################################### BIGQUERY READ QUERY FUNCTIONS ###############################
###########################################################################################

def read_query_bigquery_table_extended(
    project_id: str,
    query: str,
    bigquery_client: Optional[bigquery.Client] = None,
    max_job_errors_to_log: int = 7,
    pipelinemon: Optional[Pipelinemon] = None,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    raise_e: bool = False
) -> FunctionResult:
    """Executes a BigQuery SQL read query.

    Args:
        project_id: GCP Project ID
        query: SQL query string
        bigquery_client: Optional pre-initialized BigQuery client
        max_job_errors_to_log: Max number of job errors to include in logs
        pipelinemon: Optional pipeline monitoring object
        logger: Optional logger instance
        print_out: Whether to print output
        raise_e: Whether to raise exceptions

    Returns:
        FunctionResult containing query results
    """
    function_name = inspect.currentframe().f_code.co_name
    result = FunctionResult(function_name)
    result.add_metadata(project_id=project_id, query=query)

    try:
        # Input validation and client setup
        if not project_id or not query:
            raise ValueError("project_id and query are required")
        bigquery_client = bigquery_client or bigquery.Client(project=project_id)

        # Execute query
        result.add_state("QUERY_READ_STARTED")
        query_job = bigquery_client.query(query)
        rows = query_job.result()

        # Handle job result
        _handle_query_job_result(query_job=query_job,
                                 result=result,
                                 action=Action.READ_QUERY,
                                 rows=rows,
                                 max_job_issues_to_log=max_job_errors_to_log,
                                 pipelinemon=pipelinemon,
                                 logger=logger)

    except Exception as e:
        handle_pipeline_operation_exception(
            e=e,
            result=result,
            action=Action.READ_QUERY,
            resource=DataResource.DB_BIGQUERY,
            logger=logger,
            pipelinemon=pipelinemon,
            raise_e=raise_e,
            print_out=print_out
        )
    finally:
        result.final()
    return result


def read_query_for_rows_matching_dates_bigquery_extended(
    project_id: str,
    table_full_path: str,
    date_column: str,
    rows_list: Dict[str, Any],
    date_range: Optional[Tuple[Any, Any]] = None,
    max_job_errors_to_log: int = 7,
    bigquery_client: Optional[bigquery.Client] = None,
    pipelinemon: Optional[Pipelinemon] = None,
    logger: Optional[logging.Logger] = None,
    raise_e: bool = False,
    print_out: bool = False
) -> FunctionResult:
    """Queries BigQuery table for rows matching field values and optional date range.

    Args:
        project_id: GCP Project ID
        table_full_path: Full table path (project.dataset.table)
        date_column: Name of date column to filter
        rows_list: Dict of field names and values to match
        date_range: Optional (start_date, end_date) tuple
        max_job_errors_to_log: Max number of job errors to include in logs
        bigquery_client: Optional pre-initialized BigQuery client
        pipelinemon: Optional pipeline monitoring object
        logger: Optional logger instance
        raise_e: Whether to raise exceptions
        print_out: Whether to print output

    Returns:
        FunctionResult containing matching rows
    """
    function_name = inspect.currentframe().f_code.co_name
    result = FunctionResult(function_name)
    result.add_metadata(
        project_id=project_id,
        table_full_path=table_full_path,
        date_column=date_column
    )

    try:
        # Initialize client
        bigquery_client = bigquery_client or bigquery.Client(project=project_id)

        # Build the WHERE clause dynamically
        where_clauses = []
        query_parameters = []

        # Add field conditions
        for field, value in rows_list.items():
            where_clauses.append(f"{field} = @{field}")
            param_type=_convert_python_type_to_bigquery(value)
            query_parameters.append(bigquery.ScalarQueryParameter(field, param_type, value))

        # Add date range if provided
        if date_range:
            start_date, end_date = date_range
            column_type = _convert_python_type_to_bigquery(start_date or end_date )
            if start_date and end_date:
                where_clauses.append(f"{date_column} BETWEEN @start_date AND @end_date")
                query_parameters.extend([
                    bigquery.ScalarQueryParameter("start_date", column_type, start_date),
                    bigquery.ScalarQueryParameter("end_date", column_type, end_date)
                ])
            elif start_date:
                where_clauses.append(f"{date_column} >= @start_date")
                query_parameters.append(
                    bigquery.ScalarQueryParameter("start_date", column_type, start_date)
                )
            elif end_date:
                where_clauses.append(f"{date_column} <= @end_date")
                query_parameters.append(
                    bigquery.ScalarQueryParameter("end_date", column_type, end_date)
                )

    ####### RETURNING ONLY DATE COLUMN IN STRING FORMAT
        query = f"""
                SELECT 
                FORMAT_DATE('%Y-%m-%d', {date_column}) as {date_column}
                FROM `{table_full_path}`
                WHERE {" AND ".join(where_clauses)}
                ORDER BY {date_column} DESC
                """

#### EXAMPLE HOW IT WILL LOOK TRANSLATES:
# query = f"""SELECT date_id FROM `{table_full_path}`
#              WHERE asset_id = @asset_id AND date_id BETWEEN @records_oldest_date AND @records_recent_date  """
# job_config = bigquery.QueryJobConfig(
#                   query_parameters=[bigquery.ScalarQueryParameter("asset_id", "STRING", asset_id),
#                                    bigquery.ScalarQueryParameter("records_recent_date", "DATE", sourced_records_recent_date),
#                                    bigquery.ScalarQueryParameter("records_oldest_date", "DATE", sourced_records_oldest_date))   


        result.add_state("QUERY_READ_JOB_STARTED")
       
        query_read_job = bigquery_client.query(
                        query,
                        job_config=bigquery.QueryJobConfig(query_parameters=query_parameters),
                        project=project_id
                    )
        query_response_rows = query_read_job.result() # Wait for the job to complete
        _handle_query_job_result(query_job=query_read_job,
                                    result=result,
                                    action=Action.READ_QUERY,
                                    rows=query_response_rows,
                                    max_job_issues_to_log=max_job_errors_to_log,
                                    single_column=True,
                                    pipelinemon=pipelinemon,
                                    logger=logger)


    except Exception as e:
        handle_pipeline_operation_exception(
            e=e,
            result=result,
            action=Action.READ_QUERY,
            resource=DataResource.DB_BIGQUERY,
            logger=logger,
            pipelinemon=pipelinemon,
            print_out=print_out,
            raise_e=raise_e
        )
    finally:
        result.final()
    return result

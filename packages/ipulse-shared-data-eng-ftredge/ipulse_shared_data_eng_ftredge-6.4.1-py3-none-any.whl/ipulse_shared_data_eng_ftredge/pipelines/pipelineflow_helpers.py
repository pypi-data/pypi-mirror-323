import contextlib
from typing import Optional
import logging
from ipulse_shared_base_ftredge import LogLevel, AbstractResource, StructLog, ProgressStatus
from .pipelinemon import Pipelinemon
from .pipelineflow import PipelineTask

@contextlib.contextmanager
def task_validation_and_execution_context(task: PipelineTask, 
                         pipelinemon: Pipelinemon, 
                         generallogger: logging.Logger,
                         sequence_ref: Optional[str] = None,
                         intetionally_skip: bool = False):
    """Context manager for standardized task execution handling."""
    if intetionally_skip:
        generallogger.info(f"Task '{task.name}' is intentionally skipped.")
        yield False
        return
    if not task.validate_and_start(sequence_ref=sequence_ref):
        generallogger.warning(f"Task '{task.name}' failed validation. Final report: {task.final_report}")
        yield False
        return

    with pipelinemon.context(task.name):
        try:
            yield True
            task.final()

        except Exception as e:
            task.add_issue(str(e))

        finally:
            task.final()
            if task.final_log_level == LogLevel.ERROR:
                generallogger.warning(f"Task {task.name} FAILED. Final report: {task.final_report}")
                pipelinemon.add_log(StructLog(
                    level=LogLevel.ERROR,
                    resource=AbstractResource.PIPELINE_TASK,
                    progress_status=task.progress_status,
                    description=task.final_report
                ))
            elif task.final_log_level == LogLevel.WARNING:
                generallogger.warning(f"Task  has WARNINGS. Final report: {task.final_report}")
                pipelinemon.add_log(StructLog(
                    level=LogLevel.WARNING,
                    resource=AbstractResource.PIPELINE_TASK,
                    progress_status=task.progress_status,
                    description=task.final_report
                ))
            else:
                notices =""
                if task.final_log_level == LogLevel.NOTICE:
                    notices= f"NOTCES: {task.notices}"
                generallogger.info(f"Task '{task.name}' finished with Status: {task.progress_status}. {notices}")
                
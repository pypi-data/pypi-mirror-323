from osbot_utils.type_safe.Type_Safe import Type_Safe


class Flow_Run__Config(Type_Safe):
    add_task_to_self       : bool = True
    log_to_console         : bool = False
    log_to_memory          : bool = True
    logging_enabled        : bool = True
    print_logs             : bool = False
    print_none_return_value: bool = False
    print_finished_message : bool = False


def format_error(e: Exception) -> str:
    """
    Возвращает сообщение об ошибке с указанием файла и строки
    где исключение реально возникло (последний фрейм traceback).
    """
    import traceback

    tb = e.__traceback__
    if tb is None:
        return str(e)

    # Идём до последнего фрейма в цепочке
    while tb.tb_next is not None:
        tb = tb.tb_next

    filename = tb.tb_frame.f_code.co_filename
    lineno = tb.tb_lineno
    func = tb.tb_frame.f_code.co_name

    # Полный traceback для лога в консоль
    full_tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    print(full_tb)

    return f"{str(e)} | In_file: {filename}, line {lineno}, in {func}"

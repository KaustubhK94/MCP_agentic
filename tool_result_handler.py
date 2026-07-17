# tool_results_handler.py



from travel_state import TOOL_CONFIG, update_result


async def handle_tool_result(ctx, event):
    config = TOOL_CONFIG.get(event.tool_name)
    if config is None:
        return
    result_key = config.get("result_key")
    if result_key is None:
        return

    await update_result(
        ctx,
        result_key,
        event.tool_output.raw_output,
    )
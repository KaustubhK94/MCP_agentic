# tool_results_handler.py


from travel_state import update_result


async def handle_tool_result(ctx, event):
    await update_result(
        ctx,
        event.tool_name,
        event.tool_output.raw_output,
    )
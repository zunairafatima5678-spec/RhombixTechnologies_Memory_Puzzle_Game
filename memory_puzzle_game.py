
import asyncio
import random
from nicegui import ui

# Game settings
TOTAL_PAIRS = 6
TIME_LIMIT = 45

# Game state
state = {
    "cards": [],
    "revealed": [],
    "matched": [],
    "first_selection": None,
    "score": 0,
    "time_left": TIME_LIMIT,
    "is_locked": False,
    "game_over": False,
}

timer_event = None
container = None
grid_container = None
time_display = None
score_display = None


def start_game():
    global timer_event

    # Stop the previous timer
    if timer_event is not None:
        timer_event.cancel()
        timer_event = None

    # Create and shuffle cards
    emojis = ["🍎", "🍌", "🍇", "🍉", "🍓", "🍒"]
    state["cards"] = emojis[:TOTAL_PAIRS] * 2
    random.shuffle(state["cards"])

    # Reset game state
    state["revealed"] = [False] * len(state["cards"])
    state["matched"] = [False] * len(state["cards"])
    state["first_selection"] = None
    state["score"] = 0
    state["time_left"] = TIME_LIMIT
    state["is_locked"] = False
    state["game_over"] = False

    render_game_ui()
    timer_event = ui.timer(1.0, tick_timer)


def tick_timer():
    if state["game_over"]:
        return

    if state["time_left"] > 0:
        state["time_left"] -= 1

        if time_display is not None:
            time_display.text = (
                f"⏳ Time: {state['time_left']}s"
            )

    if state["time_left"] <= 0:
        state["game_over"] = True

        if timer_event is not None:
            timer_event.cancel()

        render_game_over(False)


async def handle_card_click(idx):
    if state["game_over"] or state["is_locked"]:
        return

    if state["revealed"][idx]:
        return

    # Reveal selected card
    state["revealed"][idx] = True
    first_idx = state["first_selection"]

    # First card
    if first_idx is None:
        state["first_selection"] = idx
        refresh_grid()
        return

    # Second card
    state["first_selection"] = None

    # Correct match
    if state["cards"][first_idx] == state["cards"][idx]:
        state["matched"][first_idx] = True
        state["matched"][idx] = True
        state["score"] += 1

        if score_display is not None:
            score_display.text = (
                f"🎯 Score: {state['score']} / {TOTAL_PAIRS}"
            )

        refresh_grid()

        # Win condition
        if state["score"] == TOTAL_PAIRS:
            state["game_over"] = True

            if timer_event is not None:
                timer_event.cancel()

            render_game_over(True)

    else:
        # Incorrect match
        state["is_locked"] = True
        refresh_grid()

        await asyncio.sleep(0.7)

        # Do not change the board if the game ended
        if state["game_over"]:
            return

        state["revealed"][first_idx] = False
        state["revealed"][idx] = False
        state["is_locked"] = False

        refresh_grid()


def refresh_grid():
    if grid_container is None:
        return

    grid_container.clear()

    with grid_container:
        for i, card in enumerate(state["cards"]):

            # Correctly matched cards
            if state["matched"][i]:
                ui.button(card).classes(
                    "w-20 h-20 text-3xl font-bold rounded-xl "
                    "bg-emerald-800 text-white shadow-md"
                ).props("disable")

            # Revealed cards: dark background, colorful fruit
            elif state["revealed"][i]:
                ui.button(card).classes(
                    "w-20 h-20 text-3xl font-bold rounded-xl "
                    "bg-slate-800 text-white shadow-md"
                ).props("disable")

            # Hidden cards: blue background
            else:
                ui.button(
                    "❓",
                    on_click=lambda idx=i: handle_card_click(idx)
                ).classes(
                    "w-20 h-20 text-3xl font-bold rounded-xl "
                    "bg-sky-600 text-white "
                    "hover:bg-sky-500 shadow-md cursor-pointer"
                )


def render_start_screen():
    container.clear()

    with container:
        ui.label("🧩 Memory Puzzle Game").classes(
            "text-4xl font-bold my-8 text-cyan-400"
        )

        ui.label(
            "Match the fruit pairs and test your memory "
            "before time runs out!"
        ).classes(
            "text-gray-300 text-lg mb-6 text-center"
        )

        ui.button(
            "START GAME",
            on_click=start_game
        ).classes(
            "bg-sky-600 text-white font-bold px-10 py-4 text-xl "
            "rounded-xl hover:bg-sky-500 shadow-lg cursor-pointer"
        )


def render_game_ui():
    global grid_container, time_display, score_display

    container.clear()

    with container:
        ui.label("🧩 Memory Puzzle Game").classes(
            "text-3xl font-bold mt-4 text-cyan-400"
        )

        ui.label(
            "Match the pairs within the given time limit!"
        ).classes(
            "text-gray-300 text-base mb-6 text-center"
        )

        # Cards grid
        grid_container = ui.element("div").classes(
            "grid grid-cols-3 gap-4 justify-center my-2"
        )

        refresh_grid()

        # Status bar
        with ui.element("div").classes(
            "flex justify-around items-center w-80 "
            "bg-gray-900 p-4 rounded-xl border "
            "border-gray-800 my-4"
        ):
            time_display = ui.label(
                f"⏳ Time: {state['time_left']}s"
            ).classes(
                "font-bold text-cyan-400 text-lg"
            )

            score_display = ui.label(
                f"🎯 Score: {state['score']} / {TOTAL_PAIRS}"
            ).classes(
                "font-bold text-emerald-400 text-lg"
            )

        ui.button(
            "Restart Game",
            on_click=start_game
        ).classes(
            "bg-gray-700 text-white px-6 py-2 "
            "rounded-lg hover:bg-gray-600 cursor-pointer"
        )


def render_game_over(is_win):
    container.clear()

    with container:
        ui.label("🧩 Memory Puzzle Game").classes(
            "text-3xl font-bold mt-6 text-cyan-400 mb-6"
        )

        if is_win:
            ui.label(
                "🎉 Congratulations! You matched all pairs!"
            ).classes(
                "text-green-400 text-xl font-bold mb-6 text-center"
            )
        else:
            ui.label(
                "⏰ Time's up! Game Over."
            ).classes(
                "text-red-400 text-xl font-bold mb-6 text-center"
            )

        ui.label(
            f"Final Score: {state['score']} / {TOTAL_PAIRS}"
        ).classes("text-white text-lg mb-6")

        ui.button(
            "PLAY AGAIN",
            on_click=start_game
        ).classes(
            "bg-emerald-600 text-white font-bold px-8 py-3 "
            "text-lg rounded-xl hover:bg-emerald-500 "
            "shadow-lg cursor-pointer"
        )


# Styling
ui.add_head_html("""
<style>
    body {
        background-color: #0e1117;
        color: white;
        font-family: Arial, sans-serif;
    }
</style>
""")

# Main layout
with ui.element("div").classes(
    "w-full flex flex-col items-center justify-center min-h-screen"
) as main_container:
    container = main_container

render_start_screen()

ui.run(port=8082, reload=False)

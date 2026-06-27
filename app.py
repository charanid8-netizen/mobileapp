import flet as ft
import time, asyncio, random, threading, json, os

def main(page: ft.Page):
    page.title = "Multi-tool App"
    page.theme_mode = "light"

    # ---------------- Stopwatch ----------------
    stopwatch_text = ft.Text("00:00:00")
    running = False
    start_time = 0
    elapsed = 0

    async def update_stopwatch():
        nonlocal elapsed
        while running:
            elapsed = time.time() - start_time
            h, m, s = int(elapsed // 3600), int((elapsed % 3600) // 60), int(elapsed % 60)
            stopwatch_text.value = f"{h:02}:{m:02}:{s:02}"
            page.update()
            await asyncio.sleep(1)

    def start_stopwatch(e):
        nonlocal running, start_time
        if not running:
            running = True
            start_time = time.time() - elapsed
            page.run_task(update_stopwatch)

    def stop_stopwatch(e):
        nonlocal running
        running = False

    def reset_stopwatch(e):
        nonlocal running, elapsed
        running = False
        elapsed = 0
        stopwatch_text.value = "00:00:00"
        page.update()

    stopwatch_tab = ft.Column([
        ft.Text("Stopwatch", size=20, weight=ft.FontWeight.BOLD),
        stopwatch_text,
        ft.Row([
            ft.Button("Start", on_click=start_stopwatch),
            ft.Button("Stop", on_click=stop_stopwatch),
            ft.Button("Reset", on_click=reset_stopwatch),
        ])
    ])

    # ---------------- To-do ----------------
    TASKS_FILE = "tasks.json"
    todo_list = ft.ListView(expand=True)
    todo_input = ft.TextField(hint_text="Add task")

    def load_tasks():
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r") as f:
                data = json.load(f)
                for item in data:
                    add_task(None, item["label"], item["done"])

    def save_tasks():
        data = []
        for row in todo_list.controls:
            checkbox = row.controls[0]
            data.append({"label": checkbox.label, "done": checkbox.value})
        with open(TASKS_FILE, "w") as f:
            json.dump(data, f)

    def add_task(e, label=None, done=False):
        text = label if label else todo_input.value.strip()
        if text:
            task_checkbox = ft.Checkbox(label=text, value=done)

            def remove_task(ev):
                todo_list.controls.remove(task_row)
                save_tasks()
                page.update()

            def mark_done(ev):
                if task_checkbox.value:
                    task_checkbox.label_style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                else:
                    task_checkbox.label_style = None
                save_tasks()
                page.update()

            task_checkbox.on_change = mark_done
            delete_btn = ft.IconButton(icon=ft.icons.Icons.DELETE, on_click=remove_task)

            task_row = ft.Row([task_checkbox, delete_btn])
            todo_list.controls.append(task_row)

            if not label:
                todo_input.value = ""
            save_tasks()
            page.update()

    def clear_all(e):
        todo_list.controls.clear()
        save_tasks()
        page.update()

    todo_tab = ft.Column([
        ft.Text("To‑do List", size=20, weight=ft.FontWeight.BOLD),
        todo_input,
        ft.Row([
            ft.Button("Add", on_click=add_task),
            ft.Button("Clear All", on_click=clear_all),
        ]),
        todo_list
    ])
    load_tasks()

    # ---------------- Calculator ----------------
    calc_input = ft.Text(value="")
    calc_result = ft.Text("")

    def handle(symbol):
        if symbol == "C":
            calc_input.value = ""
            calc_result.value = ""
        elif symbol == "=":
            try:
                calc_result.value = str(eval(calc_input.value))
            except Exception:
                calc_result.value = "Error"
        else:
            calc_input.value += symbol
        page.update()

    buttons = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", "C", "=", "+"]
    ]

    grid = ft.Column([
        ft.Row([ft.Button(b, on_click=lambda e, s=b: handle(s), width=60, height=50) for b in row])
        for row in buttons
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=5)

    calc_tab = ft.Container(
        content=ft.Column(
            [
                ft.Text("Calculator", size=22, weight=ft.FontWeight.BOLD),
                calc_input,
                grid,
                calc_result
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        expand=True,
        alignment=ft.Alignment(0, 0)
    )

    # ---------------- Catch Game ----------------
    catch_score = 0
    time_left = 10
    game_over = True
    catch_text = ft.Text("Score:0", size=16)
    timer_text = ft.Text("Press start to play", size=16, weight=ft.FontWeight.BOLD)

    def move_button_randomly():
        catch_btn.top = random.randint(20, 230)
        catch_btn.left = random.randint(20, 220)

    def catch(e):
        nonlocal catch_score, game_over
        if game_over:
            return
        catch_score += 1
        catch_text.value = f"Caught! Score: {catch_score}"
        move_button_randomly()
        page.update()

    catch_btn = ft.Button("Catch me!", on_click=catch, left=100, top=150, visible=False)
    catch_game_area = ft.Stack([catch_btn], width=300, height=300)

    def game_loop():
        nonlocal time_left, game_over, catch_score
        while time_left > 0:
            time.sleep(1)
            time_left -= 1
            try:
                timer_text.value = f"Time left: {time_left}s"
                if time_left > 0:
                    move_button_randomly()
                page.update()
            except Exception:
                break
        try:
            game_over = True
            catch_btn.visible = False
            start_btn.visible = True
            timer_text.value = "⏰ Time is up!"
            catch_text.value = f"⏰ Final score: {catch_score} points!"
            page.update()
        except Exception:
            pass

    def start_game(e):
        nonlocal catch_score, time_left, game_over
        catch_score = 0
        time_left = 10
        game_over = False
        catch_text.value = "Score:0"
        timer_text.value = "Time left:10s"
        catch_btn.visible = True
        start_btn.visible = False
        move_button_randomly()
        page.update()
        threading.Thread(target=game_loop, daemon=True).start()

    start_btn = ft.Button("▶ Start Game", on_click=start_game)
    catch_game = ft.Column([
        ft.Text("Catch Game", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([catch_text, timer_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
        start_btn,
        catch_game_area
    ], spacing=5, alignment=ft.MainAxisAlignment.START)

    catch_tab = ft.Container(content=catch_game, expand=True, padding=10)

    # ---------------- Guessing Game ----------------
    secret_number = random.randint(1, 100)
    guess_input = ft.TextField(hint_text="Enter guess (1-100)")
    guess_result = ft.Text("")

    def check_guess(e):
        nonlocal secret_number
        try:
            g = int(guess_input.value)
            if g == secret_number:
                guess_result.value = "Correct! New number generated."
                secret_number = random.randint(1, 100)
            elif g < secret_number:
                guess_result.value = "Too low!"
            else:
                guess_result.value = "Too high!"
        except:
            guess_result.value = "Enter a valid number."
        page.update()

    guess_btn = ft.Button("Guess", on_click=check_guess)
    guessing_game = ft.Column([
        ft.Text("Guessing Game", size=18, weight=ft.FontWeight.BOLD),
        guess_input,
        guess_btn,
        guess_result
    ], spacing=5, alignment=ft.MainAxisAlignment.START)

    guess_tab = ft.Container(content=guessing_game, expand=True, padding=10)

       # ---------------- Navigation ----------------
    views = [stopwatch_tab, todo_tab, calc_tab, catch_tab, guess_tab]
    current_view = ft.Container(content=views[0], expand=True)

    def change_view(e):
        current_view.content = views[e.control.selected_index]
        page.update()

    nav = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.icons.Icons.ACCESS_ALARM, label="Stopwatch"),
            ft.NavigationBarDestination(icon=ft.icons.Icons.CHECKLIST, label="To-do"),
            ft.NavigationBarDestination(icon=ft.icons.Icons.CALCULATE, label="Calculator"),
            ft.NavigationBarDestination(icon=ft.icons.Icons.TOUCH_APP, label="Catch Game"),
            ft.NavigationBarDestination(icon=ft.icons.Icons.PSYCHOLOGY, label="Guess Game"),
        ],
        on_change=change_view,
    )

    # Add everything to the page
    page.add(current_view, nav)

# ---------------- Run the app ----------------
ft.run(main)

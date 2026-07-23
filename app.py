import flet as ft
import time, asyncio, random, threading, json, os

def main(page: ft.Page):
    page.title = "Multi-tool App"
    page.theme_mode = "light"

    # ---------------- Stopwatch ---------------- 
    stopwatch_text = ft.Text(
    "00:00:00",
    size=70,                      
    weight=ft.FontWeight.BOLD,
    color="blue"
)
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

    def pause_stopwatch(e):
        nonlocal running
        running = False   

    def stop_stopwatch(e):
        nonlocal running
        running = False    

    def reset_stopwatch(e):
        nonlocal running, elapsed
        running = False
        elapsed = 0
        stopwatch_text.value = "00:00:00"
        page.update()
# ---- Stopwatch tab ----
    stopwatch_tab = ft.Column([
        ft.Text("Stopwatch", size=24, weight=ft.FontWeight.BOLD),
        stopwatch_text,
        ft.Row([
        ft.Button("Start", on_click=start_stopwatch),
        ft.Button("Pause", on_click=pause_stopwatch),
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
   #------------------------Calculator-----------------------------
    import math
    calc_input = ft.Text(value="", size=20, weight=ft.FontWeight.NORMAL)
    calc_result = ft.Text(
        "",
        size=24,
        weight=ft.FontWeight.BOLD,
        color="blue",   # highlight answer
        selectable=True
    )

    # Handle button clicks
    def handle(symbol):
        if symbol == "C":
            calc_input.value = ""
            calc_result.value = ""
        elif symbol == "=":
            try:
                calc_result.value = str(eval(calc_input.value))
            except Exception:
                calc_result.value = "Error"
        elif symbol == "⌫":
            calc_input.value = calc_input.value[:-1]
        elif symbol == "√":
            try:
                calc_result.value = str(math.sqrt(float(calc_input.value)))
            except Exception:
                calc_result.value = "Error"
        elif symbol == "^":
            calc_input.value += "**"  
        elif symbol == "!":
            try:
                n = int(calc_input.value)
                calc_result.value = str(math.factorial(n))
            except Exception:
                calc_result.value = "Error"
        else:
            calc_input.value += symbol
        page.update()

    # Buttons layout
    buttons = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", ".", "=", "+"],
        ["(", ")", "%", "⌫"],
        ["C", "√", "^", "!"]
    ]

    # Build grid
    grid = ft.Column([
        ft.Row([
            ft.Button(
                b,
                on_click=lambda e, s=b: handle(s),
                width=60,
                height=50
            ) for b in row
        ])
        for row in buttons
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=5)

    # Calculator tab container
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
    difficulty = "easy"

    catch_text = ft.Text("Score:0", size=16)
    timer_text = ft.Text("Press start to play", size=16, weight=ft.FontWeight.BOLD)

  
    def set_difficulty(e):
        nonlocal difficulty
        difficulty = e.control.value
        print("Difficulty changed to:", difficulty)
        timer_text.value = f"Difficulty set to {difficulty}"
        page.update()
        
    difficulty_dropdown = ft.Dropdown(
        value="easy",
    options=[
        ft.dropdown.Option("easy"),
        ft.dropdown.Option("medium"),
        ft.dropdown.Option("hard")
    ],
    
    on_select = set_difficulty,
)
    #difficulty_dropdown.on_select = set_difficulty
    
    def move_button_randomly():
        catch_btn.top = random.randint(20, 230)
        catch_btn.left = random.randint(20, 220)
    def catch(e):
        global catch_score, game_over
        if game_over:
            return
        catch_score += 1
        catch_text.value = f"Caught! Score: {catch_score}"
        move_button_randomly()
        page.update()

    catch_btn = ft.Button("Catch 😜 me!", on_click=catch, left=100, top=150, visible=False)
    catch_game_area = ft.Stack([catch_btn], width=300, height=300)

    def start_game(e):
        global catch_score, time_left, game_over
        catch_score = 0
        game_over = False
        catch_text.value = "Score:0"
        difficulty = difficulty_dropdown.value

        print(f'i am checking menu value : {difficulty}')
        if difficulty == "easy":
            time_left = 15
        elif difficulty == "medium":
            time_left = 10
        else:
            time_left = 5
         
        timer_text.value = f"Time left:{time_left}s"
        catch_btn.visible = True
        start_btn.visible = False
        move_button_randomly()
        page.update()
        threading.Thread(target=game_loop, daemon=True).start()

    start_btn = ft.Button("▶ Start Game", on_click=start_game)
    def game_loop():
        global time_left, game_over, catch_score

        if difficulty == "easy":
            move_interval = 1.0
        elif difficulty == "medium":
            move_interval = 0.7
        else:
            move_interval = 0.4

        last_move = time.time()

        while time_left > 0:
            time.sleep(1)
            time_left -= 1

            if time.time() - last_move >= move_interval:
                move_button_randomly()
                last_move = time.time()

            timer_text.value = f"Time left: {time_left}s"
            page.update()
        game_over = True
        catch_btn.visible = False
        start_btn.visible = True
        timer_text.value = "⏰ Time is up!"
        catch_text.value = f"⏰ Final score: {catch_score} points!"
        page.update()


    catch_game = ft.Column([
    ft.Text("Catch Game", size=18, weight=ft.FontWeight.BOLD),
    ft.Row([catch_text, timer_text],
           alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
           width=400),
    difficulty_dropdown,
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

    # ---------------- Calendar ----------------
    import pytz
    from datetime import datetime
    calendar_output = ft.Text()

    def show_date(e):
        ist = pytz.timezone("Asia/Kolkata")
        picked = e.control.value
        if isinstance(picked, datetime):
            picked_ist = picked.astimezone(ist)
            calendar_output.value = picked_ist.strftime("%d %B %Y")
        else:
            calendar_output.value = str(picked)
        page.update()
    calendar_picker = ft.DatePicker(on_change=show_date)
    def open_picker(e):
        page.show_dialog(calendar_picker)

    calendar_tab = ft.Column([
        ft.Text("Calendar", size=22, weight=ft.FontWeight.BOLD),
        ft.Button("Pick a date", on_click=open_picker),
        calendar_output
    ])

       # ---------------- Navigation ----------------
    views = [stopwatch_tab, todo_tab, calc_tab, calendar_tab, catch_tab, guess_tab]
    current_view = ft.Container(content=views[0], expand=True)

    def change_view(e):
        current_view.content = views[e.control.selected_index]
        page.update()

    nav = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.icons.Icons.ACCESS_ALARM, label="Stopwatch"),
            ft.NavigationBarDestination(icon=ft.icons.Icons.CHECKLIST, label="To-do"),
            ft.NavigationBarDestination(icon=ft.icons.Icons.CALCULATE, label="Calculator"),
            ft.NavigationBarDestination(icon=ft.icons.Icons.CALENDAR_MONTH, label="Calendar"),
            ft.NavigationBarDestination(icon=ft.icons.Icons.TOUCH_APP, label="Catch Game"),
            ft.NavigationBarDestination(icon=ft.icons.Icons.PSYCHOLOGY, label="Guess Game")
        ],
        on_change=change_view,
    )

    # Add everything to the page
    page.add(current_view, nav)

# ---------------- Run the app ----------------
ft.run(main)

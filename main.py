import sys
from blinker import Signal
import utility
import time

event = Signal('change_status')
stat = False

def AutoClicker(correct_star_percentage=0.6, click_the_freeze_button=False): 
    try: 
        correct_star_percentage = float(correct_star_percentage)
        click_the_freeze_button = bool(click_the_freeze_button)

        if correct_star_percentage > 0 and click_the_freeze_button is not None:
            keywords1 = ["Blum", "Telegram"]
            windows1 = utility.list_windows_by_title(keywords1)

            filtered_windows1 = [index for index, (string, _) in enumerate(windows1) if string == 'TelegramDesktop']

            if len(filtered_windows1) > 0:
                hwnd1 = windows1[filtered_windows1[0]][1]

                target_colors_hex = ["#c9e100", "#bae70e"]
                nearby_colors_hex = ["#abff61", "#87ff27"]
                threshold = 0.8
                auto_clicker = utility.AutoClicker(hwnd1, target_colors_hex, nearby_colors_hex, threshold, correct_star_percentage, click_the_freeze_button)
                
                try:
                    auto_clicker.click_color_areas()
                    global stat
                    stat = auto_clicker.running

                    def on_event():
                        global stat
                        stat = not auto_clicker.running
                        auto_clicker.toggle_script()

                    event.connect(on_event)

                except Exception as e:
                    for i in reversed(range(5)):
                        time.sleep(1)
    except ValueError:
        raise ValueError(f"Invalid value for correct_star_percentage: {correct_star_percentage}")

if __name__ == "__main__":
    speed = sys.argv[1]
    pause = sys.argv[2]
    AutoClicker(speed, pause)
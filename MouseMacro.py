import tkinter as tk
from tkinter import ttk, messagebox

import pyautogui
import keyboard
import pickle
import time
import threading

import win32api
import win32gui


# ============================================================
# 화면에 좌표 위치 사각형 표시
# ============================================================
class Draw:
    def __init__(self, root):
        self.root = root
        self.markers = []

    def clear(self):
        for marker in self.markers:
            try:
                marker.destroy()
            except:
                pass

        self.markers.clear()

    def make_line(self, x, y, w, h):
        """초록색 선 하나 생성"""

        line = tk.Toplevel(self.root)

        # 테두리 없는 창
        line.overrideredirect(True)

        # 항상 위
        line.attributes("-topmost", True)

        # 초록색
        line.configure(bg="lime")

        # 위치와 크기
        line.geometry(
            f"{w}x{h}+{x}+{y}"
        )

        # 창 생성 반영
        line.update_idletasks()

        hwnd = line.winfo_id()

        # ------------------------------------------------
        # 마우스 클릭 통과
        # ------------------------------------------------
        GWL_EXSTYLE = -20

        WS_EX_TRANSPARENT = 0x00000020
        WS_EX_TOOLWINDOW = 0x00000080
        WS_EX_NOACTIVATE = 0x08000000

        style = win32gui.GetWindowLong(
            hwnd,
            GWL_EXSTYLE
        )

        win32gui.SetWindowLong(
            hwnd,
            GWL_EXSTYLE,
            style
            | WS_EX_TRANSPARENT
            | WS_EX_TOOLWINDOW
            | WS_EX_NOACTIVATE
        )

        self.markers.append(line)

    def rect(
        self,
        x,
        y,
        w=25,
        h=25,
        thickness=2
    ):

        left = x - w // 2
        top = y - h // 2

        # ──────────────
        # 위쪽
        # ──────────────
        self.make_line(
            left,
            top,
            w,
            thickness
        )

        # ──────────────
        # 아래쪽
        # ──────────────
        self.make_line(
            left,
            top + h - thickness,
            w,
            thickness
        )

        # │ 왼쪽
        self.make_line(
            left,
            top,
            thickness,
            h
        )

        # │ 오른쪽
        self.make_line(
            left + w - thickness,
            top,
            thickness,
            h
        )


# ============================================================
# GUI 프로그램
# ============================================================
class MacroGUI:
    def __init__(self, root):
        self.root = root

        self.root.title("마우스 매크로")
        self.root.geometry("820x620")
        self.root.resizable(False, False)

        # PyAutoGUI 설정
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0

        # 데이터
        # (x, y, delay, event, clicks)
        self.data = []

        # 매크로 실행 여부
        self.running = False

        # 좌표 등록 대기 여부
        self.capture_waiting = False

        # 좌표 등록 시 사용할 설정값
        self.capture_delay = 1.0
        self.capture_event = "cl"
        self.capture_clicks = 1

        # 화면 그리기
        self.drawer = Draw(self.root)

        # GUI 생성
        self.create_gui()

        # Ctrl 키 감지
        self.ctrl_hook = keyboard.on_press_key(
            "ctrl",
            self.ctrl_pressed
        )

        # ESC 키 감지
        self.esc_hook = keyboard.on_press_key(
            "esc",
            self.esc_pressed
        )

        # 창 종료 이벤트
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

    # ========================================================
    # GUI 구성
    # ========================================================
    def create_gui(self):

        # ----------------------------------------------------
        # 제목
        # ----------------------------------------------------
        title_label = ttk.Label(
            self.root,
            text="마우스 매크로 설정",
            font=("맑은 고딕", 16, "bold")
        )

        title_label.pack(
            pady=(15, 5)
        )

        # ----------------------------------------------------
        # 좌표 목록
        # ----------------------------------------------------
        list_frame = ttk.LabelFrame(
            self.root,
            text="등록된 좌표"
        )

        list_frame.pack(
            padx=15,
            pady=10,
            fill="both",
            expand=True
        )

        columns = (
            "num",
            "x",
            "y",
            "delay",
            "event",
            "clicks"
        )

        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=12,
            selectmode="extended"
        )

        self.tree.heading(
            "num",
            text="#"
        )

        self.tree.heading(
            "x",
            text="X"
        )

        self.tree.heading(
            "y",
            text="Y"
        )

        self.tree.heading(
            "delay",
            text="지연 시간"
        )

        self.tree.heading(
            "event",
            text="이벤트"
        )

        self.tree.heading(
            "clicks",
            text="클릭 횟수"
        )

        self.tree.column(
            "num",
            width=50,
            anchor="center"
        )

        self.tree.column(
            "x",
            width=100,
            anchor="center"
        )

        self.tree.column(
            "y",
            width=100,
            anchor="center"
        )

        self.tree.column(
            "delay",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "event",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "clicks",
            width=100,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(5, 0),
            pady=5
        )

        scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 5),
            pady=5
        )

        # ----------------------------------------------------
        # 좌표 설정
        # ----------------------------------------------------
        setting_frame = ttk.LabelFrame(
            self.root,
            text="좌표 설정"
        )

        setting_frame.pack(
            padx=15,
            pady=5,
            fill="x"
        )

        # 지연 시간
        ttk.Label(
            setting_frame,
            text="지연 시간"
        ).grid(
            row=0,
            column=0,
            padx=(15, 5),
            pady=12
        )

        self.delay_entry = ttk.Entry(
            setting_frame,
            width=10
        )

        self.delay_entry.insert(
            0,
            "1"
        )

        self.delay_entry.grid(
            row=0,
            column=1,
            padx=5
        )

        ttk.Label(
            setting_frame,
            text="초"
        ).grid(
            row=0,
            column=2,
            padx=(0, 15)
        )

        # 이벤트
        ttk.Label(
            setting_frame,
            text="이벤트"
        ).grid(
            row=0,
            column=3,
            padx=5
        )

        self.event_combo = ttk.Combobox(
            setting_frame,
            values=[
                "좌클릭",
                "우클릭"
            ],
            state="readonly",
            width=10
        )

        self.event_combo.current(0)

        self.event_combo.grid(
            row=0,
            column=4,
            padx=5
        )

        # 클릭 횟수
        ttk.Label(
            setting_frame,
            text="클릭 횟수"
        ).grid(
            row=0,
            column=5,
            padx=(15, 5)
        )

        self.click_entry = ttk.Entry(
            setting_frame,
            width=10
        )

        self.click_entry.insert(
            0,
            "1"
        )

        self.click_entry.grid(
            row=0,
            column=6,
            padx=5
        )

        # ----------------------------------------------------
        # 좌표 관리 버튼
        # ----------------------------------------------------
        coordinate_button_frame = ttk.Frame(
            self.root
        )

        coordinate_button_frame.pack(
            padx=15,
            pady=8,
            fill="x"
        )

        self.capture_btn = ttk.Button(
            coordinate_button_frame,
            text="좌표 추가",
            command=self.capture_position
        )

        self.capture_btn.pack(
            side="left",
            padx=5
        )

        ttk.Button(
            coordinate_button_frame,
            text="선택 삭제",
            command=self.delete_selected
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            coordinate_button_frame,
            text="전체 삭제",
            command=self.clear_all
        ).pack(
            side="left",
            padx=5
        )

        ttk.Separator(
            coordinate_button_frame,
            orient="vertical"
        ).pack(
            side="left",
            fill="y",
            padx=10
        )

        ttk.Button(
            coordinate_button_frame,
            text="저장",
            command=self.save_setting
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            coordinate_button_frame,
            text="불러오기",
            command=self.load_setting
        ).pack(
            side="left",
            padx=5
        )

        # ----------------------------------------------------
        # 실행 버튼
        # ----------------------------------------------------
        run_frame = ttk.Frame(
            self.root
        )

        run_frame.pack(
            padx=15,
            pady=8,
            fill="x"
        )

        self.start_btn = ttk.Button(
            run_frame,
            text="▶ 매크로 시작",
            command=self.start_macro
        )

        self.start_btn.pack(
            side="left",
            padx=5
        )

        self.stop_btn = ttk.Button(
            run_frame,
            text="■ 매크로 중지",
            command=self.stop_macro,
            state="disabled"
        )

        self.stop_btn.pack(
            side="left",
            padx=5
        )

        # ----------------------------------------------------
        # 상태
        # ----------------------------------------------------
        self.status_label = ttk.Label(
            self.root,
            text="대기 중"
        )

        self.status_label.pack(
            padx=20,
            pady=(3, 12),
            anchor="w"
        )

    # ========================================================
    # 좌표 추가 버튼
    # ========================================================
    def capture_position(self):

        # 이미 좌표 등록 대기 중이면 취소
        if self.capture_waiting:
            self.capture_waiting = False

            self.capture_btn.config(
                text="좌표 추가"
            )

            self.status_label.config(
                text="좌표 등록이 취소되었습니다."
            )

            return

        try:
            delay = float(
                self.delay_entry.get()
            )

            clicks = int(
                self.click_entry.get()
            )

            if delay < 0:
                raise ValueError

            if clicks <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "입력 오류",
                "지연 시간과 클릭 횟수를 확인하세요."
            )

            return

        # 좌클릭 / 우클릭 변환
        if self.event_combo.get() == "좌클릭":
            event = "cl"
        else:
            event = "cr"

        # 현재 설정값 저장
        self.capture_delay = delay
        self.capture_event = event
        self.capture_clicks = clicks

        # Ctrl 입력 대기
        self.capture_waiting = True

        self.capture_btn.config(
            text="좌표 등록 취소"
        )

        self.status_label.config(
            text="마우스를 원하는 위치로 이동한 후 Ctrl 키를 누르세요."
        )

    # ========================================================
    # Ctrl 눌렀을 때
    # ========================================================
    def ctrl_pressed(self, event):

        # 좌표 추가 상태가 아니면 무시
        if not self.capture_waiting:
            return

        # 중복 입력 방지
        self.capture_waiting = False

        # 현재 마우스 위치
        position = pyautogui.position()

        x = position.x
        y = position.y

        # 데이터 추가
        self.data.append(
            (
                x,
                y,
                self.capture_delay,
                self.capture_event,
                self.capture_clicks
            )
        )

        # GUI 업데이트는 Tkinter 메인 스레드에서
        self.root.after(
            0,
            lambda: self.capture_finished(
                x,
                y
            )
        )

    # ========================================================
    # 좌표 등록 완료
    # ========================================================
    def capture_finished(self, x, y):

        self.refresh_tree()

        self.capture_btn.config(
            text="좌표 추가"
        )

        self.status_label.config(
            text=f"좌표 등록 완료: X={x}, Y={y}"
        )

    # ========================================================
    # ESC 키
    # ========================================================
    def esc_pressed(self, event):

        # 좌표 등록 중이면 등록 취소
        if self.capture_waiting:

            self.capture_waiting = False

            self.root.after(
                0,
                self.cancel_capture
            )

        # 매크로 실행 중이면 중지
        if self.running:
            self.running = False

    def cancel_capture(self):

        self.capture_btn.config(
            text="좌표 추가"
        )

        self.status_label.config(
            text="좌표 등록이 취소되었습니다."
        )

    # ========================================================
    # 리스트 새로고침
    # ========================================================
    def refresh_tree(self):

        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 다시 입력
        for index, item in enumerate(
            self.data,
            start=1
        ):

            x, y, delay, event, clicks = item

            if event == "cl":
                event_text = "좌클릭"
            elif event == "cr":
                event_text = "우클릭"
            else:
                event_text = event

            self.tree.insert(
                "",
                "end",
                values=(
                    index,
                    x,
                    y,
                    delay,
                    event_text,
                    clicks
                )
            )
        
        # 화면의 좌표 표시도 새로 갱신
        self.refresh_markers()
    
    def refresh_markers(self):

        # 기존 네모 모두 삭제
        self.drawer.clear()

        # 현재 등록된 모든 좌표에 네모 생성
        for item in self.data:

            x = item[0]
            y = item[1]

            self.drawer.rect(
                x,
                y,
                25,
                25
            )

    # ========================================================
    # 선택한 좌표 삭제
    # ========================================================
    def delete_selected(self):

        selected = self.tree.selection()

        if not selected:
            messagebox.showinfo(
                "알림",
                "삭제할 좌표를 선택하세요."
            )
            return

        indexes = []

        for tree_item in selected:

            values = self.tree.item(
                tree_item,
                "values"
            )

            index = int(
                values[0]
            ) - 1

            indexes.append(index)

        # 뒤에서부터 삭제해야 인덱스가 안 꼬임
        for index in sorted(
            indexes,
            reverse=True
        ):
            del self.data[index]

        self.refresh_tree()

        self.status_label.config(
            text="선택한 좌표를 삭제했습니다."
        )

    # ========================================================
    # 전체 삭제
    # ========================================================
    def clear_all(self):

        if not self.data:
            return

        result = messagebox.askyesno(
            "전체 삭제",
            "등록된 모든 좌표를 삭제할까요?"
        )

        if not result:
            return

        self.data.clear()

        self.refresh_tree()

        self.status_label.config(
            text="모든 좌표를 삭제했습니다."
        )

    # ========================================================
    # 설정 저장
    # ========================================================
    def save_setting(self):

        try:
            with open(
                "setting.txt",
                "wb"
            ) as file:

                pickle.dump(
                    self.data,
                    file
                )

            self.status_label.config(
                text="setting.txt 저장 완료"
            )

        except Exception as e:

            messagebox.showerror(
                "저장 오류",
                str(e)
            )

    # ========================================================
    # 설정 불러오기
    # ========================================================
    def load_setting(self):

        try:
            with open(
                "setting.txt",
                "rb"
            ) as file:

                loaded_data = pickle.load(
                    file
                )

            self.data = loaded_data

            self.refresh_tree()

            self.status_label.config(
                text="setting.txt 불러오기 완료"
            )

        except FileNotFoundError:

            messagebox.showwarning(
                "파일 없음",
                "setting.txt 파일이 없습니다."
            )

        except Exception as e:

            messagebox.showerror(
                "불러오기 오류",
                str(e)
            )

    # ========================================================
    # 매크로 시작
    # ========================================================
    def start_macro(self):

        if self.running:
            return

        if not self.data:

            messagebox.showwarning(
                "알림",
                "등록된 좌표가 없습니다."
            )

            return

        # 좌표 등록 중이었다면 취소
        self.capture_waiting = False

        self.capture_btn.config(
            text="좌표 추가"
        )

        self.refresh_markers()

        self.running = True

        self.start_btn.config(
            state="disabled"
        )

        self.stop_btn.config(
            state="normal"
        )

        self.status_label.config(
            text="매크로 실행 중... ESC 또는 중지 버튼으로 중지"
        )

        # GUI가 멈추지 않도록 별도 스레드
        thread = threading.Thread(
            target=self.macro_worker,
            daemon=True
        )

        thread.start()

    # ========================================================
    # 매크로 실행 스레드
    # ========================================================
    def macro_worker(self):

        while self.running:

            for index, item in enumerate(
                self.data
            ):

                if not self.running:
                    break

                x, y, delay, event, clicks = item

                # 현재 실행 위치 GUI에 표시
                self.root.after(
                    0,
                    lambda idx=index, px=x, py=y:
                    self.update_running_status(
                        idx,
                        px,
                        py
                    )
                )

                # 해당 좌표로 이동
                pyautogui.moveTo(
                    x,
                    y,
                    duration=0
                )

                # 클릭 실행
                if event == "cr":

                    pyautogui.click(
                        button="right",
                        clicks=clicks,
                        interval=0
                    )

                elif event == "cl":

                    pyautogui.click(
                        button="left",
                        clicks=clicks,
                        interval=0
                    )

                # 단순 time.sleep(delay)를 사용하면
                # 긴 delay 동안 중지 반응이 늦을 수 있으므로
                # 짧게 나눠서 확인
                start_time = time.time()

                while (
                    time.time() - start_time
                    < delay
                ):

                    if not self.running:
                        break

                    time.sleep(0.01)

        # 실행 종료 후 GUI 복구
        self.root.after(
            0,
            self.macro_finished
        )

    # ========================================================
    # 실행 중 상태 표시
    # ========================================================
    def update_running_status(
        self,
        index,
        x,
        y
    ):

        if not self.running:
            return

        self.status_label.config(
            text=(
                f"매크로 실행 중 - "
                f"{index + 1}번째 좌표 "
                f"({x}, {y})"
            )
        )

    # ========================================================
    # 매크로 중지
    # ========================================================
    def stop_macro(self):

        if not self.running:
            return

        self.running = False

        self.drawer.clear()

        self.status_label.config(
            text="매크로 중지 중..."
        )

    # ========================================================
    # 매크로 종료 후
    # ========================================================
    def macro_finished(self):

        self.running = False

        self.drawer.clear()

        self.start_btn.config(
            state="normal"
        )

        self.stop_btn.config(
            state="disabled"
        )

        self.status_label.config(
            text="매크로가 중지되었습니다."
        )

    # ========================================================
    # 프로그램 종료
    # ========================================================
    def on_close(self):

        self.running = False

        self.drawer.clear()

        try:
            keyboard.unhook(
                self.ctrl_hook
            )
        except:
            pass

        try:
            keyboard.unhook(
                self.esc_hook
            )
        except:
            pass

        self.root.destroy()


# ============================================================
# 프로그램 시작
# ============================================================
if __name__ == "__main__":

    root = tk.Tk()

    app = MacroGUI(root)

    root.mainloop()
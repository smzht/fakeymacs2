# -*- mode: python; coding: utf-8-unix -*-

####################################################################################################
## Vim 用のキーの設定を行う（その２）
####################################################################################################

try:
    # 設定されているか？
    fc.vim2_target
except:
    # Vim 用のキーバインドを利用するアプリケーションソフトを指定する
    # （アプリケーションソフトは、プロセス名称のみ（ワイルドカード指定可）、もしくは、プロセス名称、
    #   クラス名称、ウィンドウタイトル（リストによる複数指定可）のリスト（ワイルドカード指定可、
    #   リストの後ろの項目から省略可）を指定してください）
    fc.vim2_target = [["WindowsTerminal.exe", "CASCADIA_HOSTING_WINDOW_CLASS", ["* - vim*",
                                                                                "* - nvim*"]],
                      ["cmd.exe",             "ConsoleWindowClass",            ["* - vim*",
                                                                                "* - nvim*"]],
                      ["powershell.exe",      "ConsoleWindowClass",            ["* - vim*",
                                                                                "* - nvim*"]],
                      ["*vim.exe",            "*",                             ["* - vim*",
                                                                                "* - nvim*"]],
                      ["neovide.exe",         "*",                             ["* - vim*",
                                                                                "* - nvim*"]],
                      ]

try:
    # 設定されているか？
    fc.vim2_keep_in_insert_mode
except:
    # インサートモードで C-g を押下した際、インサートモート居続けるかどうかを指定する
    # （True: インサートモードに居続ける、False: ノーマルモードに移行する）
    fc.vim2_keep_in_insert_mode = False

try:
    # 設定されているか？
    fc.vim2_insert_normal_mode_key
except:
    # インサートノーマルモードに移行するためのキーを指定する
    fc.vim2_insert_normal_mode_key = "C-o"

# --------------------------------------------------------------------------------------------------

class FakeymacsVim:
    pass

fakeymacs_vim = FakeymacsVim()

vim_target = targetRegexify(fc.vim_target)
vim_status = False
vim_title = ""

fakeymacs_vim.mode = ""

def is_vim_kept(title):
    if vim_status:
        title1 = re.sub(r" [-(].*", "", title)
        title2 = re.sub(r" [-(].*", "", vim_title)

        result1 = title.replace(vim_title, "")
        result2 = vim_title.replace(title, "")

        if title1 == title2 or " +" in [result1, result2]:
            m = re.search(r" \[(.*?)\]$", title)
            fakeymacs_vim.mode = m.group(1)
            keep = True
        else:
            keep = False
    else:
        keep = False

    return keep

def is_vim_target(window):
    global vim_status, vim_title

    if window is not fakeymacs.last_window or fakeymacs.force_update:
        if (fakeymacs.is_emacs_target == False and
            not getText(window).startswith("!") and
            (vim_target[0].match(getProcessName(window)) or
             any(checkWindow(*app, window=window) for app in vim_target[1]))):

            title = getText(window)
            if not is_vim_kept(title):
                resetVim()

            vim_status = True
            vim_title = title
        else:
            vim_status = False

    return vim_status

if fc.use_emacs_ime_mode:
    keymap_vim2 = keymap.defineWindowKeymap(check_func=lambda wnd: (is_vim_target(wnd) and
                                                                   not is_emacs_ime_mode(wnd)))
else:
    keymap_vim2 = keymap.defineWindowKeymap(check_func=is_vim_target)

fakeymacs.is_vim_kept = is_vim_kept
fakeymacs.keymap_vim2 = keymap_vim2

fakeymacs_vim.insert_normal_mode = False
fakeymacs_vim.is_prefix_key = False
fakeymacs_vim.last_key = None

# prefix key のリスト
# （リストの階層は、prefix key が続くことを意味し、[] は終了を意味する。
#   また、None は次のリストの階層に移行しないことを意味する）
prefix_key_list = [[["g"],
                    [[["'", "`",             # ジャンプリストに異動
                       "r"],                 # 範囲の文字置換
                      []]]],

                   [["r",
                     "q", "@",               # マクロ関連
                     "f", "S-f", "t", "S-t", # ジャンプ関連
                     "m", "'", "`",          # マーク関連
                     "[", "]",               # 構造に基づくジャンプ
                     "Z",                    # 終了関連
                     '"'],                   # レジスタプレフィックス
                    []],

                   [["z"],
                    [[["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], None]]],

                   [["C-w"],
                    [[["1", "2", "3", "4", "5", "6", "7", "8", "9"],
                      [[["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], None],
                       [["g"], []]]],
                     [["g"], []]]],
                   ]

def applyAll(xs, func):
    result = []
    for x in xs:
        if isinstance(x, list):
            result.append(applyAll(x, func))
        else:
            if x == None:
                result.append(None)
            else:
                result.append(func(x))
    return result

prefix_key_list = applyAll(prefix_key_list, specialCharToKeyStr)

## 共通関数
def resetVim():
    reset_undo(reset_counter(execute_ex_command("noh", esc=True)))()
    fakeymacs.is_searching = None

def checkPrefixKey(*key_list):
    global p_key_list

    if not is_operator_pending():
        for key in key_list:
            key = specialCharToKeyStr(key)
            is_prefix_key = False

            if not is_text_mode1():
                if fakeymacs_vim.is_prefix_key == False:
                    p_key_list = prefix_key_list

                for c_key_list in p_key_list:
                    if key in c_key_list[0]:
                        is_prefix_key = True
                        if c_key_list[1] is not None:
                            p_key_list = c_key_list[1]
                        break

            fakeymacs_vim.is_prefix_key = is_prefix_key
            fakeymacs_vim.last_key = key

            if fakeymacs_vim.is_prefix_key == False:
                fakeymacs_vim.insert_normal_mode = False

    if fc.debug:
        print("fakeymacs_vim.is_prefix_key : " + str(fakeymacs_vim.is_prefix_key))

def is_operator_pending():
    return fakeymacs_vim.mode.startswith("no")

def is_pending_key_sequence():
    return (is_operator_pending() or
            fakeymacs_vim.is_prefix_key)

def is_command_line():
    return fakeymacs_vim.mode.startswith("c")

def is_insert_mode():
    return (not fakeymacs_vim.insert_normal_mode and
            (fakeymacs_vim.mode.startswith("i") or
             fakeymacs_vim.mode.startswith("s") or
             fakeymacs_vim.mode.startswith("R")))

def is_normal_mode():
    return fakeymacs_vim.mode.startswith("n")

def is_insert_normal_mode():
    return fakeymacs_vim.insert_normal_mode

def is_visual_mode():
    return fakeymacs_vim.mode.startswith("v")

def is_text_mode1():
    return (is_command_line() or
            is_insert_mode())

def is_text_mode2():
    return (is_command_line() or
            is_visual_mode() or
            is_insert_mode())

def define_key_v1(keys, command, skip_check=True):
    if skip_check:
        # 設定をスキップするキーの処理を行う
        if "keymap_vim" in fc.skip_mapping_key:
            for skey in fc.skip_mapping_key["keymap_vim"]:
                if fnmatch.fnmatch(keys, skey):
                    print(f"skip key mapping : [keymap_vim2] {keys}")
                    return

    define_key(keymap_vim2, keys, command)

def define_key_v2(keys, command, skip_check=True):
    def _command():
        if is_pending_key_sequence():
            escape()
        else:
            command()

    define_key_v1(keys, _command, skip_check)

def self_insert_command_v1(*key_list, usjis_conv=True):
    func = self_insert_command(*key_list, usjis_conv=usjis_conv)
    def _func():
        checkPrefixKey(*key_list)
        func()
    return _func

def self_insert_command_v2(*key_list, usjis_conv=True):
    func = self_insert_command2(*key_list, usjis_conv=usjis_conv)
    def _func():
        checkPrefixKey(*key_list)
        func()
    return _func

def self_insert_command_v3(*key_list, usjis_conv=True):
    func = self_insert_command_v2(*key_list, usjis_conv=usjis_conv)
    def _func():
        # ノーマルモードで日本語を入力した際は、インサートモードにする
        if getImeStatus():
            if is_normal_mode() or is_insert_normal_mode():
                adjust_ime_status(self_insert_command_v1("i"))()

            elif is_visual_mode():
                adjust_ime_status(self_insert_command_v1("c"))()
        func()
    return _func

def digit(number):
    def _func():
        if fakeymacs.is_universal_argument:
            digit_argument(number)
        else:
            reset_undo(reset_counter(repeat(self_insert_command_v3(str(number)))))()
    return _func

def adjust_ime_status(command):
    def _func():
        ime_status = getImeStatus()
        if ime_status:
            setImeStatus(0)
        command()
        if ime_status:
            delay()
            setImeStatus(1)
    return _func

def execute_nm_command(*key_list, esc=False):
    def _func():
        if is_command_line():
            return False

        if esc:
            escape()
            delay(0.05)
            escape()

        if is_insert_mode():
            self_insert_command_v1(fc.vim2_insert_normal_mode_key)()

        adjust_ime_status(self_insert_command_v1(*key_list))()

        return True
    return _func

def execute_ex_command(ex_command, enter=True, esc=False):
    def _func():
        if is_command_line():
            return False

        if esc:
            escape()
            delay(0.05)
            escape()

        def _command():
            self_insert_command_v1(":")()
            princ(ex_command)
            if enter:
                self_insert_command_v1("Enter")()

        if is_insert_mode():
            self_insert_command_v1(fc.vim2_insert_normal_mode_key)()

        if enter:
            adjust_ime_status(_command)()
        else:
            setImeStatus(0)
            _command()

        return True
    return _func

def enter_insert_normal_mode():
    if is_insert_normal_mode():
        escape()

    elif is_insert_mode():
        self_insert_command_v1(fc.vim2_insert_normal_mode_key)()
        setImeStatus(0)
        fakeymacs_vim.insert_normal_mode = True

def enter_search_mode(key):
    def _func():
        if is_text_mode1():
            repeat(self_insert_command_v2(key))()

        elif getImeStatus():
            repeat(self_insert_command_v3(key))()
        else:
            if is_pending_key_sequence():
                self_insert_command_v1(key)()
            else:
                self_insert_command_v1(key)()
                if key == "*":
                    fakeymacs.is_searching = True
                else:
                    fakeymacs.is_searching = False
    return _func

## ファイル操作
def find_file():
    execute_ex_command("edit ", enter=False, esc=True)()

def save_buffer():
    execute_ex_command("write")()

def write_file():
    execute_ex_command("write ", enter=False)()

## カーソル移動
def backward_char():
    self_insert_command_v1("Left")()

def forward_char():
    self_insert_command_v1("Right")()

def backward_word():
    self_insert_command_v1("C-Left")()

def forward_word():
    self_insert_command_v1("C-Right")()

def previous_line():
    self_insert_command_v1("Up")()

def next_line():
    self_insert_command_v1("Down")()

def move_beginning_of_line():
    self_insert_command_v1("Home")()

def move_end_of_line():
    if is_text_mode2():
        self_insert_command_v1("End")()
    else:
        self_insert_command_v1("End", "Right")()

def beginning_of_buffer():
    self_insert_command_v1("C-Home", "Home")()

def end_of_buffer():
    self_insert_command_v1("C-End", "Right")()

def goto_line():
    execute_ex_command("", enter=False)()

def scroll_up():
    self_insert_command_v1("PageUp")()

def scroll_down():
    self_insert_command_v1("PageDown")()

def recenter():
    execute_nm_command("z", "z")()

## カット / コピー / 削除 / アンドゥ
def delete_backward_char():
    if is_command_line():
        self_insert_command_v1("Back")()

    elif is_visual_mode():
        self_insert_command_v1("Delete")()
    else:
        execute_nm_command("S-x")()

def delete_char():
    if is_command_line():
        self_insert_command_v1("Delete")()

    elif is_visual_mode():
        self_insert_command_v1("Delete")()
    else:
        # 改行も削除できるようにビジュアルモードに移行してから削除している
        execute_nm_command("v", "x")()

def backward_kill_word():
    execute_nm_command("d", "b")()

def kill_word():
    execute_nm_command("d", "w")()

def kill_line():
    if is_visual_mode():
        escape()

    execute_nm_command("v", "$", "Delete")()

def kill_region():
    if is_visual_mode():
        self_insert_command_v1("Delete")()

def kill_ring_save():
    if is_visual_mode():
        execute_nm_command("y")()

def yank():
    execute_nm_command("g", "S-p")()

def undo():
    if fakeymacs.is_undo_mode:
        execute_nm_command("u")()
    else:
        execute_nm_command("C-r")()

def set_mark_command(key):
    def _func():
        if not is_command_line():
            execute_nm_command(key)()
    return _func

def mark_whole_buffer():
    if not is_command_line():
        if is_visual_mode():
            escape()

        end_of_buffer()
        set_mark_command("S-v")()
        beginning_of_buffer()

def mark_page():
    mark_whole_buffer()

## テキストの入れ替え
def transpose_chars():
    if not is_command_line():
        delete_char()
        forward_char()
        yank()
        backward_char()

## バッファ操作
def kill_buffer():
    execute_ex_command("bp|bd#", esc=True)()

def previous_buffer():
    execute_ex_command("bprevious", esc=True)()

def next_buffer():
    execute_ex_command("bnext", esc=True)()

def switch_to_buffer():
    next_buffer()

def list_buffers():
    execute_ex_command("ls", esc=True)()

## ウィンドウ操作
def delete_window():
    execute_nm_command("C-w", "c", esc=True)()

def delete_other_windows():
    execute_nm_command("C-w", "o")()

def split_window_below():
    execute_ex_command("split")()

def split_window_right():
    execute_ex_command("vsplit")()

def other_window():
    execute_nm_command("C-w", "w", esc=True)()

## タブ操作
def create_tab():
    execute_ex_command("tabnew ", enter=False, esc=True)()

def close_tab():
    execute_ex_command("tabclose", esc=True)()

def previous_tab():
    execute_ex_command("tabprevious", esc=True)()

def next_tab():
    execute_ex_command("tabnext", esc=True)()

def list_tabs():
    execute_ex_command("tabs", esc=True)()

## 文字列検索
def isearch(direction):
    def _func():
        if fakeymacs.is_searching is None:
            if execute_nm_command({"backward":"?", "forward":"/"}[direction])():
                fakeymacs.is_searching = False

        elif fakeymacs.is_searching == False:
            self_insert_command_v1({"backward":"C-t", "forward":"C-g"}[direction])()

        elif fakeymacs.is_searching == True:
            execute_nm_command({"backward":"S-n", "forward":"n"}[direction])()
    return _func

def isearch_backward():
    isearch("backward")()

def isearch_forward():
    isearch("forward")()

def isearch_repeat(key):
    def _func():
        if is_text_mode1():
            repeat(self_insert_command_v2(key))()

        elif getImeStatus():
            repeat(self_insert_command_v3(key))()
        else:
            if is_pending_key_sequence():
                self_insert_command_v1(key)()
            else:
                self_insert_command_v1(key)()
                fakeymacs.is_searching = True
    return _func

## キーボードマクロ
def keyboard_macro_start():
    execute_nm_command("q", "a", esc=True)()

def keyboard_macro_stop():
    execute_nm_command("q", esc=True)()

def keyboard_macro_play():
    execute_nm_command("@", "a", esc=True)()

## 矩形選択
def rectangle_mark_mode():
    set_mark_command("C-v")()

## その他
def escape(keep_in_im=False):
    if is_command_line():
        self_insert_command_v1("Esc")()

    elif is_insert_mode():
        if not keep_in_im:
            setImeStatus(0)
            self_insert_command_v1("Esc", "`", "^")()
    else:
        self_insert_command_v1("Esc")()

def space():
    self_insert_command_v1("Space")()

def newline(enter_im=False):
    def _func():
        if enter_im:
            if is_normal_mode():
                adjust_ime_status(self_insert_command_v1("i"))()

        self_insert_command_v1("Enter")()

        if fakeymacs.is_searching == False:
            fakeymacs.is_searching = True
    return _func

def indent_for_tab_command():
    self_insert_command_v1("Tab")()

def keyboard_quit():
    if is_normal_mode() or is_insert_mode():
        if fakeymacs.is_undo_mode:
            fakeymacs.is_undo_mode = False
        else:
            fakeymacs.is_undo_mode = True

    escape(keep_in_im=fc.vim2_keep_in_insert_mode)

    if fakeymacs.is_searching == False:
        fakeymacs.is_searching = None

    elif fakeymacs.is_searching == True:
        execute_ex_command("noh")()

def execute_extended_command():
    execute_ex_command("", enter=False, esc=True)()

def kill_emacs():
    setImeStatus(0)
    execute_ex_command("quitall")()

## マルチストロークキーの設定
define_key_v1("Ctl-x",  keymap.defineMultiStrokeKeymap(fc.ctl_x_prefix_key))
define_key_v1("C-q",    keymap.defineMultiStrokeKeymap("C-q"))
define_key_v1("M-",     keymap.defineMultiStrokeKeymap("Esc"))
define_key_v1("M-g",    keymap.defineMultiStrokeKeymap("M-g"))
define_key_v1("M-g M-", keymap.defineMultiStrokeKeymap("M-g Esc"))

## 数字キーの設定
for n in range(10):
    key = str(n)
    define_key_v1(key, digit(n))
    if fc.use_ctrl_digit_key_for_digit_argument:
        define_key_v1(f"C-{key}", digit2(n))
    define_key_v1(f"M-{key}", digit2(n))
    define_key_v1(f"S-{key}", reset("uc", repeat(self_insert_command_v3(f"S-{key}"))))

## アルファベットキーの設定
for vkey in range(VK_A, VK_Z + 1):
    key = vkToStr(vkey)
    for mod in ["", "S-"]:
        mkey = mod + key
        define_key_v1(mkey, reset("uc", repeat(self_insert_command_v3(mkey))))

## 特殊文字キーの設定
define_key_v1("Space"  , reset("uc", repeat(self_insert_command_v1("Space"))))
define_key_v1("S-Space", reset("uc", repeat(self_insert_command_v1("S-Space"))))

for vkey in [VK_OEM_MINUS, VK_OEM_PLUS, VK_OEM_COMMA, VK_OEM_PERIOD,
             VK_OEM_1, VK_OEM_2, VK_OEM_3, VK_OEM_4, VK_OEM_5, VK_OEM_6, VK_OEM_7, VK_OEM_102]:
    key = vkToStr(vkey)
    for mod in ["", "S-"]:
        mkey = mod + key
        define_key_v1(mkey, reset("uc", repeat(self_insert_command_v3(mkey))))

## 10key の特殊文字キーの設定
for vkey in [VK_MULTIPLY, VK_ADD, VK_SUBTRACT, VK_DECIMAL, VK_DIVIDE]:
    key = vkToStr(vkey)
    define_key_v1(key, reset("uc", repeat(self_insert_command_v3(key))))

## quoted-insert キーの設定
for vkey in vkeys():
    key = vkToStr(vkey)
    for mod1, mod2, mod3, mod4 in itertools.product(["", "W-"], ["", "A-"], ["", "C-"], ["", "S-"]):
        mkey = mod1 + mod2 + mod3 + mod4 + key
        define_key_v1(f"C-q {mkey}", self_insert_command_v1(mkey))

## Esc キーの設定
if fc.use_esc_as_meta:
    define_key_v1("Esc Esc", escape)
else:
    define_key_v1("Esc", escape)

if fc.use_ctrl_openbracket_as_meta:
    define_key_v1("C-[ C-[", escape)
else:
    define_key_v1("C-[", escape)

## 「インサートノーマルモード移行」のキー設定
if not getKeyCommand(keymap_ime, "C-o"):
    define_key_v2("C-o", reset("uc", enter_insert_normal_mode))

define_key_v2("C-A-o", reset("uc", enter_insert_normal_mode))

## 「検索モード移行」のキー設定
for key in ["/", "?", "*"]:
    define_key_v1(key, reset("uc", enter_search_mode(key)))

## universal-argument キーの設定
define_key_v2("C-u", universal_argument)

## 「ファイル操作」のキー設定
define_key_v2("Ctl-x C-f", reset("uc", find_file))
define_key_v2("Ctl-x C-s", reset("uc", save_buffer))
define_key_v2("Ctl-x C-w", reset("uc", write_file))

## 「カーソル移動」のキー設定
define_key_v1("C-b",       reset("uc", repeat(backward_char)))
define_key_v1("C-f",       reset("uc", repeat(forward_char)))
define_key_v1("M-b",       reset("uc", repeat(backward_word)))
define_key_v1("M-f",       reset("uc", repeat(forward_word)))
define_key_v1("C-p",       reset("uc", repeat(previous_line)))
define_key_v1("C-n",       reset("uc", repeat(next_line)))
define_key_v1("C-a",       reset("uc", move_beginning_of_line))
define_key_v1("C-e",       reset("uc", move_end_of_line))
define_key_v1("M-<",       reset("uc", beginning_of_buffer))
define_key_v1("M->",       reset("uc", end_of_buffer))
define_key_v1("M-g g",     reset("uc", goto_line))
define_key_v1("M-g M-g",   reset("uc", goto_line))
define_key_v2("C-l",       reset("uc", recenter))

define_key_v1("Left",      reset("uc", repeat(backward_char)))
define_key_v1("Right",     reset("uc", repeat(forward_char)))
define_key_v1("C-Left",    reset("uc", repeat(backward_word)))
define_key_v1("C-Right",   reset("uc", repeat(forward_word)))
define_key_v1("Up",        reset("uc", repeat(previous_line)))
define_key_v1("Down",      reset("uc", repeat(next_line)))
define_key_v1("Home",      reset("uc", move_beginning_of_line))
define_key_v1("End",       reset("uc", move_end_of_line))
define_key_v1("C-Home",    reset("uc", beginning_of_buffer))
define_key_v1("C-End",     reset("uc", end_of_buffer))
define_key_v2("PageUp",    reset("uc", scroll_up))
define_key_v2("PageDown",  reset("uc", scroll_down))

## 「カット / コピー / 削除 / アンドゥ」のキー設定
define_key_v1("C-h",       reset("uc", repeat(delete_backward_char)))
define_key_v2("C-d",       reset("uc", repeat(delete_char)))
define_key_v2("M-Delete",  reset("uc", repeat(backward_kill_word)))
define_key_v2("M-d",       reset("uc", repeat(kill_word)))
define_key_v2("C-k",       reset("uc", repeat(kill_line)))
define_key_v2("C-w",       reset("uc", kill_region))
define_key_v2("M-w",       reset("uc", kill_ring_save))
define_key_v2("C-y",       reset("uc", repeat(yank)))
define_key_v2("C-/",       reset("c",  undo))
define_key_v2("Ctl-x u",   reset("c",  undo))

define_key_v1("Back",      reset("uc", repeat(delete_backward_char)))
define_key_v2("Delete",    reset("uc", repeat(delete_char)))
define_key_v2("C-Back",    reset("uc", repeat(backward_kill_word)))
define_key_v2("C-Delete",  reset("uc", repeat(kill_word)))
define_key_v2("C-c",       reset("uc", kill_ring_save))
define_key_v2("C-v",       reset("uc", repeat(yank)))
define_key_v2("C-z",       reset("c",  undo))
define_key_v2("C-_",       reset("c",  undo))
define_key_v2("C-@",       reset("uc", set_mark_command("v")))
define_key_v2("C-Space",   reset("uc", set_mark_command("v")))
define_key_v2("Ctl-x h",   reset("uc", mark_whole_buffer))
define_key_v2("Ctl-x C-p", reset("uc", mark_page))

## 「テキストの入れ替え」のキー設定
define_key_v2("C-t",       reset("uc", transpose_chars))

## 「バッファ操作」のキー設定
define_key_v2("M-k",       reset("uc", kill_buffer))
define_key_v2("Ctl-x k",   reset("uc", kill_buffer))
define_key_v2("Ctl-x b",   reset("uc", switch_to_buffer))
define_key_v2("Ctl-x C-b", reset("uc", list_buffers))

define_key_v2("M-p",       reset("uc", previous_buffer))
define_key_v2("M-n",       reset("uc", next_buffer))
define_key_v2("M-Up",      reset("uc", previous_buffer))
define_key_v2("M-Down",    reset("uc", next_buffer))

## 「ウィンドウ操作」のキー設定
define_key_v2("Ctl-x 0",   reset("uc", delete_window))
define_key_v2("Ctl-x 1",   delete_other_windows)
define_key_v2("Ctl-x 2",   split_window_below)
define_key_v2("Ctl-x 3",   split_window_right)
define_key_v2("Ctl-x o",   reset("uc", other_window))

## 「タブ操作」のキー設定
define_key_v2("C-A-t",     reset("uc", create_tab))
define_key_v2("C-A-c",     reset("uc", close_tab))
define_key_v2("C-A-p",     reset("uc", previous_tab))
define_key_v2("C-A-n",     reset("uc", next_tab))
define_key_v2("C-A-l",     reset("uc", list_tabs))

## 「文字列検索」のキー設定
define_key_v2("C-r",       reset("uc", isearch_backward))
define_key_v2("C-s",       reset("uc", isearch_forward))

for key in ["S-n", "n"]:
    define_key_v1(key,     reset("uc", isearch_repeat(key)))

## 「キーボードマクロ」のキー設定
define_key_v2("Ctl-x (",   keyboard_macro_start)
define_key_v2("Ctl-x )",   keyboard_macro_stop)
define_key_v2("Ctl-x e",   reset("uc", repeat(keyboard_macro_play)))

## 「矩形選択」のキー設定
define_key_v2("C-A-Space", reset("uc", rectangle_mark_mode))

## 「その他」のキー設定
define_key_v2("Enter",     reset("uc", repeat(newline())))
define_key_v2("C-m",       reset("uc", repeat(newline())))
define_key_v2("C-Enter",   reset("uc", repeat(newline(enter_im=True))))
define_key_v1("C-g",       reset("sc", keyboard_quit))
define_key_v2("M-x",       reset("uc", execute_extended_command))
define_key_v2("Ctl-x C-c", reset("uc", kill_emacs))

## 「タブ」のキー設定
if fc.use_ctrl_i_as_tab:
    define_key_v1("C-i",   reset("uc", indent_for_tab_command))

## 「スクロール」のキー設定
if fc.scroll_key:
    define_key_v2(fc.scroll_key[0], reset("uc", scroll_up))
    define_key_v2(fc.scroll_key[1], reset("uc", scroll_down))

# --------------------------------------------------------------------------------------------------

## config_personal.py ファイルの読み込み
exec(readConfigExtension(r"vim_key\config_personal.py", msg=False), dict(globals(), **locals()))

# デバッグ表示モード
IS_DEBUG_PRINT_MODE_IN_FRONTEND = True

##_________________________________________________________________________________________________
# global関数

def debug_print(d, message):
    if IS_DEBUG_PRINT_MODE_IN_FRONTEND:
        print(f'==============[Front-end] (DEBUG PRINT) {message}==============')
        print(d)
    return
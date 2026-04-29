import pyautogui
from PIL import Image
import time
import os
import traceback
from AppKit import NSImage
from Vision import VNRecognizeTextRequest, VNImageRequestHandler

# ========== 配置区 ==========
keywords = ["有号", "有"]
alert_sound = "/System/Library/Sounds/Glass.aiff"
cooldown = 3
last_alert = 0
# ===========================

def get_mouse_region():
    print("=" * 50)
    print("区域拾取说明：")
    print("使用快捷键 shift + command + 4 拖拽选区，左上角+右下角坐标")
    print("输入格式示例：300 200 800 500")
    print("=" * 50)
    while True:
        try:
            input_str = input("请输入检测区域坐标(x1 y1 x2 y2)：").strip()
            x1, y1, x2, y2 = map(int, input_str.split())
            if x1 >= x2 or y1 >= y2:
                print("❌ 错误：x1 < x2 、 y1 < y2")
                continue
            width = x2 - x1
            height = y2 - y1
            print(f"✅ 已锁定区域：{x1, y1} 宽{width} 高{height}")
            return (x1, y1, width, height)
        except ValueError:
            print("❌ 格式错误，请输入4个数字，空格分隔")

def vision_ocr(image_path):
    try:
        ns_img = NSImage.alloc().initWithContentsOfFile_(image_path)
        if not ns_img:
            return ""
        req = VNRecognizeTextRequest.alloc().init()
        req.setRecognitionLanguages_(["zh-Hans"])
        handler = VNImageRequestHandler.alloc().initWithCGImage_options_(ns_img.CGImage(), None)
        handler.performRequests_error_([req], None)
        text = ""
        for res in req.results():
            candidate = res.topCandidates_(1)
            if candidate:
                text += candidate[0].string() + " "
        return text
    except Exception as e:
        print(f"OCR识别异常：{e}")
        return ""

if __name__ == "__main__":
    region = get_mouse_region()
    x1, y1, width, height = region
    print("\n🚀 开始后台监控，控制台实时打印识别内容")
    print("🛑 停止方式：控制台 Ctrl + C\n")

    try:
        while True:
            shot = pyautogui.screenshot(region=(x1, y1, width, height))
            tmp_path = "/tmp/ocr_temp.png"
            shot.save(tmp_path)

            ocr_text = vision_ocr(tmp_path)
            print(f"📝 识别内容：{ocr_text.strip()}")

            now_time = time.time()
            for kw in keywords:
                if kw in ocr_text and (now_time - last_alert) > cooldown:
                    print(f"🔔 命中关键词：【{kw}】")
                    os.system(f"afplay {alert_sound}")
                    last_alert = now_time
                    break

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n✅ 已手动停止监控程序")
    except Exception as e:
        print(f"\n❌ 程序出错：{e}")
        traceback.print_exc()

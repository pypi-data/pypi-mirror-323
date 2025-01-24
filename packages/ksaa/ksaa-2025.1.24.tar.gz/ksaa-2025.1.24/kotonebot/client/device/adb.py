import logging
from typing import Callable, cast
from typing_extensions import override

import numpy as np
import cv2
from cv2.typing import MatLike
from adbutils import AdbClient, adb
from adbutils._device import AdbDevice as Device

from kotonebot.backend.util import Rect, is_rect
from ..protocol import DeviceABC, ClickableObjectProtocol


logger = logging.getLogger(__name__)

class AdbDevice(DeviceABC):
    def __init__(self, device: Device) -> None:
        super().__init__()
        self.device = device

    @override
    def launch_app(self, package_name: str) -> None:
        self.device.shell(f"monkey -p {package_name} 1")
    
    @override
    def click(self, arg1=None, arg2=None) -> None:
        if arg1 is None:
            self.__click_last()
        elif is_rect(arg1):
            self.__click_rect(arg1)
        elif isinstance(arg1, int) and isinstance(arg2, int):
            self.__click_point(arg1, arg2)
        elif isinstance(arg1, ClickableObjectProtocol):
            self.__click_clickable(arg1)
        else:
            raise ValueError(f"Invalid arguments: {arg1}, {arg2}")

    def __click_last(self) -> None:
        if self.last_find is None:
            raise ValueError("No last find result. Make sure you are not calling the 'raw' functions.")
        self.click(self.last_find)

    def __click_rect(self, rect: Rect) -> None:
        # 从矩形中心的 60% 内部随机选择一点
        x = rect[0] + rect[2] // 2 + np.random.randint(-int(rect[2] * 0.3), int(rect[2] * 0.3))
        y = rect[1] + rect[3] // 2 + np.random.randint(-int(rect[3] * 0.3), int(rect[3] * 0.3))
        x = int(x)
        y = int(y)
        self.click(x, y)

    def __click_point(self, x: int, y: int) -> None:
        for hook in self.click_hooks_before:
            logger.debug(f"Executing click hook before: ({x}, {y})")
            x, y = hook(x, y)
            logger.debug(f"Click hook before result: ({x}, {y})")
        logger.debug(f"Click: {x}, {y}")
        self.device.shell(f"input tap {x} {y}")

    def __click_clickable(self, clickable: ClickableObjectProtocol) -> None:
        self.click(clickable.rect)

    @override
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: float|None = None) -> None:
        if duration is not None:
            logger.warning("Swipe duration is not supported with AdbDevice. Ignoring duration.")
        self.device.shell(f"input touchscreen swipe {x1} {y1} {x2} {y2}")

    @override
    def screenshot(self) -> MatLike:
        if self.screenshot_hook_before is not None:
            logger.debug("execute screenshot hook before")
            img = self.screenshot_hook_before()
            if img is not None:
                logger.debug("screenshot hook before returned image")
                return img
        img = self.screenshot_raw()
        if self.screenshot_hook_after is not None:
            img = self.screenshot_hook_after(img)
        return img

    @override
    def screenshot_raw(self) -> MatLike:
        return cv2.cvtColor(np.array(self.device.screenshot()), cv2.COLOR_RGB2BGR)

    @property
    def screen_size(self) -> tuple[int, int]:
        ret = cast(str, self.device.shell("wm size")).strip('Physical size: ')
        spiltted = tuple(map(int, ret.split("x")))
        landscape = self.orientation == 'landscape'
        spiltted = tuple(sorted(spiltted, reverse=landscape))
        if len(spiltted) != 2:
            raise ValueError(f"Invalid screen size: {ret}")
        return spiltted
    
    @staticmethod
    def list_devices() -> list[str]:
        raise NotImplementedError
    
    @override
    def start_app(self, package_name: str) -> None:
        self.device.shell(f"monkey -p {package_name} 1")

    @override
    def detect_orientation(self):
        # 判断方向：https://stackoverflow.com/questions/10040624/check-if-device-is-landscape-via-adb
        # 但是上面这种方法不准确
        # 因此这里直接通过截图判断方向
        img = self.screenshot()
        if img.shape[0] > img.shape[1]:
            return 'portrait'
        return 'landscape'
    
    @override
    def current_package(self) -> str | None:
        # https://blog.csdn.net/guangdeshishe/article/details/117154406
        result_text = self.device.shell('dumpsys activity top | grep ACTIVITY | tail -n 1')
        logger.debug(f"adb returned: {result_text}")
        if not isinstance(result_text, str):
            logger.error(f"Invalid result_text: {result_text}")
            return None
        result_text = result_text.strip()
        if result_text == '':
            logger.error("No current package found")
            return None
        _, activity, _, pid = result_text.split(' ')
        package = activity.split('/')[0]
        return package

        
if __name__ == "__main__":
    print("server version:", adb.server_version())
    adb.connect("127.0.0.1:16384", )
    print("devices:", adb.device_list())
    d = adb.device_list()[0]
    dd = AdbDevice(d)
    # dd.launch_app("com.android.settings")

    # 实时展示画面
    import cv2
    import numpy as np
    while True:
        img = dd.screenshot()
        # img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
        # img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        cv2.imshow("screen", img)
        # 50% 缩放
        img = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4))
        # 获取当前时间
        import time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        # 在图像上绘制时间
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, current_time, (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.waitKey(1)



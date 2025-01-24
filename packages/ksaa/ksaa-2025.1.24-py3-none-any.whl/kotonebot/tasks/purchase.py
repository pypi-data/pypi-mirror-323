"""从商店购买物品"""
import logging

from . import R
from .common import conf
from kotonebot.backend.util import cropped
from kotonebot import task, device, image, ocr, action, sleep
from .actions.scenes import goto_home, goto_shop, at_daily_shop

logger = logging.getLogger(__name__)

@action('购买 Money 物品')
def money_items():
    """
    购买マニー物品

    前置条件：位于商店页面的マニー Tab
    """
    logger.info(f'Purchasing マニー items.')
    # [screenshots\shop\money1.png]
    results = image.find_all(R.Daily.TextShopRecommended)
    # device.click(results[0])
    index = 1
    for index, result in enumerate(results, 1):
        # [screenshots\shop\dialog.png]
        logger.info(f'Purchasing #{index} item.')
        device.click(result)
        sleep(0.5)
        with cropped(device, y1=0.3):
            purchased = image.wait_for(R.Daily.TextShopPurchased, timeout=1)
            if purchased is not None:
                logger.info(f'AP item #{index} already purchased.')
                continue
            comfirm = image.expect_wait(R.Common.ButtonConfirm, timeout=2)
            # 如果数量不是最大，调到最大
            while image.find(R.Daily.ButtonShopCountAdd, colored=True):
                logger.debug('Adjusting quantity(+1)...')
                device.click()
                sleep(0.3)
            logger.debug(f'Confirming purchase...')
            device.click(comfirm)
            sleep(1.5)
    logger.info(f'Purchasing マニー items completed. {index} items purchased.')

@action('购买 AP 物品')
def ap_items():
    """
    购买 AP 物品

    前置条件：位于商店页面的 AP Tab
    """
    # [screenshots\shop\ap1.png]
    logger.info(f'Purchasing AP items.')
    results = image.find_all(R.Daily.IconShopAp, threshold=0.7)
    sleep(1)
    # 按 X, Y 坐标排序从小到大
    results = sorted(results, key=lambda x: (x.position[0], x.position[1]))
    # 按照配置文件里的设置过滤
    item_indices = conf().purchase.ap_items
    logger.info(f'Purchasing AP items: {item_indices}')
    for index in item_indices:
        if index <= len(results):
            logger.info(f'Purchasing #{index} AP item.')
            device.click(results[index])
            sleep(0.5)
            with cropped(device, y1=0.3):
                purchased = image.wait_for(R.Daily.TextShopPurchased, timeout=1)
                if purchased is not None:
                    logger.info(f'AP item #{index} already purchased.')
                    continue
                comfirm = image.expect_wait(R.Common.ButtonConfirm, timeout=2)
                # 如果数量不是最大,调到最大
                while image.find(R.Daily.ButtonShopCountAdd, colored=True):
                    logger.debug('Adjusting quantity(+1)...')
                    device.click()
                    sleep(0.3)
                logger.debug(f'Confirming purchase...')
                device.click(comfirm)
                sleep(1.5)
        else:
            logger.warning(f'AP item #{index} not found')
    logger.info(f'Purchasing AP items completed. {len(item_indices)} items purchased.')

@task('商店购买')
def purchase():
    """
    从商店购买物品
    """
    if not conf().purchase.enabled:
        logger.info('Purchase is disabled.')
        return
    if not at_daily_shop():
        goto_shop()
    # 进入每日商店 [screenshots\shop\shop.png]
    # [ap1.png]
    device.click(image.expect(R.Daily.ButtonDailyShop)) # TODO: memoable
    sleep(1)

    # 购买マニー物品
    if conf().purchase.money_enabled:
        image.expect_wait(R.Daily.IconShopMoney)
        money_items()
        sleep(0.5)
    else:
        logger.info('Money purchase is disabled.')
    
    # 购买 AP 物品
    if conf().purchase.ap_enabled:
        # 点击 AP 选项卡
        device.click(image.expect_wait(R.Daily.TextTabShopAp, timeout=2)) # TODO: memoable
        # 等待 AP 选项卡加载完成
        image.expect_wait(R.Daily.IconShopAp)
        ap_items()
        sleep(0.5)
    else:
        logger.info('AP purchase is disabled.')
    
    goto_home()

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s')
    logger.setLevel(logging.DEBUG)
    # money_items()
    # ap_items([0, 1, 3])
    purchase()

import asyncio

from dotenv import load_dotenv

from pounce.agent.agent import PounceAgent
from pounce.browser.browser import Browser
from pounce.model import get_model, ModelEnum

load_dotenv()


async def run():
    model = get_model(ModelEnum.qwen3_vl_235b_a22b_instruct)  # 暂只支持一个模型
    browser = Browser()
    agent = PounceAgent(
        model=model,
        browser=browser,
        report_path=r'D:\code\os\pounce\artifactory'
    )

    task_info = """
    - 步骤1：访问 http://localhost:3000/360-profile
    - 步骤2：输入 ID值 在ID输入框中（例如：输入测试用户的ID值:_TIHK1s65mzzap2s6）
    - 步骤3：点击 查询按钮
    - 步骤4：滚动 页面到行程可视化组件区域
    - 步骤5：点击 行程可视化图表中的航班点或连线（展开订单详情，确保点击的是prdType为"F"的航班订单）
    """
    # task_info="""
    # 1. 访问 https://tw.trip.com/sale/w/4491/tw-payday.html?locale=zh-TW&pageid=cont_RuQJj129snDvuO5&preview=true&_foxpage_ticket=axgAMF4gqh
    # 2. Scroll down to find a button that says "Show More" or "search more **" or similar text. Be careful not to click the tabs or banners at the top.
    # 3. If you find a button that meets the criteria in step 1, click it. Be careful not to click the same button more than twice. If clicking a button redirects to a new page, return to the original page.
    # 4. If you do not find such a button, scroll down the page.
    # 5. Repeat steps 1 through 3 until you reach the end of the page.Note that the task can only be completed when you reach the bottom of the page，The bottom of the page contains the payment method.
    # """

    result = await agent.run(task_info)
    print(agent.used_token)


if __name__ == '__main__':
    asyncio.run(run())

    # todo 步骤拆分
    # model层面计费
    # action check 抽system
    # assertion 抽出来
    # 失败重试次数限制，防止无休止死循环
    # system 通用性，考虑后面接电脑

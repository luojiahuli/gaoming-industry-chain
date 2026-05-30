"""Playwright 截图 - 高明区产业链知识图谱关键视图"""
import os, sys, json, time

sys.path.insert(0, os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

URL = "http://localhost:8001"


def capture():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        # 1. 主视图 - 图谱全貌
        print("[1/5] 截取图谱主视图...")
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(3000)  # 等待力导向图稳定
        page.screenshot(path=os.path.join(OUTPUT_DIR, "01-graph-overview.png"), full_page=False)
        print("      → assets/01-graph-overview.png")

        # 2. 搜索功能
        print("[2/5] 截取搜索功能...")
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(2000)
        search_input = page.locator("#search-input")
        search_input.fill("润泽")
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "02-search.png"), full_page=False)
        print("      → assets/02-search.png")

        # 3. 节点详情 - 点击一个企业节点
        print("[3/5] 截取企业节点详情...")
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(3000)
        # 点击链条上的一个企业节点
        try:
            # 尝试点击海天味业节点
            page.locator("text=海天味业").first.click()
            page.wait_for_timeout(1500)
        except:
            pass
        page.screenshot(path=os.path.join(OUTPUT_DIR, "03-enterprise-detail.png"), full_page=False)
        print("      → assets/03-enterprise-detail.png")

        # 4. 产业分析弹窗
        print("[4/5] 截取产业分析弹窗...")
        # 关闭详情面板
        try:
            page.locator("#panel-close").click()
        except:
            pass
        page.wait_for_timeout(500)
        # 点击产业分析按钮
        page.locator("button:has-text('产业分析')").click()
        page.wait_for_timeout(2000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "04-analysis.png"), full_page=False)
        print("      → assets/04-analysis.png")
        # 关闭弹窗
        try:
            page.locator("#modal-close").click()
        except:
            pass

        # 5. 产业链详情
        print("[5/5] 截取产业链节点详情...")
        page.wait_for_timeout(500)
        try:
            page.locator("text=现代物流/临空经济").first.click()
            page.wait_for_timeout(1500)
        except:
            pass
        page.screenshot(path=os.path.join(OUTPUT_DIR, "05-chain-detail.png"), full_page=False)
        print("      → assets/05-chain-detail.png")

        browser.close()
        print(f"\n✅ 截图完成! 共5张, 保存至 {OUTPUT_DIR}")


if __name__ == "__main__":
    capture()

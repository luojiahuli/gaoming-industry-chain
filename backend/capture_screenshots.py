"""Playwright 截图 - 高明区产业链知识图谱关键视图 (增强版)"""
import os, sys, json, time

sys.path.insert(0, os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

URL = "http://localhost:8000"


def capture():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        # 1. 主视图 - 图谱全貌
        print("[1/7] 截取图谱主视图...")
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "01-graph-overview.png"), full_page=False)
        print("      → assets/01-graph-overview.png")

        # 2. 搜索功能
        print("[2/7] 截取搜索功能...")
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(2000)
        search_input = page.locator("#search-input")
        search_input.fill("润泽")
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "02-search.png"), full_page=False)
        print("      → assets/02-search.png")
        search_input.clear()

        # 3. 企业节点详情 - 海天味业
        print("[3/7] 截取企业节点详情...")
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(3000)
        try:
            page.locator("text=海天味业").first.click()
            page.wait_for_timeout(1500)
        except:
            pass
        page.screenshot(path=os.path.join(OUTPUT_DIR, "03-enterprise-detail.png"), full_page=False)
        print("      → assets/03-enterprise-detail.png")

        # 4. 产业分析弹窗
        print("[4/7] 截取产业分析弹窗...")
        try:
            page.locator("#panel-close").click()
        except:
            pass
        page.wait_for_timeout(500)
        page.locator("button:has-text('产业分析')").click()
        page.wait_for_timeout(2000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "04-analysis.png"), full_page=False)
        print("      → assets/04-analysis.png")
        try:
            page.locator("#modal-close").click()
        except:
            pass

        # 5. 产业链详情 - 现代物流/临空经济
        print("[5/7] 截取产业链节点详情...")
        page.wait_for_timeout(500)
        try:
            page.locator("text=现代物流/临空经济").first.click()
            page.wait_for_timeout(1500)
        except:
            pass
        page.screenshot(path=os.path.join(OUTPUT_DIR, "05-chain-detail.png"), full_page=False)
        print("      → assets/05-chain-detail.png")
        try:
            page.locator("#panel-close").click()
        except:
            pass

        # 6. 产业链缺口节点详情 - 点击一个缺口节点
        print("[6/7] 截取产业链缺口节点...")
        page.wait_for_timeout(1000)
        # 找一个缺口节点点击 (供应链缺口/技术缺口/上游缺口/下游缺口)
        gap_node_found = False
        for gap_keyword in ["航空内饰", "高端工业陶瓷", "CNC数控", "IGBT", "半导体封"]:
            try:
                page.locator(f"text={gap_keyword}").first.click()
                page.wait_for_timeout(1500)
                gap_node_found = True
                break
            except:
                continue
        if not gap_node_found:
            # 尝试点击任何带有缺口标记的节点
            try:
                page.locator("text=新能源").nth(0).click()
                page.wait_for_timeout(1000)
            except:
                pass
        page.screenshot(path=os.path.join(OUTPUT_DIR, "06-gap-detail.png"), full_page=False)
        print("      → assets/06-gap-detail.png")
        try:
            page.locator("#panel-close").click()
        except:
            pass

        # 7. 热门行业筛选功能
        print("[7/7] 截取热门行业筛选...")
        page.wait_for_timeout(500)
        try:
            page.locator("#hot-filter").select_option("低空经济")
            page.wait_for_timeout(1000)
        except:
            pass
        page.screenshot(path=os.path.join(OUTPUT_DIR, "07-hot-industry-filter.png"), full_page=False)
        print("      → assets/07-hot-industry-filter.png")

        browser.close()
        print(f"\n✅ 截图完成! 共7张, 保存至 {OUTPUT_DIR}")


if __name__ == "__main__":
    capture()

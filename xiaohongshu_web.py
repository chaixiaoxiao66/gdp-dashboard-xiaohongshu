# -*- coding: utf-8 -*-
"""
小红书文案生成器 - Streamlit Web SaaS版 v1.0
- 支持文旅商家和散客用户双模式
- 预留API接口（豆包/MiniMax）
- 包含天人山水大地艺术园真实数据
"""

import streamlit as st
import json
import random
from typing import List, Optional
from datetime import datetime

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="文旅小红书文案神器",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 样式 ====================

st.markdown("""
<style>
    /* 主色调 */
    :root {
        --primary-color: #FF6B6B;
        --secondary-color: #4ECDC4;
        --bg-color: #F7F9FC;
    }
    
    /* 标题样式 */
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* 卡片样式 */
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* 文案标题 */
    .content-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    /* 标签样式 */
    .tag {
        display: inline-block;
        background: #FFE8E8;
        color: #FF6B6B;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 4px;
    }
    
    /* 红线警告 */
    .red-line-warning {
        background: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    /* 成功提示 */
    .success-box {
        background: #D4EDDA;
        border-left: 4px solid #28A745;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
    
    /* 侧边栏样式 */
    .sidebar-section {
        background: #F8F9FA;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== API配置 ====================

class APIConfig:
    """API配置类"""
    
    # === API配置 ===
    
    # 豆包API（字节跳动）
    DOUBAO_API_KEY = ""
    DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    DOUBAO_MODEL = "doubao-pro-32k"
    
    # MiniMax API
    MINIMAX_API_KEY = ""
    MINIMAX_BASE_URL = "https://api.minimax.chat/v1"
    MINIMAX_MODEL = "abab6.5s-chat"
    
    # OpenAI API（✅ 已配置）
    OPENAI_API_KEY = "sk-hcoq6Nlrjr6UaIThfeWHQeuJVtjLBLz3FaaiYze9Mw9gZGKl"
    OPENAI_BASE_URL = "https://api.xcode.best/v1"  # api111代理地址
    OPENAI_MODEL = "gpt-5.4"
    
    # ========================
    
    @classmethod
    def get_active_api(cls):
        """获取当前激活的API"""
        if cls.OPENAI_API_KEY:
            return "openai", cls.OPENAI_API_KEY, cls.OPENAI_BASE_URL, cls.OPENAI_MODEL
        elif cls.DOUBAO_API_KEY:
            return "doubao", cls.DOUBAO_API_KEY, cls.DOUBAO_BASE_URL, cls.DOUBAO_MODEL
        elif cls.MINIMAX_API_KEY:
            return "minimax", cls.MINIMAX_API_KEY, cls.MINIMAX_BASE_URL, cls.MINIMAX_MODEL
        else:
            return None, None, None, None


# ==================== 红线词库 ====================

RED_LINE_WORDS = {
    "最": "超",
    "第一": "顶级推荐",
    "唯一": "独特",
    "顶级": "超棒",
    "最好": "超好",
    "必去": "推荐去",
    "必打卡": "值得打卡",
    "必玩": "推荐玩",
    "必吃": "推荐吃",
    "一定要": "建议",
    "最低价": "性价比超高",
    "最便宜": "很划算",
    "超便宜": "很划算",
    "白菜价": "很划算",
    "打折": "优惠",
}

FORBIDDEN_WORDS = [
    "包治百病", "疗效", "治疗", "治愈率",
    "加微信", "微信号", "扫码", "二维码",
    "代购", "走私", "免税",
]


# ==================== 景区数据 ====================

class SpotDatabase:
    """景区数据库 - 内置天人山水真实数据"""
    
    # 天人山水大地艺术园（真实数据）
    TIANREN_SHANSHUI = {
        "name": "天人山水大地艺术园",
        "type": "自然+艺术",
        "location": "广东省广州市从化区太平镇天人山水流溪河畔",
        "highlights": [
            "诺诺庄园（网红打卡点）",
            "乐佺·印象馆（文化艺术展）",
            "日夕廊（最美日落观景点）",
            "牛路转角处",
            "湿地文化馆",
            "水月·静轩",
            "花上·清明",
            "清晓·花间",
            "月下·花田",
            "千红不合醴陵过",
            "拾光·畔",
            "花现爱丽丝"
        ],
        "features": [
            "华南最大大地艺术装置",
            "8000种四季花卉",
            "流溪河畔原生态",
            "100+艺术打卡点",
            "研学教育基地",
            "轻奢露营体验"
        ],
        "activities": [
            "四季花季（春樱花、夏荷花、秋粉黛乱子草、冬梅）",
            "艺术展览",
            "研学课程",
            "露营音乐会",
            "自然教育"
        ],
        "target": ["亲子", "情侣", "闺蜜", "研学团建", "摄影爱好者"],
        "price": "门票：108-158元/人（套票）",
        "tips": [
            "建议自驾，园区较大",
            "穿舒适的鞋，带防晒",
            "预约制入园",
            "园区内餐厅人均80-150元",
            "可带宠物入园"
        ],
        "best_time": "全年适宜，春季最佳（2-4月花季）",
        "transportation": "自驾/打车，导航'天人山水大地艺术园'",
        "contact": "官方公众号：天人山水"
    }
    
    SPOTS = {
        "天人山水大地艺术园": TIANREN_SHANSHUI,
    }
    
    @classmethod
    def get_spot_names(cls):
        return list(cls.SPOTS.keys())
    
    @classmethod
    def get_spot(cls, name: str):
        return cls.SPOTS.get(name)


# ==================== 文案生成器 ====================

class ContentGenerator:
    """文案生成器核心类"""
    
    @staticmethod
    def call_openai_api(prompt: str) -> str:
        """调用OpenAI API"""
        import openai
        
        api_key = APIConfig.OPENAI_API_KEY
        base_url = APIConfig.OPENAI_BASE_URL.strip() if APIConfig.OPENAI_BASE_URL else None
        
        if not api_key:
            return None
        
        try:
            if base_url:
                # 使用自定义代理
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
            else:
                # 使用官方API
                client = openai.OpenAI(
                    api_key=api_key
                )
            
            response = client.chat.completions.create(
                model=APIConfig.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的小红书文案专家，帮助文旅从业者生成爆款文案。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            # 显示更友好的错误提示
            if "401" in error_msg or "authentication" in error_msg.lower():
                st.error("❌ API认证失败：请检查API Key是否正确")
            elif "403" in error_msg:
                st.error("❌ API访问被拒绝：请检查API权限或账户余额")
            elif "429" in error_msg:
                st.error("❌ API请求过多：请稍后再试")
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                st.error("❌ 网络连接失败：请检查网络或配置代理")
            else:
                st.error(f"❌ API调用失败：{error_msg}")
            return None
    
    @staticmethod
    def call_api(prompt: str, style: str = "种草风") -> Optional[str]:
        """统一API调用入口"""
        api_name, api_key, base_url, model = APIConfig.get_active_api()
        
        if api_name == "openai" and api_key:
            return ContentGenerator.call_openai_api(prompt)
        elif api_name == "doubao" and api_key:
            return ContentGenerator.call_doubao_api(prompt)
        elif api_name == "minimax" and api_key:
            return ContentGenerator.call_minimax_api(prompt)
        else:
            return None  # 返回None表示使用模拟数据
    
    @staticmethod
    def call_doubao_api(prompt: str) -> str:
        """调用豆包API"""
        import requests
        
        try:
            response = requests.post(
                f"{APIConfig.DOUBAO_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {APIConfig.DOUBAO_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": APIConfig.DOUBAO_MODEL,
                    "messages": [
                        {"role": "system", "content": "你是一个专业的小红书文案专家，帮助文旅从业者生成爆款文案。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.8
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                st.error(f"豆包API调用失败：{response.status_code}")
                return None
        except Exception as e:
            st.error(f"豆包API错误：{str(e)}")
            return None
    
    @staticmethod
    def call_minimax_api(prompt: str) -> str:
        """调用MiniMax API"""
        import requests
        
        try:
            response = requests.post(
                f"{APIConfig.MINIMAX_BASE_URL}/text/chatcompletion_v2",
                headers={
                    "Authorization": f"Bearer {APIConfig.MINIMAX_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": APIConfig.MINIMAX_MODEL,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                st.error(f"MiniMax API调用失败：{response.status_code}")
                return None
        except Exception as e:
            st.error(f"MiniMax API错误：{str(e)}")
            return None
    
    # 小红书爆款标题公式
    TITLE_FORMULAS = {
        "种草风": [
            "{emoji} 发现宝藏！{name}美到窒息！",
            "😭 为什么现在才发现{name}！",
            "✨ {name}｜{target}必打卡清单",
            "{emoji} {name}超全攻略！建议收藏！",
            "📍 {name}，来了就不想走！"
        ],
        "攻略风": [
            "📖 {name}超全攻略｜{target}必看！",
            "⏰ {name}一日游时间线｜超详细！",
            "💰 {name}省钱攻略｜人均{price}玩到嗨！",
            "📍 {name}怎么玩？看完这篇就够了！",
            "⚠️ {name}避坑指南｜去过的人这么说..."
        ],
        "Vlog风": [
            "📹 {name} Vlog｜{time}的治愈时刻",
            "🎬 跟我一起去{name}！",
            "✨ {name} 24小时｜vlog记录",
            "📱 真实探店{name}，发现意外惊喜！",
            "🎥 {name}一日游｜附超详细攻略"
        ],
        "故事风": [
            "💭 我和{name}的故事",
            "🌙 {name}｜一场意外的相遇",
            "写给想去{name}的你",
            "{name}，谢谢你的出现",
            "在{name}，我找到了..."
        ]
    }
    
    @staticmethod
    def generate_titles(spot_data: dict, style: str, count: int = 5) -> List[str]:
        """生成标题"""
        import random
        
        templates = ContentGenerator.TITLE_FORMULAS.get(style, ContentGenerator.TITLE_FORMULAS["种草风"])
        
        emojis = ["🌸", "✨", "🏔️", "🌿", "📍", "💫", "🌊", "🍃"]
        
        titles = []
        for i, template in enumerate(random.sample(templates, min(count, len(templates)))):
            title = template.format(
                name=spot_data.get("name", ""),
                target="、".join(spot_data.get("target", [])[:2]),
                price=spot_data.get("price", "").replace("门票：", "").replace("元/人（套票）", ""),
                time=spot_data.get("best_time", ""),
                emoji=random.choice(emojis)
            )
            titles.append(title)
        
        return titles
    
    @staticmethod
    def generate_content(spot_data: dict, style: str, user_type: str) -> dict:
        """生成正文内容"""
        
        name = spot_data.get("name", "")
        highlights = spot_data.get("highlights", [])[:5]
        features = spot_data.get("features", [])
        location = spot_data.get("location", "")
        price = spot_data.get("price", "")
        tips = spot_data.get("tips", [])
        target = "、".join(spot_data.get("target", [])[:2])
        
        if style == "种草风":
            content = f"""姐妹们！这个宝藏地方我真的要安利一万次！📍{name}

{features[0] if features else '太美了'}！

📍位置：{location}
💰花费：{price}

真的绝了！{target}闭眼冲！

✨【必打卡点】
{chr(10).join(['• ' + h for h in highlights[:3]])}

tips：{tips[0] if tips else '记得提前预约'}"""

        elif style == "攻略风":
            content = f"""整理了一整天的攻略！建议收藏！

📍【基本信息】
景点：{name}
位置：{location}
门票：{price}

🎯【必玩项目】
{chr(10).join(['✅ ' + h for h in highlights[:5]])}

💡【实用Tips】
{chr(10).join(['• ' + t for t in tips[:3]])}

【路线推荐】
上午：抵达→核心景点打卡
中午：园区餐厅用餐
下午：深度游玩→拍照
傍晚：看日落→返程

收藏起来，下次去照着玩！

#{name} #旅行攻略 #保姆级教程"""

        elif style == "Vlog风":
            content = f"""剪辑了一个周末的vlog！

📍地点：{name}
👥同行：{target}

这一趟真的太治愈了！

{features[0] if features else '风景超美'}！
{features[1] if len(features) > 1 else ''}

📸【vlog亮点】
{chr(10).join(['• ' + h for h in highlights[:3]])}

想看完整vlog的姐妹点个赞～

#{name} #旅行vlog #治愈系"""

        else:  # 故事风
            content = f"""一直想来{name}，终于实现了！

记得第一次看到这里的照片
心里就埋下了一颗种子

现在，终于站在这里了

{highlights[0] if highlights else '太美了'}！

那一刻，觉得一切都值得

有些地方，真的要亲身去感受
才能明白它的美

{name}在等你

#{name} #旅行故事 #心路历程"""
        
        return {
            "content": content,
            "highlights": highlights[:3],
            "tags": [name, "旅行推荐", target, "周末去哪儿"]
        }
    
    @staticmethod
    def check_red_line(text: str) -> dict:
        """检查红线词"""
        warnings = []
        replaced = text
        
        for word in FORBIDDEN_WORDS:
            if word in text:
                warnings.append(f"🚫 禁止词：'{word}'，必须删除")
        
        for old, new in RED_LINE_WORDS.items():
            if old in text:
                replaced = replaced.replace(old, new)
                warnings.append(f"⚠️ 已替换：'{old}' → '{new}'")
        
        return {
            "original": text,
            "replaced": replaced,
            "warnings": warnings,
            "has_issue": len(warnings) > 0
        }


# ==================== Streamlit UI ====================

def main():
    """主函数"""
    
    # 标题
    st.markdown('<h1 class="main-title">📱 文旅小红书文案神器</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #666; margin-bottom: 2rem;">
        🚀 一键生成符合小红书规则的爆款文案 | 支持文旅商家和散客用户
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== 侧边栏配置 ====================
    
    with st.sidebar:
        st.markdown("## ⚙️ 配置")
        
        # API配置区域
        with st.expander("🔑 API配置", expanded=True):
            st.info("填入API信息即可使用真实AI生成")
            
            # API服务商选择
            api_provider = st.selectbox("选择API服务商", ["OpenAI", "豆包", "MiniMax"])
            
            if api_provider == "OpenAI":
                openai_key = st.text_input("OpenAI API Key", value="sk-hcoq6Nlrjr6UaIThfeWHQeuJVtjLBLz3FaaiYze9Mw9gZGKl", type="password", help="sk-xxx格式的API Key")
                openai_base_url = st.text_input("API地址", value="https://api.xcode.best/v1", placeholder="https://api.openai.com/v1", help="代理地址，api111填 https://api.xcode.best/v1")
                openai_model = st.selectbox("模型", ["gpt-5.4", "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"])
                
                if openai_key:
                    APIConfig.OPENAI_API_KEY = openai_key
                    APIConfig.OPENAI_BASE_URL = openai_base_url.strip()
                    APIConfig.OPENAI_MODEL = openai_model
                    if openai_base_url:
                        st.success(f"✅ OpenAI API已配置（代理：{openai_base_url}）")
                    else:
                        st.success("✅ OpenAI API已配置（官方API）")
                        
            elif api_provider == "豆包":
                doubao_key = st.text_input("豆包API Key", value="", type="password")
                if doubao_key:
                    APIConfig.DOUBAO_API_KEY = doubao_key
                    st.success("✅ 豆包API已配置")
                    
            else:
                minimax_key = st.text_input("MiniMax API Key", value="", type="password")
                if minimax_key:
                    APIConfig.MINIMAX_API_KEY = minimax_key
                    st.success("✅ MiniMax API已配置")
        
        # 小红书规则
        with st.expander("📋 小红书红线规则", expanded=False):
            st.markdown("""
            **🚫 禁止使用：**
            - 绝对化：最、第一、顶级、唯一
            - 强制词：必去、必打卡、必玩、必吃
            - 价格诱导：最低价、超便宜、白菜价
            - 引流词：加微信、微信号、扫码、二维码
            
            **✅ 正确姿势：**
            - 用"超"、"很"、"非常"替代
            - 用"推荐"、"值得"替代"必"
            - 真实分享，避免夸大
            """)
        
        st.markdown("---")
        st.markdown("Made with ❤️ for 文旅从业者")
    
    # ==================== 主内容区 ====================
    
    # 标签页
    tab1, tab2, tab3 = st.tabs(["📝 快速生成", "🗃️ 景区库", "📊 我的创作"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📍 输入信息")
            
            # 用户类型
            user_type = st.radio(
                "👤 用户类型",
                ["文旅商家（推广景区）", "散客用户（真实分享）"],
                horizontal=True
            )
            
            # 景区选择方式
            input_mode = st.radio(
                "景区输入方式",
                ["选择已有景区", "自定义景区"],
                horizontal=True
            )
            
            if input_mode == "选择已有景区":
                spot_name = st.selectbox(
                    "选择景区",
                    SpotDatabase.get_spot_names()
                )
                spot_data = SpotDatabase.get_spot(spot_name)
                
                if spot_data:
                    st.success(f"✅ 已选择：{spot_data['name']}")
                    
                    # 展示景区信息
                    with st.expander("📖 查看景区详情", expanded=False):
                        st.markdown(f"**类型：** {spot_data['type']}")
                        st.markdown(f"**位置：** {spot_data['location']}")
                        st.markdown(f"**价格：** {spot_data['price']}")
                        st.markdown(f"**最佳时间：** {spot_data['best_time']}")
                        st.markdown(f"**目标人群：** {', '.join(spot_data['target'])}")
                        st.markdown(f"**特色亮点：**")
                        for f in spot_data['features']:
                            st.markdown(f"  - {f}")
            else:
                # 自定义输入
                spot_name = st.text_input("景区名称", placeholder="如：西湖")
                spot_type = st.selectbox("景区类型", ["山水", "古镇", "乐园", "博物馆", "海滩", "城市", "自然"])
                spot_features = st.text_area("特色亮点（每行一个）", placeholder="如：断桥残雪\n雷峰塔\n西湖音乐喷泉")
                spot_location = st.text_input("位置", placeholder="如：浙江杭州")
                
                spot_data = {
                    "name": spot_name,
                    "type": spot_type,
                    "highlights": spot_features.split('\n') if spot_features else [],
                    "features": spot_features.split('\n') if spot_features else [],
                    "location": spot_location,
                    "price": "待定",
                    "tips": ["建议提前预约", "带防晒", "穿舒适的鞋"],
                    "target": ["亲子", "情侣", "闺蜜"]
                }
            
            # 文案风格
            style = st.selectbox(
                "🎨 文案风格",
                ["种草风", "攻略风", "Vlog风", "故事风"]
            )
            
            # 生成数量
            count = st.slider("生成数量", 1, 5, 3)
            
            # 生成按钮
            generate_btn = st.button("🚀 一键生成文案", type="primary", use_container_width=True)
            
            # API状态提示
            api_name, api_key, _, _ = APIConfig.get_active_api()
            if api_key:
                st.success(f"✅ 已连接 {api_name.upper()} API（真实生成）")
            else:
                st.info("ℹ️ 未配置API，使用模拟数据演示")
        
        with col2:
            st.markdown("### 📱 生成结果")
            
            if generate_btn:
                if not spot_name:
                    st.error("请输入景区名称")
                else:
                    api_name, api_key, _, _ = APIConfig.get_active_api()
                    
                    if api_key:
                        # 使用真实API生成
                        with st.spinner(f"🤖 正在通过{api_name.upper()}生成文案..."):
                            # 构建Prompt
                            prompt = f"""你是一个小红书文案专家，帮文旅从业者生成爆款文案。

【小红书红线规则 - 必须遵守】
1. 禁止使用：最、第一、顶级、唯一、必去、必打卡、必玩、必吃
2. 禁止价格诱导：最低价、超便宜、白菜价
3. 禁止引流：加微信、微信号、扫码、二维码
4. 禁止医疗健康类描述
5. 内容必须有价值，不能纯广告

【景区信息】
名称：{spot_data.get('name', '')}
类型：{spot_data.get('type', '')}
位置：{spot_data.get('location', '')}
特色：{', '.join(spot_data.get('features', [])[:5])}
必打卡点：{', '.join(spot_data.get('highlights', [])[:5])}
价格：{spot_data.get('price', '')}
Tips：{', '.join(spot_data.get('tips', [])[:3])}

【用户类型】{'文旅商家（推广景区）' if '商家' in user_type else '散客用户（真实分享）'}
【文案风格】{style}
【数量】{count}条

请生成{count}条小红书文案，每条包含：
1. 吸引人的标题（带emoji）
2. 正文内容（分段清晰，带emoji）
3. 推荐标签（5个热门话题）
4. 配图建议（3张）

格式要求：
- 标题要新颖有趣，能吸引点击
- 正文要真实、有温度，像朋友分享
- 标签要热门相关
- 符合小红书社区规范"""

                            result = ContentGenerator.call_api(prompt, style)
                            
                            if result:
                                st.success(f"✅ 通过{api_name.upper()}成功生成！")
                                
                                # 展示结果
                                st.markdown("---")
                                st.markdown("### 📋 生成结果")
                                st.text_area("生成内容", value=result, height=400, key="api_result")
                                
                                # 红线检测
                                red_line_result = ContentGenerator.check_red_line(result)
                                if red_line_result["has_issue"]:
                                    st.markdown("### 🔍 红线检测报告")
                                    for warning in red_line_result["warnings"]:
                                        if "🚫" in warning:
                                            st.error(warning)
                                        else:
                                            st.warning(warning)
                                else:
                                    st.success("✅ 未检测到红线问题")
                            else:
                                st.error("API调用失败，请检查API配置")
                    else:
                        # 使用模拟数据
                        with st.spinner("正在生成文案（模拟数据）..."):
                            import time
                            time.sleep(0.5)
                            
                            # 生成标题
                            titles = ContentGenerator.generate_titles(spot_data, style, count)
                            
                            # 生成正文
                            content_result = ContentGenerator.generate_content(spot_data, style, user_type)
                            
                            # 红线检测
                            red_line_result = ContentGenerator.check_red_line(content_result["content"])
                            
                            # 展示结果
                            for i, title in enumerate(titles, 1):
                                with st.container():
                                    st.markdown("---")
                                    st.markdown(f"#### 文案 {i}")
                                    
                                    # 标题
                                    st.markdown(f"**📌 标题：**")
                                    st.markdown(f"{title}")
                                    
                                    # 正文
                                    st.markdown(f"**📝 正文：**")
                                    st.text_area(
                                        f"正文_{i}",
                                        value=content_result["content"],
                                        height=200,
                                        key=f"content_{i}"
                                    )
                                    
                                    # 标签
                                    st.markdown(f"**🏷️ 推荐标签：**")
                                    tags_html = " ".join([f"<span class='tag'>#{tag}</span>" for tag in content_result["tags"]])
                                    st.markdown(tags_html, unsafe_allow_html=True)
                                    
                                    # 配图建议
                                    st.markdown(f"**📸 配图建议：**")
                                    for j, img in enumerate(content_result["highlights"], 1):
                                        st.markdown(f"  图{j}：{img}")
                                    
                                    # 复制按钮
                                    full_text = f"{title}\n\n{content_result['content']}\n\n{' '.join(['#'+tag for tag in content_result['tags']])}"
                                    st.button(f"📋 复制文案 {i}", key=f"copy_{i}")
                        
                        # 红线检测报告
                        if red_line_result["has_issue"]:
                            st.markdown("---")
                            st.markdown("### 🔍 红线检测报告")
                            for warning in red_line_result["warnings"]:
                                if "🚫" in warning:
                                    st.error(warning)
                                else:
                                    st.warning(warning)
                        else:
                            st.success("✅ 未检测到红线问题")
    
    with tab2:
        st.markdown("### 🗃️ 景区库")
        
        for name, spot in SpotDatabase.SPOTS.items():
            with st.expander(f"📍 {name}", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**类型：** {spot['type']}")
                    st.markdown(f"**位置：** {spot['location']}")
                    st.markdown(f"**价格：** {spot['price']}")
                    st.markdown(f"**最佳时间：** {spot['best_time']}")
                    st.markdown(f"**交通：** {spot['transportation']}")
                    
                    st.markdown("**✨ 特色亮点：**")
                    for f in spot['features']:
                        st.markdown(f"  - {f}")
                    
                    st.markdown("**🎯 必打卡点：**")
                    for h in spot['highlights']:
                        st.markdown(f"  📍 {h}")
                
                with col2:
                    st.markdown("**👥 目标人群：**")
                    for t in spot['target']:
                        st.markdown(f"  - {t}")
                    
                    st.markdown("**💡 实用Tips：**")
                    for tip in spot['tips']:
                        st.markdown(f"  • {tip}")
    
    with tab3:
        st.markdown("### 📊 我的创作")
        st.info("功能开发中... 即将支持历史记录管理")
        
        # TODO: 后续加入历史记录功能
        st.markdown("""
        **计划功能：**
        - 📁 保存生成过的文案
        - ⭐ 收藏喜欢的文案
        - 📤 导出为Word/Excel
        - 📊 数据统计（生成数量、使用频率）
        """)
    
    # ==================== 底部 ====================
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #999; font-size: 0.8rem;">
        📱 文旅小红书文案神器 v1.0 | 支持商家+散客双模式 | 自动规避红线规则<br>
        Made with ❤️ for 文旅数字化从业者
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
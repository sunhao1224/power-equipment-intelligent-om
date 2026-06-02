"""运维问答服务"""
import random
from datetime import datetime
from app.models.chat import ChatRequest, ChatResponse, Reference
from app.mock_data.knowledge import search_knowledge
from app.mock_data.equipment import get_equipment_by_id


# 模拟的问答回复模板
_ANSWER_TEMPLATES = {
    "温度": "根据您提供的信息和我们的知识库分析，变压器油温异常升高通常需要关注以下几个方面：\n\n"
            "1. **负荷检查**：首先确认当前负荷是否超过额定值，过载运行会导致油温持续上升。\n\n"
            "2. **冷却系统**：检查风扇、油泵等冷却设备是否正常运行，散热器是否有堵塞。\n\n"
            "3. **DGA分析**：建议立即进行油色谱分析，重点关注总烃和C2H2的变化趋势。"
            "若总烃超过150ppm或C2H2超过5ppm，可能存在内部过热或放电故障。\n\n"
            "4. **处置建议**：若油温持续升高且超过85°C，建议立即降低负荷至额定60%，"
            "并安排专业人员进行现场检查。\n\n"
            "根据DL/T 572-2010《电力变压器运行规程》，变压器上层油温不宜超过85°C，"
            "温升不超过55K。",

    "DGA": "根据DL/T 722-2014《变压器油中溶解气体分析和判断导则》，DGA分析的关键指标和判断标准如下：\n\n"
           "**注意值（ppm）**：\n"
           "- 总烃：150 ppm\n"
           "- H2：150 ppm\n"
           "- C2H2：5 ppm（220kV及以上）\n\n"
           "**IEC三比值法**：\n"
           "通过C2H2/C2H4、CH4/H2、C2H4/C2H6三个比值组合判断故障类型：\n"
           "- 局部放电：比值组合 0-1-0\n"
           "- 低温过热（<150°C）：比值组合 0-0-1\n"
           "- 高温过热（>700°C）：比值组合 0-2-2\n"
           "- 电弧放电：比值组合 1-0-2\n\n"
           "**产气速率**：总烃绝对产气速率大于12mL/d应引起注意。",

    "局放": "关于局部放电检测与诊断，以下是专业分析：\n\n"
            "1. **UHF检测法**：特高频法灵敏度高（可达5pC），是GIS局放检测的首选方法。\n\n"
            "2. **PRPD谱图分析**：\n"
            "   - 自由颗粒：全相位分布，幅值分散\n"
            "   - 悬浮电位：对称分布于工频峰值附近\n"
            "   - 绝缘子表面缺陷：集中在0-90°和180-270°区间\n"
            "   - 尖端放电：集中在工频正负峰值\n\n"
            "3. **处理建议**：UHF信号幅值超过300mV应引起重视，"
            "建议结合超声波检测进行定位，必要时安排停电处理。",

    "断路器": "关于断路器运维，以下是关键要点：\n\n"
              "1. **机械特性监测**：断路器故障约70%为机械故障，重点关注：\n"
              "   - 分合闸时间偏差（分闸±3ms，合闸±5ms）\n"
              "   - 行程-时间曲线变化\n"
              "   - 线圈电流波形分析\n\n"
              "2. **SF6气体管理**：\n"
              "   - 压力应保持在额定值±5%范围内\n"
              "   - 年泄漏率不超过1%\n"
              "   - 微水含量：断路器气室≤150μL/L\n\n"
              "3. **操动机构**：液压机构24小时保压试验压降不超过0.5MPa，"
              "操作次数达到厂家规定值应安排检修。",

    "维护": "关于设备维护策略，基于状态的维修（CBM）建议如下：\n\n"
            "**健康指数评估分级**：\n"
            "- 90-100分（优良）：可延长检修周期\n"
            "- 70-89分（合格）：按正常周期检修\n"
            "- 50-69分（注意）：缩短检修周期，安排专项检测\n"
            "- <50分（不合格）：尽快安排停电检修\n\n"
            "**评估维度权重**：\n"
            "- 绝缘状态：40%\n"
            "- 机械性能：25%\n"
            "- 电气性能：25%\n"
            "- 运行历史：10%\n\n"
            "建议根据设备健康状态动态调整维护计划，优先处理健康指数低于70分的设备。",

    "default": "根据您的问题，我从知识库中检索了相关信息。以下是我的分析和建议：\n\n"
               "作为电力设备智能运维系统，我可以为您提供以下方面的专业支持：\n\n"
               "1. **故障诊断**：基于DGA、局放、温度等多源数据的综合故障诊断\n"
               "2. **状态评估**：设备健康指数评估和趋势分析\n"
               "3. **维护决策**：基于状态的智能维护计划生成\n"
               "4. **知识检索**：运维规程、标准、专家经验的语义搜索\n\n"
               "请您提供更具体的问题描述或设备信息，我将为您进行更深入的分析。",
}


class ChatService:
    """运维问答服务"""

    def __init__(self):
        self._conversations: dict[str, list[dict]] = {}

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        message = request.message
        equipment_id = request.equipment_id

        # 搜索相关知识
        knowledge_results = search_knowledge(message, top_k=5)

        # 构建引用
        references = [
            Reference(
                title=kr["title"],
                source=kr["source"],
                relevance=kr["relevance"],
            )
            for kr in knowledge_results
        ]

        # 生成回答
        answer = self._generate_answer(message, equipment_id, knowledge_results)

        # 计算置信度
        confidence = self._calculate_confidence(message, knowledge_results)

        # 记录会话
        conv_id = request.conversation_id
        if conv_id not in self._conversations:
            self._conversations[conv_id] = []
        self._conversations[conv_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat(),
        })
        self._conversations[conv_id].append({
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.now().isoformat(),
        })

        return ChatResponse(
            answer=answer,
            references=references,
            confidence=confidence,
            conversation_id=conv_id,
        )

    def _generate_answer(self, message: str, equipment_id: str | None, knowledge: list[dict]) -> str:
        """生成AI回答（Mock）"""
        message_lower = message.lower()

        # 设备上下文
        equipment_context = ""
        if equipment_id:
            eq = get_equipment_by_id(equipment_id)
            if eq:
                equipment_context = (
                    f"\n\n---\n**当前设备信息**：{eq['name']}（{eq['equipment_id']}）\n"
                    f"- 类型：{eq['type_name']}，型号：{eq['model']}\n"
                    f"- 厂家：{eq['manufacturer']}，电压等级：{eq['voltage_level']}\n"
                    f"- 所属变电站：{eq['substation']}\n"
                    f"- 健康指数：{eq['health_index']}分，状态：{eq['status_name']}\n"
                )

        # 关键词匹配
        for keyword, template in _ANSWER_TEMPLATES.items():
            if keyword == "default":
                continue
            if keyword in message_lower:
                return template + equipment_context

        # 默认回复
        answer = _ANSWER_TEMPLATES["default"]
        if knowledge:
            answer += "\n\n**相关知识参考**：\n"
            for i, kr in enumerate(knowledge[:3], 1):
                answer += f"\n{i}. 《{kr['title']}》（{kr['source']}）"
        return answer + equipment_context

    def _calculate_confidence(self, message: str, knowledge: list[dict]) -> float:
        """计算置信度"""
        if not knowledge:
            return round(random.uniform(0.5, 0.7), 2)

        max_relevance = max(kr["relevance"] for kr in knowledge)
        avg_relevance = sum(kr["relevance"] for kr in knowledge) / len(knowledge)

        confidence = 0.4 * max_relevance + 0.4 * avg_relevance + 0.2 * min(1.0, len(knowledge) / 5)
        return round(min(0.98, max(0.3, confidence)), 2)

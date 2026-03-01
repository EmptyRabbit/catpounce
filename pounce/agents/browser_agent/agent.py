import os
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

from pounce.agents.baes_agent import BaseAgent
from pounce.agents.browser_agent.action_type import Action
from pounce.agents.browser_agent.node.screenshot import ScreenshotNode
from pounce.agents.core.node.visual_planning import VisualPlanningNode
from pounce.agents.core.state import VisualPlanInputState, VisualPlanState


class BrowserAgent(BaseAgent):
    def __init__(self, model, browser, keep_browser=False, report_path: str = None):
        super().__init__(model)
        self.browser = browser
        self.report_path = report_path

    async def get_graph(self):
        builder = StateGraph(VisualPlanState, input_schema=VisualPlanInputState)
        screenshot_node = ScreenshotNode(self.browser)

        builder.add_node('screenshot', screenshot_node.screenshot)
        builder.add_node('planning', VisualPlanningNode.get_next_action)
        builder.add_node('action', self.call_browser_agent)
        builder.add_node('action_analysis', self.call_browser_agent)

        builder.add_edge(START, 'planning')

        memory = MemorySaver()
        graph = builder.compile(name="Browser Agent", checkpointer=memory)
        return graph

    async def run(self, state: VisualPlanInputState[Action], max_step=30) -> VisualPlanState[Action]:
        resp = await self.ainvoke(input=state, recursion_limit=max_step)
        return resp
